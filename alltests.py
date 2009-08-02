#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys

def suite():
    modules_to_test = ('cli_parse_cgp_test', 'cli_methodmissing_test', )
    test_module = __import__('test')
    alltests = unittest.TestSuite()
    
    for module in modules_to_test:
        __import__('test.%s' % module)
        m = test_module.__getattribute__(module)
        alltests.addTest(unittest.findTestCases(m))
        
    return alltests

if __name__ == '__main__':
    if './src' not in sys.path:
           sys.path.append('./src/')
    unittest.main(defaultTest='suite')
