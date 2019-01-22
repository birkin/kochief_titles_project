# -*- coding: utf-8 -*-

"""
For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import json, logging, os


#################################################
## Django settings
#################################################

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = unicode( os.environ['KC_NWTTLS__SECRET_KEY'] )

DEBUG = json.loads( os.environ['KC_NWTTLS__DEBUG_JSON'] )  # will be True or False
# TEMPLATE_DEBUG = DEBUG

ADMINS = json.loads( os.environ['KC_NWTTLS__ADMINS_JSON'] )

ALLOWED_HOSTS = json.loads( os.environ['KC_NWTTLS__ALLOWED_HOSTS'] )  # list

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    #'kochief.cataloging',
    'kochief.discovery',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

LOGIN_URL = '/login/'  # https://docs.djangoproject.com/en/1.11/ref/settings/#login-url
LOGIN_REDIRECT_URL = '/info/' # https://docs.djangoproject.com/en/1.11/ref/settings/#login-redirect-url

ROOT_URLCONF = 'kochief.urls'

template_dirs = json.loads( os.environ['KC_NWTTLS__TEMPLATES_JSON'] )
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': template_dirs,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'kochief.passenger_wsgi.application'

DATABASES = json.loads( os.environ['KC_NWTTLS__DATABASES_JSON'] )

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'  # original setting is 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# dummy ugettext -- see https://www.djangoproject.com/documentation/i18n/
ugettext = lambda s: s

STATIC_URL = os.environ['KC_NWTTLS__STATIC_URL']
STATIC_ROOT = os.environ['KC_NWTTLS__STATIC_ROOT']  # needed for collectstatic command
STATICFILES_DIRS = json.loads( os.environ['KC_NWTTLS__STATICFILES_DIRS_JSON'] )

SERVER_EMAIL = os.environ['KC_NWTTLS__SERVER_EMAIL']
EMAIL_HOST = os.environ['KC_NWTTLS__EMAIL_HOST']
EMAIL_PORT = int( os.environ['KC_NWTTLS__EMAIL_PORT'] )

SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

logging.getLogger('requests').setLevel( logging.WARNING )
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'logfile': {
            'level':'DEBUG',
            'class':'logging.FileHandler',  # note: configure server to use system's log-rotate to avoid permissions issues
            'filename': os.environ.get(u'KC_NWTTLS__LOG_PATH'),
            'formatter': 'standard',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        'kochief': {
            'handlers': ['logfile'],
            'level': os.environ.get(u'KC_NWTTLS__LOG_LEVEL'),
            'propagate': False
        },
    }
}

CSRF_TRUSTED_ORIGINS = json.loads( os.environ['KC_NWTTLS__CSRF_TRUSTED_ORIGINS_JSON'] )

## TODO: eliminate this
BASE_URL = unicode( os.environ['KC_NWTTLS__BASE_URL'] )
if BASE_URL[-1:] is not '/':  # since the server may or may not result in the '/', let's make the setting predictable
    BASE_URL = '%s/' % BASE_URL



#################################################
## cataloging app settings (kochief)
#################################################

# Namespace for local resources.  If relative, site domain will be prepended
# when triples are serialized.
LOCALNS = BASE_URL + 'r/'

# EMAIL_HOST = 'mail-relay.brown.edu'

# # Import for local overrides
# try:
#     from kochief_titles_local_settings.settings_local import *
# except ImportError, e:
#     print e
#     pass

#For local libraries
import sys
pylib_path = os.path.join(BASE_DIR, 'pylib')
sys.path.append(pylib_path)


#################################################
## discovery web-app settings
#################################################

SOLR_URL = unicode( os.environ['KC_NWTTLS__SOLR_URL'] )

SOLR_DIR = BASE_DIR + 'solr/'

LOG_LEVEL = unicode( os.environ['KC_NWTTLS__WEBAPP_LOG_LEVEL'] )
LOG_PATH = unicode( os.environ['KC_NWTTLS__WEBAPP_LOG_PATH'] )

# III, Unicorn, or Horizon -- affects both display and index/ingest
ILS = 'III'

# MAJAX_URL is for use with https://libx.org/majax/



# (has no effect if ILS != 'III')
MAJAX_URL = '' #'https://josiah.brown.edu:2082/screens/majax.js'

# Set CATALOG_RECORD_URL to something else if you want to pass through
# to your catalog, e.g. 'https://innopac.library.drexel.edu/record=%s'.
# The %s is replaced by the item id.
CATALOG_RECORD_URL = 'https://library.brown.edu/find/Record/%s'

# Number of facet terms to display by default.
MAX_FACET_TERMS_BASIC = 4

# Number of facet terms to display when you hit "show more".
MAX_FACET_TERMS_EXPANDED = 25

# Number of terms to display for index facets.
INDEX_FACET_TERMS = 100

# Facet display on the index page.  Note that values for "field" are
# appended with "_facet".  If sort_by_count is False, terms will be
# sorted "in their natural index order" according to Solr docs --
# usually alphabetical.

ITEMS_PER_PAGE = 20

SEARCH_CACHE_TIME = 6000    # in seconds

MAJAX2_URL = None

# Facet display on the index page.  Note that values for "field" are
# appended with "_facet".  If sort_by_count is False, terms will be
# sorted "in their natural index order" according to Solr docs --
# usually alphabetical.

ugettext = lambda s: s  # see <https://stackoverflow.com/questions/1329278/using-settings-languages-with-properly-translated-names-using-gettext>

INDEX_FACETS = [
    {
        'name': ugettext('Discipline'),
        'field': 'discipline',
        'sort_by_count': False,
    },
    {
        'name': ugettext('Format'),
        'field': 'format',
        'sort_by_count': False,
    },
    {
        'name': ugettext('Location'),
        'field': 'building',
        'sort_by_count': False,
    },
    {
        'name': ugettext('Date'),
        'field': 'pubyear',
        'sort_by_count': False,
    },
    {
        'name': ugettext('Language'),
        'field': 'language',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Topic'),
        'field': 'topic',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Subject'),
        'field': 'subject',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Name'),
        'field': 'personal_name',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Genre'),
        'field': 'genre',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Place'),
        'field': 'place',
        'sort_by_count': True,
    },
]

# Facet display in the results sidebar.
FACETS = [
    {
        'name': ugettext('Discipline'),
        'field': 'discipline',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Collection'),
        'field': 'collection',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Location'),
        'field': 'building',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Format'),
        'field': 'format',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Date'),
        'field': 'pubyear',
        'sort_by_count': False,
    },
    {
        'name': ugettext('Language'),
        'field': 'language',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Name'),
        'field': 'name',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Topic'),
        'field': 'topic',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Genre'),
        'field': 'genre',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Dubbed Language'),
        'field': 'language_dubbed',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Subtitled Language'),
        'field': 'language_subtitles',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Place'),
        'field': 'place',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Publisher'),
        'field': 'imprint',
        'sort_by_count': True,
    },
]

# Sort options for results, by (DISPLAY, SOLR_PARAM).
SORTS = (
    (ugettext('newest'), 'accession_date desc'),
    (ugettext('oldest'), 'accession_date asc'),
    (ugettext('relevance'), ''),
    (ugettext('title'), 'title_sort asc'),
)

## for discovery.views.rssfeed()
CATALOG_URL = 'https://library.brown.edu/find'

## for discovery.utility_code.sitemap_index()
APP_DOMAIN = unicode( os.environ['KC_NWTTLS__APP_DOMAIN'] )  # includes trailing slash


#################################################
## discovery.parsers settings
#################################################

# SERVICES_URL = unicode( os.environ['KC_NWTTLS__SERVICES_URL'] )
CALLNUMBER_SERVICE_URL = unicode( os.environ['KC_NWTTLS__CALLNUMBER_SERVICE_URL'] )
LOCATION_SERVICE_URL = unicode( os.environ['KC_NWTTLS__LOCATION_SERVICE_URL'] )

## Number of records to post to solr at a time. `parsers.brown_marc.py` will break the record count up into this number.
SOLR_COMMIT_CHUNKS = 1000

## Index routine will skip any records with a catalog date more than this number of days ago
MAX_CATALOGED_DAYS = 180

#Query called that will remove records that have 'expired'.
#Currently 6 months.
#Called by manage.py index -expired
EXPIRED_RECORDS_QUERY = 'accession_date:[* TO NOW-6MONTH+1DAY/DAY]'
#Check for records that haven't been updated in over a week.
#These could be deleted records or records where the catalog
#date was changed to a later date after the last index.
#Should be few of these.
NOT_UPDATED_RECORDS_QUERY = 'last_updated:[* TO NOW-1DAYS]'

## Integer for year cutoff for which the publication date facet will start returning a decade rather than individual year.
PUB_YEAR_RANGE_START = 2000

PARSER_LOG_PATH = unicode( os.environ['KC_NWTTLS__PARSER_LOG_PATH'] )
PARSER_LOG_LEVEL = unicode( os.environ['KC_NWTTLS__PARSER_LOG_LEVEL'] )

DISCIPLINE_MAPPINGS_BACKUP_JSON_URL = unicode( os.environ['KC_NWTTLS__DISCIPLINE_MAPPINGS_BACKUP_JSON_URL'] )
LOCATION_FORMAT_BACKUP_JSON_URL = unicode( os.environ['KC_NWTTLS__LOCATION_FORMAT_BACKUP_JSON_URL'] )


#################################################
## addtional info
#################################################

# Copyright 2007 Casey Durfee
# Copyright 2007 Gabriel Farrell
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

## EOF ##
