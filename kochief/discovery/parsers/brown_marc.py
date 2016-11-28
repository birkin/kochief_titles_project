"""Brown implementation of a Kochief MARC parser using solr.py."""

import sys
if sys.getdefaultencoding() == 'ascii':
    reload(sys)
    sys.setdefaultencoding( 'utf-8' )  # hack; TODO, handle strings & unicode explicitly

import datetime
import logging
import os
import pprint
import re
import sys
import time
import unicodedata
import urllib
import urllib2
from operator import itemgetter, attrgetter


#Do this for now.  Put as management command in the future
#allow script to import main ap
sys.path.append(os.pardir)
#allow script to import from working directory
sys.path.append(os.curdir)

#get django info
from django.core.management import setup_environ
from kochief import settings
setup_environ(settings)


from django.conf import settings
from django.contrib.sites.models import Site
from django.utils import simplejson

#Local project version of pymarc
from kochief.pylib import pymarc
from kochief.pylib.pymarc import MARCReader
#Local callnumber normalizer
from kochief.pylib import callnumber

#pysolr
from kochief.pylib import solr
# import solr

try:
    set
except NameError:
    from sets import Set as set

# local libs
import marc_maps

## set up file logger
level_dct = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
logging.basicConfig(
    filename=settings.PARSER_LOG_PATH, level=level_dct[settings.PARSER_LOG_LEVEL],
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.info( 'starting...' )


#check for overriding SOLR_URL
print len(sys.argv)
if len(sys.argv) > 2:
	settings.SOLR_URL = sys.argv[1]
print>>sys.stderr, "Indexing this: ", settings.SOLR_URL

FIELDNAMES = [
    'audience',
    'author',
    'bib_num',
    'collection',
    'contents',
    'corporate_name',
    'ctrl_num',
    'description',
    'format',
    'full_title',
    'genre',
    'id',
    'imprint',
    'isbn',
    'language',
    'language_dubbed',
    'language_subtitles',
    'oclc_num',
    'notes',
    'personal_name',
    'place',
    'publisher',
    'pubyear',
    'series',
    'summary',
    'title',
    'title_sort',
    'native_title',
    'topic',
    'upc',
    'url',
    'call_number',
    'discipline',
    'accession_date',
    'last_updated',
    'building'
]

def convert_date(datestr):
   """III Only reports two digit year numbers."""
   from datetime import datetime, timedelta, date
   dgroups = datestr.split('-')
   try:
       month = int(dgroups[0])
       day = int(dgroups[1])
       year = int(dgroups[2])
   except ValueError, e:
       #print>>sys.stderr, e, ' in date function.'
       return
   this_year = (date.today().year) - 2000
   #If the year integer is greater than the current year then,
   #pad with 1900.
   if year > this_year:
       year = 1900 + year
   else:
       year = 2000 + year
   try:
       return datetime(year, month, day) #.isoformat() + 'Z'
   except ValueError:
           return

def get_accession_date(record):
    from datetime import datetime, timedelta, date
    """Convert III cat date to ISO str for solr."""
    #998|b11-08-10
    cdate = convert_date(record['998']['b'])
    if not cdate:
        return
    if (datetime.today() - cdate) > timedelta(days=settings.MAX_CATALOGED_DAYS):
        return
    return cdate.isoformat() + 'Z'

PUB_YEAR = re.compile('(?:2[0-9]0u|\?)?[0-9]{3}u|\?')
def get_publication_date(record):
    from datetime import datetime, date
    """Try to find pub date and convert to ISO str for solr.
    Will return decades - 1980s - for dates before what is
    defined in settings."""
    #=008  100315s2010\\\\it\a\\\\\b\\\\001\0\ita\\
    o08 = record['008'].data
    date1 = o08[7:11]
    if PUB_YEAR.search(date1):
        date1 = date1.replace('u', '0')
    #Will convert to date object even though we will report
    #just the year string.  This will return null for 19uu
    #fields which we don't want to appear in facets.
    try:
        date_obj = date(year=int(date1), month=1, day=1)
        #Throw out bad data for years greater than two year in
        #advance.
        if date_obj.year > (date.today().year + 2):
            return
    except ValueError:
        print>>sys.stderr, "Can't find date for %s." % date1
        return
    #Try returning by decade after 10 years
    if date_obj.year >= settings.PUB_YEAR_RANGE_START:
        return str(date_obj.year)
    else:
        decade_prefix = str(date_obj.year)[:3]
        return "%s0s" % decade_prefix

def get_callnumber(record):
    """Brown call number routine."""
    call_number = None
    #Check item record first
    if record['945']:
        if record['945']['a']:
            call_number = record['945']['a']
            if record['945']['b']:
                call_number += ' ' + record['945']['b']
    #If call num not in item record, then check bib in this order.
    if not call_number:
        if record['090']:
           call_number = record['090'].format_field()
        elif record['050']:
           call_number = record['050'].format_field()
    return call_number

def get_id(record):
    try:
        return record['907']['a'][1:-1]
    except AttributeError:
        # try other fields for id?
        #sys.stderr.write("\nNo value in ID field, leaving ID blank\n")
        #record['id'] = ''
        # if it has no id let's not include it
        return

def normalize(value):
    if value:
        return value.replace('.', '').strip(',:/; ')

def is_serial(record):
    #Bib level
    if record['998']['c'] == 's':
        return True
    #Format
    if record['998']['d'] == 's':
        return True
    return False

def is_serial_solutions_update(record):
    from datetime import datetime, timedelta, date
    try:
        if record['910']['a'] == 'Serials Solutions Change':
            #Create date is in 907[c]
            create_date = convert_date(record['907']['c'])
            if (datetime.today() - create_date) > timedelta(days=settings.MAX_CATALOGED_DAYS):
                return True
    except TypeError:
        return
    return


def multi_field_list(fields, indicators):
    values = []
    for f in fields:
        for i in indicators:
            values.extend(subfield_list(f, i))
    return set(values)

def subfield_list(field, subfield_indicator):
    subfields = field.get_subfields(subfield_indicator)
    if subfields is not None:
        return [normalize(subfield) for subfield in subfields]
    else:
        return []

def get_title(record):
    try:
        title = ' '.join(record['245'].get_subfields('a', 'b')).strip('/').strip()
    except AttributeError:
        print>>sys.stderr, idx['id'], ' has no title.'
        return
    try:
        nonfiling = int(record['245'].indicator2)
    except ValueError:
        nonfiling = 0

    title_sort = title[nonfiling:].strip()

    return (title, title_sort)

def get_disciplines(call_number):
    """Brown routine for assigning high level subjects/disciplines."""
    #import urllib
    #try:
    #    response = simplejson.load(urllib.urlopen('%s%s' % (settings.CALL_NUMBER_SERVICE_URL, call_number)))
    #except ValueError, e:
        #print>>sys.stderr, e
    #    return []
    sub_list = []
    try:
        nc = callnumber.normalize(call_number)
    except:
        if call_number:
            #print>>sys.stderr, call_number
            pass
        return set(sub_list)

    for disc in discipline_dict.values():
        for point in disc['points']:
            if nc == point['start']:
                sub_list.append(disc['name'])
            if nc >= point['start']:
                if nc <= point['stop']:
                    sub_list.append(disc['name'])
    #for items in response['result']['items']:
    #    sub_list += items['brown_disciplines']
    if len(sub_list) == 0:
        #print>>sys.stderr, call_number
        pass
    return set(sub_list)

def create_marc_file_list():
    marc_records = []
    for root, dirs, files in os.walk(sys.argv[1]):
        for name in files:
            if name.endswith('mrc'):
                fname = os.path.join(root, name)
                fsize = os.stat(fname).st_size
                marc_records.append((fname, fsize))
    flist = sorted(marc_records, key=itemgetter(1))
    marc_records = [f[0] for f in flist]
    return marc_records

def new_title(record):
    """Determine if title is 'new' or not.
    If new the accession date is returned."""
    #Suppressed
    if record['998']['e'] == 'n':
        #print>>sys.stderr, "Skipping suppressed %s." % idx['id']
        return
    #Gov docs.
    if record['086']:
        #print>>sys.stderr, "Skipping gov doc %s." % idx['id']
        return
    #Serials
    if is_serial(record):
        #print>>sys.stderr, "Skipping serial %s." % idx['id']
        return
    #SerSol records with cat date not equal to create date
    if is_serial_solutions_update(record):
        #print>>sys.stderr, "Skipping serial solutions update %s." % record['907']['a']
        return
    accession_date = get_accession_date(record)
    if accession_date:
        #print>>sys.stderr, "Old or uncataloged record.  %s" % idx['id']
        return accession_date
    return

def discipline_mappings():
    try:
        # url = service_url + 'call_number/v1/?data=dump'
        url = settings.CALLNUMBER_SERVICE_URL
        log.debug( 'getting discipline mappings from url, ```}```'.format(url) )
        map = urllib2.urlopen( url, timeout=5 )
        map = simplejson.load(map)
        discipline_dict = map['result']['items']
        #print>>sys.stderr, discipline_dict
        return discipline_dict
    except Exception as e:
        log.warning( 'exception getting discipline-mapping json, `{}`'.format(repr(e)) )
        url = settings.DISCIPLINE_MAPPINGS_BACKUP_JSON_URL
        map = urllib2.urlopen( url )
        map = simplejson.load(map)
        discipline_dict = map['result']['items']
        return discipline_dict

def location_format_mappings():
    try:
        url = service_url + 'location_format/v1/?data=dump'
        map = urllib2.urlopen( url, timeout=5 )
        map = simplejson.load(map)
        location_format_dict = map['result']['items']
        #print>>sys.stderr, location_format_dict
        return location_format_dict
        #print location_format_dict.keys()
        #sys.exit()
    except Exception as e:
        log.warning( 'exception getting location-format-mapping json, `{}`'.format(repr(e)) )
        url = settings.LOCATION_FORMAT_BACKUP_JSON_URL
        map = urllib2.urlopen( url )
        map = simplejson.load(map)
        location_format_dict = map['result']['items']
        return location_format_dict

def marc_miner(record):
    idx = {}
    count = 0
    count += 1
    idx['id'] = get_id(record)
    #Brown skips - returns accession date if 'new'.
    accession_date = new_title(record)
    if not accession_date:
        return
    #print>>sys.stderr, idx['id']
    idx['accession_date'] = accession_date
    #idx['title'] = record.title()
    title_details = get_title(record)
    if title_details:
        idx['title'] = title_details[0]
        idx['full_title'] = idx['title']
        idx['title_sort'] = title_details[1]
    idx['author'] = record.author()
    if record['260']:
        idx['imprint'] = record['260'].format_field()
        idx['publisher'] = normalize(record['260']['b'])

    idx['call_number'] = get_callnumber(record)
    if record['001']:
        idx['ctrl_num'] = record['001'].value()
    try:
        oclc_number = record['001'].value()
    except AttributeError:
        oclc_number = ''
    idx['oclc_num'] = oclc_number.lstrip('ocm').lstrip('ocn')
    idx['isbn'] = record.isbn()

    if record['880']:
        for native_field in record.get_fields('880'):
            try:
                if native_field['6'][:3] == '245':
                    try:
                        idx['native_title'] = ' '.join(native_field.get_subfields('a', 'b')).strip('/').strip()
                    except UnicodeDecodeError:
                        print>>sys.stderr, "Unicode problem in native title for %s." % idx['id']
            except TypeError:
                pass

    description_fields = record.get_fields('300')
    idx['description'] = [field.value() for field in description_fields]

    series_fields = record.get_fields('440', '490')
    idx['series'] = multi_field_list(series_fields, 'a')

    notes_fields = record.get_fields('500')
    idx['notes'] = [field.value() for field in notes_fields]

    contents_fields = record.get_fields('505')
    idx['contents'] = multi_field_list(contents_fields, 'a')

    summary_fields = record.get_fields('520')
    idx['summary'] = [field.value() for field in summary_fields]

    subjname_fields = record.get_fields('600')
    subjectnames = multi_field_list(subjname_fields, 'a')

    subjentity_fields = record.get_fields('610')
    subjectentities = multi_field_list(subjentity_fields, 'ab')

    subject_fields = record.subjects()  # gets all 65X fields

    genres = []
    topics = []
    places = []
    for field in subject_fields:
        genres.extend(subfield_list(field, 'v'))
        topics.extend(subfield_list(field, 'x'))
        places.extend(subfield_list(field, 'z'))
        if field.tag == '650':
            if field['a'] != 'Video recordings for the hearing impaired.':
                topics.append(normalize(field['a']))
        elif field.tag == '651':
            places.append(normalize(field['a']))
        elif field.tag == '655':
            if field['a'] != 'Video recordings for the hearing impaired.':
                genres.append(normalize(field['a']))
        #for subfield_indicator in ('a', 'v', 'x', 'y', 'z'):
        #    more_topics = subfield_list(subfield_indicator)
        #    topics.extend(more_topics)
    idx['genre'] = set(genres)
    idx['topic'] = set(topics)
    idx['place'] = set(places)

    personal_name_fields = record.get_fields('700')
    idx['personal_name'] = []
    for field in personal_name_fields:
        subfields = field.get_subfields('a', 'b', 'c', 'd')
        personal_name = ' '.join([x.strip() for x in subfields])
        if personal_name not in idx['personal_name']:
            idx['personal_name'].append(personal_name)

    corporate_name_fields = record.get_fields('710')
    idx['corporate_name'] = []
    for field in corporate_name_fields:
        subfields = field.get_subfields('a', 'b')
        corporate_name = ' '.join([x.strip() for x in subfields])
        if corporate_name not in idx['corporate_name']:
            idx['corporate_name'].append(corporate_name)

    try:
        language_code = record['008'].data[35:38]
        idx['language'] = marc_maps.LANGUAGE_CODING_MAP[language_code]
    except KeyError:
        #idx['language'] = ''
        pass

    idx['building'] = []
    item_fields = record.get_fields('945')
    for item in item_fields:
        if not item['y']:
            print>>sys.stderr, "no item record number.  Skipping"
            continue
        if item['l']:
            lcode = item['l'].strip()
            try:
                building_format = location_format_dict[lcode]
            except KeyError:
                #print>>sys.stderr, '%s not found for %s.' % (lcode, idx['id'])
                pass
        #Passs those where building format can't be determined
        try:
            idx['format'] = building_format['format']
            building = building_format['building']
            idx['building'].append(building)
            if idx['format'] == 'Book':
                if 'Online' in idx['building']:
                    idx['format'] = 'eBook'
            try:
                if record.leader[6] == 'c':
                    idx['format'] = 'Score'
                elif record['998']['c'] == 'c':
                    idx['format'] = 'Score'
            except IndexError:
                pass
        except UnboundLocalError:
            pass



    #buildings = []
    #for building, display, format in building_format:
    #    print building_format
    #    buildings.append(building)
    #    idx['format'] = format
    idx['building'] = set(idx['building'])
    #idx['building']
    #idx['format']
    call_number = get_callnumber(record)
    idx['discipline'] = get_disciplines(call_number)

    idx['pubyear'] = get_publication_date(record)
    #Solr style date
    idx['last_updated'] = datetime.datetime.now().isoformat() + 'Z'
    #Testing
    #idx['last_updated'] = datetime.datetime.now() - datetime.timedelta(days=15)
    #idx['last_updated'] = idx['last_updated'].isoformat() + 'Z'
    return idx

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    Cribbed from: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def post_to_solr(index_set, file_set):
    # log.debug( 'type(index_set), `{}`'.format(type(index_set)) )
    # for entry in index_set:
    #     log.debug( 'type(entry), `{}`'.format(type(entry)) )
    s = solr.SolrConnection(settings.SOLR_URL.rstrip('/'))
    if len(index_set) > settings.SOLR_COMMIT_CHUNKS:
        log.debug( 'chunking' )
        post_sets = chunks(index_set, settings.SOLR_COMMIT_CHUNKS)
        for i_set in post_sets:
            start_rec = i_set[0]['id']
            end_rec = i_set[-1]['id']
            print>>sys.stderr, "%s.  Committing %d records to Solr, %s to %s." % (file_set, len(i_set), start_rec, end_rec)
            #try:
            response = s.add_many(i_set)
            s.commit()
            #print>>sys.stderr, response
            #except:
            #print>>sys.stderr, 'solr commit failed.'
    else:
        for entry in index_set:
            log.debug( 'entry, ```{}```'.format(pprint.pformat(entry)) )
            # for k,v in entry.items():
            #     log.debug( 'k, `{thekey}`; type(v), `{thevalue}`'.format(thekey=k, thevalue=type(v)) )
        print>>sys.stderr, "%s. Commiting %d records to Solr." % (file_set, len(index_set))
        try:
            response = s.add_many(index_set)
            s.commit()
            #print>>sys.stderr, response
        except Exception as e:
            print 'solr commit failed; see logs'
            log.error( 'solr commit failed; exception, `{}`'.format(repr(e)) )

def marc_indexer(marc_file):
    print>>sys.stderr, "Indexing %s." % marc_file
    index_set = []
    set_count = 0
    for record in MARCReader(file(marc_file)):
        idx = marc_miner(record)
        if idx:
            index_set.append(idx)
    post_to_solr(index_set, file_set=marc_file)


def main(marc_file_list):
    for marc_file in marc_file_list:
        marc_indexer(marc_file)

if __name__ == "__main__":
    start = time.time()
    ## pull from settings
    service_url = settings.SERVICES_URL
    callnumber_service_url = settings.CALLNUMBER_SERVICE_URL
    ## location format mappings
    location_format_dict = location_format_mappings()
    ## discipline mappings
    discipline_dict = discipline_mappings()
    marc_file_list = create_marc_file_list()
    main(marc_file_list)
    print "Elapsed Time: %s" % (time.time() - start)
