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

# from django.conf.urls.defaults import *
from django.conf.urls import url
from utility_code import sitemaps
#from kochief.discovery.feeds import atomFeed, rssFeed
from kochief.discovery import views

urlpatterns = [
    # url(r'^record/(.+)$', kochief.discovery.views.record, name='discovery-record'),
    url( r'^record/(.+)$', views.record, name='discovery-record' ),
    url( r'^search$', views.search, name='discovery-search' ),
    url( r'^unapi$', views.unapi, name='discovery-unapi' ),
    url( r'^feed/rss/$', views.rssFeed ),
    url( r'^$', views.index, name='discovery-index' ),  # APPEND_SLASH setting not working, hence views.index() hack
    url( r'^info/$', views.info, name='info_url' ),
    url( r'^error_check/$', views.error_check, name='info_url' ),
]


# urlpatterns = patterns('kochief.discovery.views',
#     url(r'^record/(.+)$', 'record', name='discovery-record'),
#     url(r'^search$', 'search', name='discovery-search'),
#     url(r'^unapi$', 'unapi', name='discovery-unapi'),
#     url(r'^feed/rss/$', 'rssFeed'),
#     url(r'^$', 'index', name='discovery-index'),  # APPEND_SLASH setting not working, hence views.index() hack
#     url( r'^info/$', 'info', name='info_url' ),
# )
