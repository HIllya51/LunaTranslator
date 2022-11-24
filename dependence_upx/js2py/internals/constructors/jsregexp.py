from __future__ import unicode_literals
from ..conversions import *
from ..func_utils import *
from ..base import SpaceTuple

REG_EXP_FLAGS = ('g', 'i', 'm')


def RegExp(this, args):
    pattern = get_arg(args, 0)
    flags = get_arg(args, 1)
    if GetClass(pattern) == 'RegExp':
        if not is_undefined(flags):
            raise MakeError(
                'TypeError',
                'Cannot supply flags when constructing one RegExp from another'
            )
        # return unchanged
        return pattern
    #pattern is not a regexp
    if is_undefined(pattern):
        pattern = u''
    else:
        pattern = to_string(pattern)
    flags = to_string(flags) if not is_undefined(flags) else u''
    for flag in flags:
        if flag not in REG_EXP_FLAGS:
            raise MakeError(
                'SyntaxError',
                'Invalid flags supplied to RegExp constructor "%s"' % flag)
    if len(set(flags)) != len(flags):
        raise MakeError(
            'SyntaxError',
            'Invalid flags supplied to RegExp constructor "%s"' % flags)
    return args.space.NewRegExp(pattern, flags)


def RegExpCreate(args, space):
    _args = SpaceTuple(args)
    _args.space = space
    return RegExp(undefined, _args)
