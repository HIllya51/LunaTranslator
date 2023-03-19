from __future__ import unicode_literals

# -*- coding: utf-8 -*-
import re
from ..conversions import *
from ..func_utils import *
from .jsregexp import RegExpExec

DIGS = set(u'0123456789')
WHITE = u"\u0009\u000A\u000B\u000C\u000D\u0020\u00A0\u1680\u180E\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u2028\u2029\u202F\u205F\u3000\uFEFF"


def replacement_template(rep, source, span, npar):
    """Takes the replacement template and some info about the match and returns filled template
       """
    n = 0
    res = ''
    while n < len(rep) - 1:
        char = rep[n]
        if char == '$':
            if rep[n + 1] == '$':
                res += '$'
                n += 2
                continue
            elif rep[n + 1] == '`':
                # replace with string that is BEFORE match
                res += source[:span[0]]
                n += 2
                continue
            elif rep[n + 1] == '\'':
                # replace with string that is AFTER match
                res += source[span[1]:]
                n += 2
                continue
            elif rep[n + 1] in DIGS:
                dig = rep[n + 1]
                if n + 2 < len(rep) and rep[n + 2] in DIGS:
                    dig += rep[n + 2]
                num = int(dig)
                # we will not do any replacements if we dont have this npar or dig is 0
                if not num or num > len(npar):
                    res += '$' + dig
                else:
                    # None - undefined has to be replaced with ''
                    res += npar[num - 1] if npar[num - 1] else ''
                n += 1 + len(dig)
                continue
        res += char
        n += 1
    if n < len(rep):
        res += rep[-1]
    return res


###################################################


class StringPrototype:
    def toString(this, args):
        if GetClass(this) != 'String':
            raise MakeError('TypeError',
                            'String.prototype.toString is not generic')
        if type(this) == unicode:
            return this
        assert type(this.value) == unicode
        return this.value

    def valueOf(this, args):
        if GetClass(this) != 'String':
            raise MakeError('TypeError',
                            'String.prototype.valueOf is not generic')
        if type(this) == unicode:
            return this
        assert type(this.value) == unicode
        return this.value

    def charAt(this, args):
        cok(this)
        pos = to_int(get_arg(args, 0))
        s = to_string(this)
        if 0 <= pos < len(s):
            return s[pos]
        return u''

    def charCodeAt(this, args):
        cok(this)
        pos = to_int(get_arg(args, 0))
        s = to_string(this)
        if 0 <= pos < len(s):
            return float(ord(s[pos]))
        return NaN

    def concat(this, args):
        cok(this)
        return to_string(this) + u''.join(map(to_string, args))

    def indexOf(this, args):
        cok(this)
        search = to_string(get_arg(args, 0))
        pos = to_int(get_arg(args, 1))
        s = to_string(this)
        return float(s.find(search, min(max(pos, 0), len(s))))

    def lastIndexOf(this, args):
        cok(this)
        search = to_string(get_arg(args, 0))
        pos = get_arg(args, 1)
        s = to_string(this)
        pos = 10**12 if is_nan(pos) else to_int(pos)
        return float(s.rfind(search, 0, min(max(pos, 0) + 1, len(s))))

    def localeCompare(this, args):
        cok(this)
        s = to_string(this)
        that = to_string(get_arg(args, 0))
        if s < that:
            return -1.
        elif s > that:
            return 1.
        return 0.

    def match(this, args):
        cok(this)
        s = to_string(this)
        regexp = get_arg(args, 0)
        r = args.space.NewRegExp(
            regexp, '') if GetClass(regexp) != 'RegExp' else regexp
        if not r.glob:
            return RegExpExec(r, s, space=args.space)
        r.put('lastIndex', float(0))
        found = []
        previous_last_index = 0
        last_match = True
        while last_match:
            result = RegExpExec(r, s, space=args.space)
            if is_null(result):
                last_match = False
            else:
                this_index = r.get('lastIndex')
                if this_index == previous_last_index:
                    r.put('lastIndex', float(this_index + 1))
                    previous_last_index += 1
                else:
                    previous_last_index = this_index
                matchStr = result.get('0')
                found.append(matchStr)
        if not found:
            return null
        return args.space.ConstructArray(found)

    def replace(this, args):
        # VERY COMPLICATED. to check again.
        cok(this)
        s = to_string(this)
        searchValue = get_arg(args, 0)
        replaceValue = get_arg(args, 1)
        res = ''
        if not is_callable(replaceValue):
            replaceValue = to_string(replaceValue)
            func = False
        else:
            func = True
        # Replace all  ( global )
        if GetClass(searchValue) == 'RegExp' and searchValue.glob:
            last = 0
            for e in re.finditer(searchValue.pat, s):
                res += s[last:e.span()[0]]
                if func:
                    # prepare arguments for custom func (replaceValue)
                    call_args = (e.group(), ) + e.groups() + (e.span()[1], s)
                    # convert all types to JS before Js bytecode call...
                    res += to_string(
                        replaceValue.call(
                            this, ensure_js_types(call_args,
                                                  space=args.space)))
                else:
                    res += replacement_template(replaceValue, s, e.span(),
                                                e.groups())
                last = e.span()[1]
            res += s[last:]
            return res
        elif GetClass(searchValue) == 'RegExp':
            e = re.search(searchValue.pat, s)
            if e is None:
                return s
            span = e.span()
            pars = e.groups()
            match = e.group()
        else:
            match = to_string(searchValue)
            ind = s.find(match)
            if ind == -1:
                return s
            span = ind, ind + len(match)
            pars = ()
        res = s[:span[0]]
        if func:
            call_args = (match, ) + pars + (span[1], s)
            # convert all types to JS before Js bytecode call...
            res += to_string(
                replaceValue.call(this,
                                  ensure_js_types(call_args,
                                                  space=args.space)))
        else:
            res += replacement_template(replaceValue, s, span, pars)
        res += s[span[1]:]
        return res

    def search(this, args):
        cok(this)
        string = to_string(this)
        regexp = get_arg(args, 0)
        if GetClass(regexp) == 'RegExp':
            rx = regexp
        else:
            rx = args.space.NewRegExp(regexp, '')
        res = re.search(rx.pat, string)
        if res is not None:
            return float(res.span()[0])
        return -1.

    def slice(this, args):
        cok(this)
        s = to_string(this)
        start = to_int(get_arg(args, 0))
        length = len(s)
        end = get_arg(args, 1)
        end = length if is_undefined(end) else to_int(end)
        #From = max(length+start, 0) if start<0 else min(length, start)
        #To = max(length+end, 0) if end<0 else min(length, end)
        return s[start:end]

    def split(this, args):
        # its a bit different from re.split!
        cok(this)
        s = to_string(this)
        separator = get_arg(args, 0)
        limit = get_arg(args, 1)
        lim = 2**32 - 1 if is_undefined(limit) else to_uint32(limit)
        if not lim:
            return args.space.ConstructArray([])
        if is_undefined(separator):
            return args.space.ConstructArray([s])
        len_s = len(s)
        res = []
        R = separator if GetClass(separator) == 'RegExp' else to_string(
            separator)
        if not len_s:
            if SplitMatch(s, 0, R) is None:
                return args.space.ConstructArray([s])
            return args.space.ConstructArray([])
        p = q = 0
        while q != len_s:
            e, cap = SplitMatch(s, q, R)
            if e is None or e == p:
                q += 1
                continue
            res.append(s[p:q])
            p = q = e
            if len(res) == lim:
                return args.space.ConstructArray(res)
            for element in cap:
                res.append(element)
                if len(res) == lim:
                    return args.space.ConstructArray(res)
        res.append(s[p:])
        return args.space.ConstructArray(res)

    def substring(this, args):
        cok(this)
        s = to_string(this)
        start = to_int(get_arg(args, 0))
        length = len(s)
        end = get_arg(args, 1)
        end = length if is_undefined(end) else to_int(end)
        fstart = min(max(start, 0), length)
        fend = min(max(end, 0), length)
        return s[min(fstart, fend):max(fstart, fend)]

    def substr(this, args):
        cok(this)
        #I hate this function and its description in specification
        r1 = to_string(this)
        r2 = to_int(get_arg(args, 0))
        length = get_arg(args, 1)
        r3 = 10**20 if is_undefined(length) else to_int(length)
        r4 = len(r1)
        r5 = r2 if r2 >= 0 else max(0, r2 + r4)
        r6 = min(max(r3, 0), r4 - r5)
        if r6 <= 0:
            return ''
        return r1[r5:r5 + r6]

    def toLowerCase(this, args):
        cok(this)
        return to_string(this).lower()

    def toLocaleLowerCase(this, args):
        cok(this)
        return to_string(this).lower()

    def toUpperCase(this, args):
        cok(this)
        return to_string(this).upper()

    def toLocaleUpperCase(this, args):
        cok(this)
        return to_string(this).upper()

    def trim(this, args):
        cok(this)
        return to_string(this).strip(WHITE)


def SplitMatch(s, q, R):
    # s is Py String to match, q is the py int match start and R is Js RegExp or String.
    if GetClass(R) == 'RegExp':
        res = R.match(s, q)
        return (None, ()) if res is None else (res.span()[1], res.groups())
    # R is just a string
    if s[q:].startswith(R):
        return q + len(R), ()
    return None, ()
