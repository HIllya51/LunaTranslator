from __future__ import unicode_literals
from ..conversions import *
from ..func_utils import *

import six
if six.PY3:
    basestring = str
    long = int
    xrange = range
    unicode = str

RADIX_SYMBOLS = {
    0: '0',
    1: '1',
    2: '2',
    3: '3',
    4: '4',
    5: '5',
    6: '6',
    7: '7',
    8: '8',
    9: '9',
    10: 'a',
    11: 'b',
    12: 'c',
    13: 'd',
    14: 'e',
    15: 'f',
    16: 'g',
    17: 'h',
    18: 'i',
    19: 'j',
    20: 'k',
    21: 'l',
    22: 'm',
    23: 'n',
    24: 'o',
    25: 'p',
    26: 'q',
    27: 'r',
    28: 's',
    29: 't',
    30: 'u',
    31: 'v',
    32: 'w',
    33: 'x',
    34: 'y',
    35: 'z'
}


def to_str_rep(num):
    if is_nan(num):
        return 'NaN'
    elif is_infinity(num):
        sign = '-' if num < 0 else ''
        return sign + 'Infinity'
    elif int(num) == num:  # dont print .0
        return unicode(int(num))
    return unicode(num)  # todo: Make it 100% consistent with Node


class NumberPrototype:
    def toString(this, args):
        if GetClass(this) != 'Number':
            raise MakeError('TypeError',
                            'Number.prototype.valueOf is not generic')
        if type(this) != float:
            this = this.value
        radix = get_arg(args, 0)
        if is_undefined(radix):
            return to_str_rep(this)
        r = to_int(radix)
        if r == 10:
            return to_str_rep(this)
        if r not in xrange(2, 37) or radix != r:
            raise MakeError(
                'RangeError',
                'Number.prototype.toString() radix argument must be an integer between 2 and 36'
            )
        num = to_int(this)
        if num < 0:
            num = -num
            sign = '-'
        else:
            sign = ''
        res = ''
        while num:
            s = RADIX_SYMBOLS[num % r]
            num = num // r
            res = s + res
        return sign + (res if res else '0')

    def valueOf(this, args):
        if GetClass(this) != 'Number':
            raise MakeError('TypeError',
                            'Number.prototype.valueOf is not generic')
        if type(this) != float:
            this = this.value
        return this

    def toFixed(this, args):
        if GetClass(this) != 'Number':
            raise MakeError(
                'TypeError',
                'Number.prototype.toFixed called on incompatible receiver')
        if type(this) != float:
            this = this.value
        fractionDigits = get_arg(args, 0)
        digs = to_int(fractionDigits)
        if digs < 0 or digs > 20:
            raise MakeError(
                'RangeError',
                'toFixed() digits argument must be between 0 and 20')
        elif is_infinity(this):
            return 'Infinity' if this > 0 else '-Infinity'
        elif is_nan(this):
            return 'NaN'
        return format(this, '-.%df' % digs)

    def toExponential(this, args):
        if GetClass(this) != 'Number':
            raise MakeError(
                'TypeError',
                'Number.prototype.toExponential called on incompatible receiver'
            )
        if type(this) != float:
            this = this.value
        fractionDigits = get_arg(args, 0)
        digs = to_int(fractionDigits)
        if digs < 0 or digs > 20:
            raise MakeError(
                'RangeError',
                'toFixed() digits argument must be between 0 and 20')
        elif is_infinity(this):
            return 'Infinity' if this > 0 else '-Infinity'
        elif is_nan(this):
            return 'NaN'
        return format(this, '-.%de' % digs)

    def toPrecision(this, args):
        if GetClass(this) != 'Number':
            raise MakeError(
                'TypeError',
                'Number.prototype.toPrecision called on incompatible receiver')
        if type(this) != float:
            this = this.value
        precision = get_arg(args, 0)
        if is_undefined(precision):
            return to_string(this)
        prec = to_int(precision)
        if is_nan(this):
            return 'NaN'
        elif is_infinity(this):
            return 'Infinity' if this > 0 else '-Infinity'
        digs = prec - len(str(int(this)))
        if digs >= 0:
            return format(this, '-.%df' % digs)
        else:
            return format(this, '-.%df' % (prec - 1))


NumberPrototype.toLocaleString = NumberPrototype.toString
