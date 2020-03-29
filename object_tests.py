import unittest
from b1u3object import String


class ObjectTest(unittest.TestCase):
    def test_string_hash_key(self):
        hello1 = String(value="Hello World")
        hello2 = String(value="Hello World")
        diff1 = String(value="My name is Johny")
        diff2 = String(value="My name is Johny")
        self.assertEqual(hello1.hash_key(), hello2.hash_key())
        self.assertEqual(diff1.hash_key(), diff2.hash_key())
        self.assertNotEqual(hello1.hash_key(), diff1.hash_key())


