#!/usr/bin/env python
"""
Test the stackify.log module
"""

import unittest
from mock import patch, Mock
import json

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


if __name__=='__main__':
    unittest.main()

