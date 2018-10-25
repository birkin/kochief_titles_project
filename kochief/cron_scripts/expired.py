import os, sys, urllib2
from django.conf import settings


## configure django environment
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kochief.settings")
cwd = os.getcwd()  # this assumes the cron call has cd-ed into the project directory
if cwd not in sys.path:
    sys.path.append( cwd )
django.setup()


data = '<delete><query>%s</query></delete>' % settings.EXPIRED_RECORDS_QUERY
r = urllib2.Request( settings.SOLR_URL + 'update?commit=true' )
r.add_header( 'Content-Type', 'text/xml' )
r.add_data( data )
f = urllib2.urlopen( r )
print "Solr response to deletion request for records with a cat date older than the time specified in settings.py."
print f.read()
