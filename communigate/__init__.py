#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import re
import md5
import string
from datetime import datetime, date

class CgDataException(Exception):
	def __init__(self, buffer, occurred_at, expecting = ''):
	    self.message = "Error parsing data returned from the server. The error occurred near '%s' (pos: %d) while expecting %s.\nThe data returned by the server follows:\n\n%s\n" % (buffer[occurred_at:10], occurred_at, expecting, buffer)
	    self.buffer = buffer
	    self.occurred_at = occurred_at
	    self.expecting = expecting
	
	def __str__(self):
		return self.message
		
class CgGeneralException(Exception):
	def __init__(self, msg):
		self.message = msg
	
	def __str__(self):
		return self.message
		
		
class CgDataBlock:
	def __init__(self, str):
		self.datablock = base64.b64encode(str).replace("\n", "")

class CLI:
    __connectionCounter = 0
    CLI_CODE_OK = 200
    CLI_CODE_OK_INLINE = 201
    CLI_CODE_PASSWORD = 300
    CLI_CODE_UNKNOW_USER = 500
    CLI_CODE_GEN_ERR = 501
    CLI_CODE_STRANGE = 10000
    _mailboxEncoding = 'UTF7-IMAP'
    _defaultEnconding = 'UTF-8'

    def __getattribute__(self, name):
        return object.__getattribute__(self, name)
    
    def __methodmissing__(self, *args, **kwargs):
        cmd = []
        cmd.append(self.__missing_method_name.upper().replace('_', ''))
        for arg in args:
            cmd.append(self.printWords(arg))
        
        for key in kwargs.keys():
            cmd.append(key.upper())
            cmd.append(self.printWords(kwargs[key]))
        
        self.send(' '.join(cmd))
        self.parseResponse()
        
        if not self.isSuccess():
            raise CgGeneralException(self._errorMessage)
        
    
    def __getattr__(self, name):
        self.__missing_method_name = name # Could also be a property
        return getattr(self, '__methodmissing__')
	
    def __init__(self, peer_address, login, password, peer_port = 106, timeout = 60, debug = True):
        self.__missing_method_name = None # Hack!
        self._lineSize = 1024
        self._peerAddress = string.strip(peer_address)
        self._peerPort = int(peer_port)
        self._login = string.strip(login)
        self._password = string.strip(password)
        self._timeOut = int(timeout)
        self._sp = None
        self._debug = debug
        self._logged = False # true se já tiver autenticado na CLI
        self._bannerCode = '' # <753.1213987978@cgate.mobimail.com.br>
        self._errorCode = 0
        self._errorMessage = ''
        self._translateStrings = 0
        self._span = 0
        self._len = 0
        self._data = ''
        self._currentCGateCommand = ''
        self._inlineResponse = ''
        self._connected = False
        
        vars = ['peerAddress', 'login', 'password', 'peerPort', 'timeOut']
        
        for v in vars:
            if not self.__dict__["_%s" % v]:
                raise ValueError("%s is empty" % v)

    def connect(self):
        if self._connected:
            return None
            
        try:
        	self._sp = socket.socket()
        	self._sp.connect((self._params["hostname"], self._params["port"]))
        except socket.error, msg:
        	raise CgGeneralException("Unable to connect to host %s on port %d: %s" % (self._params["hostname"], self._params["port"], msg))

        response = self._sp.recv(4096)
        exp = re.compile(r'(\<.*\@*\>)')
        if (exp.search(response) == None):
            raise ValueError("No banner from the server")
        else:
        	self._bannerCode = exp.group(0)

        CLI.__connectionCounter += 1
        self._connected = True
    
    def login(self):
        m = md5.new()
        m.update(self._banner_code + self._params["password"])
        hash = m.hexdigest()
        command = "APOP %s %s" % (self._login, hash)
        self.send(command, False)
        self.parseResponse()
        
        if not self.isSuccess():
            raise CgGeneralException(self._errorMessage)
            
            
        self._logged = True
        self.inline()
    
    def send(self, command, checkLogged = True):
        if not self._sp:
            self.connect()
        
        if not self._logged and checkLogged:
            self.login()
            
        self._currentCGateCommand = command
        self._sp.send("%s\n" % command)
        
    
    def getErrorCode(self):
        return self._errorCode
        
    def getErrorMessage(self):
        return self._errorMessage
        
    def getErrorCommand(self):
        return self._currentCGateCommand
        
    def isSuccess(self):
        return self._errorCode == CLI.CLI_CODE_OK or self._errorCode == CLI.CLI_CODE_OK_INLINE
        
    def setDebug(self, debug = True):
        self._debug = debug
        
    def setStrangeError(self, line, code):
        if isinstance(code, int):
            self._errorCode = code
        else:
            self._errorCode =  CLI.CLI_CODE_STRANGE
            
        self._errorMessage = string.rstrip(line)
        return False
        
	def parseResponse(self):
	    line = self._sp.recv(4096)
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
	        	        
    def convertOutput(self, data, translate):
        if data == None:
            return '#NULL#'
    
        elif not data:
            return ''

        elif isinstance(data, list):
            out = '('
            first = True
            for value in data:
                if not first:
                    out += ','
                else:
                    first = False
                out += self.convertOutput(value, self._translateStrings)
            out += ')'
            return out

        elif isinstance(data, dict):
            out = '{'
            for k in data.keys():
                out += self.convertOutput(k, self._translateStrings) + '='
                out += self.convertOutput(data[k], self._translateStrings) + ';'
    
            out += '}'
            return out

        elif isinstance(data, int) or isinstance(data, float):
            return "#%s" % str(data)

        elif isinstance(data, datetime):
            return data.strftime("#T%d-%m-%Y_%H:%M:%S")

        elif isinstance(data, date):
            return data.strftime("#T%d-%m-%Y")

        else:
            matches = re.compile(r'[\W_]').search(data)
            if matches != None or data == '':
                if translate:
                    data = re.compile(r'\\((?![enr\d]))').sub('\\\\' + matches.group(1), data)
                    data = data.replace('\"', '\\\"')
            
                for i in range(0x00, 0x1F):
                    data = data.replace(chr(i), "\\" + str(int(i)))
            
                data = data.replace(chr(0x7F), "\\127")
                return self.quoteString(data)
            else:
                return data
                
    def printWords(self, data):
        return self.convertOutput(data, self._translateStrings)
        
    def getWords(self):
        if self._errorCode == CLI.CLI_CODE_OK_INLINE:
            return self._inlineResponse
        
        line = self._errorMessage
        line = line.strip()
        return line
        
    def skipSpaces(self):
        r = re.compile(r'\s')
        while (self._span < self._len) and r.search(self._data[self._span:self._span+1]):
            self._span += 1
            
    def readIp(self):
        ip = ''
        port = ''
        ipRead = False
        while (self._span < self._len):
            ch = self._data[self._span]
            if not ipRead:
                if (ch == ']'):
                    ipRead = True
                else:
                    ip += ch
            else:
                if re.compile(r'(?:\:|\d)').match(ch) == None:
                    break
                elif ch != ':':
                    port += ch
            
            self._span += 1

        if port and len(port) > 0: 
            return (ip, int(port))
        else:
            return ip

            
    
    def readTime(self):
        if len(self._data) - self._span < 11 or self._data[self._span+11] == '_':
            result = datetime.strptime(self._data[self._span:self._span+10], '%d-%m-%Y').date()
            self._span += 10
        else:
            result = datetime.strptime(self._data[self._span:self._span+19], '%d-%m-%Y_%H:%M:%S')
            self._span += 19
            
        return result
    
    def readNumeric(self):
        result = ''
        r = re.compile(r'[-\d\.]')
        while (self._span < self._len):
            ch = self._data[self._span]
            if r.match(ch) != None:
                result += ch
                self._span += 1
            else:
                break
        
        if '.' in result:
            return float(result)
        else:
            return int(result)
            
    def readWord(self):
        isQuoted = False
        isBlock = False
        result = ''
        self.skipSpaces()
        
        if self._data[self._span] == '"':
            isQuoted = True
            self._span += 1
        elif self._data[self._span] == '[':
            isBlock = True
        
        while (self._span < self._len):
            ch = self._data[self._span]
            if isQuoted:
                if ch == '\\':
                    if re.compile(r'^(?:\"|\\|\d\d\d)').match(self._data[self._span+1:self._span+4]) != None:
                        self._span += 1
                        ch = self._data[self._span:self._span+3]
                        
                        if re.compile(r'\d\d\d').match(ch) != None:
                            self._span += 2
                            ch = chr(ch)
                        else:
                            ch = ch[0]
                            if self._translateStrings:
                                ch = '\\' + ch
                elif ch == '"':
                    self._span += 1
                    break
                    
            elif isBlock:
                if ch == ']':
                    result += ch
                    self._span += 1
                    break
                    
            elif re.compile(r'[\-a-zA-Z0-9\x80-\xff_\.\@\!\#\%\:]').search(ch) != None:
                pass
                
            else:
                break
            
            result += ch
            self._span += 1
    
        return result
            
    def readKey(self):
        return self.readWord()
        
    def readValue(self):
        self.skipSpaces()
        ch = self._data[self._span]
        next_ch = self._data[self._span+1]
        
        if ch == '#' and next_ch == 'I':
            self._span += 3
            return self.readIp()
        
        elif ch == '#' and next_ch == 'T':
            self._span += 2
            return self.readTime()
            
        if ch == '#' and next_ch != 'T':
            self._span += 1
            return self.readNumeric() 

        
        elif ch == '{':
            self._span += 1
            return self.readDictionary()
            
        elif ch == '(':
            self._span += 1
            return self.readArray()
        
        else:
            return self.readWord()
            
    def readArray(self):
        result = []
        while (self._span < self._len):
            self.skipSpaces()
            if self._data[self._span] == ')':
                self._span += 1
                break
            else:
                theValue = self.readValue()
                self.skipSpaces()
                result.append(theValue)
                
                if self._span < self._len:
                    if self._data[self._span] == ',':
                        self._span += 1
                    
                    elif self._data[self._span] == ')':
                        pass
                        
                    else:
                        raise CgDataException(self._data, self._span, "','")
            
        return result
    
    def readDictionary(self):
        result = {}
        while (self._span < self._len):
            self.skipSpaces()
            if self._data[self._span:self._span+1] == '}':
                self._span += 1
                break
            
            else:
                theKey = self.readKey()
                self.skipSpaces()
                
                if self._data[self._span:self._span+1] != '=':
                    raise CgDataException(self._data, self._span, "=")

                self._span += 1
                result[theKey] = self.readValue()
                self.skipSpaces()
                
                if self._data[self._span:self._span+1] != ';':
                    raise CgDataException(self._data, self._span, ';')
                    
                self._span += 1
                
        return result
        
    def parseWords(self, data):
        self._data = data
        self._span = 0
        self._len = len(data)
        return self.readValue()

    def quoteString(self, theString):
        return '"%s"' % theString
                        
                        
    def logout(self):
        self.send('QUIT')
        self.parseResponse()
        self._sp.close()
        self._sp = None
        self._connected = False
        self._logged = False
        
				
