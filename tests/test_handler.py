"""
Test the stackify.handler module
"""

import unittest
from mock import patch, Mock

try:
    import Queue as queue
except ImportError:
    import queue

from stackify.handler import StackifyHandler, StackifyListener
from stackify.application import ApiConfiguration

import logging


class TestHandler(unittest.TestCase):
    '''
    Test the StackifyHandler class
    '''

    def test_queue_full(self):
        '''The queue should evict when full'''
        q = queue.Queue(1)
        handler = StackifyHandler(queue_=q, listener=Mock())
        # don't print warnings on overflow, so mute stackify logger
        logging.getLogger('stackify').propagate = False
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
        # don't print warnings on http crashes, so mute stackify logger
        logging.getLogger('stackify').propagate = False

    @patch('stackify.handler.LogMsg')
    @patch('stackify.handler.StackifyListener.send_group')
    @patch('stackify.handler.HTTPClient.POST')
    def test_not_identified(self, post, send_group, logmsg):
        '''The HTTPClient identifies automatically if needed'''
        listener = StackifyListener(queue_=Mock(), config=self.config)
        listener.handle(Mock())
        self.assertTrue(listener.http.identified)

    @patch('stackify.handler.LogMsg')
    @patch('stackify.handler.LogMsgGroup')
    @patch('stackify.handler.HTTPClient.POST')
    def test_send_group_if_needed(self, post, logmsggroup, logmsg):
        '''The listener sends groups of messages'''
        listener = StackifyListener(queue_=Mock(), max_batch=3, config=self.config)
        listener.http.identified = True

        listener.handle(1)
        self.assertFalse(post.called)
        listener.handle(2)
        self.assertFalse(post.called)
        self.assertEqual(len(listener.messages), 2)
        listener.handle(3)
        self.assertTrue(post.called)
        self.assertEqual(len(listener.messages), 0)
        listener.handle(4)
        self.assertEqual(post.call_count, 1)
        self.assertEqual(len(listener.messages), 1)

    @patch('stackify.handler.LogMsg')
    @patch('stackify.handler.StackifyListener.send_group')
    def test_clear_queue_shutdown(self, send_group, logmsg):
        '''The listener sends the leftover messages on the queue when shutting down'''
        listener = StackifyListener(queue_=Mock(), max_batch=3, config=self.config)
        listener.http.identified = True
        listener._thread = Mock()

        listener.handle(1)
        listener.handle(2)
        self.assertFalse(send_group.called)
        listener.stop()
        self.assertTrue(send_group.called)

    @patch('stackify.handler.LogMsg')
    @patch('stackify.handler.LogMsgGroup')
    @patch('stackify.handler.HTTPClient.send_log_group')
    def test_send_group_crash(self, send_log_group, logmsggroup, logmsg):
        '''The listener drops messages after retrying'''
        listener = StackifyListener(queue_=Mock(), max_batch=3, config=self.config)
        listener.http.identified = True

        send_log_group.side_effect = Exception

        listener.handle(1)
        listener.handle(2)
        listener.handle(3)
        self.assertEqual(len(listener.messages), 0)
        listener.handle(4)
        self.assertEqual(len(listener.messages), 1)
        self.assertEqual(send_log_group.call_count, 1)


if __name__=='__main__':
    unittest.main()

