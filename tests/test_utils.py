"""
Test the stackify.__init__ setup functions
"""

import unittest
from mock import patch
from .bases import ClearEnvTest

import stackify
import logging


class TestInit(ClearEnvTest):
    '''
    Test the logger init functionality
    '''

    def setUp(self):
        super(TestInit, self).setUp()
        self.config = stackify.transport.application.ApiConfiguration(
            application='test_appname',
            environment='test_environment',
            api_key='test_apikey',
            api_url='test_apiurl')
        self.loggers = []

    def tearDown(self):
        super(TestInit, self).tearDown()
        global_loggers = logging.Logger.manager.loggerDict
        for logger in self.loggers:
            del global_loggers[logger.name]

    def test_utils_data_to_json_unserializable(self):
        dummy = Dummy()
        result = stackify.utils.data_to_json(dummy)
        substring = '<tests.test_utils.Dummy object at'
        self.assertTrue(substring in result)

    def test_utils_data_to_json_dict(self):
        dummy = {
            'test': 'test'
        }
        result = stackify.utils.data_to_json(dummy)
        expected = '{"test": "test"}'
        self.assertEqual(expected, result)

    def test_utils_data_to_json_list(self):
        dummy = [1, 2, 3]
        result = stackify.utils.data_to_json(dummy)
        expected = '[1, 2, 3]'
        self.assertEqual(expected, result)

    def test_utils_data_to_json_tuple(self):
        dummy = (1, 2)
        result = stackify.utils.data_to_json(dummy)
        expected = '[1, 2]'
        self.assertEqual(expected, result)

    def test_utils_data_to_json_dummy_iterable(self):
        dummy = DummyInterable()
        result = stackify.utils.data_to_json(dummy)
        expected = '{"a": 21}'
        self.assertEqual(expected, result)

    def test_utils_data_to_json_dummy_object_with_property(self):
        dummy = DummyProperty()
        result = stackify.utils.data_to_json(dummy)
        expected = '{"x": 5}'
        self.assertEqual(expected, result)

    @patch('logging.Logger.exception')
    def test_utils_data_to_json_dummy_object_circular(self, func):
        dummy = DummyProperty()
        data = {
            'test': '1',
            'dummy': dummy,
            'payload': {}
        }
        data['payload']['dummy'] = data

        result = stackify.utils.data_to_json(data)
        func.assert_called()

        substring = "'dummy': <tests.test_utils.DummyProperty object at"
        self.assertTrue(substring in result)

    def test_utils_data_to_json_dummy_request(self):
        dummy = DummyRequest()
        result = stackify.utils.data_to_json(dummy)
        substring = '{"_messages": "<tests.test_utils.Dummy object at'
        self.assertTrue(substring in result)


class Dummy(object):
    pass


class DummyInterable:
    def __iter__(self):
        self.a = 1
        return self

    def __next__(self):
        if self.a <= 20:
            x = self.a
            self.a += 1
            return x
        else:
            raise StopIteration

    def next(self):
        return self.__next__()


class DummyProperty(object):
    def __init__(self):
        self.x = 5


class DummyRequest(object):
    def __init__(self):
        self._messages = Dummy()


if __name__ == '__main__':
    unittest.main()
