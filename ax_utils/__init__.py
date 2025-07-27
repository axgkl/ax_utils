import os
import sys

# see build test script:
if os.environ.get('ENFORCE_GEVENT_DURING_BUILD_TESTS'):
    # this is a test-only requirement - we do work in gevent but not
    # require it. Since we are the base paket for all others we make sure here
    # that our tests do indeed work in such an environ:
    from gevent import monkey

    monkey.patch_all()


def package_home(globals_dict):
    __name__ = globals_dict['__name__']
    module = sys.modules[__name__]
    if hasattr(module, '__path__'):
        r = module.__path__[0]
    elif '.' in __name__:
        r = sys.modules[__name__[: __name__.rfind('.')]].__path__[0]
    else:
        r = __name__
    return os.path.abspath(r)


def get_object_from_module(full_name, search_folder):
    """Returns an arbitrary item from a module.
        Note that the item is returned, not imported. This can be used for
        dynamic loading of classes/factories according to a configuration.

        Sample call:
        producer_class = get_object_from_module\
                ("ax_utils.event_sources.parallel_queue.Job_Producer",\
                "/opt/axtract")
    """
    if '.' not in full_name:
        msg = 'Need a module where to search the object: %s'
        raise Exception(msg % full_name)

    mod_name, object_name = full_name.rsplit('.', 1)

    # Ensure we are really loading from search_folder. If we append() to
    # sys.path, full_name could be loaded from some other path if a module
    # of that name happens to exist there.
    sys.path.insert(0, search_folder)
    try:
        mod = __import__(mod_name, globals(), locals(), [object_name])
    finally:
        sys.path.remove(search_folder)

    # object_name is a global variable in the module
    return getattr(mod, object_name)


def my_members(tclass):
    """Return only direct member vars, not from parents

    Usefull mainly in interactive sessions.
    """
    inherited = set()
    for base_class in tclass.__bases__:
        inherited |= set(dir(base_class))
    return list(set(dir(tclass)) - inherited)


def obj_members(obj, direct_only=True, with_values=None, fmt=None):
    """show all members, except those starting with __"""
    if hasattr(obj, '__class__'):
        tclass = obj.__class__
    else:
        tclass = obj
    if with_values:
        l1, l2, l3, l4 = {}, {}, {}, {}
    else:
        l1, l2, l3, l4 = [], [], [], []
    res = {
        'mine': {'methods': l1, 'parameters': l2},
        'inherited': {'methods': l3, 'parameters': l4},
    }
    mine = my_members(tclass)
    inherited = dir(tclass)
    for i in inherited:
        if i.startswith('__'):
            continue
        if i in mine:
            m = res.get('mine')
        else:
            if direct_only:
                continue
            m = res.get('inherited')
        v = '%s' % getattr(tclass, i)
        if ' method ' in v:
            m1 = m.get('methods')
        else:
            m1 = m.get('parameters')
        if with_values:
            m1[i] = v
        else:
            m1.append(i)
    if direct_only:
        del res['inherited']
    if fmt:
        from ax_utils.formatting.pretty_print import dict_to_txt

        return dict_to_txt(res, fmt=fmt)
    return res
