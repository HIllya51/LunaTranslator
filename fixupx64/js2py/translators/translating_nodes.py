from __future__ import unicode_literals
from pyjsparser.pyjsparserdata import *
from .friendly_nodes import *
import random
import six

if six.PY3:
    from functools import reduce
    xrange = range
    unicode = str
# number of characters above which expression will be split to multiple lines in order to avoid python parser stack overflow
# still experimental so I suggest to set it to 400 in order to avoid common errors
# set it to smaller value only if you have problems with parser stack overflow
LINE_LEN_LIMIT = 400  #  200  # or any other value - the larger the smaller probability of errors :)


class ForController:
    def __init__(self):
        self.inside = [False]
        self.update = ''

    def enter_for(self, update):
        self.inside.append(True)
        self.update = update

    def leave_for(self):
        self.inside.pop()

    def enter_other(self):
        self.inside.append(False)

    def leave_other(self):
        self.inside.pop()

    def is_inside(self):
        return self.inside[-1]


class InlineStack:
    NAME = 'PyJs_%s_%d_'

    def __init__(self):
        self.reps = {}
        self.names = []

    def inject_inlines(self, source):
        for lval in self.names:  # first in first out! Its important by the way
            source = inject_before_lval(source, lval, self.reps[lval])
        return source

    def require(self, typ):
        name = self.NAME % (typ, len(self.names))
        self.names.append(name)
        return name

    def define(self, name, val):
        self.reps[name] = val

    def reset(self):
        self.rel = {}
        self.names = []


class ContextStack:
    def __init__(self):
        self.to_register = set([])
        self.to_define = {}

    def reset(self):
        self.to_register = set([])
        self.to_define = {}

    def register(self, var):
        self.to_register.add(var)

    def define(self, name, code):
        self.to_define[name] = code
        self.register(name)

    def get_code(self):
        code = 'var.registers([%s])\n' % ', '.join(
            repr(e) for e in self.to_register)
        for name, func_code in six.iteritems(self.to_define):
            code += func_code
        return code


def clean_stacks():
    global Context, inline_stack
    Context = ContextStack()
    inline_stack = InlineStack()


def to_key(literal_or_identifier):
    ''' returns string representation of this object'''
    if literal_or_identifier['type'] == 'Identifier':
        return literal_or_identifier['name']
    elif literal_or_identifier['type'] == 'Literal':
        k = literal_or_identifier['value']
        if isinstance(k, float):
            return unicode(float_repr(k))
        elif 'regex' in literal_or_identifier:
            return compose_regex(k)
        elif isinstance(k, bool):
            return 'true' if k else 'false'
        elif k is None:
            return 'null'
        else:
            return unicode(k)

def is_iteration_statement(cand):
    if not isinstance(cand, dict):
        # Multiple statements.
        return False
    return cand.get("type", "?") in {"ForStatement", "ForInStatement", "WhileStatement", "DoWhileStatement"}



def trans(ele, standard=False):
    """Translates esprima syntax tree to python by delegating to appropriate translating node"""
    try:
        node = globals().get(ele['type'])
        if not node:
            raise NotImplementedError('%s is not supported!' % ele['type'])
        if standard:
            node = node.__dict__[
                'standard'] if 'standard' in node.__dict__ else node
        return node(**ele)
    except:
        #print ele
        raise


def limited(func):
    '''Decorator limiting resulting line length in order to avoid python parser stack overflow -
      If expression longer than LINE_LEN_LIMIT characters then it will be moved to upper line
     USE ONLY ON EXPRESSIONS!!! '''

    def f(standard=False, **args):
        insert_pos = len(
            inline_stack.names
        )  # in case line is longer than limit we will have to insert the lval at current position
        # this is because calling func will change inline_stack.
        # we cant use inline_stack.require here because we dont know whether line overflows yet
        res = func(**args)
        if len(res) > LINE_LEN_LIMIT:
            name = inline_stack.require('LONG')
            inline_stack.names.pop()
            inline_stack.names.insert(insert_pos, name)
            res = 'def %s(var=var):\n    return %s\n' % (name, res)
            inline_stack.define(name, res)
            return name + '()'
        else:
            return res

    f.__dict__['standard'] = func
    return f


# ==== IDENTIFIERS AND LITERALS  =======

inf = float('inf')


def Literal(type, value, raw, regex=None):
    if regex:  # regex
        return 'JsRegExp(%s)' % repr(compose_regex(value))
    elif value is None:  # null
        return 'var.get(u"null")'
    # Todo template
    # String, Bool, Float
    return 'Js(%s)' % repr(value) if value != inf else 'Js(float("inf"))'


def Identifier(type, name):
    return 'var.get(%s)' % repr(name)


@limited
def MemberExpression(type, computed, object, property):
    far_left = trans(object)
    if computed:  # obj[prop] type accessor
        # may be literal which is the same in every case so we can save some time on conversion
        if property['type'] == 'Literal':
            prop = repr(to_key(property))
        else:  # worst case
            prop = trans(property)
    else:  # always the same since not computed (obj.prop accessor)
        prop = repr(to_key(property))
    return far_left + '.get(%s)' % prop


def ThisExpression(type):
    return 'var.get(u"this")'


@limited
def CallExpression(type, callee, arguments):
    arguments = [trans(e) for e in arguments]
    if callee['type'] == 'MemberExpression':
        far_left = trans(callee['object'])
        if callee['computed']:  # obj[prop] type accessor
            # may be literal which is the same in every case so we can save some time on conversion
            if callee['property']['type'] == 'Literal':
                prop = repr(to_key(callee['property']))
            else:  # worst case
                prop = trans(
                    callee['property'])  # its not a string literal! so no repr
        else:  # always the same since not computed (obj.prop accessor)
            prop = repr(to_key(callee['property']))
        arguments.insert(0, prop)
        return far_left + '.callprop(%s)' % ', '.join(arguments)
    else:  # standard call
        return trans(callee) + '(%s)' % ', '.join(arguments)


# ========== ARRAYS ============


def ArrayExpression(type, elements):  # todo fix null inside problem
    return 'Js([%s])' % ', '.join(trans(e) if e else 'None' for e in elements)


# ========== OBJECTS =============


def ObjectExpression(type, properties):
    name = None
    elems = []
    after = ''
    for p in properties:
        if p['kind'] == 'init':
            elems.append('%s:%s' % Property(**p))
        else:
            if name is None:
                name = inline_stack.require('Object')
            if p['kind'] == 'set':
                k, setter = Property(
                    **p
                )  # setter is just a lval referring to that function, it will be defined in InlineStack automatically
                after += '%s.define_own_property(%s, {"set":%s, "configurable":True, "enumerable":True})\n' % (
                    name, k, setter)
            elif p['kind'] == 'get':
                k, getter = Property(**p)
                after += '%s.define_own_property(%s, {"get":%s, "configurable":True, "enumerable":True})\n' % (
                    name, k, getter)
            else:
                raise RuntimeError('Unexpected object propery kind')
    definition = 'Js({%s})' % ','.join(elems)
    if name is None:
        return definition
    body = '%s = %s\n' % (name, definition)
    body += after
    body += 'return %s\n' % name
    code = 'def %s():\n%s' % (name, indent(body))
    inline_stack.define(name, code)
    return name + '()'


def Property(type, kind, key, computed, value, method, shorthand):
    if shorthand or computed:
        raise NotImplementedError(
            'Shorthand and Computed properties not implemented!')
    k = to_key(key)
    if k is None:
        raise SyntaxError('Invalid key in dictionary! Or bug in Js2Py')
    v = trans(value)
    return repr(k), v


# ========== EXPRESSIONS ============


@limited
def UnaryExpression(type, operator, argument, prefix):
    a = trans(
        argument, standard=True
    )  # unary involve some complex operations so we cant use line shorteners here
    if operator == 'delete':
        if argument['type'] in ('Identifier', 'MemberExpression'):
            # means that operation is valid
            return js_delete(a)
        return 'PyJsComma(%s, Js(True))' % a  # otherwise not valid, just perform expression and return true.
    elif operator == 'typeof':
        return js_typeof(a)
    return UNARY[operator](a)


@limited
def BinaryExpression(type, operator, left, right):
    a = trans(left)
    b = trans(right)
    # delegate to our friends
    return BINARY[operator](a, b)


@limited
def UpdateExpression(type, operator, argument, prefix):
    a = trans(
        argument, standard=True
    )  # also complex operation involving parsing of the result so no line length reducing here
    return js_postfix(a, operator == '++', not prefix)


@limited
def AssignmentExpression(type, operator, left, right):
    operator = operator[:-1]
    if left['type'] == 'Identifier':
        if operator:
            return 'var.put(%s, %s, %s)' % (repr(to_key(left)), trans(right),
                                            repr(operator))
        else:
            return 'var.put(%s, %s)' % (repr(to_key(left)), trans(right))
    elif left['type'] == 'MemberExpression':
        far_left = trans(left['object'])
        if left['computed']:  # obj[prop] type accessor
            # may be literal which is the same in every case so we can save some time on conversion
            if left['property']['type'] == 'Literal':
                prop = repr(to_key(left['property']))
            else:  # worst case
                prop = trans(
                    left['property'])  # its not a string literal! so no repr
        else:  # always the same since not computed (obj.prop accessor)
            prop = repr(to_key(left['property']))
        if operator:
            return far_left + '.put(%s, %s, %s)' % (prop, trans(right),
                                                    repr(operator))
        else:
            return far_left + '.put(%s, %s)' % (prop, trans(right))
    else:
        raise SyntaxError('Invalid left hand side in assignment!')


six


@limited
def SequenceExpression(type, expressions):
    return reduce(js_comma, (trans(e) for e in expressions))


@limited
def NewExpression(type, callee, arguments):
    return trans(callee) + '.create(%s)' % ', '.join(
        trans(e) for e in arguments)


@limited
def ConditionalExpression(
        type, test, consequent,
        alternate):  # caused plenty of problems in my home-made translator :)
    return '(%s if %s else %s)' % (trans(consequent), trans(test),
                                   trans(alternate))


# ===========  STATEMENTS =============


def BlockStatement(type, body):
    return StatementList(
        body)  # never returns empty string! In the worst case returns pass\n


def ExpressionStatement(type, expression):
    return trans(expression) + '\n'  # end expression space with new line


def BreakStatement(type, label):
    if label:
        return 'raise %s("Breaked")\n' % (get_break_label(label['name']))
    else:
        return 'break\n'


def ContinueStatement(type, label):
    if label:
        return 'raise %s("Continued")\n' % (get_continue_label(label['name']))
    else:
        return 'continue\n'


def ReturnStatement(type, argument):
    return 'return %s\n' % (trans(argument)
                            if argument else "var.get('undefined')")


def EmptyStatement(type):
    return 'pass\n'


def DebuggerStatement(type):
    return 'pass\n'


def DoWhileStatement(type, body, test):
    inside = trans(body) + 'if not %s:\n' % trans(test) + indent('break\n')
    result = 'while 1:\n' + indent(inside)
    return result


def ForStatement(type, init, test, update, body):
    update = indent(trans(update)) if update else ''
    init = trans(init) if init else ''
    if not init.endswith('\n'):
        init += '\n'
    test = trans(test) if test else '1'
    if not update:
        result = '#for JS loop\n%swhile %s:\n%s%s\n' % (
            init, test, indent(trans(body)), update)
    else:
        result = '#for JS loop\n%swhile %s:\n' % (init, test)
        body = 'try:\n%sfinally:\n    %s\n' % (indent(trans(body)), update)
        result += indent(body)
    return result


def ForInStatement(type, left, right, body, each):
    res = 'for PyJsTemp in %s:\n' % trans(right)
    if left['type'] == "VariableDeclaration":
        addon = trans(left)  # make sure variable is registered
        if addon != 'pass\n':
            res = addon + res  # we have to execute this expression :(
        # now extract the name
        try:
            name = left['declarations'][0]['id']['name']
        except:
            raise RuntimeError('Unusual ForIn loop')
    elif left['type'] == 'Identifier':
        name = left['name']
    else:
        raise RuntimeError('Unusual ForIn loop')
    res += indent('var.put(%s, PyJsTemp)\n' % repr(name) + trans(body))
    return res


def IfStatement(type, test, consequent, alternate):
    # NOTE we cannot do elif because function definition inside elif statement would not be possible!
    IF = 'if %s:\n' % trans(test)
    IF += indent(trans(consequent))
    if not alternate:
        return IF
    ELSE = 'else:\n' + indent(trans(alternate))
    return IF + ELSE


def LabeledStatement(type, label, body):
    # todo consider using smarter approach!
    inside = trans(body)
    defs = ''
    if is_iteration_statement(body) and (inside.startswith('while ') or inside.startswith(
            'for ') or inside.startswith('#for')):
        # we have to add contine label as well...
        # 3 or 1 since #for loop type has more lines before real for.
        sep = 1 if not inside.startswith('#for') else 3
        cont_label = get_continue_label(label['name'])
        temp = inside.split('\n')
        injected = 'try:\n' + '\n'.join(temp[sep:])
        injected += 'except %s:\n    pass\n' % cont_label
        inside = '\n'.join(temp[:sep]) + '\n' + indent(injected)
        defs += 'class %s(Exception): pass\n' % cont_label
    break_label = get_break_label(label['name'])
    inside = 'try:\n%sexcept %s:\n    pass\n' % (indent(inside), break_label)
    defs += 'class %s(Exception): pass\n' % break_label
    return defs + inside


def StatementList(lis):
    if lis:  # ensure we don't return empty string because it may ruin indentation!
        code = ''.join(trans(e) for e in lis)
        return code if code else 'pass\n'
    else:
        return 'pass\n'


def PyimportStatement(type, imp):
    lib = imp['name']
    jlib = 'PyImport_%s' % lib
    code = 'import %s as %s\n' % (lib, jlib)
    #check whether valid lib name...
    try:
        compile(code, '', 'exec')
    except:
        raise SyntaxError(
            'Invalid Python module name (%s) in pyimport statement' % lib)
    # var.pyimport will handle module conversion to PyJs object
    code += 'var.pyimport(%s, %s)\n' % (repr(lib), jlib)
    return code


def SwitchStatement(type, discriminant, cases):
    #TODO there will be a problem with continue in a switch statement.... FIX IT
    code = 'while 1:\n' + indent('SWITCHED = False\nCONDITION = (%s)\n')
    code = code % trans(discriminant)
    for case in cases:
        case_code = None
        if case['test']:  # case (x):
            case_code = 'if SWITCHED or PyJsStrictEq(CONDITION, %s):\n' % (
                trans(case['test']))
        else:  # default:
            case_code = 'if True:\n'
        case_code += indent('SWITCHED = True\n')
        case_code += indent(StatementList(case['consequent']))
        # one more indent for whole
        code += indent(case_code)
    # prevent infinite loop and sort out nested switch...
    code += indent('SWITCHED = True\nbreak\n')
    return code


def ThrowStatement(type, argument):
    return 'PyJsTempException = JsToPyException(%s)\nraise PyJsTempException\n' % trans(
        argument)


def TryStatement(type, block, handler, handlers, guardedHandlers, finalizer):
    result = 'try:\n%s' % indent(trans(block))
    # complicated catch statement...
    if handler:
        identifier = handler['param']['name']
        holder = 'PyJsHolder_%s_%d' % (to_hex(identifier),
                                       random.randrange(1e8))
        identifier = repr(identifier)
        result += 'except PyJsException as PyJsTempException:\n'
        # fill in except ( catch ) block and remember to recover holder variable to its previous state
        result += indent(
            TRY_CATCH.replace('HOLDER',
                              holder).replace('NAME', identifier).replace(
                                  'BLOCK', indent(trans(handler['body']))))
    # translate finally statement if present
    if finalizer:
        result += 'finally:\n%s' % indent(trans(finalizer))
    return result


def LexicalDeclaration(type, declarations, kind):
    raise NotImplementedError(
        'let and const not implemented yet but they will be soon! Check github for updates.'
    )


def VariableDeclarator(type, id, init):
    name = id['name']
    # register the name if not already registered
    Context.register(name)
    if init:
        return 'var.put(%s, %s)\n' % (repr(name), trans(init))
    return ''


def VariableDeclaration(type, declarations, kind):
    code = ''.join(trans(d) for d in declarations)
    return code if code else 'pass\n'


def WhileStatement(type, test, body):
    result = 'while %s:\n' % trans(test) + indent(trans(body))
    return result


def WithStatement(type, object, body):
    raise NotImplementedError('With statement not implemented!')


def Program(type, body):
    inline_stack.reset()
    code = ''.join(trans(e) for e in body)
    # here add hoisted elements (register variables and define functions)
    code = Context.get_code() + code
    # replace all inline variables
    code = inline_stack.inject_inlines(code)
    return code


# ======== FUNCTIONS ============


def FunctionDeclaration(type, id, params, defaults, body, generator,
                        expression):
    if generator:
        raise NotImplementedError('Generators not supported')
    if defaults:
        raise NotImplementedError('Defaults not supported')
    if not id:
        return FunctionExpression(type, id, params, defaults, body, generator,
                                  expression) + '\n'
    JsName = id['name']
    PyName = 'PyJsHoisted_%s_' % JsName
    PyName = PyName if is_valid_py_name(PyName) else 'PyJsHoistedNonPyName'
    # this is quite complicated
    global Context
    previous_context = Context
    # change context to the context of this function
    Context = ContextStack()
    # translate body within current context
    code = trans(body)
    # get arg names
    vars = [v['name'] for v in params]
    # args are automaticaly registered variables
    Context.to_register.update(vars)
    # add all hoisted elements inside function
    code = Context.get_code() + code
    # check whether args are valid python names:
    used_vars = []
    for v in vars:
        if is_valid_py_name(v):
            used_vars.append(v)
        else:  # invalid arg in python, for example $, replace with alternatice arg
            used_vars.append('PyJsArg_%s_' % to_hex(v))
    header = '@Js\n'
    header += 'def %s(%sthis, arguments, var=var):\n' % (
        PyName, ', '.join(used_vars) + (', ' if vars else ''))
    # transfer names from Py scope to Js scope
    arg_map = dict(zip(vars, used_vars))
    arg_map.update({'this': 'this', 'arguments': 'arguments'})
    arg_conv = 'var = Scope({%s}, var)\n' % ', '.join(
        repr(k) + ':' + v for k, v in six.iteritems(arg_map))
    # and finally set the name of the function to its real name:
    footer = '%s.func_name = %s\n' % (PyName, repr(JsName))
    footer += 'var.put(%s, %s)\n' % (repr(JsName), PyName)
    whole_code = header + indent(arg_conv + code) + footer
    # restore context
    Context = previous_context
    # define in upper context
    Context.define(JsName, whole_code)
    return 'pass\n'


def FunctionExpression(type, id, params, defaults, body, generator,
                       expression):
    if generator:
        raise NotImplementedError('Generators not supported')
    if defaults:
        raise NotImplementedError('Defaults not supported')
    JsName = id['name'] if id else 'anonymous'
    if not is_valid_py_name(JsName):
        ScriptName = 'InlineNonPyName'
    else:
        ScriptName = JsName
    PyName = inline_stack.require(ScriptName)  # this is unique

    # again quite complicated
    global Context
    previous_context = Context
    # change context to the context of this function
    Context = ContextStack()
    # translate body within current context
    code = trans(body)
    # get arg names
    vars = [v['name'] for v in params]
    # args are automaticaly registered variables
    Context.to_register.update(vars)
    # add all hoisted elements inside function
    code = Context.get_code() + code
    # check whether args are valid python names:
    used_vars = []
    for v in vars:
        if is_valid_py_name(v):
            used_vars.append(v)
        else:  # invalid arg in python, for example $, replace with alternatice arg
            used_vars.append('PyJsArg_%s_' % to_hex(v))
    header = '@Js\n'
    header += 'def %s(%sthis, arguments, var=var):\n' % (
        PyName, ', '.join(used_vars) + (', ' if vars else ''))
    # transfer names from Py scope to Js scope
    arg_map = dict(zip(vars, used_vars))
    arg_map.update({'this': 'this', 'arguments': 'arguments'})
    if id:  # make self available from inside...
        if id['name'] not in arg_map:
            arg_map[id['name']] = PyName
    arg_conv = 'var = Scope({%s}, var)\n' % ', '.join(
        repr(k) + ':' + v for k, v in six.iteritems(arg_map))
    # and finally set the name of the function to its real name:
    footer = '%s._set_name(%s)\n' % (PyName, repr(JsName))
    whole_code = header + indent(arg_conv + code) + footer
    # restore context
    Context = previous_context
    # define in upper context
    inline_stack.define(PyName, whole_code)
    return PyName


LogicalExpression = BinaryExpression
PostfixExpression = UpdateExpression

clean_stacks()

if __name__ == '__main__':
    import codecs
    import time
    import pyjsparser

    c = None  #'''`ijfdij`'''
    if not c:
        with codecs.open("esp.js", "r", "utf-8") as f:
            c = f.read()

    print('Started')
    t = time.time()
    res = trans(pyjsparser.PyJsParser().parse(c))
    dt = time.time() - t + 0.000000001
    print('Translated everyting in', round(dt, 5), 'seconds.')
    print('Thats %d characters per second' % int(len(c) / dt))
    with open('res.py', 'w') as f:
        f.write(res)
