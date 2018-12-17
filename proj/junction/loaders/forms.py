#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Junction Applications
# Author: Aaron MacGillivary
# Project: elite3eloader

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, Form

from junction.loaders.models import Loader, Attribute, History, LoaderXOQL
from junction.servers.models import Server


class HistoryForm(ModelForm):
    xoql = forms.ChoiceField(choices=(), required=False, label='XOQL')

    def __init__(self,*args,**kwargs):
        loader = kwargs.pop('loader', None)
        super (HistoryForm,self ).__init__(*args,**kwargs)
        self.fields['server'].queryset = Server.objects.filter(active=True)
        if loader:
            self.loader = loader
            self.fields['xoql'].choices = LoaderXOQL.objects.filter(loader=loader).values_list('id', 'name')

    class Meta:
        model = History
        fields = ['server', 'data', 'column_headers']
        # 'data', 'column_headers'
        # widgets = {
        #     'data': forms.Textarea(attrs={'rows': 2,}),
        #     'column_headers': forms.Textarea(attrs={'rows': 2, }),
        # }
        widgets = {
            'data': forms.HiddenInput(),
            'column_headers': forms.HiddenInput(),
        }


class LoaderForm(ModelForm):

    class Meta:
        model = Loader
        fields = ['name', 'description', 'process','parent_action', 'parent_object',
                  'child_action', 'child_object', ]
        widgets = {
            'name': forms.TextInput(attrs={'autofocus': 'true', }),
            'description': forms.Textarea(attrs={'rows': 3, })
        }


class AttributeForm(ModelForm):

    def __init__(self, *args, **kwargs):
        loader = kwargs.pop('loader', None)
        super(AttributeForm, self).__init__(*args, **kwargs)
        if loader:
            self.loader = loader

    class Meta:
        model = Attribute
        fields = ['name', 'alias_field', 'is_key', 'type' ,'sort',]

    def clean_name(self):
        cleaned_name = self.cleaned_data['name']
        if self.initial['name'] != cleaned_name:
            if Attribute.objects.filter(name=cleaned_name, loader=self.loader).exists():
                raise ValidationError('Attribute with this Name already exists for this loader')

        # Always return cleaned_data
        return cleaned_name


class LoaderXOQLForm(ModelForm):

    def __init__(self, *args, **kwargs):
        loader = kwargs.pop('loader', None)
        super(LoaderXOQLForm, self).__init__(*args, **kwargs)
        if loader:
            self.loader = loader

    class Meta:
        model = LoaderXOQL
        fields = ['name', 'description', 'xoql', ]

        widgets = {
            'name': forms.TextInput(attrs={'autofocus': 'true', }),
            'description': forms.Textarea(attrs={'rows': 2, }),
            'xoql': forms.Textarea(attrs={'class': 'textarea-xml', 'rows': '20', })
        }

    def clean_name(self):
        cleaned_name = self.cleaned_data['name']
        if self.initial['name'] != cleaned_name:
            if LoaderXOQL.objects.filter(name=cleaned_name, loader=self.loader).exists():
                raise ValidationError('XOQL with this Name already exists for this loader')

        return cleaned_name