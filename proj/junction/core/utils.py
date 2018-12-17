#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Junction Applications
# Author: Aaron MacGillivary
# Project: elite3eloader
import os

from requests import Session
from requests_ntlm import HttpNtlmAuth
if os.name == 'nt':
    from requests_negotiate_sspi import HttpNegotiateAuth
from zeep import Client
from zeep.transports import Transport


class Elite3eServices():
    """
    Manages calls to 3e Transaction Services
    """

    def __init__(self, domain=None, username=None, password=None, wapi=None, port=80, instance=None, protocol='http'):
        self.wapi = wapi
        self.port = port
        self.instance = instance
        self.domain = domain
        self.username = username
        self.password = password
        self.protocol = protocol
        self.client = None

    def connect(self):
        """ Establishes the connection to Elite using local credentials """
        wsdl = f"{self.protocol}://{self.wapi}:{self.port}/{self.instance}/WebUI/Transactionservice.asmx?wsdl"

        if self.domain and self.username and self.password:
            session = Session()
            session.auth = HttpNtlmAuth(f'{self.domain}\\{self.username}', self.password)
            try:
                self.client = Client(wsdl, transport=Transport(session=session))
            except:
                raise Exception("Connection to 3E has been severed or could not be established. "
                                "Check the credentials and network connection.")

        elif os.name == "nt":
            session = Session()
            session.auth = HttpNegotiateAuth()
            self.client = Client(wsdl)
        else:
            raise Exception("You must be on Windows in a Windows network, or provide username, password and domain")

    def disconnect(self):
        # zeep uses requests which handles closing the connection
        pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def __del__(self):
        self.disconnect()

    @staticmethod
    def __version__():
        return '{ver}'.format(ver='18.12.01.1342')

    def execute_process(self, process_xml=None):
        return self.client.service.ExecuteProcess(processXML=process_xml, returnInfo=1)

    def get_archetype_data(self, select_xml=None):
        return self.client.service.GetArchetypeData(selectXml=select_xml)

