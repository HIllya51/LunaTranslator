import binascii

from pyjsparser import PyJsParser
import six
if six.PY3:
    basestring = str
    long = int
    xrange = range
    unicode = str

REGEXP_CONVERTER = PyJsParser()


def to_hex(s):
    return binascii.hexlify(s.encode('utf8')).decode(
        'utf8')  # fucking python 3, I hate it so much


    # wtf was wrong with s.encode('hex') ???
def indent(lines, ind=4):
    return ind * ' ' + lines.replace('\n', '\n' + ind * ' ').rstrip(' ')


def inject_before_lval(source, lval, code):
    if source.count(lval) > 1:
        print()
        print(lval)
        raise RuntimeError('To many lvals (%s)' % lval)
    elif not source.count(lval):
        print()
        print(lval)
        assert lval not in source
        raise RuntimeError('No lval found "%s"' % lval)
    end = source.index(lval)
    inj = source.rfind('\n', 0, end)
    ind = inj
    while source[ind + 1] == ' ':
        ind += 1
    ind -= inj
    return source[:inj + 1] + indent(code, ind) + source[inj + 1:]


def get_continue_label(label):
    return CONTINUE_LABEL % to_hex(label)


def get_break_label(label):
    return BREAK_LABEL % to_hex(label)


def is_valid_py_name(name):
    try:
        compile(name + ' =  11', 'a', 'exec')
    except:
        return False
    return True


def indent(lines, ind=4):
    return ind * ' ' + lines.replace('\n', '\n' + ind * ' ').rstrip(' ')


def compose_regex(val):
    reg, flags = val
    #reg = REGEXP_CONVERTER._unescape_string(reg)
    return u'/%s/%s' % (reg, flags)


def float_repr(f):
    if int(f) == f:
        return repr(int(f))
    return repr(f)


def argsplit(args, sep=','):
    """used to split JS args (it is not that simple as it seems because
       sep can be inside brackets).

       pass args *without* brackets!

       Used also to parse array and object elements, and more"""
    parsed_len = 0
    last = 0
    splits = []
    for e in bracket_split(args, brackets=['()', '[]', '{}']):
        if e[0] not in ('(', '[', '{'):
            for i, char in enumerate(e):
                if char == sep:
                    splits.append(args[last:parsed_len + i])
                    last = parsed_len + i + 1
        parsed_len += len(e)
    splits.append(args[last:])
    return splits


def bracket_split(source, brackets=('()', '{}', '[]'), strip=False):
    """DOES NOT RETURN EMPTY STRINGS (can only return empty bracket content if strip=True)"""
    starts = [e[0] for e in brackets]
    in_bracket = 0
    n = 0
    last = 0
    while n < len(source):
        e = source[n]
        if not in_bracket and e in starts:
            in_bracket = 1
            start = n
            b_start, b_end = brackets[starts.index(e)]
        elif in_bracket:
            if e == b_start:
                in_bracket += 1
            elif e == b_end:
                in_bracket -= 1
                if not in_bracket:
                    if source[last:start]:
                        yield source[last:start]
                    last = n + 1
                    yield source[start + strip:n + 1 - strip]
        n += 1
    if source[last:]:
        yield source[last:]


def js_comma(a, b):
    return 'PyJsComma(' + a + ',' + b + ')'


def js_or(a, b):
    return '(' + a + ' or ' + b + ')'


def js_bor(a, b):
    return '(' + a + '|' + b + ')'


def js_bxor(a, b):
    return '(' + a + '^' + b + ')'


def js_band(a, b):
    return '(' + a + '&' + b + ')'


def js_and(a, b):
    return '(' + a + ' and ' + b + ')'


def js_strict_eq(a, b):
    return 'PyJsStrictEq(' + a + ',' + b + ')'


def js_strict_neq(a, b):
    return 'PyJsStrictNeq(' + a + ',' + b + ')'


#Not handled by python in the same way like JS. For example 2==2==True returns false.
# In JS above would return true so we need brackets.
def js_abstract_eq(a, b):
    return '(' + a + '==' + b + ')'


#just like ==
def js_abstract_neq(a, b):
    return '(' + a + '!=' + b + ')'


def js_lt(a, b):
    return '(' + a + '<' + b + ')'


def js_le(a, b):
    return '(' + a + '<=' + b + ')'


def js_ge(a, b):
    return '(' + a + '>=' + b + ')'


def js_gt(a, b):
    return '(' + a + '>' + b + ')'


def js_in(a, b):
    return b + '.contains(' + a + ')'


def js_instanceof(a, b):
    return a + '.instanceof(' + b + ')'


def js_lshift(a, b):
    return '(' + a + '<<' + b + ')'


def js_rshift(a, b):
    return '(' + a + '>>' + b + ')'


def js_shit(a, b):
    return 'PyJsBshift(' + a + ',' + b + ')'


def js_add(
        a,
        b):  # To simplify later process of converting unary operators + and ++
    return '(%s+%s)' % (a, b)


def js_sub(a, b):  # To simplify
    return '(%s-%s)' % (a, b)


def js_mul(a, b):
    return '(' + a + '*' + b + ')'


def js_div(a, b):
    return '(' + a + '/' + b + ')'


def js_mod(a, b):
    return '(' + a + '%' + b + ')'


def js_typeof(a):
    cand = list(bracket_split(a, ('()', )))
    if len(cand) == 2 and cand[0] == 'var.get':
        return cand[0] + cand[1][:-1] + ',throw=False).typeof()'
    return a + '.typeof()'


def js_void(a):
    # eval and return undefined
    return 'PyJsComma(%s, Js(None))' % a


def js_new(a):
    cands = list(bracket_split(a, ('()', )))
    lim = len(cands)
    if lim < 2:
        return a + '.create()'
    n = 0
    while n < lim:
        c = cands[n]
        if c[0] == '(':
            if cands[n - 1].endswith(
                    '.get') and n + 1 >= lim:  # last get operation.
                return a + '.create()'
            elif cands[n - 1][0] == '(':
                return ''.join(cands[:n]) + '.create' + c + ''.join(
                    cands[n + 1:])
            elif cands[n - 1] == '.callprop':
                beg = ''.join(cands[:n - 1])
                args = argsplit(c[1:-1], ',')
                prop = args[0]
                new_args = ','.join(args[1:])
                create = '.get(%s).create(%s)' % (prop, new_args)
                return beg + create + ''.join(cands[n + 1:])
        n += 1
    return a + '.create()'


def js_delete(a):
    #replace last get with delete.
    c = list(bracket_split(a, ['()']))
    beg, arglist = ''.join(c[:-1]).strip(), c[-1].strip(
    )  #strips just to make sure... I will remove it later
    if beg[-4:] != '.get':
        print(a)
        raise SyntaxError('Invalid delete operation')
    return beg[:-3] + 'delete' + arglist


def js_neg(a):
    return '(-' + a + ')'


def js_pos(a):
    return '(+' + a + ')'


def js_inv(a):
    return '(~' + a + ')'


def js_not(a):
    return a + '.neg()'


def js_postfix(a, inc, post):
    bra = list(bracket_split(a, ('()', )))
    meth = bra[-2]
    if not meth.endswith('get'):
        raise SyntaxError('Invalid ++ or -- operation.')
    bra[-2] = bra[-2][:-3] + 'put'
    bra[-1] = '(%s,Js(%s.to_number())%sJs(1))' % (bra[-1][1:-1], a,
                                                  '+' if inc else '-')
    res = ''.join(bra)
    return res if not post else '(%s%sJs(1))' % (res, '-' if inc else '+')


def js_pre_inc(a):
    return js_postfix(a, True, False)


def js_post_inc(a):
    return js_postfix(a, True, True)


def js_pre_dec(a):
    return js_postfix(a, False, False)


def js_post_dec(a):
    return js_postfix(a, False, True)


CONTINUE_LABEL = 'JS_CONTINUE_LABEL_%s'
BREAK_LABEL = 'JS_BREAK_LABEL_%s'
PREPARE = '''HOLDER = var.own.get(NAME)\nvar.force_own_put(NAME, PyExceptionToJs(PyJsTempException))\n'''
RESTORE = '''if HOLDER is not None:\n    var.own[NAME] = HOLDER\nelse:\n    del var.own[NAME]\ndel HOLDER\n'''
TRY_CATCH = '''%stry:\nBLOCKfinally:\n%s''' % (PREPARE, indent(RESTORE))

OR = {'||': js_or}
AND = {'&&': js_and}
BOR = {'|': js_bor}
BXOR = {'^': js_bxor}
BAND = {'&': js_band}

EQS = {
    '===': js_strict_eq,
    '!==': js_strict_neq,
    '==': js_abstract_eq,  # we need == and != too. Read a note above method
    '!=': js_abstract_neq
}

#Since JS does not have chained comparisons we need to implement all cmp methods.
COMPS = {
    '<': js_lt,
    '<=': js_le,
    '>=': js_ge,
    '>': js_gt,
    'instanceof': js_instanceof,  #todo change to validitate
    'in': js_in
}

BSHIFTS = {'<<': js_lshift, '>>': js_rshift, '>>>': js_shit}

ADDS = {'+': js_add, '-': js_sub}

MULTS = {'*': js_mul, '/': js_div, '%': js_mod}
BINARY = {}
BINARY.update(ADDS)
BINARY.update(MULTS)
BINARY.update(BSHIFTS)
BINARY.update(COMPS)
BINARY.update(EQS)
BINARY.update(BAND)
BINARY.update(BXOR)
BINARY.update(BOR)
BINARY.update(AND)
BINARY.update(OR)
#Note they dont contain ++ and -- methods because they both have 2 different methods
# correct method will be found automatically in translate function
UNARY = {
    'typeof': js_typeof,
    'void': js_void,
    'new': js_new,
    'delete': js_delete,
    '!': js_not,
    '-': js_neg,
    '+': js_pos,
    '~': js_inv,
    '++': None,
    '--': None
}
