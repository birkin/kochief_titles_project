# -*- coding: utf-8 -*-

from __future__ import unicode_literals
""" Helpers for kochief/discovery/views.py """

import json, logging, os
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
        if oclc:
            bibkey_lst.append( 'OCLC{}'.format(oclc) )
        if bibkey_lst:
            bibkey_str = ','.join(bibkey_lst)
            params['bibkeys'] = bibkey_str
        r = requests.get( 'https://books.google.com/books', params=params, timeout=30 )
        url = r.url
        logger.debug( 'url, ```{}```'.format(url) )
        return url

    def grab_thumbnail_url( self, url ):
        """ Performs lookup.
            Called by ? """
        thumbnail_url = ''
        r = requests.get( url, timeout=30 )
        jsn = r.content[19:-1]
        logger.debug( jsn )
        d = json.loads( jsn )
        for ( key, info_dct_value ) in d.items():
            if 'thumbnail_url' in info_dct_value.keys():
                thumbnail_url = d[key]['thumbnail_url']
            break
        if '&edge=curl' in thumbnail_url:
            thumbnail_url = thumbnail_url.replace( '&edge=curl', '' )
        logger.debug( 'thumbnail_url, ```{}```'.format(thumbnail_url) )
        return thumbnail_url

    # end class ThumbnailGrabber()
