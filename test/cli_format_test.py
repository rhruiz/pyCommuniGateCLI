# -*- coding: utf-8 -*-

import unittest
from communigate import CLI
import datetime

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
    
    def setResponse(response):
        self.response = response
        
    def parseResponse(self):
        line = self.response
        cleanLine = string.strip(line)

        matches = re.compile(r'^(\d+)\s(.*)$').search(line)
        if matches != None:
            self._errorCode = matches.group(0)

            if matches.group(1) == CLI.CLI_CODE_OK_INLINE:
                self._inlineResponse = matches.group(2)
                self._errorMessage = 'OK'
            else:
                self._errorMessage = string.rstrip(matches.group(2))
                return self.isSuccess()
        else:
            self.setStrangeError(line, CLI.CLI_CODE_STRANGE)
	
	def send(self, cmd, checkLogged = True):
	    self._currentCGateCommand = command
	        
    
class CliFormatTestCase(unittest.TestCase):

    def setUp(self):
        self.cli = CliForTest()
        
    def tearDown(self):
        self.cli = None
    
    def test_parsing_simple_string(self):
        data = self.cli.parseWords('String')
        self.assertEquals('String', data)
    
    def test_pasing_quoted_strings(self):
        data = self.cli.parseWords('"Quoted String"')
        self.assertEquals('Quoted String', data)

    def test_parsing_strings_with_inner_quotes(self):
        data = self.cli.parseWords('"a \\"string\\" within string"')
        self.assertEquals("a \"string\" within string", data)

    def test_parsing_ints(self):
        data = self.cli.parseWords('#50')
        self.assertEquals(50, data)

    def test_parsing_negative_ints(self):
        data = self.cli.parseWords('#-50')
        self.assertEquals(-50, data)
    
    def test_parsing_date(self):
        expected = datetime.datetime(2009, 10, 22)
        data = self.cli.parseWords('#T22-10-2009')
        self.assertEquals(expected, data)
    
    def test_parsing_time(self):
        expected = datetime.datetime(2009, 10, 22, 15, 24, 45)
        data = self.cli.parseWords('#T22-10-2009_15:24:45')
        self.assertEquals(expected, data)
    
    def test_parsing_lists(self):
        data = self.cli.parseWords('("Domain Settings", Domain)')
        self.assertEquals(['Domain Settings', 'Domain'], data)
    
    def test_parsing_dicts(self):
        data = self.cli.parseWords('{Name=Unit;LastName="Test da Silva";}')
        self.assertEquals({'Name': 'Unit', 'LastName': 'Test da Silva'}, data)

    def test_parsing_ip(self):
        data = self.cli.parseWords('#I[10.0.44.55]')
        self.assertEquals('10.0.44.55', data)

    def test_parsing_ip_with_port(self):
        data = self.cli.parseWords('#I[10.0.44.55]:25')
        self.assertEquals(('10.0.44.55', 25), data)

    def test_parsing_ipv6_with_port(self):
        data = self.cli.parseWords('#I[2001:470:1f01:2565::a:80f]:25')
        self.assertEquals(('2001:470:1f01:2565::a:80f', 25), data)
    
    def test_parsing_ipv6(self):
        data = self.cli.parseWords('#I[2001:470:1f01:2565::a:80f]')
        self.assertEquals('2001:470:1f01:2565::a:80f', data)
    def test_parsing_nested_dicts(self):
        expected = datetime.datetime(2009, 10, 22, 15, 24, 45)
        data = self.cli.parseWords('{ServiceClasses={Guests={Changed=#T22-10-2009_15:24:45;Folders=(INBOX, "Sent Items");Source=#I[127.127.127.127];};Staff={Source=#I[127.0.0.1]:25;Name="name \\"nested\\" string";MaxAccounts=#20;};};}')
        self.assertEquals({'ServiceClasses': {'Guests': {'Changed': expected, 'Folders': ['INBOX', 'Sent Items'], 'Source': '127.127.127.127'}, 'Staff': {'Source': ('127.0.0.1', 25), 'Name': 'name "nested" string', 'MaxAccounts': 20}}}, data)