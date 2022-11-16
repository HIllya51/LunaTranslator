from __future__ import unicode_literals

from ..conversions import *
from ..func_utils import *


class RegExpPrototype:
    def toString(this, args):
        flags = u''
        try:
            if this.glob:
                flags += u'g'
            if this.ignore_case:
                flags += u'i'
            if this.multiline:
                flags += u'm'
        except:
            pass
        try:
            v = this.value if this.value else u'(?:)'
        except:
            v = u'(?:)'
        return u'/%s/' % v + flags

    def test(this, args):
        string = get_arg(args, 0)
        return RegExpExec(this, string, args.space) is not null

    def _exec(
            this, args
    ):  # will be changed to exec in base.py. cant name it exec here...
        string = get_arg(args, 0)
        return RegExpExec(this, string, args.space)


def RegExpExec(this, string, space):
    if GetClass(this) != 'RegExp':
        raise MakeError('TypeError', 'RegExp.prototype.exec is not generic!')
    string = to_string(string)
    length = len(string)
    i = to_int(this.get('lastIndex')) if this.glob else 0
    matched = False
    while not matched:
        if i < 0 or i > length:
            this.put('lastIndex', 0.)
            return null
        matched = this.match(string, i)
        i += 1
    start, end = matched.span()  #[0]+i-1, matched.span()[1]+i-1
    if this.glob:
        this.put('lastIndex', float(end))
    arr = convert_to_js_type(
        [matched.group()] + list(matched.groups()), space=space)
    arr.put('index', float(start))
    arr.put('input', unicode(string))
    return arr
