from __future__ import unicode_literals

from ..conversions import *
from ..func_utils import *


def Number(this, args):
    if len(args) == 0:
        return 0.
    return to_number(args[0])


def NumberConstructor(args, space):
    temp = space.NewObject()
    temp.prototype = space.NumberPrototype
    temp.Class = 'Number'
    temp.value = float(to_number(get_arg(args, 0)) if len(args) > 0 else 0.)
    return temp


CONSTS = {
    'MAX_VALUE': 1.7976931348623157e308,
    'MIN_VALUE': 5.0e-324,
    'NaN': NaN,
    'NEGATIVE_INFINITY': Infinity,
    'POSITIVE_INFINITY': -Infinity
}
