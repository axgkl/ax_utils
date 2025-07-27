import sys


def out(msg):
    if sys.stdout.isatty():
        print(msg)


def set_defaultencoding(encoding='utf-8', force=None):
    """
    Offering to setting the default str() encoding process wide to UTF-8:
    We do it only if it is not changed already, from ascii (
    for a reason we assume, like when testing with 'undefined')
    """

    def unalias(enc):
        # UTF-8, utf8...:
        return enc.lower().replace('-', '')

    _cur_enc = sys.getdefaultencoding()
    cur_enc = unalias(_cur_enc)
    if cur_enc == unalias(encoding):
        return
    if 'ascii' not in cur_enc:
        if not force:
            # already changed - but to sth else:
            # should we raise? I think no. Maybe a test wrapper set it away, now
            # the default process setup starts and wants utf-8. That should work
            # w/o probs. So:
            out(
                (
                    'NOT setting defaultencoding to %s - already changed to %s. '
                    'Consider the force flag.'
                )
                % (encoding, _cur_enc)
            )
            return
        else:
            out(
                'Defaultencoding already changed to %s! Forcing to %s.'
                % ((_cur_enc, encoding))
            )

    _cur_stdout = sys.stdout
    _cur_stdin = sys.stdin
    _cur_stderr = sys.stderr
    reload(sys)
    sys.stdout = _cur_stdout
    sys.stdin = _cur_stdin
    sys.stderr = _cur_stderr

    sys.setdefaultencoding(encoding)
    out('Changed the default encoding process wide to %s(!)' % encoding)


def json_loads_bytes():
    """
    Since unicode is returned by json.loads we avoid having to change core
    logic involving json.loads once and for all through a monkey patch of the
    json lib(s)
    Note: suds, soappy return bytes. xml libs not checked but assumed to do as
    well.
    """

    from ._convert_nested import encode_nested

    def patch_lib(lib):
        lib.loads_decoded = lib.loads

        def loads_encoded(*a, **kw):
            unic = lib.loads_decoded(*a, **kw)
            return encode_nested(unic)

        lib.loads = loads_encoded
        out(
            (
                '%10s: Patched to return bytes at deserialization. '
                'Use %s.loads_decoded() to get unicode.'
            )
            % ((lib.__name__,) * 2)
        )

    import json

    if hasattr(json, 'loads_decoded'):
        # already patched:
        return
    patch_lib(json)

    try:
        import simplejson
    except ImportError:
        pass
    else:
        patch_lib(simplejson)
