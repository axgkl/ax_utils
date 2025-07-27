import pickle
import unittest

from ax_utils.props_to_tree import (
    c_props_to_tree,
    c_tree_to_props,
    py_props_to_tree,
    py_tree_to_props,
)


class TestPropsToTree(unittest.TestCase):
    example = {
        'I.MS.FOO': 1,
        'I.FS.XXX': 2,
        'I.MS.XXX': 3,
        'I.SH.IR.FR.SN.GK.KP': 'MB',
        'X': 4,
        'XXX.FFFF': 4,
    }

    def _check(self, tree):
        self.assertEqual(tree['I']['MS']['FOO'], 1)
        self.assertEqual(tree['I']['FS']['XXX'], 2)
        self.assertEqual(tree['I']['MS']['XXX'], 3)
        self.assertEqual(tree['I']['SH']['IR']['FR']['SN']['GK']['KP'], 'MB')
        self.assertEqual(tree['X'], 4)
        self.assertEqual(tree['XXX']['FFFF'], 4)

    def test_simple_py(self):
        self._check(py_props_to_tree(self.example))

    def test_c_version(self):
        self._check(c_props_to_tree(self.example))

    def test_simple_py_complex_tree(self):
        start = {'I.MS.FOO': {'WAN.LAN': {'NUM.FAB': 1}}}
        # IMPORTANT: Props to tree is not capable to convert the values also
        # the problem is the convert backwards ! we dont know the orgiginal
        # structure
        ref = {'I': {'MS': {'FOO': {'WAN.LAN': {'NUM.FAB': 1}}}}}
        self.assertEqual(ref, py_props_to_tree(start))

    def test_pickle_result(self):
        doc = {'I.MS.FOO': 1, 'I.MS.BAR': 2}
        ref = {'I': {'MS': {'FOO': 1, 'BAR': 2}}}

        ret = pickle.loads(pickle.dumps(py_props_to_tree(doc)))
        self.assertEqual(ref, ret)

        ret = pickle.loads(pickle.dumps(c_props_to_tree(doc)))
        self.assertEqual(ref, ret)

    def test_with_unicode(self):
        data = {'a.b': 1}
        ref = {'a': {'b': 1}}

        self.assertEqual(ref, py_props_to_tree(data))
        self.assertEqual(ref, c_props_to_tree(data))

    def test_with_wrong_key(self):
        data = {(): 1}

        with self.assertRaises(Exception):
            py_props_to_tree(data)

        with self.assertRaises(Exception):
            c_props_to_tree(data)


class TestTreeToProps(unittest.TestCase):
    tree = {
        'I': {'F': {'X': 1}, 'XXXX': {'FFF': 3, 'FD': 7}},
        'Foo': 1,
        'aaa': {'b': {'c': {'d': 1}}},
    }

    def _check(self, props):
        self.assertEqual(props['I.F.X'], 1)
        self.assertEqual(props['I.XXXX.FFF'], 3)
        self.assertEqual(props['I.XXXX.FD'], 7)
        self.assertEqual(props['Foo'], 1)
        self.assertEqual(props['aaa.b.c.d'], 1)

    def test_simple(self):
        self._check(py_tree_to_props(self.tree))

    def test_with_unicode(self):
        data = {'a': {'b': 1}}
        ref = {'a.b': 1}

        self.assertEqual(ref, c_tree_to_props(data))
        self.assertEqual(ref, py_tree_to_props(data))

    def test_fast(self):
        self._check(c_tree_to_props(self.tree))
