# -*- coding: utf-8 -*-

"""
WSGI config.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

"""
Note: no need to activate the virtual-environment here for passenger.
- the project's httpd/passenger.conf section allows specification of the python-path via `PassengerPython`, which auto-activates it.
- the auto-activation provides access to modules, but not, automatically, env-vars.
- passenger env-vars loading under python3.x is enabled via the `SenEnv` entry in the project's httpd/passenger.conf section.
  - usage: `SetEnv KC_NWTTLS__SETTINGS_PATH /path/to/KC_NWTTLS__env_settings.sh`
  - `SenEnv` requires apache env_module; info: <https://www.phusionpassenger.com/library/indepth/environment_variables.html>,
     enabled by default on macOS 10.12.4, and our dev and production servers.

For activating the virtual-environment manually, don't source the settings file directly. Instead, add to `project_env/bin/activate`:
  export KC_NWTTLS__SETTINGS_PATH="/path/to/KC_NWTTLS__env_settings.sh"
  source $KC_NWTTLS__SETTINGS_PATH
This allows not only the sourcing, but also creates the env-var used below by shellvars.
"""

import os, pprint, sys
import shellvars
from django.core.wsgi import get_wsgi_application


# print( 'the initial env, ```{}```'.format( pprint.pformat(dict(os.environ)) ) )

PROJECT_DIR_PATH = os.path.dirname( os.path.dirname(os.path.abspath(__file__)) )
ENV_SETTINGS_FILE = os.environ['KC_NWTTLS__SETTINGS_PATH']  # set in `httpd/passenger.conf`, and `env/bin/activate`

## update path
sys.path.append( PROJECT_DIR_PATH )

## reference django settings
os.environ[u'DJANGO_SETTINGS_MODULE'] = 'kochief.settings'  # so django can access its settings

## load up env vars
var_dct = shellvars.get_vars( ENV_SETTINGS_FILE )
for ( key, val ) in var_dct.items():
    os.environ[key.decode('utf-8')] = val.decode('utf-8')

# print( 'the final env, ```{}```'.format( pprint.pformat(dict(os.environ)) ) )

## gogogo
application = get_wsgi_application()











# # -*- coding: utf-8 -*-

# from __future__ import unicode_literals

# import os, sys


# APP = 'kochief'

# # path is the parent directory
# path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# #This wsgi file is in the main project folder so we don't need to app the grand-parent
# #folder of the wsgi file.
# project_dir = path


# ## activate virtual env
# #activate_this = os.path.join(project_dir, APP, 'env_/bin/activate_this.py')
# #execfile(activate_this, dict(__file__=activate_this))
# current_directory = os.path.dirname(os.path.abspath(__file__))
# ACTIVATE_FILE = os.path.abspath( '%s/../../env_nwttls/bin/activate_this.py' % current_directory )
# execfile( ACTIVATE_FILE, dict(__file__=ACTIVATE_FILE) )


# # we check for path because we're told to at the tail end of
# # https://code.google.com/p/modwsgi/wiki/ConfigurationDirectives#WSGIReloadMechanism
# if project_dir not in sys.path:
#     sys.path.append(project_dir)


# # os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % APP
# SETTINGS_MODULE = 'kochief.settings'
# os.environ[u'DJANGO_SETTINGS_MODULE'] = SETTINGS_MODULE  # so django can access its settings


# os.environ['PYTHON_EGG_CACHE'] = '/opt/local/django_projects/django_cache/egg_cache'
# import django.core.handlers.wsgi
# application = django.core.handlers.wsgi.WSGIHandler()


# ## environment additions
# os.environ[u'DJANGO_SETTINGS_MODULE'] = SETTINGS_MODULE  # so django can access its settings


# ## load up env vars
# SETTINGS_FILE = os.environ['KC_NWTTLS__SETTINGS_PATH']  # set in activate_this.py, and activated above
# import shellvars
# var_dct = shellvars.get_vars( SETTINGS_FILE )
# for ( key, val ) in var_dct.items():
#     os.environ[key] = val
