#!/usr/bin/env python
"""
Test the stackify.http module
"""

import unittest
from mock import patch, Mock

import stackify.http


class TestClient(unittest.TestCase):
    '''
    Test the HTTP Client and associated utilities
    '''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_logger_no_config(self):
        '''GZIP encoder works'''
        correct = list('\x1f\x8b\x08\x00    \x02\xff\xf3H\xcd\xc9\xc9\xd7Q(\xcf/\xcaIQ\x04\x00\xe6\xc6\xe6\xeb\r\x00\x00\x00')
        gzipped = list(stackify.http.gzip_compress('Hello, world!'))
        gzipped[4:8] = '    ' # blank the mtime
        self.assertEqual(gzipped, correct)

if __name__=='__main__':
    unittest.main()

