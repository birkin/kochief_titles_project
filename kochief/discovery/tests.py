# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging, os, pprint, random
from types import NoneType

from django.conf import settings
from django.http import HttpRequest
from django.test import Client, TestCase


TestCase.maxDiff = None


class DummyTest( TestCase ):
    """ Tests views via Client. """

    def setUp(self):
        self.client = Client()

    def test_dummy(self):
        result = 1
        self.assertEqual( 2, result )

