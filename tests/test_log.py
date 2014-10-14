"""
Test the stackify.log module
"""

import unittest
from mock import patch, Mock
import json
import sys

import stackify.log

from stackify.log import LogMsg
import logging
import json
import time
#logging.LogRecord('name','level','pathname','lineno','msg','args','exc_info','func')


class TestLogPopulate(unittest.TestCase):
    '''
    Test populating log objects with data
    '''

    def test_record_to_error(self):
        '''LogMsgs can load logger records'''
        record = logging.LogRecord('name',logging.WARNING,'pathname',32,
                'message',(),(),'func')
        record.my_extra = [1,2,3]
        msg = LogMsg()
        msg.from_record(record)

        curr_ms = time.time() * 1000

        self.assertEqual(msg.SrcMethod, 'func')
        self.assertEqual(msg.SrcLine, 32)
        self.assertEqual(msg.Th, 'MainThread')
        self.assertEqual(msg.Msg, 'message')
        self.assertTrue(msg.EpochMs <= curr_ms)
        self.assertEqual(json.loads(msg.data), {'my_extra':[1,2,3]})

    def test_record_exception(self):
        '''LogMsgs can parse exception information'''
        class CustomException(Exception):
            def __str__(self):
                return 'My custom exception'

        try:
            raise CustomException()
        except:
            record = logging.LogRecord('my exception',logging.WARNING,'somepath',12,
                    'a thing happened',(),sys.exc_info())

        msg = LogMsg()
        msg.from_record(record)

        self.assertEqual(msg.Ex.OccurredEpochMillis, msg.EpochMs)
        stack = msg.Ex.Error.StackTrace[0]
        self.assertTrue(stack.CodeFileName.endswith('test_log.py'))
        self.assertEqual(msg.Ex.Error.Message, 'My custom exception')
        self.assertEqual(msg.Ex.Error.ErrorType, 'CustomException')
        self.assertEqual(msg.Ex.Error.SourceMethod, 'test_record_exception')


if __name__=='__main__':
    unittest.main()

