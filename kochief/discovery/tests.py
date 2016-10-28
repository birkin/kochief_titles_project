# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging, os, pprint, random
import urlparse
from django.test import TestCase
from kochief.discovery.lib.discovery_helper import ThumbnailGrabber


TestCase.maxDiff = None


class DummyTest( TestCase ):
    """ Tests views via Client. """

    def setUp(self):
        self.client = Client()

    def test_dummy(self):
        result = 1
        self.assertEqual( 1, result )

    # end class DummyTest()


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
            'https://books.google.com/books/content?id=1ECcAgAAQBAJ&printsec=frontcover&img=1&zoom=5',
            self.grabber.grab_thumbnail_url( url )
            )

    # end class ThumbnailGrabberTest()
