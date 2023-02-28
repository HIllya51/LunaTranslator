from .simplex import *
from .conversions import *

import six
if six.PY3:
    basestring = str
    long = int
    xrange = range
    unicode = str


def get_arg(arguments, n):
    if len(arguments) <= n:
        return undefined
    return arguments[n]


def ensure_js_types(args, space=None):
    return tuple(convert_to_js_type(e, space=space) for e in args)


def convert_to_js_type(e, space=None):
    t = type(e)
    if is_js_type(e):
        return e
    if t in (int, long, float):
        return float(e)
    elif isinstance(t, basestring):
        return unicode(t)
    elif t in (list, tuple):
        if space is None:
            raise MakeError(
                'TypeError',
                'Actually an internal error, could not convert to js type because space not specified'
            )
        return space.ConstructArray(ensure_js_types(e, space=space))
    elif t == dict:
        if space is None:
            raise MakeError(
                'TypeError',
                'Actually an internal error, could not convert to js type because space not specified'
            )
        new = {}
        for k, v in e.items():
            new[to_string(convert_to_js_type(k, space))] = convert_to_js_type(
                v, space)
        return space.ConstructObject(new)
    else:
        raise MakeError('TypeError', 'Could not convert to js type!')


def is_js_type(e):
    if type(e) in PRIMITIVES:
        return True
    elif hasattr(e, 'Class') and hasattr(e, 'value'):  # not perfect but works
        return True
    else:
        return False


# todo optimise these 2!
def js_array_to_tuple(arr):
    length = to_uint32(arr.get(u'length'))
    return tuple(arr.get(unicode(e)) for e in xrange(length))


def js_array_to_list(arr):
    length = to_uint32(arr.get(u'length'))
    return [arr.get(unicode(e)) for e in xrange(length)]


def js_arr_length(arr):
    return to_uint32(arr.get(u'length'))
