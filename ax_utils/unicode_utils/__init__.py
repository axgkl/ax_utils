# -*- coding: utf-8 -*-

# Ignore import errors here since they cannot be caught by unittests
try:
    from ._convert_nested import decode_nested, encode_nested
    from ._isutf8 import is_utf8
except:
    pass

# Converts an object to 'str' or 'unicode', depending on the object itself.
# It just a *MORE* efficient way of:  '%s' % (ob,)
# Don't delete this line here, it is used as imports from other modules.
try:
    from ._convert_nested import as_basestring
except Exception:

    def as_basestring(ob):
        return '%s' % (ob,)


# MySQL's unicode support is restriced for their 'utf8' to BMP only (3 bytes).
# So Python's (full) 'utf-8' codec must be harmonized with theirs for any mysql
# connection via this:
import codecs

codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)

from .monkey_patches import json_loads_bytes, set_defaultencoding

# This is a backport of python3.5 'backslashreplace'
# To use it do:
# 1) Somewhere at import time:
# codecs.register_error("ax_backslashreplace_backport", ax_backslashreplace_backport)


# 2) Within the application use this
# bytes_obj.decode('...', 'ax_backslashreplace_backport')
def ax_backslashreplace_backport(error):
    if not isinstance(error, UnicodeDecodeError):
        raise Exception('Only UnicodeDecodeError are supported')

    bad_slice = error.object[error.start : error.end]

    # Iterating byte strings returns in on 3.x but str on 2.x
    as_int = lambda x: x if isinstance(x, int) else ord(x)
    replaced = ''.join('\\x{:02x}'.format(as_int(c)) for c in bad_slice)
    return (replaced, error.end)
