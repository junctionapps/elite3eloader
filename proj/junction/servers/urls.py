#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Junction Applications
# Author: Aaron MacGillivary
# Project: elite3eloader

from . import views
from django.urls import path

app_name = 'servers'

urlpatterns = [
    path('', views.list, name='server_list'),
    path('<slug:server_slug>', views.list, name='server_edit'),

]