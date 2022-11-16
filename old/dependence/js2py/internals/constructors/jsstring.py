from ..conversions import *
from ..func_utils import *
from six import unichr

def fromCharCode(this, args):
    res = u''
    for e in args:
        res += unichr(to_uint16(e))
    return res


def String(this, args):
    if len(args) == 0:
        return u''
    return to_string(args[0])


def StringConstructor(args, space):
    temp = space.NewObject()
    temp.prototype = space.StringPrototype
    temp.Class = 'String'
    temp.value = to_string(get_arg(args, 0)) if len(args) > 0 else u''
    return temp
