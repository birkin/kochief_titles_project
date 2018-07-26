# -*- coding: utf-8 -*-

from __future__ import unicode_literals
""" Helper for kochief/discovery/views.info() """

import datetime, json, logging, os, subprocess
from django.conf import settings


log = logging.getLogger(__name__)
log_level = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
log.setLevel( log_level[settings.LOG_LEVEL] )
if not logging._handlers:
    handler = logging.FileHandler( settings.LOG_PATH, mode='a', encoding='utf-8', delay=False )
    formatter = logging.Formatter( '[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s' )
    handler.setFormatter( formatter )
    log.addHandler( handler )


def get_commit():
    """ Returns commit-string.
        Called by views.info() """
    original_directory = os.getcwd()
    # print()
    log.debug( 'BASE_DIR, ```%s```' % settings.BASE_DIR )
    # git_dir = os.path.abspath( os.path.join(settings.BASE_DIR, os.pardir) )
    git_dir = settings.BASE_DIR
    log.debug( 'git_dir, ```%s```' % git_dir )
    os.chdir( git_dir )
    output = subprocess.check_output( ['git', 'log'], stderr=subprocess.STDOUT )
    os.chdir( original_directory )
    lines = output.split( '\n' )
    commit = lines[0]
    return commit


def get_branch():
    """ Returns branch.
        Called by views.info() """
    original_directory = os.getcwd()
    # git_dir = os.path.abspath( os.path.join(settings.BASE_DIR, os.pardir) )
    git_dir = settings.BASE_DIR
    os.chdir( git_dir )
    output = subprocess.check_output( ['git', 'branch'], stderr=subprocess.STDOUT )
    os.chdir( original_directory )
    lines = output.split( '\n' )
    branch = 'init'
    for line in lines:
        if line[0:1] == '*':
            branch = line[2:]
            break
    return branch
