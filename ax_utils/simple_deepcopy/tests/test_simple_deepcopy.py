import copy
import time
import unittest

from ax_utils.ax_tree.ax_tree import AXTree
from ax_utils.simple_deepcopy._simple_deepcopy import deepcopy
from ax_utils.unicode_utils.tests.sample_objects import big_doc


class HowDeepIsYourLove(object):
    def __init__(self):
        self.a = 1
        self.b = 3
        self.c = 4

    def __eq__(self, other):
        c1 = self.a = other.a
        c2 = self.b = other.b
        c3 = self.c = other.c
        return c1 and c2 and c3


class TestSimpleDeepCopy(unittest.TestCase):
    def test_copy_long_int(self):
        val = 2**64 + 282931
        ret = deepcopy(val)
        self.assertEqual(val, ret)
        self.assertEqual(id(val), id(ret))

    def test_copy_dict(self):
        val = {'a': 1}
        ret = deepcopy(val)
        self.assertEqual(val, ret)
        self.assertNotEqual(id(val), id(ret))

    def test_copy_big_ob(self):
        ret = deepcopy(big_doc)
        self.assertEqual(big_doc, ret)

    def test_fallback_to_deepcopy(self):
        ob = HowDeepIsYourLove()
        ret = deepcopy([ob, ob, ob])
        self.assertEqual([ob, ob, ob], ret)

    def test_speed_small_ob(self):
        return
        # On small objects the speedup is factor 40.

        start = time.time()
        for _ in range(10**5):
            deepcopy(big_doc['props'])
        print('fast', time.time() - start)

        start = time.time()
        for _ in range(10**5):
            copy.deepcopy(big_doc['props'])
        print('slow', time.time() - start)

    def test_speed_big_ob(self):
        return
        # On small objects the speedup is factor 38.

        start = time.time()
        for _ in range(10**4):
            deepcopy(big_doc)
        print('fast', time.time() - start)

        start = time.time()
        for _ in range(10**4):
            copy.deepcopy(big_doc)
        print('slow', time.time() - start)

    def test_ax_tree(self):
        src = AXTree({'a.b.c': 1})
        dst = deepcopy(src)

        self.assertIsInstance(dst, AXTree)
        self.assertNotEqual(id(dst), id(src))
        self.assertEqual(dst, src)
        self.assertIsInstance(dst['a.b'], AXTree)
