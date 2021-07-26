from unittest import TestCase

from stackifyapm.utils.compat import b
from stackifyapm.utils.compat import iterkeys
from stackifyapm.utils.compat import iteritems


class CompatTest(TestCase):
    def setUp(self):
        self.dict_data = {
            "key1": "value1",
            "key2": "value2"
        }
        self.list_data = ["foo", "bar"]

    def test_convert_string_to_byte(self):
        byte = '1'

        value = b(byte)

        assert isinstance(value, bytes)

    def test_iterkeys_should_return_iterator(self):
        iter_keys = iterkeys(self.dict_data)

        self.assert_instance_is_an_iterator(iter_keys)

    def test_iteritems_should_return_iterator(self):
        iter_items = iteritems(self.dict_data)

        self.assert_instance_is_an_iterator(iter_items)

    def assert_instance_is_an_iterator(self, item):
        try:
            iter(item)
            assert True
        except Exception:
            assert False
