#!/usr/bin/env python
"""
Test the stackify.formats module
"""

import unittest
from mock import patch, Mock
import json

from stackify.formats import JSONObject

class TestJSONObject(unittest.TestCase):
    '''
    Test the JSON serializer object
    '''

    def test_json_attributes(self):
        '''Attributes are serialized in JSON'''
        class MyTest(JSONObject):
            def __init__(self):
                self.a = '1'
                self.b = 2
                self.c = False
        result = MyTest().toJSON()

        self.assertEqual(json.loads(result), {'a': '1', 'b': 2, 'c': False})

    def test_nested_json(self):
        '''Nested classes are serialized in JSON'''
        class MyParent(JSONObject):
            def __init__(self, children):
                self.children = children

        class MyChild(JSONObject):
            def __init__(self, color):
                self.color = color

        result = MyParent([MyChild('red'), MyChild('green')]).toJSON()

        self.assertEqual(json.loads(result), {'children': [{'color': 'red'}, {'color': 'green'}]})

    def test_nonempty_attributes(self):
        '''Only nonempty attributes are serialized'''
        class MyTest(JSONObject):
            def __init__(self):
                self.a = '1'
                self.b = False
                self.c = None
                self.d = []
        result = MyTest().toJSON()

        self.assertEqual(json.loads(result), {'a': '1', 'b': False, 'd': []})


if __name__=='__main__':
    unittest.main()

