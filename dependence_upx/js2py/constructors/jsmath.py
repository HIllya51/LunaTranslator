from ..base import *
import math
import random

Math = PyJsObject(prototype=ObjectPrototype)
Math.Class = 'Math'

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

for constant, value in CONSTANTS.items():
    Math.define_own_property(
        constant, {
            'value': Js(value),
            'writable': False,
            'enumerable': False,
            'configurable': False
        })


class MathFunctions:
    def abs(x):
        a = x.to_number().value
        if a != a:  # it must be a nan
            return NaN
        return abs(a)

    def acos(x):
        a = x.to_number().value
        if a != a:  # it must be a nan
            return NaN
        try:
            return math.acos(a)
        except:
            return NaN

    def asin(x):
        a = x.to_number().value
        if a != a:  # it must be a nan
            return NaN
        try:
            return math.asin(a)
        except:
            return NaN

    def atan(x):
        a = x.to_number().value
        if a != a:  # it must be a nan
            return NaN
        return math.atan(a)

    def atan2(y, x):
        a = x.to_number().value
        b = y.to_number().value
        if a != a or b != b:  # it must be a nan
            return NaN
        return math.atan2(b, a)

    def ceil(x):
        a = x.to_number().value
        if a != a:  # it must be a nan
            return NaN
        return math.ceil(a)

    def floor(x):
        a = x.to_number().value
        if a != a:  # it must be a nan
            return NaN
        return math.floor(a)

    def round(x):
        a = x.to_number().value
        if a != a:  # it must be a nan
            return NaN
        return round(a)

    def sin(x):
        a = x.to_number().value
        if a != a:  # it must be a nan
            return NaN
        return math.sin(a)

    def cos(x):
        a = x.to_number().value
        if a != a:  # it must be a nan
            return NaN
        return math.cos(a)

    def tan(x):
        a = x.to_number().value
        if a != a:  # it must be a nan
            return NaN
        return math.tan(a)

    def log(x):
        a = x.to_number().value
        if a != a:  # it must be a nan
            return NaN
        try:
            return math.log(a)
        except:
            return NaN

    def exp(x):
        a = x.to_number().value
        if a != a:  # it must be a nan
            return NaN
        return math.exp(a)

    def pow(x, y):
        a = x.to_number().value
        b = y.to_number().value
        if a != a or b != b:  # it must be a nan
            return NaN
        try:
            return a**b
        except:
            return NaN

    def sqrt(x):
        a = x.to_number().value
        if a != a:  # it must be a nan
            return NaN
        try:
            return a**0.5
        except:
            return NaN

    def min():
        if not len(arguments):
            return Infinity
        lis = tuple(e.to_number().value for e in arguments.to_list())
        if any(e != e for e in lis):  # we dont want NaNs
            return NaN
        return min(*lis)

    def max():
        if not len(arguments):
            return -Infinity
        lis = tuple(e.to_number().value for e in arguments.to_list())
        if any(e != e for e in lis):  # we dont want NaNs
            return NaN
        return max(*lis)

    def random():
        return random.random()


fill_prototype(Math, MathFunctions, default_attrs)
