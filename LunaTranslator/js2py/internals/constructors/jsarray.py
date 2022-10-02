from ..conversions import *
from ..func_utils import *


def Array(this, args):
    return ArrayConstructor(args, args.space)


def ArrayConstructor(args, space):
    if len(args) == 1:
        l = get_arg(args, 0)
        if type(l) == float:
            if to_uint32(l) == l:
                return space.NewArray(l)
            else:
                raise MakeError(
                    'RangeError',
                    'Invalid length specified for Array constructor (must be uint32)'
                )
        else:
            return space.ConstructArray([l])
    else:
        return space.ConstructArray(list(args))


def isArray(this, args):
    x = get_arg(args, 0)
    return is_object(x) and x.Class == u'Array'
