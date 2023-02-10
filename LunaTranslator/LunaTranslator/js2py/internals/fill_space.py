from __future__ import unicode_literals

from .base import Scope
from .func_utils import *
from .conversions import *
import six
from .prototypes.jsboolean import BooleanPrototype
from .prototypes.jserror import ErrorPrototype
from .prototypes.jsfunction import FunctionPrototype
from .prototypes.jsnumber import NumberPrototype
from .prototypes.jsobject import ObjectPrototype
from .prototypes.jsregexp import RegExpPrototype
from .prototypes.jsstring import StringPrototype
from .prototypes.jsarray import ArrayPrototype
from .prototypes import jsjson
from .prototypes import jsutils

from .constructors import jsnumber, jsstring, jsarray, jsboolean, jsregexp, jsmath, jsobject, jsfunction, jsconsole



def fill_proto(proto, proto_class, space):
    for i in dir(proto_class):
        e = getattr(proto_class, i)
        if six.PY2:
            if hasattr(e, '__func__'):
                meth = e.__func__
            else:
                continue
        else:
            if hasattr(e, '__call__') and not i.startswith('__'):
                meth = e
            else:
                continue
        meth_name = meth.__name__.strip('_')  # RexExp._exec -> RegExp.exec
        js_meth = space.NewFunction(meth, space.ctx, (), meth_name, False, ())
        set_non_enumerable(proto, meth_name, js_meth)
    return proto


def easy_func(f, space):
    return space.NewFunction(f, space.ctx, (), f.__name__, False, ())


def Empty(this, args):
    return undefined


def set_non_enumerable(obj, name, prop):
    obj.define_own_property(
        unicode(name), {
            'value': prop,
            'writable': True,
            'enumerable': False,
            'configurable': True
        }, True)


def set_protected(obj, name, prop):
    obj.define_own_property(
        unicode(name), {
            'value': prop,
            'writable': False,
            'enumerable': False,
            'configurable': False
        }, True)


def fill_space(space, byte_generator):
    # set global scope
    global_scope = Scope({}, space, parent=None)
    global_scope.THIS_BINDING = global_scope
    global_scope.registers(byte_generator.declared_vars)
    space.GlobalObj = global_scope

    space.byte_generator = byte_generator

    # first init all protos, later take care of constructors and details

    # Function must be first obviously, we have to use a small trick to do that...
    function_proto = space.NewFunction(Empty, space.ctx, (), 'Empty', False,
                                       ())
    space.FunctionPrototype = function_proto  # this will fill the prototypes of the methods!
    fill_proto(function_proto, FunctionPrototype, space)

    # Object next
    object_proto = space.NewObject()  # no proto
    fill_proto(object_proto, ObjectPrototype, space)
    space.ObjectPrototype = object_proto
    function_proto.prototype = object_proto

    # Number
    number_proto = space.NewObject()
    number_proto.prototype = object_proto
    fill_proto(number_proto, NumberPrototype, space)
    number_proto.value = 0.
    number_proto.Class = 'Number'
    space.NumberPrototype = number_proto

    # String
    string_proto = space.NewObject()
    string_proto.prototype = object_proto
    fill_proto(string_proto, StringPrototype, space)
    string_proto.value = u''
    string_proto.Class = 'String'
    space.StringPrototype = string_proto

    # Boolean
    boolean_proto = space.NewObject()
    boolean_proto.prototype = object_proto
    fill_proto(boolean_proto, BooleanPrototype, space)
    boolean_proto.value = False
    boolean_proto.Class = 'Boolean'
    space.BooleanPrototype = boolean_proto

    # Array
    array_proto = space.NewArray(0)
    array_proto.prototype = object_proto
    fill_proto(array_proto, ArrayPrototype, space)
    space.ArrayPrototype = array_proto

    # JSON
    json = space.NewObject()
    json.put(u'stringify', easy_func(jsjson.stringify, space))
    json.put(u'parse', easy_func(jsjson.parse, space))

    # Utils
    parseFloat = easy_func(jsutils.parseFloat, space)
    parseInt = easy_func(jsutils.parseInt, space)
    isNaN = easy_func(jsutils.isNaN, space)
    isFinite = easy_func(jsutils.isFinite, space)

    # Error
    error_proto = space.NewError(u'Error', u'')
    error_proto.prototype = object_proto
    error_proto.put(u'name', u'Error')
    fill_proto(error_proto, ErrorPrototype, space)
    space.ErrorPrototype = error_proto

    def construct_constructor(typ):
        def creator(this, args):
            message = get_arg(args, 0)
            if not is_undefined(message):
                msg = to_string(message)
            else:
                msg = u''
            return space.NewError(typ, msg)

        j = easy_func(creator, space)
        j.name = unicode(typ)

        set_protected(j, 'prototype', space.ERROR_TYPES[typ])

        set_non_enumerable(space.ERROR_TYPES[typ], 'constructor', j)

        def new_create(args, space):
            message = get_arg(args, 0)
            if not is_undefined(message):
                msg = to_string(message)
            else:
                msg = u''
            return space.NewError(typ, msg)

        j.create = new_create
        return j

    # fill remaining error types
    error_constructors = {}
    for err_type_name in (u'Error', u'EvalError', u'RangeError',
                          u'ReferenceError', u'SyntaxError', u'TypeError',
                          u'URIError'):
        extra_err = space.NewError(u'Error', u'')
        extra_err.put(u'name', err_type_name)
        setattr(space, err_type_name + u'Prototype', extra_err)
        error_constructors[err_type_name] = construct_constructor(
            err_type_name)

    assert space.TypeErrorPrototype is not None

    # RegExp
    regexp_proto = space.NewRegExp(u'(?:)', u'')
    regexp_proto.prototype = object_proto
    fill_proto(regexp_proto, RegExpPrototype, space)
    space.RegExpPrototype = regexp_proto

    # Json

    # now all these boring constructors...

    # Number
    number = easy_func(jsnumber.Number, space)
    space.Number = number
    number.create = jsnumber.NumberConstructor
    set_non_enumerable(number_proto, 'constructor', number)
    set_protected(number, 'prototype', number_proto)
    # number has some extra constants
    for k, v in jsnumber.CONSTS.items():
        set_protected(number, k, v)

    # String
    string = easy_func(jsstring.String, space)
    space.String = string
    string.create = jsstring.StringConstructor
    set_non_enumerable(string_proto, 'constructor', string)
    set_protected(string, 'prototype', string_proto)
    # string has an extra function
    set_non_enumerable(string, 'fromCharCode',
                       easy_func(jsstring.fromCharCode, space))

    # Boolean
    boolean = easy_func(jsboolean.Boolean, space)
    space.Boolean = boolean
    boolean.create = jsboolean.BooleanConstructor
    set_non_enumerable(boolean_proto, 'constructor', boolean)
    set_protected(boolean, 'prototype', boolean_proto)

    # Array
    array = easy_func(jsarray.Array, space)
    space.Array = array
    array.create = jsarray.ArrayConstructor
    set_non_enumerable(array_proto, 'constructor', array)
    set_protected(array, 'prototype', array_proto)
    array.put(u'isArray', easy_func(jsarray.isArray, space))

    # RegExp
    regexp = easy_func(jsregexp.RegExp, space)
    space.RegExp = regexp
    regexp.create = jsregexp.RegExpCreate
    set_non_enumerable(regexp_proto, 'constructor', regexp)
    set_protected(regexp, 'prototype', regexp_proto)

    # Object
    _object = easy_func(jsobject.Object, space)
    space.Object = _object
    _object.create = jsobject.ObjectCreate
    set_non_enumerable(object_proto, 'constructor', _object)
    set_protected(_object, 'prototype', object_proto)
    fill_proto(_object, jsobject.ObjectMethods, space)

    # Function
    function = easy_func(jsfunction.Function, space)
    space.Function = function

    # Math
    math = space.NewObject()
    math.Class = 'Math'
    fill_proto(math, jsmath.MathFunctions, space)
    for k, v in jsmath.CONSTANTS.items():
        set_protected(math, k, v)

    console = space.NewObject()
    fill_proto(console, jsconsole.ConsoleMethods, space)

    # set global object
    builtins = {
        'String': string,
        'Number': number,
        'Boolean': boolean,
        'RegExp': regexp,
        'exports': convert_to_js_type({}, space),
        'Math': math,
        #'Date',
        'Object': _object,
        'Function': function,
        'JSON': json,
        'Array': array,
        'parseFloat': parseFloat,
        'parseInt': parseInt,
        'isFinite': isFinite,
        'isNaN': isNaN,
        'eval': easy_func(jsfunction._eval, space),
        'console': console,
        'log': console.get(u'log'),
    }

    builtins.update(error_constructors)

    set_protected(global_scope, 'NaN', NaN)
    set_protected(global_scope, 'Infinity', Infinity)
    for k, v in builtins.items():
        set_non_enumerable(global_scope, k, v)
