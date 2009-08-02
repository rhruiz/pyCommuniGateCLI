#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys

def suite():
    modules_to_test = ('cli_parse_cgp_test',) # and so on
    alltests = unittest.TestSuite()
    for module in map(__import__, modules_to_test):
        alltests.addTest(unittest.findTestCases(module))
    return alltests

if __name__ == '__main__':
    if  '../src' not in sys.path:
        sys.path.append('../src/')
        
    unittest.main(defaultTest='suite')