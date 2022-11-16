from __future__ import unicode_literals
from ..conversions import *
from ..func_utils import *

RADIX_CHARS = {
    '1': 1,
    '0': 0,
    '3': 3,
    '2': 2,
    '5': 5,
    '4': 4,
    '7': 7,
    '6': 6,
    '9': 9,
    '8': 8,
    'a': 10,
    'c': 12,
    'b': 11,
    'e': 14,
    'd': 13,
    'g': 16,
    'f': 15,
    'i': 18,
    'h': 17,
    'k': 20,
    'j': 19,
    'm': 22,
    'l': 21,
    'o': 24,
    'n': 23,
    'q': 26,
    'p': 25,
    's': 28,
    'r': 27,
    'u': 30,
    't': 29,
    'w': 32,
    'v': 31,
    'y': 34,
    'x': 33,
    'z': 35,
    'A': 10,
    'C': 12,
    'B': 11,
    'E': 14,
    'D': 13,
    'G': 16,
    'F': 15,
    'I': 18,
    'H': 17,
    'K': 20,
    'J': 19,
    'M': 22,
    'L': 21,
    'O': 24,
    'N': 23,
    'Q': 26,
    'P': 25,
    'S': 28,
    'R': 27,
    'U': 30,
    'T': 29,
    'W': 32,
    'V': 31,
    'Y': 34,
    'X': 33,
    'Z': 35
}

# parseFloat
# parseInt
# isFinite
# isNaN


def parseInt(this, args):
    string, radix = get_arg(args, 0), get_arg(args, 1)
    string = to_string(string).lstrip()
    sign = 1
    if string and string[0] in ('+', '-'):
        if string[0] == '-':
            sign = -1
        string = string[1:]
    r = to_int32(radix)
    strip_prefix = True
    if r:
        if r < 2 or r > 36:
            return NaN
        if r != 16:
            strip_prefix = False
    else:
        r = 10
    if strip_prefix:
        if len(string) >= 2 and string[:2] in ('0x', '0X'):
            string = string[2:]
            r = 16
    n = 0
    num = 0
    while n < len(string):
        cand = RADIX_CHARS.get(string[n])
        if cand is None or not cand < r:
            break
        num = cand + num * r
        n += 1
    if not n:
        return NaN
    return float(sign * num)


def parseFloat(this, args):
    string = get_arg(args, 0)
    string = to_string(string).strip()
    sign = 1
    if string and string[0] in ('+', '-'):
        if string[0] == '-':
            sign = -1
        string = string[1:]
    num = None
    length = 1
    max_len = None
    failed = 0
    while length <= len(string):
        try:
            num = float(string[:length])
            max_len = length
            failed = 0
        except:
            failed += 1
            if failed > 4:  # cant be a number anymore
                break
        length += 1
    if num is None:
        return NaN
    return sign * float(string[:max_len])


def isNaN(this, args):
    number = get_arg(args, 0)
    if is_nan(to_number(number)):
        return True
    return False


def isFinite(this, args):
    number = get_arg(args, 0)
    num = to_number(number)
    if is_nan(num) or is_infinity(num):
        return False
    return True
