# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os, sys


APP = 'kochief'

# path is the parent directory
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#This wsgi file is in the main project folder so we don't need to app the grand-parent
#folder of the wsgi file.
project_dir = path

#activate virtual env
activate_this = os.path.join(project_dir, APP, 'env/bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))


# we check for path because we're told to at the tail end of
# http://code.google.com/p/modwsgi/wiki/ConfigurationDirectives#WSGIReloadMechanism
if project_dir not in sys.path:
    sys.path.append(project_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % APP
os.environ['PYTHON_EGG_CACHE'] = '/opt/local/django_projects/django_cache/egg_cache'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()


## environment additions
os.environ[u'DJANGO_SETTINGS_MODULE'] = SETTINGS_MODULE  # so django can access its settings

## load up env vars
SETTINGS_FILE = os.environ['KC_NWTTLS__SETTINGS_PATH']  # set in activate_this.py, and activated above
import shellvars
var_dct = shellvars.get_vars( SETTINGS_FILE )
for ( key, val ) in var_dct.items():
    os.environ[key] = val
