import collections
import copy
import datetime
import json
import sys
import time
import unittest

from ax_utils.unicode_utils import decode_nested, encode_nested

from .sample_objects import big_doc

if sys.version_info.major == 3:
    long = int


class TestConvertNested(unittest.TestCase):
    def test_equal(self):
        new_ob = encode_nested(copy.deepcopy(big_doc))
        self.assertEqual(new_ob, big_doc)

    def test_encode_happens(self):
        ob = copy.deepcopy(big_doc)
        ob['foo'] = {'a': [{'b': [(1, 2, ['\xd6sterreich'])]}]}

        ob = encode_nested(ob)

        key = tuple(ob[b'foo'])[0]
        self.assertTrue(isinstance(key, bytes))
        self.assertFalse(isinstance(key, str))

        self.assertTrue(isinstance(ob[b'foo'][b'a'][0][b'b'][0][2][0], bytes))

        self.assertFalse(isinstance(ob[b'foo'][b'a'][0][b'b'][0][2][0], str))

        ref = {b'a': [{b'b': [(1, 2, [b'\xc3\x96sterreich'])]}]}
        self.assertEqual(ob[b'foo'], ref)

    def test_long_int(self):
        self.assertEqual(2**66, encode_nested(2**66))

    def test_pymongo_int64(self):
        class Int64(int):
            pass

        ob = Int64(2**66)
        ret = encode_nested(ob)
        self.assertTrue(ob is ret)

    def test_ordered_dict(self):
        ob = collections.OrderedDict()
        ob[1] = 'a'
        ob[2] = 'b'
        ob[3] = 'c'
        ob[10000] = 'd'
        ob[20000] = 'e'

        new_ob = encode_nested(ob)

        self.assertIsInstance(new_ob, collections.OrderedDict)
        self.assertEqual((1, 2, 3, 10000, 20000), tuple(new_ob))

    def test_decode_nested(self):
        ob = {b'a': [{b'b': [(1, 2, [b'\xc3\x96sterreich'])]}]}

        new = decode_nested(ob)
        ref = {'a': [{'b': [(1, 2, ['\xd6sterreich'])]}]}
        self.assertEqual(ref, new)
        self.assertEqual(ob, encode_nested(new))

    def test_encode_datetime(self):
        ob = datetime.datetime.utcnow()
        new_ob = encode_nested(ob)
        self.assertEqual(ob, new_ob)

    def test_perf(self):
        return
        print
        nb = 100000

        start = time.time()
        for _ in range(nb):
            encode_nested(big_doc)
        print(
            'big object with %s bytes json: ' % len(json.dumps(big_doc)),
        )
        print(int(nb / (time.time() - start)), ' OPS/s')

        start = time.time()
        for _ in range(nb):
            encode_nested(big_doc['props'])
        print(
            'small object with %s bytes json: ' % len(json.dumps(big_doc['props'])),
        )
        print(int(nb / (time.time() - start)), ' OPS/s')

    def test_encode_and_decode_nested_bytearray(self):
        ob = {b'a': [{b'b': [(1, 2, [bytearray(b'\x04')])]}]}
        new = encode_nested(ob)
        # Nothing should happen, this is already bytes.
        self.assertEqual(ob, new)

        ob = {b'a': [{b'b': [(1, 2, [bytearray(b'\x04')])]}]}
        new = decode_nested(ob)
        ref = {'a': [{'b': [(1, 2, ['\x04'])]}]}
        self.assertEqual(ref, new)
        self.assertEqual(ob, encode_nested(new))
