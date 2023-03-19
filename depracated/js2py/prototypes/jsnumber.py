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
    if num.is_nan():
        return num.Js('NaN')
    elif num.is_infinity():
        sign = '-' if num.value < 0 else ''
        return num.Js(sign + 'Infinity')
    elif isinstance(num.value,
                    (long, int)) or num.value.is_integer():  # dont print .0
        return num.Js(unicode(int(num.value)))
    return num.Js(unicode(num.value))  # accurate enough


class NumberPrototype:
    def toString(radix):
        if this.Class != 'Number':
            raise this.MakeError('TypeError',
                                 'Number.prototype.valueOf is not generic')
        if radix.is_undefined():
            return to_str_rep(this)
        r = radix.to_int()
        if r == 10:
            return to_str_rep(this)
        if r not in xrange(2, 37):
            raise this.MakeError(
                'RangeError',
                'Number.prototype.toString() radix argument must be between 2 and 36'
            )
        num = this.to_int()
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

    def valueOf():
        if this.Class != 'Number':
            raise this.MakeError('TypeError',
                                 'Number.prototype.valueOf is not generic')
        return this.value

    def toLocaleString():
        return this.to_string()

    def toFixed(fractionDigits):
        if this.Class != 'Number':
            raise this.MakeError(
                'TypeError',
                'Number.prototype.toFixed called on incompatible receiver')
        digs = fractionDigits.to_int()
        if digs < 0 or digs > 20:
            raise this.MakeError(
                'RangeError',
                'toFixed() digits argument must be between 0 and 20')
        elif this.is_infinity():
            return 'Infinity' if this.value > 0 else '-Infinity'
        elif this.is_nan():
            return 'NaN'
        return format(this.value, '-.%df' % digs)

    def toExponential(fractionDigits):
        if this.Class != 'Number':
            raise this.MakeError(
                'TypeError',
                'Number.prototype.toExponential called on incompatible receiver'
            )
        digs = fractionDigits.to_int()
        if digs < 0 or digs > 20:
            raise this.MakeError(
                'RangeError',
                'toFixed() digits argument must be between 0 and 20')
        elif this.is_infinity():
            return 'Infinity' if this.value > 0 else '-Infinity'
        elif this.is_nan():
            return 'NaN'
        return format(this.value, '-.%de' % digs)

    def toPrecision(precision):
        if this.Class != 'Number':
            raise this.MakeError(
                'TypeError',
                'Number.prototype.toPrecision called on incompatible receiver')
        if precision.is_undefined():
            return this.to_string()
        prec = precision.to_int()
        if this.is_nan():
            return 'NaN'
        elif this.is_infinity():
            return 'Infinity' if this.value > 0 else '-Infinity'
        digs = prec - len(str(int(this.value)))
        if digs >= 0:
            return format(this.value, '-.%df' % digs)
        else:
            return format(this.value, '-.%df' % (prec - 1))
