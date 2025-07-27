from collections import defaultdict

from .fallback import py_props_to_tree, py_tree_to_props

try:
    from ._props_to_tree import _props_to_tree, _tree_to_props
except ImportError:
    _use_c = False
else:
    _use_c = True


def endless():
    return defaultdict(endless)


def c_props_to_tree(props):
    return _props_to_tree(props, endless())


c_tree_to_props = _tree_to_props


if _use_c:
    props_to_tree = c_props_to_tree
else:
    props_to_tree = py_props_to_tree


if _use_c:
    tree_to_props = c_tree_to_props
else:
    tree_to_props = py_tree_to_props
