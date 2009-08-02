#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from communigate import CLI
import datetime
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
	        

class CliPythonToCgpTest(unittest.TestCase):
    def setUp(self):
        self.cli = CliForTest()
    
    def tearDown(self):
        self.cli = None

    def assert_convertion(self, expected, source, translate = False):
        self.assertEquals(expected, self.cli.convertOutput(source, translate))
        
    def test_converting_none(self):
        self.assert_convertion('#NULL#', None)
    
    def test_converting_empty_string(self):
        self.assert_convertion('', '')
    
    def test_converting_ints(self):
        self.assert_convertion('#666', 666)
        
    def test_converting_negative_ints(self):
        self.assert_convertion('#-24', -24)
        
    def test_converting_floats(self):
        self.assert_convertion('#-20.36', -20.36)
    
    def test_converting_strings(self):
        self.assert_convertion('string', 'string')
        
    def test_converting_longer_strings(self):
        self.assert_convertion('"long string with spaces"', 'long string with spaces')
    
    def test_converting_dicts(self):
        self.assert_convertion('{LastName=Test;FullName="Unit Test";Name=Unit;}', {'Name': 'Unit', 'FullName': 'Unit Test', 'LastName': 'Test'})
        
    def test_covnerting_lists(self):
        self.assert_convertion('(Name,LastName,"Full Name")', ['Name', 'LastName', 'Full Name'])
        
    def test_converting_dates(self):
        self.assert_convertion('#T10-08-2002', datetime.date(2002, 8, 10))

    def test_converting_datetimes(self):
        self.assert_convertion('#T15-11-1989_14:32:25', datetime.datetime(1989, 11, 15, 14, 32, 25))