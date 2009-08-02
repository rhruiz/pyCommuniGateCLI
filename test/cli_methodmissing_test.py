#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from communigate import CLI
import unittest

class CliForTest(CLI):
    def __init__(self):
        self.__missing_method_name = None # Hack!
        self._lineSize = 1024
        self._peerAddress = '127.0.0.1'
        self._peerPort = 106
        self._login = 'postmaster'
        self._password = 'secret'
        self._timeOut = 60
        self._sp = True
        self._debug = False
        self._logged = True # true se ja tiver autenticado na CLI
        self._bannerCode = '<753.1213987978@cgate.mobimail.com.br>'
        self._errorCode = 0
        self._errorMessage = ''
        self._translateStrings = 0
        self._span = 0
        self._len = 0
        self._data = ''
        self._currentCGateCommand = ''
        self._inlineResponse = ''
        self._connected = True
        self.response = ''    

    def send(self, cmd, checkLogged = True):
        self._errorCode = CLI.CLI_CODE_OK
        self._currentCGateCommand = cmd

    def parseResponse(self):
        pass	        

class CliMethodMissingTest(unittest.TestCase):
    def setUp(self):
        self.cli = CliForTest()
    
    def tearDown(self):
        self.cli = None
        
    def test_parsing_a_simple_command(self):
        self.cli.listdomains()
        self.assertEquals("LISTDOMAINS", self.cli._currentCGateCommand)
        
    def test_parsing_a_single_argument_command(self):
        self.cli.get_account_settings('root@domain.com')
        self.assertEquals('GETACCOUNTSETTINGS "root@domain.com"', self.cli._currentCGateCommand)  
    
    def test_command_without_underscore(self):
        self.cli.getaccountsettings('root@domain.com')
        self.assertEquals('GETACCOUNTSETTINGS "root@domain.com"', self.cli._currentCGateCommand)
