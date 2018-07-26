# -*- coding: utf-8 -*-

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

from django.conf import settings
# from django.conf.urls.defaults import *
from django.contrib import admin

from discovery.utility_code import sitemaps

admin.autodiscover()

#See sitemap info: https://stackoverflow.com/questions/1392338/django-sitemap-index-example
urlpatterns = patterns('',
    url(r'^sitemap.xml$', 'kochief.discovery.utility_code.sitemap_index',
                        {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap',
                        {'sitemaps': sitemaps}),
    url(r'', include('kochief.discovery.urls')),


    # Uncomment for cataloging.
    #url(r'', include('kochief.cataloging.urls')),

    #('^admin/(.*)', admin.site.root),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )





# # -*- coding: utf-8 -*-

# from django.conf.urls import include, url
# from django.contrib import admin
# from django.views.generic import RedirectView
# from bul_cbp_app import views


# admin.autodiscover()


# urlpatterns = [

#     ## primary app urls...
#     url( r'^project_image/(?P<slug>.*)/$', views.project_image, name='project_image_url' ),
#     url( r'^project_info/(?P<slug>.*)/$', views.project_info, name='project_info_url' ),
#     url( r'^admin/', admin.site.urls ),  # eg host/project_x/admin/

#     ## support urls...
#     url( r'^bul_search/$', views.bul_search, name='bul_search_url' ),
#     url( r'^info/$', views.info, name='info_url' ),
#     url( r'^login/$', views.login, name='login_url' ),
#     url( r'^logout/$', views.logout, name='logout_url' ),
#     url( r'^problem/$', views.problem, name='problem_url' ),

#     url( r'^$', RedirectView.as_view(pattern_name='info_url') ),

#     ]
