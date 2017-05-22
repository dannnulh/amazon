# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^get_items/$', views.get_items, name='get_items'),
    url(r'^get_reviews/$', views.get_reviews, name='get_reviews'),
]
