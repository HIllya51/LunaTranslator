from __future__ import unicode_literals
# Type Conversions. to_type. All must return PyJs subclass instance
from .simplex import *


def to_primitive(self, hint=None):
    if is_primitive(self):
        return self
    if hint is None and (self.Class == 'Number' or self.Class == 'Boolean'):
        # favour number for Class== Number or Boolean default = String
        hint = 'Number'
    return self.default_value(hint)


def to_boolean(self):
    typ = Type(self)
    if typ == 'Boolean':  # no need to convert
        return self
    elif typ == 'Null' or typ == 'Undefined':  # they are both always false
        return False
    elif typ == 'Number':  # false only for 0, and NaN
        return self and self == self  # test for nan (nan -> flase)
    elif typ == 'String':
        return bool(self)
    else:  # object -  always True
        return True


def to_number(self):
    typ = Type(self)
    if typ == 'Number':  # or self.Class=='Number':   # no need to convert
        return self
    elif typ == 'Null':  # null is 0
        return 0.
    elif typ == 'Undefined':  # undefined is NaN
        return NaN
    elif typ == 'Boolean':  # 1 for True 0 for false
        return float(self)
    elif typ == 'String':
        s = self.strip()  # Strip white space
        if not s:  # '' is simply 0
            return 0.
        if 'x' in s or 'X' in s[:3]:  # hex (positive only)
            try:  # try to convert
                num = int(s, 16)
            except ValueError:  # could not convert -> NaN
                return NaN
            return float(num)
        sign = 1  # get sign
        if s[0] in '+-':
            if s[0] == '-':
                sign = -1
            s = s[1:]
        if s == 'Infinity':  # Check for infinity keyword. 'NaN' will be NaN anyway.
            return sign * Infinity
        try:  # decimal try
            num = sign * float(s)  # Converted
        except ValueError:
            return NaN  # could not convert to decimal  > return NaN
        return float(num)
    else:  # object -  most likely it will be NaN.
        return to_number(to_primitive(self, 'Number'))


def to_string(self):
    typ = Type(self)
    if typ == 'String':
        return self
    elif typ == 'Null':
        return 'null'
    elif typ == 'Undefined':
        return 'undefined'
    elif typ == 'Boolean':
        return 'true' if self else 'false'
    elif typ == 'Number':  # or self.Class=='Number':
        return js_dtoa(self)
    else:  # object
        return to_string(to_primitive(self, 'String'))


def to_object(self, space):
    typ = Type(self)
    if typ == 'Object':
        return self
    elif typ == 'Boolean':  # Unsure ... todo check here
        return space.Boolean.create((self, ), space)
    elif typ == 'Number':  # ?
        return space.Number.create((self, ), space)
    elif typ == 'String':  # ?
        return space.String.create((self, ), space)
    elif typ == 'Null' or typ == 'Undefined':
        raise MakeError('TypeError',
                        'undefined or null can\'t be converted to object')
    else:
        raise RuntimeError()


def to_int32(self):
    num = to_number(self)
    if is_nan(num) or is_infinity(num):
        return 0
    int32 = int(num) % 2**32
    return int(int32 - 2**32 if int32 >= 2**31 else int32)


def to_int(self):
    num = to_number(self)
    if is_nan(num):
        return 0
    elif is_infinity(num):
        return 10**20 if num > 0 else -10**20
    return int(num)


def to_uint32(self):
    num = to_number(self)
    if is_nan(num) or is_infinity(num):
        return 0
    return int(num) % 2**32


def to_uint16(self):
    num = to_number(self)
    if is_nan(num) or is_infinity(num):
        return 0
    return int(num) % 2**16


def to_int16(self):
    num = to_number(self)
    if is_nan(num) or is_infinity(num):
        return 0
    int16 = int(num) % 2**16
    return int(int16 - 2**16 if int16 >= 2**15 else int16)


def cok(self):
    """Check object coercible"""
    if type(self) in (UNDEFINED_TYPE, NULL_TYPE):
        raise MakeError('TypeError',
                        'undefined or null can\'t be converted to object')
