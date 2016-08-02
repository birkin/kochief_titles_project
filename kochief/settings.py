# -*- coding: utf-8 -*-

from __future__ import unicode_literals


#################################################
## Django settings
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
# along with Kochief.  If not, see <http://www.gnu.org/licenses/>.

# Django settings for the Kochief project.

import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/'

# Relative base URL of the project.  Must include a trailing slash.
BASE_URL = unicode( os.environ['KC_NWTTLS__BASE_URL'] )

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

DATABASE_ENGINE = unicode( os.environ['KC_NWTTLS__DATABASE_ENGINE'] )       # Or path to database file if using sqlite3.
DATABASE_NAME = unicode( os.environ['KC_NWTTLS__DATABASE_NAME'] )           # Or path to database file if using sqlite3.
DATABASE_USER = unicode( os.environ['KC_NWTTLS__DATABASE_USER'] )           # Not used with sqlite3 (set env-var to 'null').
DATABASE_PASSWORD = unicode( os.environ['KC_NWTTLS__DATABASE_PASSWORD'] )   # Not used with sqlite3.
DATABASE_HOST = unicode( os.environ['KC_NWTTLS__DATABASE_HOST'] )           # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = unicode( os.environ['KC_NWTTLS__DATABASE_PORT'] )           # Set to empty string for default. Not used with sqlite3.DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# dummy ugettext -- see http://www.djangoproject.com/documentation/i18n/
ugettext = lambda s: s

LANGUAGES = (
    ('fr', ugettext('French')),
    ('en', ugettext('English')),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
# MEDIA_ROOT = BASE_DIR + 'media/'
MEDIA_ROOT = unicode( os.environ['KC_NWTTLS__MEDIA_ROOT'] )

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
# MEDIA_URL = BASE_URL + 'media/'
MEDIA_URL = unicode( os.environ['KC_NWTTLS__MEDIA_URL'] )

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = BASE_URL + 'admin/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = unicode( os.environ['KC_NWTTLS__SECRET_KEY'] ).encode( 'utf-8')  # must be utf8 or django 1.1x md5_constructor middelware will throw a unicode error

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.doc.XViewMiddleware",
    "django.middleware.gzip.GZipMiddleware",
)

ROOT_URLCONF = 'kochief.urls'

TEMPLATE_DIRS = (
    BASE_DIR + 'templates/',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    #'kochief.cataloging',
    'kochief.discovery',
)

# CACHE_BACKEND = None

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "kochief.discovery.context_processors.search_history",
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True


#################################################
## cataloging app settings (kochief)
#################################################

# Namespace for local resources.  If relative, site domain will be prepended
# when triples are serialized.
LOCALNS = BASE_URL + 'r/'

EMAIL_HOST = 'mail-relay.brown.edu'

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

# III, Unicorn, or Horizon -- affects both display and index/ingest
ILS = 'III'

# MAJAX_URL is for use with http://libx.org/majax/
# (has no effect if ILS != 'III')
MAJAX_URL = '' #'http://josiah.brown.edu:2082/screens/majax.js'

# Set CATALOG_RECORD_URL to something else if you want to pass through
# to your catalog, e.g. 'http://innopac.library.drexel.edu/record=%s'.
# The %s is replaced by the item id.
CATALOG_RECORD_URL = 'http://library.brown.edu/find/Record/%s'

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

ugettext = lambda s: s  # see <http://stackoverflow.com/questions/1329278/using-settings-languages-with-properly-translated-names-using-gettext>

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
CATALOG_URL = 'http://library.brown.edu/find'

## for discovery.utility_code.sitemap_index()
APP_DOMAIN = unicode( os.environ['KC_NWTTLS__APP_DOMAIN'] )  # includes trailing slash


#################################################
## discovery.parsers settings
#################################################

SERVICES_URL = unicode( os.environ['KC_NWTTLS__SERVICES_URL'] )

## Number of records to post to solr at a time. `parsers.brown_marc.py` will break the record count up into this number.
SOLR_COMMIT_CHUNKS = 1000

## Index routine will skip any records with a catalog date more than this number of days ago
MAX_CATALOGED_DAYS = 180

## Integer for year cutoff for which the publication date facet will start returning a decade rather than individual year.
PUB_YEAR_RANGE_START = 2000

PARSER_LOG_PATH = unicode( os.environ['KC_NWTTLS__PARSER_LOG_PATH'] )
PARSER_LOG_LEVEL = unicode( os.environ['KC_NWTTLS__PARSER_LOG_LEVEL'] )

DISCIPLINE_MAPPINGS_BACKUP_JSON_URL = unicode( os.environ['KC_NWTTLS__DISCIPLINE_MAPPINGS_BACKUP_JSON_URL'] )
LOCATION_FORMAT_BACKUP_JSON_URL = unicode( os.environ['KC_NWTTLS__LOCATION_FORMAT_BACKUP_JSON_URL'] )


## EOF ##
