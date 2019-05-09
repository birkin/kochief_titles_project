# -*- coding: utf-8 -*-

from __future__ import unicode_literals

# Copyright 2007 Casey Durfee
# Copyright 2008 Gabriel Sean Farrell
#
# This file is part of Kochief.
#
# Kochief is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Kochief is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Kochief.  If not, see <https://www.gnu.org/licenses/>.

from datetime import datetime
import json
import logging
import logging.handlers
import os
import pprint
import re
import string
import subprocess
import sys
import time
import urllib

import requests

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponsePermanentRedirect
from django.template import loader, RequestContext
# from django.utils import simplejson
from django.utils.encoding import iri_to_uri
from django.utils.html import escape
from django.utils.http import urlquote
from django.utils.translation import ugettext as _
from django.views.decorators.vary import vary_on_headers
from django.utils import feedgenerator

from lib import info_helper


log = logging.getLogger(__name__)
log_level = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
log.setLevel( log_level[settings.LOG_LEVEL] )
if not logging._handlers:
    handler = logging.FileHandler( settings.LOG_PATH, mode='a', encoding='utf-8', delay=False )
    formatter = logging.Formatter( '[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s' )
    handler.setFormatter( formatter )
    log.addHandler( handler )


def info( request ):
    """ Returns basic data. """
    rq_now = datetime.now()
    commit = info_helper.get_commit()
    branch = info_helper.get_branch()
    info_txt = commit.replace( 'commit', branch )
    resp_now = datetime.now()
    taken = resp_now - rq_now
    d = {
        'request': {
            'url': '%s%s' % ( settings.BASE_URL, request.META.get('REQUEST_URI', request.META['PATH_INFO']) ),
            'timestamp': unicode( rq_now )
        },
        'response': {
            'version': info_txt,
            'timetaken': unicode( taken )
        }
    }
    output = json.dumps( d, sort_keys=True, indent=2 )
    return HttpResponse( output, content_type='application/json; charset=utf-8' )


def error_check( request ):
    """ For checking that admins receive error-emails. """
    if settings.DEBUG == True:
        1/0
    else:
        return HttpResponseNotFound( '<div>404 / Not Found</div>' )



def pubyear_sorter(terms):
    """Utility for sorting date facets by year, then by decade."""
    from operator import itemgetter
    try:
        new_term_list = []
        for term, count in terms:
            term_prefix = int(term[0:2])
            #Hard code the 20 cutoff for now but should do math.
            if term_prefix >= 20:
                new_term_list.append((int(term), term, count))
            else:
                new_term_list.append((int(term[:2]), term, count))

        sorted_list = sorted(new_term_list, key=itemgetter(1, 2), reverse=True)
        new_list = []
        for sort_prefix, term, count in sorted_list:
            new_list.append((term, count))
        return new_list
    except:
        return terms

@vary_on_headers('accept-language', 'accept-encoding')
def index(request):
    log.debug( 'starting index()' )
    ## hack, since APPEND_SLASH is not working
    # request_uri = request.META['REQUEST_URI']
    request_uri = request.META.get( 'REQUEST_URI', request.META['PATH_INFO'] )
    log.debug( 'request_uri, ```%s```' % request_uri )
    if request_uri[-1] != '/':
        log.debug( 'will redirect with slash' )
        correct_request_uri = request_uri + '/'
        return HttpResponsePermanentRedirect( correct_request_uri )
    ##
    # cache_key = request.META['HTTP_HOST']
    cache_key = request.META.get( 'HTTP_HOST', '' )
    response = cache.get(cache_key)
    if response:
        log.debug( 'response was from cache' )
        return response
    # context = RequestContext(request)
    context = {}
    params = [
        ('rows', 0),
        ('facet', 'true'),
        ('facet.limit', settings.INDEX_FACET_TERMS),
        ('facet.mincount', 1),
        ('q.alt', '*:*'),
    ]
    for facet_option in settings.INDEX_FACETS:
        params.append(('facet.field', facet_option['field'] + '_facet'))
        # sort facets by name vs. count as per the config.py file
        if not facet_option['sort_by_count']:
            #Solr 1.4 and newer, false becomes index.
            #https://wiki.apache.org/solr/SimpleFacetParameters#facet.sort
            params.append(('f.%s_facet.facet.sort' % facet_option['field'],
                'index'))

    solr_url, solr_response = get_solr_response(params)
    log.debug( 'solr_url, ```%s```' % solr_url )
    log.debug( 'solr_response, ```%s```' % solr_response )
    try:
        facet_fields = solr_response['facet_counts']['facet_fields']
    except KeyError, e:
        raise KeyError, 'Key not found in Solr response: %s' % e
    facets = []
    for facet_option in settings.INDEX_FACETS:
        field = facet_option['field']
        terms = facet_fields[field + '_facet']
        #Handle pubyear specially
        if field == 'pubyear':
            terms = pubyear_sorter(terms)
        facet = {
            'terms': terms,
            'field': field,
            'name': facet_option['name'],
        }
        facets.append(facet)
    context['facets'] = facets
    context['INDEX_FACET_TERMS'] = settings.INDEX_FACET_TERMS
    template = loader.get_template('discovery/index.html')
    # response = HttpResponse(template.render(context))
    response = HttpResponse(template.render(context))
    if not settings.DEBUG:
        cache.set(cache_key, response)
    log.debug( 'returning index response')
    return response

    ## end def index()


@vary_on_headers('accept-language', 'accept-encoding')
def search(request):
    log.debug( 'starting search()' )
    # context = RequestContext(request)
    # log.debug( 'RequestContext(request), ```%s```' % pprint.pformat(context) )
    context = {}
    if request.GET.get('history'):
        log.debug( 'history-get detected' )
        template = loader.get_template('discovery/search_history.html')
        return HttpResponse(template.render(context))

    context = get_search_results( request )

    # return HttpResponse( 'coming3' )

    # log.debug( 'context, ```%s```' % pprint.pformat(context) )
    # context.update(get_search_results(request))
    context['ILS'] = settings.ILS
    context['MAJAX2_URL'] = settings.MAJAX2_URL
    context['BASE_URL'] = settings.BASE_URL
    log.debug( 'WHOLE context, ```%s```' % pprint.pformat(context) )

    template = loader.get_template('discovery/results.html')
    log.debug( 'about to prepare response' )
    resp = template.render( context )
    log.debug( 'about to return response' )
    # return HttpResponse(template.render(context))
    return HttpResponse( resp )
    # return HttpResponse( 'FOO' )


def term_summary(doc, target):
    """Returns a summary of terms from the solr doc."""
    base_params = [
        ('rows', 0),
        ('q.alt', '*:*'),
    ]
    terms = []
    for term in doc.get(target, []):
        params = base_params[:]
        params.append(('fq', '%s_facet:"%s"' % (target, term)))
        solr_url, solr_response = get_solr_response(params)
        terms.append((solr_response['response']['numFound'], term))
    terms.sort()
    terms.reverse()
    terms = [(x[1], x[0]) for x in terms]
    return terms

@vary_on_headers('accept-language', 'accept-encoding')
def record(request, record_id):
    context = RequestContext(request)
    solr_url, doc = get_record(record_id)
    catalog_url = settings.CATALOG_RECORD_URL % record_id
    #If not doc can be found in index send to catalog.
    if not doc:
        return HttpResponsePermanentRedirect(catalog_url)
    context['doc'] = doc
    doc['record_url'] = catalog_url
    context['DEBUG'] = settings.DEBUG
    context['solr_url'] = solr_url
    context['disciplines'] = term_summary(doc, 'discipline')
    context['subject_terms'] = term_summary(doc, 'subject')
    context['MAJAX_URL'] = settings.MAJAX_URL
    template = loader.get_template('discovery/record.html')
    return HttpResponse(template.render(context))


def unapi(request):
    # context = RequestContext(request)
    context = {}
    identifier = request.GET.get('id')
    format = request.GET.get('format')
    if identifier and format:
        solr_url, doc = get_record(identifier)
        if format == 'oai_dc':
            # we'll include test for record_type when we have
            # different types of records
            #if doc['record_type'] == 'book':
            element_map = {
                'identifier': ['isbn', 'upc'],
                'title': ['title'],
                'publisher': ['publisher'],
                'language': ['language'],
                'description': ['description'],
                'subject': ['subject'],
                'date': ['year'],
                'contributor': ['name'],
                'format': ['format'],
            }
            elements = []
            for name in element_map:
                elements.extend(get_elements(name, element_map[name], doc))
            context['elements'] = elements
            template = loader.get_template('discovery/unapi-oai_dc.xml')
            # return HttpResponse(template.render(context),
            #         mimetype='application/xml')
            return HttpResponse( template.render(context), content_type='application/xml; charset=utf-8' )
        if format == 'mods':
            context['doc'] = doc
            template = loader.get_template('discovery/unapi-mods.xml')
            # return HttpResponse(template.render(context),
            #         mimetype='application/xml')
            return HttpResponse( template.render(context), content_type='application/xml; charset=utf-8' )
        else:
            raise Http404 # should be 406 -- see https://unapi.info/specs/
    if identifier:
        context['id'] = identifier
    template = loader.get_template('discovery/unapi.xml')
    # return HttpResponse(template.render(context), mimetype='application/xml')
    return HttpResponse( template.render(context), content_type='application/xml; charset=utf-8' )


def rssFeed(request):
    log.debug( 'starting rssFeed()' )
    log.debug( 'request, ```%s```' % pprint.pformat(request.__dict__) )

    from django.utils.html import escape as html_escape
    def remove_html_tags(data):
        p = re.compile(r'<.*?>')
        p = p.sub('', data)
        return p.replace('&quot;', ' ')
    context = RequestContext(request)
    log.debug( 'type(context), `%s`' % type(context) )
    log.debug( 'context.__dict__ before update, ```%s```' % pprint.pformat(context.__dict__) )

    context.update(get_search_results(request))
    log.debug( 'context.__dict__ after update, ```%s```' % pprint.pformat(context.__dict__) )

    context['ILS'] = settings.ILS
    results = context['response']['docs']
    limits_param = request.GET.get('limits', '')
    limits, fq_params = pull_limits(limits_param)
    query = request.GET.get('q', '')
    log.debug( 'query, ```%s```' % query )

    full_query_str = get_full_query_str(query, limits)
    log.debug( 'full_query_str, ```%s```' % full_query_str )

    feed = feedgenerator.Rss201rev2Feed(title='BUL new books in %s' % remove_html_tags(full_query_str),
                                   link=settings.CATALOG_URL,
                                   description='BUL new books %s' % remove_html_tags(full_query_str),
                                   language=u"en")
    for result in results:
        if result.has_key('discipline'):
            summary = "%s.  " % ", ".join(sorted(result['discipline']))
        else:
            summary = ""
        if result.has_key('summary'):
            if len(result['summary']) > 0:
                summary += "%s." % result['summary'][0]
        feed.add_item(title=result['title'],
                      link=result['record_url'],
                      unique_id=result['record_url'],
                      description=html_escape(summary)
                      #pubdate=result['accession_date']
                      )
    # response = HttpResponse(mimetype='application/xml')
    response = HttpResponse(content_type='application/xml')
    feed.write(response, 'utf-8')
    return response


def get_elements(name, fields, doc):
    elements = []
    for field in fields:
        if field in doc:
            field_values = doc[field]
            if not hasattr(field_values, '__iter__'):
                field_values = [field_values]
            for value in field_values:
                element = {'name': name, 'terms': []}
                if field == 'isbn':
                    element['terms'].append('ISBN:%s' % value)
                elif field == 'upc':
                    element['terms'].append('UPC:%s' % value)
                else:
                    element['terms'].append(value)
                elements.append(element)
    return elements

def get_record(id):
    id_query = 'id:%s' % id
    params = [
        ('q.alt', '*:*'),
        ('fq', id_query.encode('utf8')),
    ]
    solr_url, solr_response = get_solr_response(params)
    try:
        doc = solr_response['response']['docs'][0]
    except IndexError:
        return (solr_url, None)
        #raise Http404
    return (solr_url, doc)


LIMITS_RE = re.compile(r"""
(
  [+-]?      # grab an optional + or -
  [\w]+      # then a word
):           # then a colon
(
  ".*?"|     # then anything surrounded by quotes
  \(.*?\)|   # or parentheses
  \[.*?\]|   # or brackets,
  [\S]+      # or non-whitespace strings
)
""", re.VERBOSE | re.UNICODE)
def pull_limits(limits):
    """
    Pulls individual limit fields and queries out of a combined
    "limits" string and returns (1) a list of limits and (2) a list
    of fq parameters, with "_facet" added to the end of each field,
    to send on to Solr.
    """
    log.debug( 'starting pull_limits()' )
    log.debug( 'limits initially, ```%s```' % pprint.pformat(limits) )
    if '%' in limits:  # occurs on dev & production, not localbox
        limits = urllib.unquote( limits )
        log.debug( 'limits now, ```%s```' % pprint.pformat(limits) )
    parsed_limits = LIMITS_RE.findall(limits)
    limit_list = []
    fq_params = []
    for limit in parsed_limits:
        field, query = limit
        limit = u'%s:%s' % (field, query)
        limit_list.append(limit)
        fq_param = u'%s_facet:%s' % (field, query)
        fq_params.append(fq_param)
    log.debug( 'limit_list, ```%s```' % pprint.pformat(limit_list) )
    log.debug( 'fq_params, ```%s```' % pprint.pformat(fq_params) )
    return limit_list, fq_params
# def pull_limits(limits):
#     """
#     Pulls individual limit fields and queries out of a combined
#     "limits" string and returns (1) a list of limits and (2) a list
#     of fq parameters, with "_facet" added to the end of each field,
#     to send on to Solr.
#     """
#     log.debug( 'starting pull_limits()' )
#     log.debug( 'limits, ```%s```' % pprint.pformat(limits) )
#     parsed_limits = LIMITS_RE.findall(limits)
#     limit_list = []
#     fq_params = []
#     for limit in parsed_limits:
#         field, query = limit
#         limit = u'%s:%s' % (field, query)
#         limit_list.append(limit)
#         fq_param = u'%s_facet:%s' % (field, query)
#         fq_params.append(fq_param)
#     log.debug( 'limit_list, ```%s```' % pprint.pformat(limit_list) )
#     log.debug( 'fq_params, ```%s```' % pprint.pformat(fq_params) )
#     return limit_list, fq_params


POWER_SEARCH_RE = re.compile(r"""
".+?"|         # ignore anything surrounded by quotes
(
  (?:
    [+-]?      # grab an optional + or -
    [\w]+:     # then a word with a colon
  )
  (?:
    ".+?"|     # then anything surrounded by quotes
    \(.+?\)|   # or parentheses
    \[.+?\]|   # or brackets,
    [\S]+      # or non-whitespace strings
  )
)
""", re.VERBOSE | re.UNICODE)
def pull_power(query):
    """
    Pulls "power search" parts out of the query.  It returns
    (1) the query without those parts and (2) a list of those parts.

    >>> query = 'title:"tar baby" "toni morrison" -topic:(dogs justice) fiction "the book:an adventure" +author:john'
    >>> pull_power(query)
    (' "toni morrison"  fiction "the book:an adventure" ', ['title:"tar baby"', '-topic:(dogs justice)', '+author:john'])
    >>>
    """
    power_list = POWER_SEARCH_RE.findall(query)
    # drop empty strings
    power_list = [x for x in power_list if x]
    # escape for re
    escaped_power = [re.escape(x) for x in power_list]
    powerless_query = re.sub('|'.join(escaped_power), '', query)
    return powerless_query, power_list

def get_solr_response(params, host=None):
    log.debug( 'starting get_solr_response()' )
    default_params = [
        ('wt', 'json'),
        ('json.nl', 'arrarr'), # for returning facets nicer
        # ('qt', 'dismax'), # use DisMaxRequestHandler
        ('defType', 'dismax'), # use DisMaxRequestHandler
    ]
    params.extend(default_params)
    #Hack to add support for a query that will return all docs
    #without a discipline field.
    for stype, arg in params:
        if stype == 'q' and arg == 'no_discipline':
            #params.pop(index(params(stype, arg)))
            query_spot = params.index((stype, arg))
            params[query_spot] = ('q', '-(-discipline:[start TO finish] AND discipline:[* TO *])')
            dismax_spot = params.index(('qt','dismax'))
            params.pop(dismax_spot)
        elif stype == 'q' and arg == 'old_records':
            query_spot = params.index((stype, arg))
            params[query_spot] = ('q', settings.EXPIRED_RECORDS_QUERY)
            dismax_spot = params.index(('qt','dismax'))
            params.pop(dismax_spot)
        elif stype == 'q' and arg == 'not_updated_records':
            query_spot = params.index((stype, arg))
            params[query_spot] = ('q', settings.NOT_UPDATED_RECORDS_QUERY)
            dismax_spot = params.index(('qt','dismax'))
            params.pop(dismax_spot)

    urlparams = urllib.urlencode(params)
    url = '%sselect?%s' % (settings.SOLR_URL, urlparams)
    try:
        # solr_response = urllib.urlopen(url)
        solr_response = requests.get( url, timeout=30 )
    except IOError:
        raise IOError, 'Unable to connect to the Solr instance.'
    try:
        # response = simplejson.load(solr_response)
        response = json.loads( solr_response.content )
    except ValueError, e:
        # Assign so error is in variables at Django error screen
        solr_error = urllib.urlopen(url).read()
        raise ValueError, 'Solr response was not a JSON object.'
    return url, response


def get_search_results(request):
    log.debug( 'starting get_search_results()' )
    query = request.GET.get('q', '')
    log.debug( 'query, ```%s```' % query )

    page_str = request.GET.get('page')
    try:
        page = int(page_str)
    except (TypeError, ValueError):
        page = 1
    #cache_key = '%s~%s' % (query, page)
    cache_key = request.META['QUERY_STRING']
    log.debug( 'cache_key, `%s`' % cache_key )

    context = cache.get(cache_key)
    if context:
        log.debug( 'returning cached context' )
        return context
    context = {}
    context['current_sort'] = _('newest')
    context['sorts'] = [x[0] for x in settings.SORTS]
    zero_index = (settings.ITEMS_PER_PAGE * (page - 1))
    params = [
        ('rows', settings.ITEMS_PER_PAGE),
        ('facet', 'true'),
        ('facet.limit', settings.MAX_FACET_TERMS_EXPANDED),
        ('facet.mincount', 1),
        ('start', zero_index)
    ]
    for facet in settings.FACETS:
        params.append(('facet.field', facet['field'] + '_facet'))
        # sort facets by name vs. count as per the config.py file
        if not facet['sort_by_count']:
            params.append(('f.%s.facet.sort' % facet['field'], 'false'))
    powerless_query, field_queries = pull_power(query)
    if not powerless_query.strip() or powerless_query == '*':
        log.debug( 'handling initial powerless_query, ```%s```' % powerless_query.encode('utf-8') )
        params.append(('q.alt', '*:*'))
        context['sorts'] = [x[0] for x in settings.SORTS
                if x[0] != _('relevance')]
    else:
        # params.append(('q', powerless_query.encode('utf8')))
        log.debug( 'building the q.alt with powerless_query, ```%s```' % powerless_query.encode('utf-8') )
        params.append( ('q.alt', '"%s"' % powerless_query.encode('utf8')) )
        context['current_sort'] = _('relevance')
    for field_query in field_queries:
        log.debug( 'adding ->fq<- here' )
        params.append(('fq', field_query.encode('utf8')))
    limits_param = request.GET.get('limits', '')
    limits, fq_params = pull_limits(limits_param)
    for fq_param in fq_params:
        log.debug( 'fq_param, ```%s```' % fq_param )
        params.append(('fq', fq_param.encode('utf8')))

    sort = request.GET.get('sort')
    #Sort by newest by default.
    if not sort:
        sort = 'newest'
    if sort:
        context['current_sort'] = sort
        for sort_mapping in settings.SORTS:
            if sort_mapping[0] == sort:
                mapped_sort = sort_mapping[1]
        params.append(('sort', mapped_sort))
    # TODO: set up for nice display page for queries that return no results
    # or cause solr errors
    log.debug( 'params, ```%s```' % params )
    try:
        solr_url, solr_response = get_solr_response(params)
        log.debug( 'solr_url, ```%s```' % solr_url )
    except ValueError:
        return {'query': query}
    log.debug( 'context before update, ```%s...```' % pprint.pformat(context)[0:500] )
    context.update(solr_response)
    log.debug( 'context after update, ```%s...```' % pprint.pformat(context)[0:500] )

    # augment item results.
    count = 1
    for record in context['response']['docs']:
        record['count'] = count + zero_index
        count += 1
        record['name'] = record.get('personal_name', []) + \
                record.get('corporate_name', [])
        if settings.CATALOG_RECORD_URL:
            record['record_url'] = settings.CATALOG_RECORD_URL % record['id']
        else:
            record['record_url'] = reverse('discovery-record',
                    args=[record['id']])

        #needed for amazon book covers and isbn to be displayable
        if 'isbn' in record:
            record['isbn_numeric'] = ''.join( [ x for x in record['isbn'] if ( x.isdigit() or x.lower() == "x" ) ] )
        #make an array out of Serials Solutions Name and URL
        if 'SSdata' in record:
            record['SSurldetails']=[]
            for items in record['SSdata']:
                SSurlitemdetails=items.split('|')
                record['SSurldetails'].append(SSurlitemdetails)
    log.debug( 'augmenting complete' )

    # re-majigger facets
    facet_counts = context['facet_counts']
    del context['facet_counts']
    facet_fields = facet_counts['facet_fields']
    facets = []
    for facet_option in settings.FACETS:
        field = facet_option['field']
        all_terms = facet_fields[field + '_facet']
        terms = []
        # drop terms found in limits
        for term, count in all_terms:
            limit = '%s:"%s"' % (field, term)
            if limit not in limits:
                terms.append((term, count))
        if not terms:
            continue
        #Handle pubyear specially
        if field == 'pubyear':
            terms = pubyear_sorter(terms)
        if len(terms) > settings.MAX_FACET_TERMS_BASIC:
            extended_terms = terms[settings.MAX_FACET_TERMS_BASIC:]
            terms = terms[:settings.MAX_FACET_TERMS_BASIC]
            has_more = True
        else:
            extended_terms = []
            has_more = False

        facet = {
            'terms': terms,
            'extended_terms': extended_terms,
            'field': field,
            'name': facet_option['name'],
            'has_more': has_more,
        }
        facets.append(facet)
    log.debug( 're-majigger complete' )

    #find out if callnumlayerone is a limit and remove it from the facets
    #dictionary if it is so that only callnumlayer2 is displayed (i.e. if
    #100's dewey is limited, display the 10's)
    callnumlayeronefound = 0
    callnumlayertwofound = 0
    if limits:
        for limitOn in limits:
            if limitOn[:15] == 'callnumlayerone':
                callnumlayeronefound = 1
        for limitOn in limits:
            if limitOn[:15] == 'callnumlayertwo':
                callnumlayertwofound = 1
    #if callnumlayerone was not found to be a limit, remove
    #callnumlayertwo so that only callnumlayerone displays
    #(ie, show the 100's dewey only instead of 100's and 10's)
    if callnumlayeronefound == 1 or (callnumlayeronefound == 0 and callnumlayertwofound == 1):
        count = 0
        for f in facets:
            if f['field'] == 'callnumlayerone':
                del facets[count]
                break
            count += 1

    if callnumlayeronefound == 0 or (callnumlayeronefound == 1 and callnumlayertwofound == 1):
        count = 0
        for f in facets:
            if f['field'] == 'callnumlayertwo':
                del facets[count]
                break
            count += 1
    log.debug( 'callnumlayerone check done' )

    context['facets'] = facets
    context['format'] = request.GET.get('format', None)
    context['limits'] = limits
    context['limits_param'] = limits_param
    # limits_str for use in blocktrans
    limits_str = _(' and ').join(['<strong>%s</strong>' % x for x in limits])
    context['limits_str'] = limits_str
    full_query_str = get_full_query_str(query, limits)
    context['full_query_str'] = full_query_str
    context['get'] = request.META['QUERY_STRING']
    context['query'] = query
    number_found = context['response']['numFound']
    context['number_found'] = number_found
    context['start_number'] = zero_index + 1
    context['end_number'] = min(number_found, settings.ITEMS_PER_PAGE * page)
    context['pagination'] = do_pagination(page, number_found,
            settings.ITEMS_PER_PAGE)
    context['DEBUG'] = settings.DEBUG
    context['solr_url'] = solr_url
    log.debug( 'main context work complete' )
    set_search_history(request, full_query_str)
    log.debug( 'search history updated' )
    if not settings.DEBUG:
        # only cache for production
        log.debug( 'cache set' )
        cache.set(cache_key, context, settings.SEARCH_CACHE_TIME)
    test = json.dumps( context )
    log.debug( 'returning context' )
    return context

    ## end def get_search_results(request):


# def get_search_results(request):
#     log.debug( 'starting get_search_results()' )
#     query = request.GET.get('q', '')
#     log.debug( 'query, ```%s```' % query )

#     page_str = request.GET.get('page')
#     try:
#         page = int(page_str)
#     except (TypeError, ValueError):
#         page = 1
#     #cache_key = '%s~%s' % (query, page)
#     cache_key = request.META['QUERY_STRING']
#     log.debug( 'cache_key, `%s`' % cache_key )

#     context = cache.get(cache_key)
#     if context:
#         log.debug( 'returning cached context' )
#         return context
#     context = {}
#     context['current_sort'] = _('newest')
#     context['sorts'] = [x[0] for x in settings.SORTS]
#     zero_index = (settings.ITEMS_PER_PAGE * (page - 1))
#     params = [
#         ('rows', settings.ITEMS_PER_PAGE),
#         ('facet', 'true'),
#         ('facet.limit', settings.MAX_FACET_TERMS_EXPANDED),
#         ('facet.mincount', 1),
#         ('start', zero_index)
#     ]
#     for facet in settings.FACETS:
#         params.append(('facet.field', facet['field'] + '_facet'))
#         # sort facets by name vs. count as per the config.py file
#         if not facet['sort_by_count']:
#             params.append(('f.%s.facet.sort' % facet['field'], 'false'))
#     powerless_query, field_queries = pull_power(query)
#     if not powerless_query.strip() or powerless_query == '*':
#         params.append(('q.alt', '*:*'))
#         context['sorts'] = [x[0] for x in settings.SORTS
#                 if x[0] != _('relevance')]
#     else:
#         params.append(('q', powerless_query.encode('utf8')))
#         context['current_sort'] = _('relevance')
#     for field_query in field_queries:
#         log.debug( 'adding ->fq<- here' )
#         params.append(('fq', field_query.encode('utf8')))
#     limits_param = request.GET.get('limits', '')
#     limits, fq_params = pull_limits(limits_param)
#     for fq_param in fq_params:
#         log.debug( 'fq_param, ```%s```' % fq_param )
#         params.append(('fq', fq_param.encode('utf8')))

#     sort = request.GET.get('sort')
#     #Sort by newest by default.
#     if not sort:
#         sort = 'newest'
#     if sort:
#         context['current_sort'] = sort
#         for sort_mapping in settings.SORTS:
#             if sort_mapping[0] == sort:
#                 mapped_sort = sort_mapping[1]
#         params.append(('sort', mapped_sort))
#     # TODO: set up for nice display page for queries that return no results
#     # or cause solr errors
#     log.debug( 'params, ```%s```' % params )
#     try:
#         solr_url, solr_response = get_solr_response(params)
#         log.debug( 'solr_url, ```%s```' % solr_url )
#     except ValueError:
#         return {'query': query}
#     log.debug( 'context before update, ```%s...```' % pprint.pformat(context)[0:500] )
#     context.update(solr_response)
#     log.debug( 'context after update, ```%s...```' % pprint.pformat(context)[0:500] )

#     # augment item results.
#     count = 1
#     for record in context['response']['docs']:
#         record['count'] = count + zero_index
#         count += 1
#         record['name'] = record.get('personal_name', []) + \
#                 record.get('corporate_name', [])
#         if settings.CATALOG_RECORD_URL:
#             record['record_url'] = settings.CATALOG_RECORD_URL % record['id']
#         else:
#             record['record_url'] = reverse('discovery-record',
#                     args=[record['id']])

#         #needed for amazon book covers and isbn to be displayable
#         if 'isbn' in record:
#             record['isbn_numeric'] = ''.join( [ x for x in record['isbn'] if ( x.isdigit() or x.lower() == "x" ) ] )
#         #make an array out of Serials Solutions Name and URL
#         if 'SSdata' in record:
#             record['SSurldetails']=[]
#             for items in record['SSdata']:
#                 SSurlitemdetails=items.split('|')
#                 record['SSurldetails'].append(SSurlitemdetails)
#     log.debug( 'augmenting complete' )

#     # re-majigger facets
#     facet_counts = context['facet_counts']
#     del context['facet_counts']
#     facet_fields = facet_counts['facet_fields']
#     facets = []
#     for facet_option in settings.FACETS:
#         field = facet_option['field']
#         all_terms = facet_fields[field + '_facet']
#         terms = []
#         # drop terms found in limits
#         for term, count in all_terms:
#             limit = '%s:"%s"' % (field, term)
#             if limit not in limits:
#                 terms.append((term, count))
#         if not terms:
#             continue
#         #Handle pubyear specially
#         if field == 'pubyear':
#             terms = pubyear_sorter(terms)
#         if len(terms) > settings.MAX_FACET_TERMS_BASIC:
#             extended_terms = terms[settings.MAX_FACET_TERMS_BASIC:]
#             terms = terms[:settings.MAX_FACET_TERMS_BASIC]
#             has_more = True
#         else:
#             extended_terms = []
#             has_more = False

#         facet = {
#             'terms': terms,
#             'extended_terms': extended_terms,
#             'field': field,
#             'name': facet_option['name'],
#             'has_more': has_more,
#         }
#         facets.append(facet)
#     log.debug( 're-majigger complete' )

#     #find out if callnumlayerone is a limit and remove it from the facets
#     #dictionary if it is so that only callnumlayer2 is displayed (i.e. if
#     #100's dewey is limited, display the 10's)
#     callnumlayeronefound = 0
#     callnumlayertwofound = 0
#     if limits:
#         for limitOn in limits:
#             if limitOn[:15] == 'callnumlayerone':
#                 callnumlayeronefound = 1
#         for limitOn in limits:
#             if limitOn[:15] == 'callnumlayertwo':
#                 callnumlayertwofound = 1
#     #if callnumlayerone was not found to be a limit, remove
#     #callnumlayertwo so that only callnumlayerone displays
#     #(ie, show the 100's dewey only instead of 100's and 10's)
#     if callnumlayeronefound == 1 or (callnumlayeronefound == 0 and callnumlayertwofound == 1):
#         count = 0
#         for f in facets:
#             if f['field'] == 'callnumlayerone':
#                 del facets[count]
#                 break
#             count += 1

#     if callnumlayeronefound == 0 or (callnumlayeronefound == 1 and callnumlayertwofound == 1):
#         count = 0
#         for f in facets:
#             if f['field'] == 'callnumlayertwo':
#                 del facets[count]
#                 break
#             count += 1
#     log.debug( 'callnumlayerone check done' )

#     context['facets'] = facets
#     context['format'] = request.GET.get('format', None)
#     context['limits'] = limits
#     context['limits_param'] = limits_param
#     # limits_str for use in blocktrans
#     limits_str = _(' and ').join(['<strong>%s</strong>' % x for x in limits])
#     context['limits_str'] = limits_str
#     full_query_str = get_full_query_str(query, limits)
#     context['full_query_str'] = full_query_str
#     context['get'] = request.META['QUERY_STRING']
#     context['query'] = query
#     number_found = context['response']['numFound']
#     context['number_found'] = number_found
#     context['start_number'] = zero_index + 1
#     context['end_number'] = min(number_found, settings.ITEMS_PER_PAGE * page)
#     context['pagination'] = do_pagination(page, number_found,
#             settings.ITEMS_PER_PAGE)
#     context['DEBUG'] = settings.DEBUG
#     context['solr_url'] = solr_url
#     log.debug( 'main context work complete' )
#     set_search_history(request, full_query_str)
#     log.debug( 'search history updated' )
#     if not settings.DEBUG:
#         # only cache for production
#         log.debug( 'cache set' )
#         cache.set(cache_key, context, settings.SEARCH_CACHE_TIME)
#     test = json.dumps( context )
#     log.debug( 'returning context' )
#     return context

#     ## end def get_search_results(request):


def set_search_history(request, full_query_str):
    timestamp = unicode( datetime.now() )
    search_data = (request.get_full_path(), full_query_str, timestamp)
    search_history = request.session.get('search_history')
    if search_history:
        # don't add it if it's the same as the last search
        #if search_history[0][0] != search_data[0]:
        #    search_history.insert(0, search_data)
        # remove earlier searches that are the same
        for past_search_data in search_history:
            if past_search_data[0] == search_data[0]:
                search_history.remove(past_search_data)
        search_history.insert(0, search_data)
    else:
        search_history = [search_data]
    request.session['search_history'] = search_history[:10]

def get_full_query_str(query, limits):
    # TODO: need to escape query and limits, then apply "safe" filter in
    # template
    full_query_list = []
    if query:
        full_query_list.append('<strong>%s</strong>' % escape(query))
    else:
        full_query_list.append(_('everything'))
    if limits:
        full_query_list.append(_(' with '))
        limits_str = _(' and ').join(['<strong>%s</strong>' % escape(x) for x in limits])
        full_query_list.append(limits_str)
    return ''.join(full_query_list)

def do_pagination(this_page_num, total, per_page):
    if total % per_page:
        last_page_num = (total // per_page) + 1
    else:
        last_page_num = (total // per_page)
    if this_page_num < 8:
        start_page_num = 1
    elif last_page_num - this_page_num < 7:
        start_page_num = max(last_page_num - 10, 1)
    else:
        start_page_num = this_page_num - 5
    end_page_num = min(last_page_num, start_page_num + 10)

    pages = []
    for page_num in range(start_page_num, end_page_num + 1):
        pages.append({
            'selected': page_num == this_page_num,
            'start': ((page_num - 1) * per_page) + 1,
            'end': min(total, page_num * per_page),
            'number': page_num,
        })

    first_page = last_page = previous_page = next_page = None
    if start_page_num > 1:
        first_page = {
            'start': 1,
            'end': per_page,
            'number': 1,
        }
    if end_page_num < last_page_num:
        last_page = {
            'start': ((last_page_num - 1) * per_page) + 1,
            'end': total,
            'number': last_page_num,
        }
    if this_page_num > 1:
        previous_page_num = this_page_num - 1
        previous_page = {
            'start': ((previous_page_num - 1) * per_page) + 1,
            'end': previous_page_num * per_page,
            'number': previous_page_num,
        }
    if this_page_num < last_page_num:
        next_page_num = this_page_num + 1
        next_page = {
            'start': ((next_page_num - 1) * per_page) + 1,
            'end': next_page_num * per_page,
            'number': next_page_num,
        }

    variables = {
        'pages': pages,
        'previous_page': previous_page,
        'next_page': next_page,
        'first_page': first_page,
        'last_page': last_page,
    }
    return variables



