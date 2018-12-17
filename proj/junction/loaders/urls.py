#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Junction Applications
# Author: Aaron MacGillivary
# Project: elite3eloader

from . import views
from django.urls import path

app_name = 'loaders'

urlpatterns = [
    path('', views.loader_list, name='loader_list'),
    path('new/', views.loader_edit, name='loader_edit'),
    path('<slug:loader_slug>/run', views.loader_run, name='loader_run'),
    path('<slug:loader_slug>', views.loader_edit, name='loader_edit'),
    path('<slug:loader_slug>/tab/attributes/', views.loader_edit, {'active_tab': 'Attributes'},  name='loader_attribute_active'),
    path('<slug:loader_slug>/tab/advanced/', views.loader_edit, {'active_tab': 'Advanced'},  name='loader_advanced_active'),
    path('<slug:loader_slug>/attribute/<slug:attribute_slug>', views.loader_edit, name='attribute_edit'),
    path('<slug:loader_slug>/xoql/<slug:loaderxoql_slug>', views.loader_edit, name='loaderxoql_edit'),
    path('<slug:loader_slug>/history/request/<int:pk>', views.history_raw, name='loader_history_request'),
    path('<slug:loader_slug>/runxoql/', views.run_xoql, name='run_xoql'),

]