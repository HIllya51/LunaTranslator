# -*- coding: utf-8 -*-
from .jsregexp import Exec
import re
DIGS = set('0123456789')
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
    def toString():
        if this.Class != 'String':
            raise this.MakeError('TypeError',
                                 'String.prototype.toString is not generic')
        return this.value

    def valueOf():
        if this.Class != 'String':
            raise this.MakeError('TypeError',
                                 'String.prototype.valueOf is not generic')
        return this.value

    def charAt(pos):
        this.cok()
        pos = pos.to_int()
        s = this.to_string()
        if 0 <= pos < len(s.value):
            char = s.value[pos]
            if char not in s.CHAR_BANK:
                s.Js(char)  # add char to char bank
            return s.CHAR_BANK[char]
        return s.CHAR_BANK['']

    def charCodeAt(pos):
        this.cok()
        pos = pos.to_int()
        s = this.to_string()
        if 0 <= pos < len(s.value):
            return s.Js(ord(s.value[pos]))
        return s.NaN

    def concat():
        this.cok()
        s = this.to_string()
        res = s.value
        for e in arguments.to_list():
            res += e.to_string().value
        return res

    def indexOf(searchString, position):
        this.cok()
        s = this.to_string().value
        search = searchString.to_string().value
        pos = position.to_int()
        return this.Js(s.find(search, min(max(pos, 0), len(s))))

    def lastIndexOf(searchString, position):
        this.cok()
        s = this.to_string().value
        search = searchString.to_string().value
        pos = position.to_number()
        pos = 10**15 if pos.is_nan() else pos.to_int()
        return s.rfind(search, 0, min(max(pos, 0) + 1, len(s)))

    def localeCompare(that):
        this.cok()
        s = this.to_string()
        that = that.to_string()
        if s < that:
            return this.Js(-1)
        elif s > that:
            return this.Js(1)
        return this.Js(0)

    def match(regexp):
        this.cok()
        s = this.to_string()
        r = this.RegExp(regexp) if regexp.Class != 'RegExp' else regexp
        if not r.glob:
            return Exec(r, s)
        r.put('lastIndex', this.Js(0))
        found = []
        previous_last_index = 0
        last_match = True
        while last_match:
            result = Exec(r, s)
            if result.is_null():
                last_match = False
            else:
                this_index = r.get('lastIndex').value
                if this_index == previous_last_index:
                    r.put('lastIndex', this.Js(this_index + 1))
                    previous_last_index += 1
                else:
                    previous_last_index = this_index
                matchStr = result.get('0')
                found.append(matchStr)
        if not found:
            return this.null
        return found

    def replace(searchValue, replaceValue):
        # VERY COMPLICATED. to check again.
        this.cok()
        string = this.to_string()
        s = string.value
        res = ''
        if not replaceValue.is_callable():
            replaceValue = replaceValue.to_string().value
            func = False
        else:
            func = True
        # Replace all  ( global )
        if searchValue.Class == 'RegExp' and searchValue.glob:
            last = 0
            for e in re.finditer(searchValue.pat, s):
                res += s[last:e.span()[0]]
                if func:
                    # prepare arguments for custom func (replaceValue)
                    args = (e.group(), ) + e.groups() + (e.span()[1], string)
                    # convert all types to JS
                    args = map(this.Js, args)
                    res += replaceValue(*args).to_string().value
                else:
                    res += replacement_template(replaceValue, s, e.span(),
                                                e.groups())
                last = e.span()[1]
            res += s[last:]
            return this.Js(res)
        elif searchValue.Class == 'RegExp':
            e = re.search(searchValue.pat, s)
            if e is None:
                return string
            span = e.span()
            pars = e.groups()
            match = e.group()
        else:
            match = searchValue.to_string().value
            ind = s.find(match)
            if ind == -1:
                return string
            span = ind, ind + len(match)
            pars = ()
        res = s[:span[0]]
        if func:
            args = (match, ) + pars + (span[1], string)
            # convert all types to JS
            this_ = this
            args = tuple([this_.Js(x) for x in args])
            res += replaceValue(*args).to_string().value
        else:
            res += replacement_template(replaceValue, s, span, pars)
        res += s[span[1]:]
        return res

    def search(regexp):
        this.cok()
        string = this.to_string()
        if regexp.Class == 'RegExp':
            rx = regexp
        else:
            rx = this.RegExp(regexp)
        res = re.search(rx.pat, string.value)
        if res is not None:
            return this.Js(res.span()[0])
        return -1

    def slice(start, end):
        this.cok()
        s = this.to_string()
        start = start.to_int()
        length = len(s.value)
        end = length if end.is_undefined() else end.to_int()
        #From = max(length+start, 0) if start<0 else min(length, start)
        #To = max(length+end, 0) if end<0 else min(length, end)
        return s.value[start:end]

    def split(separator, limit):
        # its a bit different that re.split!
        this.cok()
        S = this.to_string()
        s = S.value
        lim = 2**32 - 1 if limit.is_undefined() else limit.to_uint32()
        if not lim:
            return []
        if separator.is_undefined():
            return [s]
        len_s = len(s)
        res = []
        R = separator if separator.Class == 'RegExp' else separator.to_string()
        if not len_s:
            if SplitMatch(s, 0, R) is None:
                return [S]
            return []
        p = q = 0
        while q != len_s:
            e, cap = SplitMatch(s, q, R)
            if e is None or e == p:
                q += 1
                continue
            res.append(s[p:q])
            p = q = e
            if len(res) == lim:
                return res
            for element in cap:
                res.append(this.Js(element))
                if len(res) == lim:
                    return res
        res.append(s[p:])
        return res

    def substring(start, end):
        this.cok()
        s = this.to_string().value
        start = start.to_int()
        length = len(s)
        end = length if end.is_undefined() else end.to_int()
        fstart = min(max(start, 0), length)
        fend = min(max(end, 0), length)
        return this.Js(s[min(fstart, fend):max(fstart, fend)])

    def substr(start, length):
        #I hate this function and its description in specification
        r1 = this.to_string().value
        r2 = start.to_int()
        r3 = 10**20 if length.is_undefined() else length.to_int()
        r4 = len(r1)
        r5 = r2 if r2 >= 0 else max(0, r2 + r4)
        r6 = min(max(r3, 0), r4 - r5)
        if r6 <= 0:
            return ''
        return r1[r5:r5 + r6]

    def toLowerCase():
        this.cok()
        return this.Js(this.to_string().value.lower())

    def toLocaleLowerCase():
        this.cok()
        return this.Js(this.to_string().value.lower())

    def toUpperCase():
        this.cok()
        return this.Js(this.to_string().value.upper())

    def toLocaleUpperCase():
        this.cok()
        return this.Js(this.to_string().value.upper())

    def trim():
        this.cok()
        return this.Js(this.to_string().value.strip(WHITE))


def SplitMatch(s, q, R):
    # s is Py String to match, q is the py int match start and R is Js RegExp or String.
    if R.Class == 'RegExp':
        res = R.match(s, q)
        return (None, ()) if res is None else (res.span()[1], res.groups())
    # R is just a string
    if s[q:].startswith(R.value):
        return q + len(R.value), ()
    return None, ()
