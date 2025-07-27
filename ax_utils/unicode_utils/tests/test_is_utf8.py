import struct
import time
import unittest

from ax_utils.unicode_utils import is_utf8


class TestIsUTF8(unittest.TestCase):
    def _gen_str(self, *args):
        return b''.join(bytes([i]) for i in args)

    def test_isutf8(self):
        self.assertTrue(is_utf8(b'a'))
        self.assertTrue(is_utf8('a'))
        self.assertFalse(is_utf8(bytes([0b11111111])))
        self.assertFalse(is_utf8(int2byte(0b10000000)))
        self.assertTrue(is_utf8(int2byte(0b01111111)))

        x = self._gen_str(0b11110001, 0b10000000, 0b10000000, 0b10000000)
        self.assertTrue(is_utf8(x))

        x = self._gen_str(0b11110011, 0b10111111, 0b10111111, 0b10111111)
        self.assertTrue(is_utf8(x))

        x = self._gen_str(0b11110001, 0b10000000, 0b10000000, 0b01000000)
        self.assertFalse(is_utf8(x))

        x = self._gen_str(0b11110001, 0b10000000, 0b10000000, 0b00000000)
        self.assertFalse(is_utf8(x))

        x = b"\xf4\\\x89\x93';"
        self.assertFalse(is_utf8(x))

    def test_perf(self):
        return
        x = 'a' * 1024

        start = time.time()
        for _ in range(10**6):
            is_utf8(x)
        print(time.time() - start)
