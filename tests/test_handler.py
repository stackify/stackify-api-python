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
from stackify.transport.application import ApiConfiguration

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
            application='test_appname',
            environment='test_environment',
            api_key='test_apikey',
            api_url='test_apiurl',
        )
        # don't print warnings on http crashes, so mute stackify logger
        logging.getLogger('stackify').propagate = False

    @patch('stackify.transport.default.DefaultTransport.create_message')
    @patch('stackify.transport.default.http.HTTPClient.POST')
    def test_not_identified(self, post, logmsg):
        '''The HTTPClient identifies automatically if needed'''
        listener = StackifyListener(queue_=Mock(), config=self.config)
        listener.handle(Mock())
        listener.send_group()
        self.assertTrue(listener.transport._transport.identified)

    @patch('stackify.transport.default.DefaultTransport.create_message')
    @patch('stackify.transport.default.DefaultTransport.create_group_message')
    @patch('stackify.transport.default.http.HTTPClient.POST')
    def test_send_group_if_needed(self, post, logmsggroup, logmsg):
        '''The listener sends groups of messages'''
        listener = StackifyListener(queue_=Mock(), max_batch=3, config=self.config)
        listener.transport._transport.identified = True

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

    @patch('stackify.transport.default.DefaultTransport.create_message')
    @patch('stackify.handler.StackifyListener.send_group')
    def test_clear_queue_shutdown(self, send_group, logmsg):
        '''The listener sends the leftover messages on the queue when shutting down'''
        listener = StackifyListener(queue_=Mock(), max_batch=3, config=self.config)
        listener.transport._transport.identified = True
        listener._thread = Mock()

        listener.handle(1)
        listener.handle(2)
        self.assertFalse(send_group.called)
        listener.stop()
        self.assertTrue(send_group.called)

    @patch('stackify.transport.default.DefaultTransport.create_message')
    @patch('stackify.transport.default.DefaultTransport.create_group_message')
    @patch('stackify.transport.default.http.HTTPClient.send_log_group')
    def test_send_group_crash(self, send_log_group, logmsggroup, logmsg):
        '''The listener drops messages after retrying'''
        listener = StackifyListener(queue_=Mock(), max_batch=3, config=self.config)
        listener.transport._transport.identified = True

        send_log_group.side_effect = Exception

        listener.handle(1)
        listener.handle(2)
        listener.handle(3)
        self.assertEqual(len(listener.messages), 0)
        listener.handle(4)
        self.assertEqual(len(listener.messages), 1)
        self.assertEqual(send_log_group.call_count, 1)

    @patch('stackify.transport.default.DefaultTransport.create_message')
    @patch('stackify.transport.default.DefaultTransport.create_group_message')
    @patch('stackify.transport.default.http.HTTPClient.send_log_group')
    def test_create_message_crash(self, send_log_group, logmsggroup, logmsg):
        '''The listener drops messages after retrying'''
        listener = StackifyListener(queue_=Mock(), max_batch=3, config=self.config)
        listener.transport._transport.identified = True

        logmsg.side_effect = Exception

        listener.handle(1)
        listener.handle(2)
        listener.handle(3)
        self.assertEqual(len(listener.messages), 0)
        listener.handle(4)
        self.assertEqual(len(listener.messages), 0)  # messages not created
        self.assertEqual(logmsg.call_count, 4)  # we called the function 4 times
        self.assertEqual(send_log_group.call_count, 0)  # since we have exceptions


if __name__ == '__main__':
    unittest.main()
