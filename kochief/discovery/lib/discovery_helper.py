# -*- coding: utf-8 -*-

from __future__ import unicode_literals
""" Helpers for kochief/discovery/views.py """

import logging, os
import requests


logger = logging.getLogger(__name__)
logging.basicConfig(
    # filename=LOG_PATH,
    level=os.environ['KC_NWTTLS__LOG_LEVEL'],
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S' )


class ThumbnailGrabber(object):
    """ Manages lookup of book-cover thumbnails. """

    def prepare_url( self, isbns, oclc ):
        """ Builds api url call.
            Called by ? """
        params = { 'jscmd': 'viewapi' }
        bibkey_lst = []
        for isbn in sorted(isbns):
            bibkey_lst.append( 'ISBN{}'.format(isbn) )
        if bibkey_lst:
            bibkey_str = ','.join(bibkey_lst)
            params['bibkeys'] = bibkey_str
        r = requests.get( 'https://books.google.com/books', params=params )
        url = r.url
        logger.debug( 'url, ```{}```'.format(url) )
        return url

    # def prepare_url( self, isbns, oclc ):
    #     """ Builds api url call.
    #         Called by ? """
    #     params = { 'jscmd': 'viewapi' }
    #     bibkey_lst = []
    #     for isbn in isbns:
    #         bibkey_lst.append( 'ISBN{}'.format(isbn) )
    #     if bibkey_lst:
    #         bibkey_str = ''.join(bibkey_lst)
    #         params['bibkeys'] = bibkey_str
    #     r = requests.get( 'https://books.google.com/books', params=params )
    #     url = r.url
    #     logger.debug( 'url, ```{}```'.format(url) )
    #     return url

    def do_lookup( self ):
        """ Performs lookup.
            Called by ? """
        return 'foo'

    # end class ThumbnailGrabber()
