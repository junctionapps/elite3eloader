#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Junction Applications
# Author: Aaron MacGillivary
# Project: elite3eloader

from django import forms

from junction.core.models import License


class UploadRestoreForm(forms.Form):
    restorefile = forms.FileField(label="Select a restore file (*.json)",
                                  widget=forms.FileInput(attrs={'accept': '.json'}))


class LicenseForm(forms.ModelForm):

    class Meta:
        model = License
        exclude = ['agreed', ]
