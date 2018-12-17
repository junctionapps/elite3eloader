#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Junction Applications
# Author: Aaron MacGillivary
# Project: elite3eloader

from django.forms import ModelForm, TextInput, PasswordInput

from junction.servers.models import Server


class ServerForm(ModelForm):

    class Meta:
        model = Server
        exclude = ['custom_wsdl', ]
        fields = ['name', 'protocol', 'wapi', 'instance', 'domain', 'username', 'password']
        widgets = {
            'name': TextInput(attrs={'autofocus': 'true', }),
            'username': TextInput(attrs={'autocomplete': "new-password", }),
            'password': PasswordInput(attrs={'autocomplete': "new-password", }),
        }
