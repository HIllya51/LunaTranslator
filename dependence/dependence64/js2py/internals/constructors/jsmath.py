from __future__ import unicode_literals

from ..conversions import *
from ..func_utils import *

import math
import random

CONSTANTS = {
    'E': 2.7182818284590452354,
    'LN10': 2.302585092994046,
    'LN2': 0.6931471805599453,
    'LOG2E': 1.4426950408889634,
    'LOG10E': 0.4342944819032518,
    'PI': 3.1415926535897932,
    'SQRT1_2': 0.7071067811865476,
    'SQRT2': 1.4142135623730951
}
def is_infinity(x):
    return x - 1e10 == x

class MathFunctions:
    def abs(this, args):
        x = get_arg(args, 0)
        a = to_number(x)
        if a != a:  # it must be a nan
            return NaN
        return abs(a)

    def acos(this, args):
        x = get_arg(args, 0)
        a = to_number(x)
        if a != a:  # it must be a nan
            return NaN
        try:
            return math.acos(a)
        except:
            return NaN

    def asin(this, args):
        x = get_arg(args, 0)
        a = to_number(x)
        if a != a:  # it must be a nan
            return NaN
        try:
            return math.asin(a)
        except:
            return NaN

    def atan(this, args):
        x = get_arg(args, 0)
        a = to_number(x)
        if a != a:  # it must be a nan
            return NaN
        return math.atan(a)

    def atan2(this, args):
        x = get_arg(args, 0)
        y = get_arg(args, 1)
        a = to_number(x)
        b = to_number(y)
        if a != a or b != b:  # it must be a nan
            return NaN
        return math.atan2(a, b)

    def ceil(this, args):
        x = get_arg(args, 0)
        a = to_number(x)
        if not is_finite(x):
            return x
        return float(math.ceil(a))

    def floor(this, args):
        x = get_arg(args, 0)
        a = to_number(x)
        if not is_finite(x):
            return x
        return float(math.floor(a))

    def round(this, args):
        x = get_arg(args, 0)
        a = to_number(x)
        if not is_finite(x):
            return x
        return float(round(a))

    def sin(this, args):
        x = get_arg(args, 0)
        a = to_number(x)
        if not is_finite(a):  # it must be a nan
            return NaN
        return math.sin(a)

    def cos(this, args):
        x = get_arg(args, 0)
        a = to_number(x)
        if not is_finite(a):  # it must be a nan
            return NaN
        return math.cos(a)

    def tan(this, args):
        x = get_arg(args, 0)
        a = to_number(x)
        if not is_finite(a):  # it must be a nan
            return NaN
        return math.tan(a)

    def log(this, args):
        x = get_arg(args, 0)
        a = to_number(x)
        if a != a:  # it must be a nan
            return NaN
        try:
            return math.log(a)
        except:
            return NaN

    def exp(this, args):
        x = get_arg(args, 0)
        a = to_number(x)
        if a != a:  # it must be a nan
            return NaN
        return math.exp(a)

    def pow(this, args):
        x = get_arg(args, 0)
        y = get_arg(args, 1)
        a = to_number(x)
        b = to_number(y)
        if a != a or b != b:  # it must be a nan
            return NaN
        try:
            return a**b
        except:
            return NaN

    def sqrt(this, args):
        x = get_arg(args, 0)
        a = to_number(x)
        if a != a:  # it must be a nan
            return NaN
        try:
            return a**0.5
        except:
            return NaN

    def min(this, args):
        if len(args) == 0:
            return Infinity
        return min(map(to_number, tuple(args)))

    def max(this, args):
        if len(args) == 0:
            return -Infinity
        return max(map(to_number, tuple(args)))

    def random(this, args):
        return random.random()
