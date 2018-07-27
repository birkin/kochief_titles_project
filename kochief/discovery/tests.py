# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json, logging, os, pprint, random
import urlparse
from django.test import TestCase
from kochief.discovery.lib.discovery_helper import ThumbnailGrabber


log = logging.getLogger(__name__)
TestCase.maxDiff = None


class ClientTest( TestCase ):
    """ Tests views via Client. """

    def test_index(self):
        """ Checks root index page. """
        response = self.client.get( '/' )  # project root part of url is assumed
        log.debug( 'response.__dict__, ```%s```' % pprint.pformat(response.__dict__) )
        self.assertEqual( 200, response.status_code )
        content = response.content.decode('utf-8')
        self.assertTrue( '<form action="/search" name="search">' in content )  # search form
        self.assertTrue( '>Browse by' in content )

    def test_info(self):
        """ Checks /info/ keys. """
        response = self.client.get( '/info/' )
        # log.debug( 'response.__dict__, ```%s```' % pprint.pformat(response.__dict__) )
        self.assertEqual( 200, response.status_code )
        payload = response._container[0]
        dct = json.loads( payload )
        self.assertEqual( ['request', 'response'], sorted(dct.keys()) )

    def test_search(self):
        """ Checks search page. """
        response = self.client.get( '/search', { 'limits': 'discipline:"Applied Math"'} )
        self.assertEqual( 200, response.status_code )
        content = response.content.decode('utf-8')
        self.assertTrue( '<li>discipline:&quot;Applied Math&quot;' in content )  # `Current filters:`




    def test_root_url_no_slash(self):
        """ Checks '/root_url redirect (no appended slash)'.
            This doesn't behave as a normal django app, which would redirect with an appended-slash. """
        response = self.client.get( '' )
        log.debug( 'response.__dict__, ```%s```' % pprint.pformat(response.__dict__) )
        self.assertEqual( 200, response.status_code )


    ## end class ClientTest()


class ThumbnailGrabberTest( TestCase ):
    """ Checks kochief.discovery.lib.discovery_helper.ThumbnailGrabber
        Test data:
            isbns = [ '0309102995', '9780309102995' ]
            oclc = '79623806'
        """

    def setUp(self):
        self.grabber = ThumbnailGrabber()

    def test_prep_url__single_isbn(self):
        """ Checks construcion of url with single isbn. """
        isbns = [ '0309102995' ]
        oclc = ''
        url = self.grabber.prepare_url(isbns, oclc)  # 'https://books.google.com/books?jscmd=viewapi&bibkeys=ISBN0309102995'
        parsed = urlparse.urlparse( url )
        self.assertEqual( 'https', parsed.scheme )
        self.assertEqual( 'books.google.com', parsed.netloc )
        self.assertEqual( '/books', parsed.path )
        self.assertEqual(
            urlparse.parse_qs( 'jscmd=viewapi&bibkeys=ISBN0309102995' ),
            urlparse.parse_qs( parsed.query )
            )

    def test_prep_url__multiple_isbns(self):
        """ Checks construcion of url with multiple isbns. """
        isbns = [ '9780309102995', '0309102995' ]
        oclc = ''
        url = self.grabber.prepare_url(isbns, oclc)  # 'https://books.google.com/books?jscmd=viewapi&bibkeys=ISBN0309102995,ISBN9780309102995'
        parsed = urlparse.urlparse( url )
        self.assertEqual( 'https', parsed.scheme )
        self.assertEqual( 'books.google.com', parsed.netloc )
        self.assertEqual( '/books', parsed.path )
        self.assertEqual(
            urlparse.parse_qs( 'jscmd=viewapi&bibkeys=ISBN0309102995,ISBN9780309102995' ),
            urlparse.parse_qs( parsed.query )
            )

    def test_prep_url__multiple_isbns_and_oclc(self):
        """ Checks construcion of url with multiple isbns and an oclc number. """
        isbns = [ '9780309102995', '0309102995' ]
        oclc = '79623806'
        url = self.grabber.prepare_url(isbns, oclc)  # 'https://books.google.com/books?jscmd=viewapi&bibkeys=ISBN0309102995,ISBN9780309102995,OCLC79623806'
        parsed = urlparse.urlparse( url )
        self.assertEqual( 'https', parsed.scheme )
        self.assertEqual( 'books.google.com', parsed.netloc )
        self.assertEqual( '/books', parsed.path )
        self.assertEqual(
            urlparse.parse_qs( 'jscmd=viewapi&bibkeys=ISBN0309102995,ISBN9780309102995,OCLC79623806' ),
            urlparse.parse_qs( parsed.query )
            )

    def test_prep_url__just_oclc(self):
        """ Checks construcion of url with just an oclc number. """
        isbns = []
        oclc = '79623806'
        url = self.grabber.prepare_url(isbns, oclc)  # 'https://books.google.com/books?jscmd=viewapi&bibkeys=OCLC79623806'
        parsed = urlparse.urlparse( url )
        self.assertEqual( 'https', parsed.scheme )
        self.assertEqual( 'books.google.com', parsed.netloc )
        self.assertEqual( '/books', parsed.path )
        self.assertEqual(
            urlparse.parse_qs( 'jscmd=viewapi&bibkeys=OCLC79623806' ),
            urlparse.parse_qs( parsed.query )
            )

    def test_grab_thumbnail_url_found(self):
        """ Checks api result for thumbnail url that exists. """
        url = 'https://books.google.com/books?jscmd=viewapi&bibkeys=ISBN0309102995,ISBN9780309102995,OCLC79623806'
        self.assertEqual(
            'https://books.google.com/books/content?id=1ECcAgAAQBAJ&printsec=frontcover&img=1&zoom=5',
            self.grabber.grab_thumbnail_url( url )
            )

    def test_grab_thumbnail_url_not_found(self):
        """ Checks api result for thumbnail url that does not exist. """
        url = 'https://books.google.com/books?jscmd=viewapi&bibkeys=OCLC43034574'
        self.assertEqual(
            '',
            self.grabber.grab_thumbnail_url( url )
            )

    # end class ThumbnailGrabberTest()
