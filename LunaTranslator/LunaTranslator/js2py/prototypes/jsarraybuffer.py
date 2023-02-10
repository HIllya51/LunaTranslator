# this is based on jsarray.py

import six

if six.PY3:
    xrange = range
    import functools


def to_arr(this):
    """Returns Python array from Js array"""
    return [this.get(str(e)) for e in xrange(len(this))]


ARR_STACK = set({})


class ArrayBufferPrototype:
    pass
