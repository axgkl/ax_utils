from collections import defaultdict


def endless():
    return defaultdict(endless)


def py_props_to_tree(props):
    tree = endless()
    for name, value in props.items():
        local = tree
        n = name.split('.')
        for x in n[:-1]:
            local = local[x]
        local[n[-1]] = value
    return tree


def py_tree_to_props(tree):
    props = {}
    _recursive([], props, tree)
    return props


def _recursive(names, to_add, curr_node):
    if isinstance(curr_node, dict):
        for name, value in curr_node.items():
            names.append(name)
            _recursive(names, to_add, value)
            names.pop()
    else:
        to_add['.'.join(names)] = curr_node
