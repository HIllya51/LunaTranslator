from ..conversions import *
from ..func_utils import *


def Boolean(this, args):
    return to_boolean(get_arg(args, 0))


def BooleanConstructor(args, space):
    temp = space.NewObject()
    temp.prototype = space.BooleanPrototype
    temp.Class = 'Boolean'
    temp.value = to_boolean(get_arg(args, 0))
    return temp
