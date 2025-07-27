import pickle
import random
import time
import unittest

from ax_utils.ax_tree._ax_tree import _AXTree
from ax_utils.ax_tree.ax_tree import AXOrderedTree, AXTree, _build_axtree, _build_base


class TestAXTree(unittest.TestCase):
    tree_class = AXTree

    def test_init(self):
        tree = self.tree_class()
        self.assertIsInstance(tree, self.tree_class)

    def test_from_dict(self):
        old = {
            'a.b.b': 2,
            'a.b.c': {'a': 3},
            'a.b.d': {'a.c': {'a.e': 1}},
        }

        ref = {'a': {'b': {'c': {'a': 3}, 'b': 2, 'd': {'a': {'c': {'a': {'e': 1}}}}}}}

        tree = self.tree_class(old)
        self.assertEqual(tree, ref)

    def test_from_iterable(self):
        tree = self.tree_class([('a.b', 1), ('b', 2)])
        ref = {'a': {'b': 1}, 'b': 2}
        self.assertEqual(tree, ref)

    def test_from_kwargs(self):
        tree = self.tree_class(a=1, b={'b': 2})
        self.assertEqual(tree, {'a': 1, 'b': {'b': 2}})

    def test_node_is_primitive(self):
        # we do NOT automaticly override nodes wich are already primitives
        tree = self.tree_class()
        tree['a'] = 1

        def wrong():
            tree['a.b'] = 1

        self.assertRaises(TypeError, wrong)

    def test_iter_keys(self):
        tree = self.tree_class([('a.b', 1), ('b.b.b.b', 2)])
        self.assertEqual(sorted(tree.iter_leaf_keys()), ['a.b', 'b.b.b.b'])

    def test_iter_values(self):
        tree = self.tree_class([('a.b', 1), ('b.b.b.b', 2)])
        self.assertEqual(sorted(tree.iter_leaf_values()), [1, 2])

    def test_iter_items(self):
        items = [('a.b', 1), ('b.b.b.b', 2)]
        tree = self.tree_class(items)

        ref = [('a.b', 1), ('b.b.b.b', 2)]
        self.assertEqual(sorted(tree.iter_leaf_items()), ref)

    def test_iter_items_with_emtpy_leaf(self):
        tree = self.tree_class({'a.b.c': {}})

        ref = [('a.b.c', {})]
        self.assertEqual(ref, list(tree.iter_leaf_items()))

    def test_iter_keys_with_emtpy_leaf(self):
        tree = self.tree_class({'a.b.c': {}})

        ref = ['a.b.c']
        self.assertEqual(ref, list(tree.iter_leaf_keys()))

    def test_iter_values_with_emtpy_leaf(self):
        tree = self.tree_class({'a.b.c': {}})

        ref = [{}]
        self.assertEqual(ref, list(tree.iter_leaf_values()))

    def test_pop(self):
        """pop() must return correct item and delete it"""
        tree = self.tree_class()
        tree['foo'] = 'FOO'
        tree['bar'] = 'BAR'

        comparison = self.tree_class()
        comparison['bar'] = 'BAR'

        item = tree.pop('foo')
        self.assertEqual(item, 'FOO')
        self.assertEqual(tree, comparison)

        # pop()ing last item must properly clean up the tree
        item = tree.pop('bar')
        self.assertEqual(item, 'BAR')
        self.assertEqual(tree, self.tree_class())

    def test_del(self):
        tree = self.tree_class(
            {
                'foo': {'bar1': 1, 'bar2': {'x': 1, 'y': 2, 'z': 3}},
                'bar': 1,
                'ccc': {'xxx': {'yyy': {'ccc': 1, 'zzz': 2}}},
            }
        )

        del tree['foo.bar2.x']
        del tree['ccc.xxx']

        ref = self.tree_class(
            {'foo': {'bar1': 1, 'bar2': {'y': 2, 'z': 3}}, 'bar': 1, 'ccc': {}}
        )
        self.assertEqual(ref, tree)

    def test_merge(self):
        tree_merge_src = self.tree_class(
            {
                'foo': {'a': {'a': 1, 'b': 2}, 'c': {'a': 1, 'b': 2}},
                'bar': {'a': {'a': 3}, 'c': {'xxx': 1, 'yyy': 2}},
            }
        )

        tree_merge_dst = self.tree_class(
            {
                'foo': {
                    'a': {'a': 1, 'b': 8, 'd': 10},
                    'c': {
                        'a': 1,
                    },
                },
                'bar': {'a': {'a': 4}},
            }
        )

        tree_merge_dst.merge(tree_merge_src)

        ref = self.tree_class(
            {
                'foo': {'a': {'a': 1, 'b': 2, 'd': 10}, 'c': {'a': 1, 'b': 2}},
                'bar': {'a': {'a': 3}, 'c': {'xxx': 1, 'yyy': 2}},
            }
        )
        self.assertEqual(ref, tree_merge_dst)

    def test_source_has_empty_dict(self):
        dst = self.tree_class({'a.b.c': 1, 'a.b.d': 2})

        src = self.tree_class({'c': {}, 'a.b': {}})

        dst.merge(src)

        ref = self.tree_class({'c': {}, 'a.b.c': 1, 'a.b.d': 2})

        self.assertEqual(ref, dst)

    def test_source_has_empty_dict_with_override(self):
        dst = self.tree_class({'a.b.c': 1, 'a.b.d': 2})

        src = self.tree_class({'c': {}, 'a.b': {}})

        dst.merge(src, override_with_empty=True)

        ref = self.tree_class({'c': {}, 'a.b': {}})

        self.assertEqual(ref, dst)

    def test_pickle_dumps(self):
        tree = self.tree_class({'a.b.c': 1, 'd': 2})
        pickle.dumps(tree, pickle.HIGHEST_PROTOCOL)

    def test_pickle_loads(self):
        tree = self.tree_class({'a.b.c': 1, 'd': 2})
        self.assertEqual(
            tree, pickle.loads(pickle.dumps(tree, pickle.HIGHEST_PROTOCOL))
        )

    def test_get(self):
        tree = self.tree_class({'a.b.c': 1, 'd': 2})

        self.assertEqual(1, tree.get('a.b.c'))
        self.assertEqual(2, tree.get('d'))
        self.assertEqual(3, tree.get('b', 3))
        self.assertEqual(4, tree.get('a.x', 4))

    def test_init_by_keys(self):
        class StrangeContainer(object):
            def __init__(self, data):
                self.data = data

            def keys(self):
                return self.data.keys()

            def __getitem__(self, key):
                return self.data[key]

        c = StrangeContainer({'a.b.c': 1, 'd': 2, 'x': {'y': 1}})
        tree = self.tree_class(c)

        ref = {'a': {'b': {'c': 1}}, 'x': {'y': 1}, 'd': 2}
        self.assertEqual(ref, tree)

    def test_init_by_seq(self):
        seq = [('a', 1), ('b.c.d', 2), ('1', 1)]
        tree = self.tree_class(seq)

        ref = {'a': 1, '1': 1, 'b': {'c': {'d': 2}}}
        self.assertEqual(ref, tree)

    def test_init_by_kwargs(self):
        kwargs = {'a.b.c': 1, 'd': 2, 'u': {'y': 1}}
        tree = self.tree_class(x=1, z=2, **kwargs)

        ref = {'a': {'b': {'c': 1}}, 'x': 1, 'z': 2, 'u': {'y': 1}, 'd': 2}
        self.assertEqual(ref, tree)

    def test_key_in_tree(self):
        kwargs = {'a.b.c': 1, 'd': 2, 'u': {'y': 1}}
        tree = self.tree_class(x=1, z=2, **kwargs)

        self.assertTrue('a.b.c' in tree)
        self.assertTrue('a' in tree)
        self.assertTrue('u' in tree)
        self.assertTrue('u.y' in tree)
        self.assertFalse('m' in tree)
        self.assertFalse('a.b.l' in tree)

    def test_subtree_not_dict(self):
        tree = self.tree_class({'a.b': [], 'x.z': 1})
        with self.assertRaises(KeyError):
            tree['a.b.x']

    def test_init_with_none(self):
        self.assertEqual({}, self.tree_class(None))

    def test_nested_get(self):
        tree = self.tree_class({'a': 42})
        self.assertEqual('x', tree.get('a.b', 'x'))
        self.assertEqual('x', tree.get('a.b.', 'x'))
        self.assertEqual('x', tree.get('a.b.c', 'x'))

    def test_copy(self):
        tree = self.tree_class({'a.b.c': 1})

        other = tree.copy()
        self.assertIsInstance(other, self.tree_class)
        self.assertEqual(1, other['a.b.c'])

        tree['x.b'] = 1
        ref = {'a.b.c': 1, 'x.b': 1}
        self.assertEqual(ref, dict(tree.iter_leaf_items()))
        self.assertEqual({'a.b.c': 1}, dict(other.iter_leaf_items()))

        # copy is a *shallow* copy.
        tree['a.b.z'] = 2
        ref = {'a.b.c': 1, 'x.b': 1, 'a.b.z': 2}
        self.assertEqual(ref, dict(tree.iter_leaf_items()))
        self.assertEqual({'a.b.c': 1, 'a.b.z': 2}, dict(other.iter_leaf_items()))


class TestAXOrderedTree(unittest.TestCase):
    tree_class = AXOrderedTree
    input_ = [
        ('.1.3.6.1.4.1.33546.1.1', 1),
        ('.1.3.6.1.4.1.33546.1.2', 2),
        ('.1.3.6.1.4.1.33546.1.3', 3),
        ('.1.3.6.1.4.1.33546.2.1', 4),
        ('.1.3.6.1.4.1.33546.2.2', 5),
        ('.1.3.6.1.4.1.33546.2.3', 6),
    ]

    def test_iter_keys(self):
        tree = self.tree_class(self.input_)
        ref = [x[0] for x in self.input_]

        self.assertEqual(list(tree.iter_leaf_keys()), ref)

    def test_iter_values(self):
        tree = self.tree_class(self.input_)
        ref = [x[1] for x in self.input_]

        self.assertEqual(list(tree.iter_leaf_values()), ref)

    def test_iter_items(self):
        tree = self.tree_class(self.input_)
        self.assertEqual(list(tree.iter_leaf_items()), self.input_)

    def test_getitem(self):
        """
        __getitem__ function has to throw the KeyError exception
        for keys that don't exist
        """
        tree = self.tree_class(self.input_)
        self.assertEqual(1, tree['.1.3.6.1.4.1.33546.1.1'])
        # check the call tree['.1.3.6.1.4.1.33546.2.3.222']
        with self.assertRaises(KeyError):
            tree['.1.3.6.1.4.1.33546.2.3.222']

    def test_get_and_has_key(self):
        """
        This test has to check the correct 'get' and 'has_key' functionality:
              if key type is correct:
              -> get returns None, if there is no such key
              -> has_key returns false, if the key doesn't exist
        """
        tree = self.tree_class(self.input_)

        # has_key() assertions
        self.assertTrue(tree.has_key('.1.3.6.1.4.1.33546.2.3'))
        self.assertFalse(tree.has_key('.1.3.6.1.4.1.33546.2.323.22'))

        # get() assertions
        self.assertEqual(6, tree.get('.1.3.6.1.4.1.33546.2.3'))
        self.assertIsNone(tree.get('.1.3.6.1.4.1.33546.2.323.22'))
        self.assertEqual(55, tree.get('.1.3.6.1.4.1.33546.2.323.22', 55))

        # __contains__ assertions
        self.assertTrue('.1.3.6.1.4.1.33546.2.3' in tree)
        self.assertFalse('.1.3.6.1.4.1.33546.2.323.22' in tree)

    def test_type_errors(self):
        """
        This test covers the check for incorrect key types
        if key type is incorrect:
        -> get and has_key have to throw the TypeError exception
        """
        tree = self.tree_class(self.input_)
        # check TypeError exceptions
        # -> 'dict' / 'list' is not hashable
        self.assertRaises(TypeError, tree.has_key, {1: 2})
        self.assertRaises(TypeError, tree.has_key, [1])
        self.assertRaises(TypeError, tree.get, {1: 2})
        self.assertRaises(TypeError, tree.get, [1])

    def test_pop(self):
        """pop() must return correct item and delete it"""
        tree = self.tree_class()
        tree['foo'] = 'FOO'
        tree['bar'] = 'BAR'

        comparison = self.tree_class()
        comparison['bar'] = 'BAR'

        item = tree.pop('foo')
        self.assertEqual(item, 'FOO')
        self.assertEqual(tree, comparison)

        # pop()ing last item must properly clean up the tree
        item = tree.pop('bar')
        self.assertEqual(item, 'BAR')
        self.assertEqual(tree, self.tree_class())

    def test_copy(self):
        tree = self.tree_class({'a.b.c': 1})

        other = tree.copy()
        self.assertIsInstance(other, self.tree_class)
        self.assertEqual(1, other['a.b.c'])

        tree['x.b'] = 1
        ref = {'a.b.c': 1, 'x.b': 1}
        self.assertEqual(ref, dict(tree.iter_leaf_items()))
        self.assertEqual({'a.b.c': 1}, dict(other.iter_leaf_items()))

        # copy is a *shallow* copy.
        tree['a.b.z'] = 2
        ref = {'a.b.c': 1, 'x.b': 1, 'a.b.z': 2}
        self.assertEqual(ref, dict(tree.iter_leaf_items()))
        self.assertEqual({'a.b.c': 1, 'a.b.z': 2}, dict(other.iter_leaf_items()))


class TestPerf(unittest.TestCase):
    level = 2

    def setUp(self):
        ## build up the classes we want to benchmark

        self.classes = []
        # AXTree with pure python implemenation
        slow_base = _build_base('_py_impl', dict)
        slow_tree = _build_axtree('_slow_tree', slow_base)
        self.classes.append(slow_tree)

        fast_tree = _build_axtree('_fast_tree', _AXTree)
        self.classes.append(fast_tree)
        self.classes.append(AXOrderedTree)
        self.classes.append(dict)

        self.NB = 10**5
        self.ITER_NB = 250

    def _insert_perf(self, cls):
        tree = cls()

        start = time.time()
        for x in range(self.NB):
            tree['DI.SV.%s' % (x % 1000)] = 1
        count = (self.NB / (time.time() - start)) / 10**6
        return 'MIO inserts per sec %s' % count

    def test_set_perf(self):
        for cls in self.classes:
            ret = (cls, self._insert_perf(cls))
            print(ret)

    def _get_perf(self, cls):
        init = [('DI.SV.%s' % x, 1) for x in range(1000)]
        tree = cls(init)

        start = time.time()
        for x in range(self.NB):
            tree['DI.SV.%s' % (x % 1000)]

        count = (self.NB / (time.time() - start)) / 10**6
        return 'MIO gets per sec: %s' % count

    def test_get_perf(self):
        for cls in self.classes:
            ret = (cls, self._get_perf(cls))
            print(ret)

    def test_contains_perf(self):
        for cls in self.classes:
            ret = (cls, self._contains_pref(cls))
            print(ret)

    def _contains_pref(self, cls):
        init = [(str(x), 1) for x in range(1000)]
        tree = cls(init)

        start = time.time()
        for x in range(self.NB):
            str(x % 1000) in tree

        count = (self.NB / (time.time() - start)) / 10**6
        return 'MIO contains per sec: %s' % count

    def test_init_perf(self):
        for cls in self.classes:
            ret = (cls, self._init_pref(cls))
            print(ret)

    def _init_pref(self, cls):
        start = time.time()
        for x in range(self.NB):
            cls()

        count = (self.NB / (time.time() - start)) / 10**6
        return 'MIO empyt inits per sec: %s' % count

    def _get_function_perf(self, cls):
        init = [(str(x), 1) for x in range(1000)]
        tree = cls(init)

        start = time.time()
        for x in range(self.NB):
            tree.get(str(x % 1000))

        count = (self.NB / (time.time() - start)) / 10**6
        return 'MIO get-function per sec: %s' % count

    def test_get_function_perf(self):
        for cls in self.classes:
            ret = (cls, self._get_function_perf(cls))
            print(ret)

    def _test_get_iter_perf(self, cls, iter_meth):
        items = 10000
        init = [('DI.SV.%s' % (300 * random.random()), 1) for x in range(items)]
        tree = cls(init)

        meth = getattr(tree, iter_meth)
        start = time.time()
        for _ in range(self.ITER_NB):
            list(meth())
        count = ((self.ITER_NB * items) / (time.time() - start)) / 10**6
        return 'MIO iterations per sec: %s' % count

    def test_iter_keys_perf(self):
        # come the leaf iteration with a plain dict iteration of keys
        # OF course the plain iterkeyys is faster ! BUT this tests gives you an
        # overview how slow we are :|
        for cls in self.classes:
            if cls is dict:
                meth = 'keys'
            else:
                meth = 'iter_leaf_keys'

            ret = (cls, self._test_get_iter_perf(cls, meth))
            print(ret)

    def test_pickle_dumps_perf(self):
        for cls in (AXTree, AXOrderedTree):
            tree = cls({'a.b.c': 1, 'd': 2})
            start = time.time()
            for _ in range(10**5):
                pickle.dumps(tree, pickle.HIGHEST_PROTOCOL)
            print('dumps', cls, time.time() - start)

    def test_pickle_loads_perf(self):
        for cls in (AXTree, AXOrderedTree):
            tree = cls({'a.b.c': 1, 'd': 2})
            dumped = pickle.dumps(tree, pickle.HIGHEST_PROTOCOL)
            start = time.time()
            for _ in range(10**5):
                pickle.loads(dumped)
            print('loads', cls, time.time() - start)


if __name__ == '__main__':
    unittest.main()
