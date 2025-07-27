"""
This module provides two AXTree classes.
An AXTree behaves exactly like a 'plain' python dict, *except* that dotted keys
like 'a.b.c.d' are converted to nested dicts of dicts.

1)
There is an AXTree class which uses a plain dict for internal storage
==> no order of the keys.
This class has a python implementation PLUS a C-Extensions for the
'core' methods (__getitem__, __setitem__, iter_leaf_*)

2)
There is AXOrderedTree class which uses a OrderedDict for internal storage
===> order of the kyes.
This class has a python implementation ONLY, no great speed
"""

import warnings
from collections import OrderedDict, deque
from collections.abc import Iterator as ABC_Iterator
from copyreg import pickle

# this is a marker for .pop(), otherwise we are not able to detect if a
# object is already in or not
_marker = object()


def _build_base(_base_name, _base_parent_type):
    """
    This builds a class with a python implementation of the basis functions.
    These functions are the 'core' functions of ax_tree.
    We build this base class dynamicly so it is possible to provide
    different _base_parent_type's.

    The C-Extensions provide exactly the same functions with the same
    behaviour.
    """

    def __init__(self, arg=None, **kwargs):
        _base_parent_type.__init__(self)
        self.update(arg, **kwargs)

    def update(self, arg=None, **kwargs):
        if arg is not None:
            if hasattr(arg, 'keys'):
                for n in arg.keys():
                    self[n] = arg[n]
            else:
                for k, v in arg:
                    self[k] = v

        for k, v in kwargs.items():
            self[k] = v

    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        return True

    def __getitem__(self, key):
        """
        Key can be a 'dotted' string. This function goes down the tree.

        For example you have a key 'a.b.c.d' will be translated into
        self['a']['b']['c']['d']
        """
        try:
            partial_keys = key.split('.')
        except AttributeError:
            # This happens if $key is not a basestring. Since all our keys must
            # be strings, we know that $key is not available.
            raise TypeError('Keys must be strings')

        current = self
        for partial_key in partial_keys:
            # Call the __getitem__ of the base type, because the base type is
            # responsible for 'really' storing the value
            if not isinstance(current, _base_parent_type):
                # This happens if you descend into undefined areas of the tree,
                # e.g. if you define
                #            x = AXOrderedTree({'1.2': "foo"})
                # and try to access x['1.2.3']
                raise KeyError('%s does not exist in the tree' % key)
            current = _base_parent_type.__getitem__(current, partial_key)

        return current

    def __setitem__(self, key, value):
        """
        Key can be a 'dottet' string. This function build automaticly the tree

        For example you have key:'a.b.c.d' value:1 then a tree like this is
        build.
        {'a' : {'b' : {'c' : {'d' : 1} } } }
        """
        parts = key.split('.')

        ## build the tree until the last key
        for n in parts[:-1]:
            # use __class__ instead of a static one, because this function is
            # used in different classes with different base classes
            self = _base_parent_type.setdefault(self, n, self.__class__())

        # if it's already an AXTree then no need to step into the value again,
        # because AXTree guarantees a well defined tree
        if isinstance(value, self.__class__):
            _base_parent_type.__setitem__(self, parts[-1], value)
        elif isinstance(value, dict):
            # step down value, because it can look like this {'a.b.d' : 1}
            _base_parent_type.__setitem__(self, parts[-1], self.__class__(value))
        else:
            _base_parent_type.__setitem__(self, parts[-1], value)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def iter_leave_keys(self):
        warn_msg = (
            'iter_leave_keys is deprecated, '
            'use iter_leaf_keys instead. '
            'The iter_leave_keys method will be removed 2014-05-15'
        )
        warnings.warn(warn_msg, DeprecationWarning, 2)
        return self.iter_leaf_keys()

    def iter_leave_values(self):
        warn_msg = (
            'iter_leave_values is deprecated, '
            'use iter_leaf_values instead. '
            'The iter_leave_values method will be removed 2014-05-15'
        )
        warnings.warn(warn_msg, DeprecationWarning, 2)
        return self.iter_leaf_values()

    def iter_leave_items(self):
        warn_msg = (
            'iter_leave_items is deprecated, '
            'use iter_leaf_items instead. '
            'The iter_leave_items method will be removed 2014-05-15'
        )
        warnings.warn(warn_msg, DeprecationWarning, 2)
        return self.iter_leaf_items()

    def iter_leaf_keys(self):
        return AXTreeKeysIterator(self)

    def iter_leaf_values(self):
        return AXTreeValuesIterator(self)

    def iter_leaf_items(self):
        return AXTreeItemsIterator(self)

    # prepare the attributes and methods for the new class to generate
    attributes = dict(locals())
    del attributes['_base_name']
    del attributes['_base_parent_type']
    # generate a new class
    return type(_base_name, (_base_parent_type,), attributes)


# Try to import the C-Extensions for AXTree
try:
    from ax_utils.ax_tree._ax_tree import _AXTree
except ImportError:
    # Fall back to the python implementation
    _AXTree = _build_base('_SlowAXTree', dict)


def _build_axtree(_base_name, _base_parent_type):
    """
    Build a AXTree Class.
    Again it is possible to provide different base classes
    """

    # We need to override *all* methods from dict, otherwise
    # __getitem__, __setitem__ from _base_parent_type are NOT used.
    # They are responsible for breaking the 'dotted' keys into the tree.

    def __delitem__(self, key):
        parts = key.split('.')
        cur = self
        for n in parts[:-1]:
            cur = cur[n]
        _base_parent_type.__delitem__(cur, parts[-1])

    def number_of_leaves(self):
        return len(list(self.iter_leaf_keys()))

    def fromkeys(self, iterable, v=None):
        for key in iterable:
            self[key] = v

    def has_key(self, key):
        return key in self

    def pop(self, key, v=_marker):
        try:
            ret = self[key]
            del self[key]
            return ret
        except KeyError:
            if v is _marker:
                raise
            return v

    def setdefault(self, key, v=None):
        try:
            return self[key]
        except KeyError:
            self[key] = v
            return v

    def merge(self, tree, **options):
        override_with_empty = options.get('override_with_empty', False)
        for key, value in tree.iter_leaf_items():
            # Don't override existing values.
            if (not override_with_empty) and (value == {} and key in self):
                continue

            self[key] = value

    def copy(self):
        return self.__class__(self)

    # Zope RestrictedPython assumess structures (that are not dict or list) to
    # have __guarded_setitem__, __guarded_delitem__, __guarded_setattr__, and
    # __guarded_delattr__ attributes. For instance, classes not having these
    # attributes are not allowed to do assignments or del operations.
    # These statements will fail if the attributes are not included:
    #     x['5'] = 1
    #     del x['7']
    # Some background can be found in the RestrictedPython/Guards.py:103
    __guarded_setitem__ = _base_parent_type.__setitem__
    __guarded_delitem__ = _base_parent_type.__delitem__

    attributes = dict(locals())
    del attributes['_base_name']
    del attributes['_base_parent_type']
    return type(_base_name, (_base_parent_type,), attributes)


# Build an AXTree-Class where a 'plain' python dictionary is used for storage
AXTree = _build_axtree('AXTree', _AXTree)

# Build an AXTree-Class where an 'OrderedDict' is used for storage
_AXOrderedTree = _build_base('_AXOrderedTree', OrderedDict)
AXOrderedTree = _build_axtree('AXOrderedTree', _AXOrderedTree)


# Registering at pickle makes pickle.dumps a little 3x faster
def pickle_ax_tree(obj):
    return AXTree, (), None, None, obj.iter_leaf_items()


pickle(AXTree, pickle_ax_tree)


# Here are python implementations of iterators over AXTree
# They are only used in
# * AXOrderedTree
# * AXTree (if the import of C-Extension fails)
class AXTreeIterator(ABC_Iterator):
    def __init__(self, tree):
        # the iterator needs to decide if he should go 'downwards' in the tree.
        # He does that by inspecting the type of a node.
        # Is the Node a Tree then move all its children onto the 'self.nodes'.
        # 'self.nodes' is a stack of nodes to iterate over on the next step.
        self._tree_class = tree.__class__
        self.nodes = deque(tree.items())

    def __iter__(self):
        return self

    def __next__(self):
        while self.nodes:
            name, value = self.nodes.popleft()
            if not isinstance(value, self._tree_class):
                return self._get(name, value)

            # If value is empty consider it as a leaf.
            if not value:
                return self._get(name, value)

            for new_name, new_value in reversed(list(value.items())):
                self.nodes.appendleft(('.'.join((name, new_name)), new_value))

        raise StopIteration()


class AXTreeKeysIterator(AXTreeIterator):
    def _get(self, name, value):
        return name


class AXTreeValuesIterator(AXTreeIterator):
    def _get(self, name, value):
        return value


class AXTreeItemsIterator(AXTreeIterator):
    def _get(self, name, value):
        return (name, value)
