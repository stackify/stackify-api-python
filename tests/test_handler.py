#!/usr/bin/env python
"""
Test the stackify.handler module
"""

import unittest
from mock import patch, Mock

try:
    import Queue as queue
except ImportError:
    import queue

import stackify.handler
from stackify.handler import StackifyHandler, StackifyListener
from stackify.application import ApiConfiguration


class TestHandler(unittest.TestCase):
    '''
    Test the StackifyHandler class
    '''

    def test_queue_full(self):
        '''The queue should evict when full'''
        q = queue.Queue(1)
        handler = StackifyHandler(queue_=q, listener=Mock())
        handler.enqueue('test1')
        handler.enqueue('test2')
        handler.enqueue('test3')
        self.assertEqual(q.qsize(), 1)
        self.assertEqual(q.get(), 'test3')

class TestListener(unittest.TestCase):
    '''
    Test the StackifyListener class
    '''

    def setUp(self):
        self.config = ApiConfiguration(
            application = 'test_appname',
            environment = 'test_environment',
            api_key = 'test_apikey',
            api_url = 'test_apiurl')

    @patch('stackify.handler.LogMsg')
    @patch.object(StackifyListener, 'send_group')
    @patch('stackify.http.HTTPClient.identify_application')
    def test_not_identified(self, logmsg, send_group, ident):
        '''The HTTPClient identifies automatically if needed'''
        q = queue.Queue(1)
        listener = StackifyListener(queue_=q, config=self.config)
        listener.handle(Mock())
        self.assertTrue(ident.called)


if __name__=='__main__':
    unittest.main()

