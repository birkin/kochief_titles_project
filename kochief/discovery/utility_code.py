# -*- coding: utf-8 -*-

#Sitemaps.

import json
from django.conf import settings
from django.core import urlresolvers, paginator
# from django.utils import simplejson

import urllib

PING_URL = "https://www.google.com/webmasters/tools/ping"

sitemap_limit = 1000
#Base for record view
item_page = 'record'

from django.http import HttpResponse, Http404
from django.template import loader
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.utils.encoding import smart_str
from django.core.paginator import EmptyPage, PageNotAnInteger

def sitemap_index(request, sitemaps):
    domain = settings.APP_DOMAIN.rstrip('/')
    sites = []
    protocol = 'http'
    for section, site in sitemaps.items():
        if callable(site):
            pages = site().paginator.num_pages
        else:
            pages = site.paginator.num_pages
        sitemap_url = urlresolvers.reverse('django.contrib.sitemaps.views.sitemap', kwargs={'section': section})
        sites.append('%s%s' % (domain, sitemap_url))
        if pages > 1:
            for page in range(2, pages+1):
                sites.append('%s/%s?p=%s' % (domain, sitemap_url, page))
    xml = loader.render_to_string('sitemap_index.xml', {'sitemaps': sites})
    return HttpResponse(xml, mimetype='application/xml')

#Override Django sitemap to avoid pulling the site name from the database.
class Sitemap:
    # This limit is defined by Google. See the index documentation at
    # https://sitemaps.org/protocol.php#index.
    limit = sitemap_limit

    def __get(self, name, obj, default=None):
        try:
            attr = getattr(self, name)
        except AttributeError:
            return default
        if callable(attr):
            return attr(obj)
        return attr

    def items(self):
        return []

    def location(self, obj):
        return obj.get_absolute_url()

    def _get_paginator(self):
        if not hasattr(self, "_paginator"):
            self._paginator = paginator.Paginator(self.items(), self.limit)
        return self._paginator
    paginator = property(_get_paginator)

    def get_urls(self, page=1):
        from django.contrib.sites.models import Site
        app_url = settings.BASE_URL
        urls = []
        for item in self.paginator.page(page).object_list:
            loc = "%s%s" % (app_url, self.__get('location', item))
            url_info = {
                'location':   loc,
                'lastmod':    self.__get('lastmod', item, None),
                'changefreq': self.__get('changefreq', item, None),
                'priority':   self.__get('priority', item, None)
            }
            urls.append(url_info)
        return urls

class TitlesSitemap(Sitemap):
    #Need to setup the site domain in Sites.  Use management command
    #in the base application.
    changefreq = "monthly"
    priority = 0.5

    def __init__(self, solr_ids):
        self.solr_ids = solr_ids

    def items(self):
        return self.solr_ids

    def location(self, id):
        return '%s/%s' % (item_page, id)



def make_sitemaps():
    #Query Solr to get all objects."""
    #Number of rows to return each time through the Solr query

    from django.core.cache import cache
    sitemap = cache.get('sitemap')
    if sitemap:
        return sitemap
        #pass
    else:
        pass

    set_size = sitemap_limit
    start = 0
    total = 0
    all = []
    map = {}
    while True:
        solr_url = '%s/select/?q=*:*&version=2.2&rows=%s&start=%s&fl=id&wt=json' %\
                         (settings.SOLR_URL.rstrip('/'),
                          set_size,
                          start)
        resp = urllib.urlopen(solr_url)
        # docs = simplejson.load(resp)
        docs = json.loads( resp )
        start = docs['response']['start']
        max = docs['response']['numFound']
        docs = docs['response']['docs']
        docs = [d['id'] for d in docs]
        #print max, start, len(docs)
        sitemap = TitlesSitemap(docs)
        total += len(docs)
        map['%s' % start] = sitemap
        #Search again if we haven't stored all of the solr ids yet.
        if total < max:
            start += 1
        else:
            break
    #Put sitemap in cache for a day.
    cache.set('sitemap', map, 86400)
    return map

sitemaps = make_sitemaps()



