'''Most important file in Js2Py implementation: PyJs class - father of all PyJs objects'''
from copy import copy
import re

from .translators.friendly_nodes import REGEXP_CONVERTER
from .utils.injector import fix_js_args
from types import FunctionType, ModuleType, GeneratorType, BuiltinFunctionType, MethodType, BuiltinMethodType
from math import floor, log10
import traceback
try:
    import numpy
    NUMPY_AVAILABLE = True
except:
    NUMPY_AVAILABLE = False

# python 3 support
import six
if six.PY3:
    basestring = str
    long = int
    xrange = range
    unicode = str


def str_repr(s):
    if six.PY2:
        return repr(s.encode('utf-8'))
    else:
        return repr(s)


def MakeError(name, message):
    """Returns PyJsException with PyJsError inside"""
    return JsToPyException(ERRORS[name](Js(message)))


def to_python(val):
    if not isinstance(val, PyJs):
        return val
    if isinstance(val, PyJsUndefined) or isinstance(val, PyJsNull):
        return None
    elif isinstance(val, PyJsNumber):
        # this can be either float or long/int better to assume its int/long when a whole number...
        v = val.value
        try:
            i = int(v) if v == v else v  # nan...
            return v if i != v else i
        except:
            return v
    elif isinstance(val, (PyJsString, PyJsBoolean)):
        return val.value
    elif isinstance(val, PyObjectWrapper):
        return val.__dict__['obj']
    elif isinstance(val, PyJsArray) and val.CONVERT_TO_PY_PRIMITIVES:
        return to_list(val)
    elif isinstance(val, PyJsObject) and val.CONVERT_TO_PY_PRIMITIVES:
        return to_dict(val)
    else:
        return JsObjectWrapper(val)


def to_dict(js_obj,
            known=None):  # fixed recursion error in self referencing objects
    res = {}
    if known is None:
        known = {}
    if js_obj in known:
        return known[js_obj]
    known[js_obj] = res
    for k in js_obj:
        name = k.value
        input = js_obj.get(name)
        output = to_python(input)
        if isinstance(output, JsObjectWrapper):
            if output._obj.Class == 'Object':
                output = to_dict(output._obj, known)
                known[input] = output
            elif output._obj.Class in [
                    'Array', 'Int8Array', 'Uint8Array', 'Uint8ClampedArray',
                    'Int16Array', 'Uint16Array', 'Int32Array', 'Uint32Array',
                    'Float32Array', 'Float64Array'
            ]:
                output = to_list(output._obj)
                known[input] = output
        res[name] = output
    return res


def to_list(js_obj, known=None):
    res = len(js_obj) * [None]
    if known is None:
        known = {}
    if js_obj in known:
        return known[js_obj]
    known[js_obj] = res
    for k in js_obj:
        try:
            name = int(k.value)
        except:
            continue
        input = js_obj.get(str(name))
        output = to_python(input)
        if isinstance(output, JsObjectWrapper):
            if output._obj.Class in [
                    'Array', 'Int8Array', 'Uint8Array', 'Uint8ClampedArray',
                    'Int16Array', 'Uint16Array', 'Int32Array', 'Uint32Array',
                    'Float32Array', 'Float64Array', 'Arguments'
            ]:
                output = to_list(output._obj, known)
                known[input] = output
            elif output._obj.Class in ['Object']:
                output = to_dict(output._obj)
                known[input] = output
        res[name] = output
    return res


def HJs(val):
    if hasattr(val, '__call__'):  #

        @Js
        def PyWrapper(this, arguments, var=None):
            args = tuple(to_python(e) for e in arguments.to_list())
            try:
                py_res = val.__call__(*args)
            except Exception as e:
                message = 'your Python function failed!  '
                try:
                    message += str(e)
                except:
                    pass
                raise MakeError('Error', message)
            return py_wrap(py_res)

        try:
            PyWrapper.func_name = val.__name__
        except:
            pass
        return PyWrapper
    if isinstance(val, tuple):
        val = list(val)
    return Js(val)


def Js(val, Clamped=False):
    '''Converts Py type to PyJs type'''
    if isinstance(val, PyJs):
        return val
    elif val is None:
        return undefined
    elif isinstance(val, basestring):
        return PyJsString(val, StringPrototype)
    elif isinstance(val, bool):
        return true if val else false
    elif isinstance(val, float) or isinstance(val, int) or isinstance(
            val, long) or (NUMPY_AVAILABLE and isinstance(
                val,
                (numpy.int8, numpy.uint8, numpy.int16, numpy.uint16,
                 numpy.int32, numpy.uint32, numpy.float32, numpy.float64))):
        # This is supposed to speed things up. may not be the case
        if val in NUM_BANK:
            return NUM_BANK[val]
        return PyJsNumber(float(val), NumberPrototype)
    elif isinstance(val, FunctionType):
        return PyJsFunction(val, FunctionPrototype)
    #elif isinstance(val, ModuleType):
    #    mod = {}
    #    for name in dir(val):
    #        value = getattr(val, name)
    #        if isinstance(value, ModuleType):
    #            continue  # prevent recursive module conversion
    #        try:
    #            jsval = HJs(value)
    #        except RuntimeError:
    #            print 'Could not convert %s to PyJs object!' % name
    #            continue
    #        mod[name] = jsval
    #    return Js(mod)
    #elif isintance(val, ClassType):

    elif isinstance(val, dict):  # convert to object
        temp = PyJsObject({}, ObjectPrototype)
        for k, v in six.iteritems(val):
            temp.put(Js(k), Js(v))
        return temp
    elif isinstance(val, (list, tuple)):  #Convert to array
        return PyJsArray(val, ArrayPrototype)
    # convert to typedarray
    elif isinstance(val, JsObjectWrapper):
        return val.__dict__['_obj']
    elif NUMPY_AVAILABLE and isinstance(val, numpy.ndarray):
        if val.dtype == numpy.int8:
            return PyJsInt8Array(val, Int8ArrayPrototype)
        elif val.dtype == numpy.uint8 and not Clamped:
            return PyJsUint8Array(val, Uint8ArrayPrototype)
        elif val.dtype == numpy.uint8 and Clamped:
            return PyJsUint8ClampedArray(val, Uint8ClampedArrayPrototype)
        elif val.dtype == numpy.int16:
            return PyJsInt16Array(val, Int16ArrayPrototype)
        elif val.dtype == numpy.uint16:
            return PyJsUint16Array(val, Uint16ArrayPrototype)

        elif val.dtype == numpy.int32:
            return PyJsInt32Array(val, Int32ArrayPrototype)
        elif val.dtype == numpy.uint32:
            return PyJsUint16Array(val, Uint32ArrayPrototype)

        elif val.dtype == numpy.float32:
            return PyJsFloat32Array(val, Float32ArrayPrototype)
        elif val.dtype == numpy.float64:
            return PyJsFloat64Array(val, Float64ArrayPrototype)
    else:  # try to convert to js object
        return py_wrap(val)
        #raise RuntimeError('Cant convert python type to js (%s)' % repr(val))
        #try:
        #    obj = {}
        #    for name in dir(val):
        #        if name.startswith('_'):  #dont wrap attrs that start with _
        #            continue
        #        value = getattr(val, name)
        #        import types
        #        if not isinstance(value, (FunctionType, BuiltinFunctionType, MethodType, BuiltinMethodType,
        #                                  dict, int, basestring, bool, float, long, list, tuple)):
        #            continue
        #        obj[name] = HJs(value)
        #    return Js(obj)
        #except:
        #    raise RuntimeError('Cant convert python type to js (%s)' % repr(val))


def Type(val):
    try:
        return val.TYPE
    except:
        raise RuntimeError('Invalid type: ' + str(val))


def is_data_descriptor(desc):
    return desc and ('value' in desc or 'writable' in desc)


def is_accessor_descriptor(desc):
    return desc and ('get' in desc or 'set' in desc)


def is_generic_descriptor(desc):
    return desc and not (is_data_descriptor(desc)
                         or is_accessor_descriptor(desc))


##############################################################################


class PyJs(object):
    PRIMITIVES = frozenset(
        ['String', 'Number', 'Boolean', 'Undefined', 'Null'])
    TYPE = 'Object'
    Class = None
    extensible = True
    prototype = None
    own = {}
    GlobalObject = None
    IS_CHILD_SCOPE = False
    CONVERT_TO_PY_PRIMITIVES = False
    value = None
    buff = None

    def __init__(self, value=None, prototype=None, extensible=False):
        '''Constructor for Number String and Boolean'''
        # I dont think this is needed anymore
        # if self.Class=='String' and not isinstance(value, basestring):
        #     raise TypeError
        # if self.Class=='Number':
        #     if not isinstance(value, float):
        #         if not (isinstance(value, int) or isinstance(value, long)):
        #             raise TypeError
        #         value = float(value)
        # if self.Class=='Boolean' and not isinstance(value, bool):
        #     raise TypeError
        self.value = value
        self.extensible = extensible
        self.prototype = prototype
        self.own = {}
        self.buff = None

    def is_undefined(self):
        return self.Class == 'Undefined'

    def is_null(self):
        return self.Class == 'Null'

    def is_primitive(self):
        return self.TYPE in self.PRIMITIVES

    def is_object(self):
        return not self.is_primitive()

    def _type(self):
        return Type(self)

    def is_callable(self):
        return hasattr(self, 'call')

    def get_own_property(self, prop):
        return self.own.get(prop)

    def get_property(self, prop):
        cand = self.get_own_property(prop)
        if cand:
            return cand
        if self.prototype is not None:
            return self.prototype.get_property(prop)

    def update_array(self):
        for i in range(self.get('length').to_uint32()):
            self.put(str(i), Js(self.buff[i]))

    def get(self, prop):  #external use!
        #prop = prop.value
        if self.Class == 'Undefined' or self.Class == 'Null':
            raise MakeError('TypeError',
                            'Undefined and null dont have properties (tried getting property %s)' % repr(prop))
        if not isinstance(prop, basestring):
            prop = prop.to_string().value
        if not isinstance(prop, basestring): raise RuntimeError('Bug')
        if NUMPY_AVAILABLE and prop.isdigit():
            if isinstance(self.buff, numpy.ndarray):
                self.update_array()
        cand = self.get_property(prop)
        if cand is None:
            return Js(None)
        if is_data_descriptor(cand):
            return cand['value']
        if cand['get'].is_undefined():
            return cand['get']
        return cand['get'].call(self)

    def can_put(self, prop):  #to check
        desc = self.get_own_property(prop)
        if desc:  #if we have this property
            if is_accessor_descriptor(desc):
                return desc['set'].is_callable(
                )  # Check if setter method is defined
            else:  #data desc
                return desc['writable']
        if self.prototype is not None:
            return self.extensible
        inherited = self.get_property(prop)
        if inherited is None:
            return self.extensible
        if is_accessor_descriptor(inherited):
            return not inherited['set'].is_undefined()
        elif self.extensible:
            return inherited['writable']
        return False

    def put(self, prop, val, op=None):  #external use!
        '''Just like in js: self.prop op= val
           for example when op is '+' it will be self.prop+=val
           op can be either None for simple assignment or one of:
           * / % + - << >> & ^ |'''
        if self.Class == 'Undefined' or self.Class == 'Null':
            raise MakeError('TypeError',
                            'Undefined and null don\'t have properties (tried setting property %s)' % repr(prop))
        if not isinstance(prop, basestring):
            prop = prop.to_string().value
        if NUMPY_AVAILABLE and prop.isdigit():
            if self.Class == 'Int8Array':
                val = Js(numpy.int8(val.to_number().value))
            elif self.Class == 'Uint8Array':
                val = Js(numpy.uint8(val.to_number().value))
            elif self.Class == 'Uint8ClampedArray':
                if val < Js(numpy.uint8(0)):
                    val = Js(numpy.uint8(0))
                elif val > Js(numpy.uint8(255)):
                    val = Js(numpy.uint8(255))
                else:
                    val = Js(numpy.uint8(val.to_number().value))
            elif self.Class == 'Int16Array':
                val = Js(numpy.int16(val.to_number().value))
            elif self.Class == 'Uint16Array':
                val = Js(numpy.uint16(val.to_number().value))
            elif self.Class == 'Int32Array':
                val = Js(numpy.int32(val.to_number().value))
            elif self.Class == 'Uint32Array':
                val = Js(numpy.uint32(val.to_number().value))
            elif self.Class == 'Float32Array':
                val = Js(numpy.float32(val.to_number().value))
            elif self.Class == 'Float64Array':
                val = Js(numpy.float64(val.to_number().value))
            if isinstance(self.buff, numpy.ndarray):
                self.buff[int(prop)] = int(val.to_number().value)
        #we need to set the value to the incremented one
        if op is not None:
            val = getattr(self.get(prop), OP_METHODS[op])(val)
        if not self.can_put(prop):
            return val
        own_desc = self.get_own_property(prop)
        if is_data_descriptor(own_desc):
            if self.Class in [
                    'Array', 'Int8Array', 'Uint8Array', 'Uint8ClampedArray',
                    'Int16Array', 'Uint16Array', 'Int32Array', 'Uint32Array',
                    'Float32Array', 'Float64Array'
            ]:
                self.define_own_property(prop, {'value': val})
            else:
                self.own[prop]['value'] = val
            return val
        desc = self.get_property(prop)
        if is_accessor_descriptor(desc):
            desc['set'].call(self, (val, ))
        else:
            new = {
                'value': val,
                'writable': True,
                'configurable': True,
                'enumerable': True
            }
            if self.Class in [
                    'Array', 'Int8Array', 'Uint8Array', 'Uint8ClampedArray',
                    'Int16Array', 'Uint16Array', 'Int32Array', 'Uint32Array',
                    'Float32Array', 'Float64Array'
            ]:
                self.define_own_property(prop, new)
            else:
                self.own[prop] = new
        return val

    def has_property(self, prop):
        return self.get_property(prop) is not None

    def delete(self, prop):
        if not isinstance(prop, basestring):
            prop = prop.to_string().value
        desc = self.get_own_property(prop)
        if desc is None:
            return Js(True)
        if desc['configurable']:
            del self.own[prop]
            return Js(True)
        return Js(False)

    def default_value(
            self, hint=None
    ):  # made a mistake at the very early stage and made it to prefer string... caused lots! of problems
        order = ('valueOf', 'toString')
        if hint == 'String' or (hint is None and self.Class == 'Date'):
            order = ('toString', 'valueOf')
        for meth_name in order:
            method = self.get(meth_name)
            if method is not None and method.is_callable():
                cand = method.call(self)
                if cand.is_primitive():
                    return cand
        raise MakeError('TypeError',
                        'Cannot convert object to primitive value')

    def define_own_property(self, prop,
                            desc):  #Internal use only. External through Object
        # prop must be a Py string. Desc is either a descriptor or accessor.
        #Messy method -  raw translation from Ecma spec to prevent any bugs. # todo check this
        current = self.get_own_property(prop)

        extensible = self.extensible
        if not current:  #We are creating a new property
            if not extensible:
                return False
            if is_data_descriptor(desc) or is_generic_descriptor(desc):
                DEFAULT_DATA_DESC = {
                    'value': undefined,  #undefined
                    'writable': False,
                    'enumerable': False,
                    'configurable': False
                }
                DEFAULT_DATA_DESC.update(desc)
                self.own[prop] = DEFAULT_DATA_DESC
            else:
                DEFAULT_ACCESSOR_DESC = {
                    'get': undefined,  #undefined
                    'set': undefined,  #undefined
                    'enumerable': False,
                    'configurable': False
                }
                DEFAULT_ACCESSOR_DESC.update(desc)
                self.own[prop] = DEFAULT_ACCESSOR_DESC
            return True
        if not desc or desc == current:  #We dont need to change anything.
            return True
        configurable = current['configurable']
        if not configurable:  #Prevent changing configurable or enumerable
            if desc.get('configurable'):
                return False
            if 'enumerable' in desc and desc['enumerable'] != current[
                    'enumerable']:
                return False
        if is_generic_descriptor(desc):
            pass
        elif is_data_descriptor(current) != is_data_descriptor(desc):
            if not configurable:
                return False
            if is_data_descriptor(current):
                del current['value']
                del current['writable']
                current['set'] = undefined  #undefined
                current['get'] = undefined  #undefined
            else:
                del current['set']
                del current['get']
                current['value'] = undefined  #undefined
                current['writable'] = False
        elif is_data_descriptor(current) and is_data_descriptor(desc):
            if not configurable:
                if not current['writable'] and desc.get('writable'):
                    return False
            if not current['writable'] and 'value' in desc and current[
                    'value'] != desc['value']:
                return False
        elif is_accessor_descriptor(current) and is_accessor_descriptor(desc):
            if not configurable:
                if 'set' in desc and desc['set'] is not current['set']:
                    return False
                if 'get' in desc and desc['get'] is not current['get']:
                    return False
        current.update(desc)
        return True

    #these methods will work only for Number class
    def is_infinity(self):
        assert self.Class == 'Number'
        return self.value == float('inf') or self.value == -float('inf')

    def is_nan(self):
        assert self.Class == 'Number'
        return self.value != self.value  #nan!=nan evaluates to true

    def is_finite(self):
        return not (self.is_nan() or self.is_infinity())

    #Type Conversions. to_type. All must return pyjs subclass instance

    def to_primitive(self, hint=None):
        if self.is_primitive():
            return self
        if hint is None and (
                self.Class == 'Number' or self.Class == 'Boolean'
        ):  # favour number for Class== Number or Boolean default = String
            hint = 'Number'
        return self.default_value(hint)

    def to_boolean(self):
        typ = Type(self)
        if typ == 'Boolean':  #no need to convert
            return self
        elif typ == 'Null' or typ == 'Undefined':  #they are both always false
            return false
        elif typ == 'Number' or typ == 'String':  #false only for 0, '' and NaN
            return Js(bool(
                self.value
                and self.value == self.value))  # test for nan (nan -> flase)
        else:  #object -  always true
            return true

    def to_number(self):
        typ = Type(self)
        if typ == 'Null':  #null is 0
            return Js(0)
        elif typ == 'Undefined':  # undefined is NaN
            return NaN
        elif typ == 'Boolean':  # 1 for true 0 for false
            return Js(int(self.value))
        elif typ == 'Number':  # or self.Class=='Number':   # no need to convert
            return self
        elif typ == 'String':
            s = self.value.strip()  #Strip white space
            if not s:  # '' is simply 0
                return Js(0)
            if 'x' in s or 'X' in s[:3]:  #hex (positive only)
                try:  # try to convert
                    num = int(s, 16)
                except ValueError:  # could not convert > NaN
                    return NaN
                return Js(num)
            sign = 1  #get sign
            if s[0] in '+-':
                if s[0] == '-':
                    sign = -1
                s = s[1:]
            if s == 'Infinity':  #Check for infinity keyword. 'NaN' will be NaN anyway.
                return Js(sign * float('inf'))
            try:  #decimal try
                num = sign * float(s)  # Converted
            except ValueError:
                return NaN  # could not convert to decimal  > return NaN
            return Js(num)
        else:  #object -  most likely it will be NaN.
            return self.to_primitive('Number').to_number()

    def to_string(self):
        typ = Type(self)
        if typ == 'Null':
            return Js('null')
        elif typ == 'Undefined':
            return Js('undefined')
        elif typ == 'Boolean':
            return Js('true') if self.value else Js('false')
        elif typ == 'Number':  #or self.Class=='Number':
            return Js(unicode(js_dtoa(self.value)))
        elif typ == 'String':
            return self
        else:  #object
            return self.to_primitive('String').to_string()

    def to_object(self):
        typ = self.TYPE
        if typ == 'Null' or typ == 'Undefined':
            raise MakeError('TypeError',
                            'undefined or null can\'t be converted to object')
        elif typ == 'Boolean':  # Unsure here... todo repair here
            return Boolean.create(self)
        elif typ == 'Number':  #?
            return Number.create(self)
        elif typ == 'String':  #?
            return String.create(self)
        else:  #object
            return self

    def to_int32(self):
        num = self.to_number()
        if num.is_nan() or num.is_infinity():
            return 0
        int32 = int(num.value) % 2**32
        return int(int32 - 2**32 if int32 >= 2**31 else int32)

    def strict_equality_comparison(self, other):
        return PyJsStrictEq(self, other)

    def cok(self):
        """Check object coercible"""
        if self.Class in ('Undefined', 'Null'):
            raise MakeError('TypeError',
                            'undefined or null can\'t be converted to object')

    def to_int(self):
        num = self.to_number()
        if num.is_nan():
            return 0
        elif num.is_infinity():
            return 10**20 if num.value > 0 else -10**20
        return int(num.value)

    def to_uint32(self):
        num = self.to_number()
        if num.is_nan() or num.is_infinity():
            return 0
        return int(num.value) % 2**32

    def to_uint16(self):
        num = self.to_number()
        if num.is_nan() or num.is_infinity():
            return 0
        return int(num.value) % 2**16

    def to_int16(self):
        num = self.to_number()
        if num.is_nan() or num.is_infinity():
            return 0
        int16 = int(num.value) % 2**16
        return int(int16 - 2**16 if int16 >= 2**15 else int16)

    def same_as(self, other):
        typ = Type(self)
        if typ != other.Class:
            return False
        if typ == 'Undefined' or typ == 'Null':
            return True
        if typ == 'Boolean' or typ == 'Number' or typ == 'String':
            return self.value == other.value
        else:  #object
            return self is other  #Id compare.

    #Not to be used by translation (only internal use)
    def __getitem__(self, item):
        return self.get(
            str(item) if not isinstance(item, PyJs) else item.to_string().
            value)

    def __setitem__(self, item, value):
        self.put(
            str(item) if not isinstance(item, PyJs) else
            item.to_string().value, Js(value))

    def __len__(self):
        try:
            return self.get('length').to_uint32()
        except:
            raise TypeError(
                'This object (%s) does not have length property' % self.Class)

    #Oprators-------------
    #Unary, other will be implemented as functions. Increments and decrements
    # will be methods of Number class
    def __neg__(self):  #-u
        return Js(-self.to_number().value)

    def __pos__(self):  #+u
        return self.to_number()

    def __invert__(self):  #~u
        return Js(Js(~self.to_int32()).to_int32())

    def neg(self):  # !u  cant do 'not u' :(
        return Js(not self.to_boolean().value)

    def __nonzero__(self):
        return self.to_boolean().value

    def __bool__(self):
        return self.to_boolean().value

    def typeof(self):
        if self.is_callable():
            return Js('function')
        typ = Type(self).lower()
        if typ == 'null':
            typ = 'object'
        return Js(typ)

    #Bitwise operators
    #  <<, >>,  &, ^, |

    # <<
    def __lshift__(self, other):
        lnum = self.to_int32()
        rnum = other.to_uint32()
        shiftCount = rnum & 0x1F
        return Js(Js(lnum << shiftCount).to_int32())

    # >>
    def __rshift__(self, other):
        lnum = self.to_int32()
        rnum = other.to_uint32()
        shiftCount = rnum & 0x1F
        return Js(Js(lnum >> shiftCount).to_int32())

    # >>>
    def pyjs_bshift(self, other):
        lnum = self.to_uint32()
        rnum = other.to_uint32()
        shiftCount = rnum & 0x1F
        return Js(Js(lnum >> shiftCount).to_uint32())

    # &
    def __and__(self, other):
        lnum = self.to_int32()
        rnum = other.to_int32()
        return Js(Js(lnum & rnum).to_int32())

    # ^
    def __xor__(self, other):
        lnum = self.to_int32()
        rnum = other.to_int32()
        return Js(Js(lnum ^ rnum).to_int32())

    # |
    def __or__(self, other):
        lnum = self.to_int32()
        rnum = other.to_int32()
        return Js(Js(lnum | rnum).to_int32())

    # Additive operators
    # + and - are implemented here

    # +
    def __add__(self, other):
        a = self.to_primitive()
        b = other.to_primitive()
        if a.TYPE == 'String' or b.TYPE == 'String':
            return Js(a.to_string().value + b.to_string().value)
        a = a.to_number()
        b = b.to_number()
        return Js(a.value + b.value)

    # -
    def __sub__(self, other):
        return Js(self.to_number().value - other.to_number().value)

    #Multiplicative operators
    # *, / and % are implemented here

    # *
    def __mul__(self, other):
        return Js(self.to_number().value * other.to_number().value)

    # /
    def __div__(self, other):
        a = self.to_number().value
        b = other.to_number().value
        if b:
            return Js(a / b)
        if not a or a != a:
            return NaN
        return Infinity if a > 0 else -Infinity

    # %
    def __mod__(self, other):
        a = self.to_number().value
        b = other.to_number().value
        if abs(a) == float('inf') or not b:
            return NaN
        if abs(b) == float('inf'):
            return Js(a)
        pyres = Js(a % b)  #different signs in python and javascript
        #python has the same sign as b and js has the same
        #sign as a.
        if a < 0 and pyres.value > 0:
            pyres.value -= abs(b)
        elif a > 0 and pyres.value < 0:
            pyres.value += abs(b)
        return Js(pyres)

    #Comparisons (I dont implement === and !== here, these
    # will be implemented as external functions later)
    # <, <=, !=, ==, >=, > are implemented here.

    def abstract_relational_comparison(self, other, self_first=True):
        ''' self<other if self_first else other<self.
           Returns the result of the question: is self smaller than other?
           in case self_first is false it returns the answer of:
                                               is other smaller than self.
           result is PyJs type: bool or undefined'''
        px = self.to_primitive('Number')
        py = other.to_primitive('Number')
        if not self_first:  #reverse order
            px, py = py, px
        if not (px.Class == 'String' and py.Class == 'String'):
            px, py = px.to_number(), py.to_number()
            if px.is_nan() or py.is_nan():
                return undefined
            return Js(px.value < py.value)  # same cmp algorithm
        else:
            # I am pretty sure that python has the same
            # string cmp algorithm but I have to confirm it
            return Js(px.value < py.value)

    #<
    def __lt__(self, other):
        res = self.abstract_relational_comparison(other, True)
        if res.is_undefined():
            return false
        return res

    #<=
    def __le__(self, other):
        res = self.abstract_relational_comparison(other, False)
        if res.is_undefined():
            return false
        return res.neg()

    #>=
    def __ge__(self, other):
        res = self.abstract_relational_comparison(other, True)
        if res.is_undefined():
            return false
        return res.neg()

    #>
    def __gt__(self, other):
        res = self.abstract_relational_comparison(other, False)
        if res.is_undefined():
            return false
        return res

    def abstract_equality_comparison(self, other):
        ''' returns the result of JS == compare.
           result is PyJs type: bool'''
        tx, ty = self.TYPE, other.TYPE
        if tx == ty:
            if tx == 'Undefined' or tx == 'Null':
                return true
            if tx == 'Number' or tx == 'String' or tx == 'Boolean':
                return Js(self.value == other.value)
            return Js(self is other)  # Object
        elif (tx == 'Undefined' and ty == 'Null') or (ty == 'Undefined'
                                                      and tx == 'Null'):
            return true
        elif tx == 'Number' and ty == 'String':
            return self.abstract_equality_comparison(other.to_number())
        elif tx == 'String' and ty == 'Number':
            return self.to_number().abstract_equality_comparison(other)
        elif tx == 'Boolean':
            return self.to_number().abstract_equality_comparison(other)
        elif ty == 'Boolean':
            return self.abstract_equality_comparison(other.to_number())
        elif (tx == 'String' or tx == 'Number') and other.is_object():
            return self.abstract_equality_comparison(other.to_primitive())
        elif (ty == 'String' or ty == 'Number') and self.is_object():
            return self.to_primitive().abstract_equality_comparison(other)
        else:
            return false

    #==
    def __eq__(self, other):
        return self.abstract_equality_comparison(other)

    #!=
    def __ne__(self, other):
        return self.abstract_equality_comparison(other).neg()

    #Other methods (instanceof)

    def instanceof(self, other):
        '''checks if self is instance of other'''
        if not hasattr(other, 'has_instance'):
            return false
        return other.has_instance(self)

    #iteration
    def __iter__(self):
        #Returns a generator of all own enumerable properties
        # since the size od self.own can change we need to use different method of iteration.
        # SLOW! New items will NOT show up.
        returned = {}
        if not self.IS_CHILD_SCOPE:
            cands = sorted(
                name for name in self.own if self.own[name]['enumerable'])
        else:
            cands = sorted(name for name in self.own)
        for cand in cands:
            check = self.own.get(cand)
            if check and check['enumerable']:
                yield Js(cand)

    def contains(self, other):
        if not self.is_object():
            raise MakeError(
                'TypeError',
                "You can\'t use 'in' operator to search in non-objects")
        return Js(self.has_property(other.to_string().value))

    #Other Special methods
    def __call__(self, *args):
        '''Call a property prop as a function (this will be global object).

        NOTE: dont pass this and arguments here, these will be added
        automatically!'''
        if not self.is_callable():
            raise MakeError('TypeError',
                            '%s is not a function' % self.typeof())
        return self.call(self.GlobalObject, args)

    def create(self, *args):
        '''Generally not a constructor, raise an error'''
        raise MakeError('TypeError', '%s is not a constructor' % self.Class)

    def __unicode__(self):
        return self.to_string().value

    def __repr__(self):
        if self.Class == 'Object':
            res = []
            for e in self:
                res.append(str_repr(e.value) + ': ' + str_repr(self.get(e)))
            return '{%s}' % ', '.join(res)
        elif self.Class == 'String':
            return str_repr(self.value)
        elif self.Class in [
                'Array', 'Int8Array', 'Uint8Array', 'Uint8ClampedArray',
                'Int16Array', 'Uint16Array', 'Int32Array', 'Uint32Array',
                'Float32Array', 'Float64Array'
        ]:
            res = []
            for e in self:
                res.append(repr(self.get(e)))
            return '[%s]' % ', '.join(res)
        else:
            val = str_repr(self.to_string().value)
            return val

    def _fuck_python3(
            self
    ):  # hack to make object hashable in python 3 (__eq__ causes problems)
        return object.__hash__(self)

    def callprop(self, prop, *args):
        '''Call a property prop as a method (this will be self).

        NOTE: dont pass this and arguments here, these will be added
        automatically!'''
        if not isinstance(prop, basestring):
            prop = prop.to_string().value
        cand = self.get(prop)
        if not cand.is_callable():
            raise MakeError('TypeError',
                            '%s is not a function (tried calling property %s of %s)' % (
                            cand.typeof(), repr(prop), repr(self.Class)))
        return cand.call(self, args)

    def to_python(self):
        """returns equivalent python object.
         for example if this object is javascript array then this method will return equivalent python array"""
        return to_python(self)

    def to_py(self):
        """returns equivalent python object.
         for example if this object is javascript array then this method will return equivalent python array"""
        return self.to_python()


if six.PY3:
    PyJs.__hash__ = PyJs._fuck_python3
    PyJs.__truediv__ = PyJs.__div__
#Define some more classes representing operators:


def PyJsStrictEq(a, b):
    '''a===b'''
    tx, ty = Type(a), Type(b)
    if tx != ty:
        return false
    if tx == 'Undefined' or tx == 'Null':
        return true
    if a.is_primitive():  #string bool and number case
        return Js(a.value == b.value)
    if a.Class == b.Class == 'PyObjectWrapper':
        return Js(a.obj == b.obj)
    return Js(a is b)  # object comparison


def PyJsStrictNeq(a, b):
    ''' a!==b'''
    return PyJsStrictEq(a, b).neg()


def PyJsBshift(a, b):
    """a>>>b"""
    return a.pyjs_bshift(b)


def PyJsComma(a, b):
    return b


from .internals.simplex import JsException as PyJsException, js_dtoa
import pyjsparser
pyjsparser.parser.ENABLE_JS2PY_ERRORS = lambda msg: MakeError('SyntaxError', msg)


class PyJsSwitchException(Exception):
    pass


PyJs.MakeError = staticmethod(MakeError)


def JsToPyException(js):
    temp = PyJsException()
    temp.mes = js
    return temp


def PyExceptionToJs(py):
    return py.mes


#Scope class it will hold all the variables accessible to user
class Scope(PyJs):
    Class = 'global'
    extensible = True
    IS_CHILD_SCOPE = True

    # todo speed up
    # in order to speed up this very important class the top scope should behave differently than
    # child scopes, child scope should not have this property descriptor thing because they cant be changed anyway
    # they are all confugurable= False

    def __init__(self, scope, closure=None):
        """Doc"""
        self.prototype = closure
        if closure is None:
            # global, top level scope
            self.own = {}
            for k, v in six.iteritems(scope):
                # set all the global items
                self.define_own_property(
                    k, {
                        'value': v,
                        'configurable': False,
                        'writable': False,
                        'enumerable': False
                    })
        else:
            # not global, less powerful but faster closure.
            self.own = scope  # simple dictionary which maps name directly to js object.

    def register(self, lval):
        # registered keeps only global registered variables
        if self.prototype is None:
            # define in global scope
            if lval in self.own:
                self.own[lval]['configurable'] = False
            else:
                self.define_own_property(
                    lval, {
                        'value': undefined,
                        'configurable': False,
                        'writable': True,
                        'enumerable': True
                    })
        elif lval not in self.own:
            # define in local scope since it has not been defined yet
            self.own[lval] = undefined  # default value

    def registers(self, lvals):
        """register multiple variables"""
        for lval in lvals:
            self.register(lval)

    def put(self, lval, val, op=None):
        if self.prototype is None:
            # global scope put, simple
            return PyJs.put(self, lval, val, op)
        else:
            # trying to put in local scope
            # we dont know yet in which scope we should place this var
            if lval in self.own:
                if op:  # increment operation
                    val = getattr(self.own[lval], OP_METHODS[op])(val)
                self.own[lval] = val
                return val
            else:
                #try to put in the lower scope since we cant put in this one (var wasn't registered)
                return self.prototype.put(lval, val, op)

    def force_own_put(self, prop, val, configurable=False):
        if self.prototype is None:  # global scope
            self.own[prop] = {
                'value': val,
                'writable': True,
                'enumerable': True,
                'configurable': configurable
            }
        else:
            self.own[prop] = val

    def get(self, prop, throw=True):
        #note prop is always a Py String
        if not isinstance(prop, basestring):
            prop = prop.to_string().value
        if self.prototype is not None:
            # fast local scope
            cand = self.own.get(prop)
            if cand is None:
                return self.prototype.get(prop, throw)
            return cand
        # slow, global scope
        if prop not in self.own:
            if throw:
                raise MakeError('ReferenceError', '%s is not defined' % prop)
            return undefined
        return PyJs.get(self, prop)

    def delete(self, lval):
        if self.prototype is not None:
            if lval in self.own:
                return false
            return self.prototype.delete(lval)
        # we are in global scope here. Must exist and be configurable to delete
        if lval not in self.own:
            # this lval does not exist, why do you want to delete it???
            return true
        if self.own[lval]['configurable']:
            del self.own[lval]
            return true
        # not configurable, cant delete
        return false

    def pyimport(self, name, module):
        self.register(name)
        self.put(name, py_wrap(module))

    def __repr__(self):
        return u'[Object Global]'

    def to_python(self):
        return to_python(self)


class This(Scope):
    IS_CHILD_SCOPE = False

    def get(self, prop, throw=False):
        return Scope.get(self, prop, throw)


class JsObjectWrapper(object):
    def __init__(self, obj):
        self.__dict__['_obj'] = obj

    def __call__(self, *args):
        args = tuple(Js(e) for e in args)
        if '_prop_of' in self.__dict__:
            parent, meth = self.__dict__['_prop_of']
            return to_python(parent._obj.callprop(meth, *args))
        return to_python(self._obj(*args))

    def __getattr__(self, item):
        if item == 'new' and self._obj.is_callable():
            # return instance initializer
            def PyJsInstanceInit(*args):
                args = tuple(Js(e) for e in args)
                return self._obj.create(*args).to_python()

            return PyJsInstanceInit
        cand = to_python(self._obj.get(str(item)))
        # handling method calling... obj.meth(). Value of this in meth should be self
        if isinstance(cand, self.__class__):
            cand.__dict__['_prop_of'] = self, str(item)
        return cand

    def __setattr__(self, item, value):
        self._obj.put(str(item), Js(value))

    def __getitem__(self, item):
        cand = to_python(self._obj.get(str(item)))
        if isinstance(cand, self.__class__):
            cand.__dict__['_prop_of'] = self, str(item)
        return cand

    def __setitem__(self, item, value):
        self._obj.put(str(item), Js(value))

    def __iter__(self):
        if self._obj.Class in [
                'Array', 'Int8Array', 'Uint8Array', 'Uint8ClampedArray',
                'Int16Array', 'Uint16Array', 'Int32Array', 'Uint32Array',
                'Float32Array', 'Float64Array'
        ]:
            return iter(self.to_list())
        elif self._obj.Class == 'Object':
            return iter(self.to_dict())
        else:
            raise MakeError('TypeError',
                            '%s is not iterable in Python' % self._obj.Class)

    def __repr__(self):
        if self._obj.is_primitive() or self._obj.is_callable():
            return repr(self._obj)
        elif self._obj.Class in ('Array', 'Int8Array', 'Uint8Array',
                                 'Uint8ClampedArray', 'Int16Array',
                                 'Uint16Array', 'Int32Array', 'Uint32Array',
                                 'Float32Array', 'Float64Array', 'Arguments'):
            return repr(self.to_list())
        return repr(self.to_dict())

    def __len__(self):
        return len(self._obj)

    def __nonzero__(self):
        return bool(self._obj)

    def __bool__(self):
        return bool(self._obj)

    def to_dict(self):
        return to_dict(self.__dict__['_obj'])

    def to_list(self):
        return to_list(self.__dict__['_obj'])


class PyObjectWrapper(PyJs):
    Class = 'PyObjectWrapper'

    def __init__(self, obj):
        self.obj = obj

    def get(self, prop):
        if not isinstance(prop, basestring):
            prop = prop.to_string().value
        try:
            if prop.isdigit():
                return py_wrap(self.obj[int(prop)])
            return py_wrap(getattr(self.obj, prop))
        except:
            return undefined

    def put(self, prop, val, op=None, throw=False):
        if not isinstance(prop, basestring):
            prop = prop.to_string().value
        try:
            if isinstance(op, bool):
                raise ValueError("Op must be a string")
            elif op is not None:
                if op:  # increment operation
                    val = getattr(self.get(prop), OP_METHODS[op])(val)
            setattr(self.obj, prop, to_python(val))
        except AttributeError:
            raise MakeError('TypeError', 'Read only object probably...')
        return val

    def __call__(self, *args):
        py_args = tuple(to_python(e) for e in args)
        try:
            py_res = self.obj.__call__(*py_args)
        except Exception as e:
            message = 'your Python function failed!  '
            try:
                message += str(e)
            except:
                pass
            raise MakeError('Error', message)
        return py_wrap(py_res)

    def callprop(self, prop, *args):
        py_args = tuple(to_python(e) for e in args)
        if not isinstance(prop, basestring):
            prop = prop.to_string().value
        return self.get(prop)(*py_args)

    def delete(self, prop):
        if not isinstance(prop, basestring):
            prop = prop.to_string().value
        try:
            if prop.isdigit():
                del self.obj[int(prop)]
            else:
                delattr(self.obj, prop)
            return true
        except:
            return false

    def __repr__(self):
        return 'PyObjectWrapper(%s)' % str(self.obj)

    def to_python(self):
        return self.obj

    def to_py(self):
        return self.obj


def py_wrap(py):
    if isinstance(py, (FunctionType, BuiltinFunctionType, MethodType,
                       BuiltinMethodType, dict, int, str, bool, float, list,
                       tuple, long, basestring)) or py is None:
        return HJs(py)
    return PyObjectWrapper(py)


##############################################################################
#Define types


#Object
class PyJsObject(PyJs):
    Class = 'Object'

    def __init__(self, prop_descs={}, prototype=None, extensible=True):
        self.prototype = prototype
        self.extensible = extensible
        self.own = {}
        for prop, desc in six.iteritems(prop_descs):
            self.define_own_property(prop, desc)

    def __repr__(self):
        return repr(self.to_python().to_dict())


ObjectPrototype = PyJsObject()


#Function
class PyJsFunction(PyJs):
    Class = 'Function'

    def __init__(self, func, prototype=None, extensible=True, source=None):
        cand = fix_js_args(func)
        has_scope = cand is func
        func = cand
        self.argcount = six.get_function_code(func).co_argcount - 2 - has_scope
        self.code = func
        self.source = source if source else '{ [python code] }'
        self.func_name = func.__name__ if not func.__name__.startswith(
            'PyJs_anonymous') else ''
        self.extensible = extensible
        self.prototype = prototype
        self.own = {}
        #set own property length to the number of arguments
        self.define_own_property(
            'length', {
                'value': Js(self.argcount),
                'writable': False,
                'enumerable': False,
                'configurable': False
            })

        if self.func_name:
            self.define_own_property(
                'name', {
                    'value': Js(self.func_name),
                    'writable': False,
                    'enumerable': False,
                    'configurable': True
                })

        # set own prototype
        proto = Js({})
        # constructor points to this function
        proto.define_own_property(
            'constructor', {
                'value': self,
                'writable': True,
                'enumerable': False,
                'configurable': True
            })
        self.define_own_property(
            'prototype', {
                'value': proto,
                'writable': True,
                'enumerable': False,
                'configurable': False
            })

    def _set_name(self, name):
        '''name is py type'''
        if self.own.get('name'):
            self.func_name = name
            self.own['name']['value'] = Js(name)

    def construct(self, *args):
        proto = self.get('prototype')
        if not proto.is_object():  # set to standard prototype
            proto = ObjectPrototype
        obj = PyJsObject(prototype=proto)
        cand = self.call(obj, *args)
        return cand if cand.is_object() else obj

    def call(self, this, args=()):
        '''Calls this function and returns a result
        (converted to PyJs type so func can return python types)

        this must be a PyJs object and args must be a python tuple of PyJs objects.

        arguments object is passed automatically and will be equal to Js(args)
        (tuple converted to arguments object).You dont need to worry about number
        of arguments you provide if you supply less then missing ones will be set
        to undefined (but not present in arguments object).
        And if you supply too much then excess will not be passed
        (but they will be present in arguments object).
        '''
        if not hasattr(args, '__iter__'):  #get rid of it later
            args = (args, )
        args = tuple(Js(e) for e in args)  # this wont be needed later

        arguments = PyJsArguments(
            args, self)  # tuple will be converted to arguments object.
        arglen = self.argcount  #function expects this number of args.
        if len(args) > arglen:
            args = args[0:arglen]
        elif len(args) < arglen:
            args += (undefined, ) * (arglen - len(args))
        args += this, arguments  #append extra params to the arg list
        try:
            return Js(self.code(*args))
        except NotImplementedError:
            raise
        except RuntimeError as e:  # maximum recursion
            try:
                msg = e.message
            except:
                msg = repr(e)
            raise MakeError('RangeError', msg)

    def has_instance(self, other):
        # I am not sure here so instanceof may not work lol.
        if not other.is_object():
            return false
        proto = self.get('prototype')
        if not proto.is_object():
            raise TypeError(
                'Function has non-object prototype in instanceof check')
        while True:
            other = other.prototype
            if not other:  # todo make sure that the condition is not None or null
                return false
            if other is proto:
                return true

    def create(self, *args):
        proto = self.get('prototype')
        if not proto.is_object():
            proto = ObjectPrototype
        new = PyJsObject(prototype=proto)
        res = self.call(new, args)
        if res.is_object():
            return res
        return new


class PyJsBoundFunction(PyJsFunction):
    def __init__(self, target, bound_this, bound_args):
        self.target = target
        self.bound_this = bound_this
        self.bound_args = bound_args
        self.argcount = target.argcount
        self.code = target.code
        self.source = target.source
        self.func_name = target.func_name
        self.extensible = True
        self.prototype = FunctionPrototype
        self.own = {}
        # set own property length to the number of arguments
        self.define_own_property(
            'length', {
                'value': target.get('length') - Js(len(self.bound_args)),
                'writable': False,
                'enumerable': False,
                'configurable': False
            })

        if self.func_name:
            self.define_own_property(
                'name', {
                    'value': Js(self.func_name),
                    'writable': False,
                    'enumerable': False,
                    'configurable': True
                })

        # set own prototype
        proto = Js({})
        # constructor points to this function
        proto.define_own_property(
            'constructor', {
                'value': self,
                'writable': True,
                'enumerable': False,
                'configurable': True
            })
        self.define_own_property(
            'prototype', {
                'value': proto,
                'writable': True,
                'enumerable': False,
                'configurable': False
            })

    def call(self, this, args=()):
        return self.target.call(self.bound_this, self.bound_args + args)

    def has_instance(self, other):
        return self.target.has_instance(other)


PyJs.PyJsBoundFunction = PyJsBoundFunction

OP_METHODS = {
    '*': '__mul__',
    '/': '__div__',
    '%': '__mod__',
    '+': '__add__',
    '-': '__sub__',
    '<<': '__lshift__',
    '>>': '__rshift__',
    '&': '__and__',
    '^': '__xor__',
    '|': '__or__',
    '>>>': 'pyjs_bshift'
}


def Empty():
    return Js(None)


#Number
class PyJsNumber(PyJs):  #Note i dont implement +0 and -0. Just 0.
    TYPE = 'Number'
    Class = 'Number'


NumberPrototype = PyJsObject({}, ObjectPrototype)
NumberPrototype.Class = 'Number'
NumberPrototype.value = 0

Infinity = PyJsNumber(float('inf'), NumberPrototype)
NaN = PyJsNumber(float('nan'), NumberPrototype)
PyJs.NaN = NaN
PyJs.Infinity = Infinity

# This dict aims to increase speed of string creation by storing character instances
CHAR_BANK = {}
NUM_BANK = {}
PyJs.CHAR_BANK = CHAR_BANK


#String
# Different than implementation design in order to improve performance
#for example I dont create separate property for each character in string, it would take ages.
class PyJsString(PyJs):
    TYPE = 'String'
    Class = 'String'
    extensible = False

    def __init__(self, value=None, prototype=None):
        '''Constructor for Number String and Boolean'''
        if not isinstance(value, basestring):
            raise TypeError  # this will be internal error
        self.value = value
        self.prototype = prototype
        self.own = {}
        # this should be optimized because its mych slower than python str creation (about 50 times!)
        # Dont create separate properties for every index. Just
        self.own['length'] = {
            'value': Js(len(value)),
            'writable': False,
            'enumerable': False,
            'configurable': False
        }
        if len(value) == 1:
            CHAR_BANK[value] = self  #, 'writable': False,
            # 'enumerable': True, 'configurable': False}

    def get(self, prop):
        if not isinstance(prop, basestring):
            prop = prop.to_string().value
        try:
            index = int(prop)
            if index < 0:
                return undefined
            char = self.value[index]
            if char not in CHAR_BANK:
                Js(char)  # this will add char to CHAR BANK
            return CHAR_BANK[char]
        except Exception:
            pass
        return PyJs.get(self, prop)

    def can_put(self, prop):
        return False

    def __iter__(self):
        for i in xrange(len(self.value)):
            yield Js(i)  # maybe create an int bank?


StringPrototype = PyJsObject({}, ObjectPrototype)
StringPrototype.Class = 'String'
StringPrototype.value = ''

CHAR_BANK[''] = Js('')


#Boolean
class PyJsBoolean(PyJs):
    TYPE = 'Boolean'
    Class = 'Boolean'


BooleanPrototype = PyJsObject({}, ObjectPrototype)
BooleanPrototype.Class = 'Boolean'
BooleanPrototype.value = False

true = PyJsBoolean(True, BooleanPrototype)
false = PyJsBoolean(False, BooleanPrototype)


#Undefined
class PyJsUndefined(PyJs):
    TYPE = 'Undefined'
    Class = 'Undefined'

    def __init__(self):
        pass


undefined = PyJsUndefined()


#Null
class PyJsNull(PyJs):
    TYPE = 'Null'
    Class = 'Null'

    def __init__(self):
        pass


null = PyJsNull()
PyJs.null = null


class PyJsArray(PyJs):
    Class = 'Array'

    def __init__(self, arr=[], prototype=None):
        self.extensible = True
        self.prototype = prototype
        self.own = {
            'length': {
                'value': Js(0),
                'writable': True,
                'enumerable': False,
                'configurable': False
            }
        }
        for i, e in enumerate(arr):
            self.define_own_property(
                str(i), {
                    'value': Js(e),
                    'writable': True,
                    'enumerable': True,
                    'configurable': True
                })

    def define_own_property(self, prop, desc):
        old_len_desc = self.get_own_property('length')
        old_len = old_len_desc[
            'value'].value  #  value is js type so convert to py.
        if prop == 'length':
            if 'value' not in desc:
                return PyJs.define_own_property(self, prop, desc)
            new_len = desc['value'].to_uint32()
            if new_len != desc['value'].to_number().value:
                raise MakeError('RangeError', 'Invalid range!')
            new_desc = dict((k, v) for k, v in six.iteritems(desc))
            new_desc['value'] = Js(new_len)
            if new_len >= old_len:
                return PyJs.define_own_property(self, prop, new_desc)
            if not old_len_desc['writable']:
                return False
            if 'writable' not in new_desc or new_desc['writable'] == True:
                new_writable = True
            else:
                new_writable = False
                new_desc['writable'] = True
            if not PyJs.define_own_property(self, prop, new_desc):
                return False
            if new_len < old_len:
                # not very efficient for sparse arrays, so using different method for sparse:
                if old_len > 30 * len(self.own):
                    for ele in self.own.keys():
                        if ele.isdigit() and int(ele) >= new_len:
                            if not self.delete(
                                    ele
                            ):  # if failed to delete set len to current len and reject.
                                new_desc['value'] = Js(old_len + 1)
                                if not new_writable:
                                    new_desc['writable'] = False
                                PyJs.define_own_property(self, prop, new_desc)
                                return False
                    old_len = new_len
                else:  # standard method
                    while new_len < old_len:
                        old_len -= 1
                        if not self.delete(
                                str(int(old_len))
                        ):  # if failed to delete set len to current len and reject.
                            new_desc['value'] = Js(old_len + 1)
                            if not new_writable:
                                new_desc['writable'] = False
                            PyJs.define_own_property(self, prop, new_desc)
                            return False
            if not new_writable:
                self.own['length']['writable'] = False
            return True
        elif prop.isdigit():
            index = int(int(prop) % 2**32)
            if index >= old_len and not old_len_desc['writable']:
                return False
            if not PyJs.define_own_property(self, prop, desc):
                return False
            if index >= old_len:
                old_len_desc['value'] = Js(index + 1)
            return True
        else:
            return PyJs.define_own_property(self, prop, desc)

    def to_list(self):
        return [
            self.get(str(e)) for e in xrange(self.get('length').to_uint32())
        ]

    def __repr__(self):
        return repr(self.to_python().to_list())


class PyJsArrayBuffer(PyJs):
    Class = 'ArrayBuffer'

    def __init__(self, arr=[], prototype=None):
        self.extensible = True
        self.prototype = prototype
        self.own = {
            'length': {
                'value': Js(0),
                'writable': True,
                'enumerable': False,
                'configurable': False
            }
        }
        for i, e in enumerate(arr):
            self.define_own_property(
                str(i), {
                    'value': Js(e),
                    'writable': True,
                    'enumerable': True,
                    'configurable': True
                })

    def define_own_property(self, prop, desc):
        old_len_desc = self.get_own_property('length')
        old_len = old_len_desc[
            'value'].value  #  value is js type so convert to py.
        if prop == 'length':
            if 'value' not in desc:
                return PyJs.define_own_property(self, prop, desc)
            new_len = desc['value'].to_uint32()
            if new_len != desc['value'].to_number().value:
                raise MakeError('RangeError', 'Invalid range!')
            new_desc = dict((k, v) for k, v in six.iteritems(desc))
            new_desc['value'] = Js(new_len)
            if new_len >= old_len:
                return PyJs.define_own_property(self, prop, new_desc)
            if not old_len_desc['writable']:
                return False
            if 'writable' not in new_desc or new_desc['writable'] == True:
                new_writable = True
            else:
                new_writable = False
                new_desc['writable'] = True
            if not PyJs.define_own_property(self, prop, new_desc):
                return False
            if new_len < old_len:
                # not very efficient for sparse arrays, so using different method for sparse:
                if old_len > 30 * len(self.own):
                    for ele in self.own.keys():
                        if ele.isdigit() and int(ele) >= new_len:
                            if not self.delete(
                                    ele
                            ):  # if failed to delete set len to current len and reject.
                                new_desc['value'] = Js(old_len + 1)
                                if not new_writable:
                                    new_desc['writable'] = False
                                PyJs.define_own_property(self, prop, new_desc)
                                return False
                    old_len = new_len
                else:  # standard method
                    while new_len < old_len:
                        old_len -= 1
                        if not self.delete(
                                str(int(old_len))
                        ):  # if failed to delete set len to current len and reject.
                            new_desc['value'] = Js(old_len + 1)
                            if not new_writable:
                                new_desc['writable'] = False
                            PyJs.define_own_property(self, prop, new_desc)
                            return False
            if not new_writable:
                self.own['length']['writable'] = False
            return True
        elif prop.isdigit():
            index = int(int(prop) % 2**32)
            if index >= old_len and not old_len_desc['writable']:
                return False
            if not PyJs.define_own_property(self, prop, desc):
                return False
            if index >= old_len:
                old_len_desc['value'] = Js(index + 1)
            return True
        else:
            return PyJs.define_own_property(self, prop, desc)

    def to_list(self):
        return [
            self.get(str(e)) for e in xrange(self.get('length').to_uint32())
        ]

    def __repr__(self):
        return repr(self.to_python().to_list())


class PyJsInt8Array(PyJs):
    Class = 'Int8Array'

    def __init__(self, arr=[], prototype=None):
        self.extensible = True
        self.prototype = prototype
        self.own = {
            'length': {
                'value': Js(0),
                'writable': True,
                'enumerable': False,
                'configurable': False
            }
        }

        for i, e in enumerate(arr):
            self.define_own_property(
                str(i), {
                    'value': Js(e),
                    'writable': True,
                    'enumerable': True,
                    'configurable': True
                })

    def define_own_property(self, prop, desc):
        old_len_desc = self.get_own_property('length')
        old_len = old_len_desc[
            'value'].value  #  value is js type so convert to py.
        if prop == 'length':
            if 'value' not in desc:
                return PyJs.define_own_property(self, prop, desc)
            new_len = desc['value'].to_uint32()
            if new_len != desc['value'].to_number().value:
                raise MakeError('RangeError', 'Invalid range!')
            new_desc = dict((k, v) for k, v in six.iteritems(desc))
            new_desc['value'] = Js(new_len)
            if new_len >= old_len:
                return PyJs.define_own_property(self, prop, new_desc)
            if not old_len_desc['writable']:
                return False
            if 'writable' not in new_desc or new_desc['writable'] == True:
                new_writable = True
            else:
                new_writable = False
                new_desc['writable'] = True
            if not PyJs.define_own_property(self, prop, new_desc):
                return False
            if new_len < old_len:
                # not very efficient for sparse arrays, so using different method for sparse:
                if old_len > 30 * len(self.own):
                    for ele in self.own.keys():
                        if ele.isdigit() and int(ele) >= new_len:
                            if not self.delete(
                                    ele
                            ):  # if failed to delete set len to current len and reject.
                                new_desc['value'] = Js(old_len + 1)
                                if not new_writable:
                                    new_desc['writable'] = False
                                PyJs.define_own_property(self, prop, new_desc)
                                return False
                    old_len = new_len
                else:  # standard method
                    while new_len < old_len:
                        old_len -= 1
                        if not self.delete(
                                str(int(old_len))
                        ):  # if failed to delete set len to current len and reject.
                            new_desc['value'] = Js(old_len + 1)
                            if not new_writable:
                                new_desc['writable'] = False
                            PyJs.define_own_property(self, prop, new_desc)
                            return False
            if not new_writable:
                self.own['length']['writable'] = False
            return True
        elif prop.isdigit():
            index = int(int(prop) % 2**32)
            if index >= old_len and not old_len_desc['writable']:
                return False
            if not PyJs.define_own_property(self, prop, desc):
                return False
            if index >= old_len:
                old_len_desc['value'] = Js(index + 1)
            return True
        else:
            return PyJs.define_own_property(self, prop, desc)

    def to_list(self):
        return [
            self.get(str(e)) for e in xrange(self.get('length').to_uint32())
        ]

    def __repr__(self):
        return repr(self.to_python().to_list())


class PyJsUint8Array(PyJs):
    Class = 'Uint8Array'

    def __init__(self, arr=[], prototype=None):
        self.extensible = True
        self.prototype = prototype
        self.own = {
            'length': {
                'value': Js(0),
                'writable': True,
                'enumerable': False,
                'configurable': False
            }
        }

        for i, e in enumerate(arr):
            self.define_own_property(
                str(i), {
                    'value': Js(e),
                    'writable': True,
                    'enumerable': True,
                    'configurable': True
                })

    def define_own_property(self, prop, desc):
        old_len_desc = self.get_own_property('length')
        old_len = old_len_desc[
            'value'].value  #  value is js type so convert to py.
        if prop == 'length':
            if 'value' not in desc:
                return PyJs.define_own_property(self, prop, desc)
            new_len = desc['value'].to_uint32()
            if new_len != desc['value'].to_number().value:
                raise MakeError('RangeError', 'Invalid range!')
            new_desc = dict((k, v) for k, v in six.iteritems(desc))
            new_desc['value'] = Js(new_len)
            if new_len >= old_len:
                return PyJs.define_own_property(self, prop, new_desc)
            if not old_len_desc['writable']:
                return False
            if 'writable' not in new_desc or new_desc['writable'] == True:
                new_writable = True
            else:
                new_writable = False
                new_desc['writable'] = True
            if not PyJs.define_own_property(self, prop, new_desc):
                return False
            if new_len < old_len:
                # not very efficient for sparse arrays, so using different method for sparse:
                if old_len > 30 * len(self.own):
                    for ele in self.own.keys():
                        if ele.isdigit() and int(ele) >= new_len:
                            if not self.delete(
                                    ele
                            ):  # if failed to delete set len to current len and reject.
                                new_desc['value'] = Js(old_len + 1)
                                if not new_writable:
                                    new_desc['writable'] = False
                                PyJs.define_own_property(self, prop, new_desc)
                                return False
                    old_len = new_len
                else:  # standard method
                    while new_len < old_len:
                        old_len -= 1
                        if not self.delete(
                                str(int(old_len))
                        ):  # if failed to delete set len to current len and reject.
                            new_desc['value'] = Js(old_len + 1)
                            if not new_writable:
                                new_desc['writable'] = False
                            PyJs.define_own_property(self, prop, new_desc)
                            return False
            if not new_writable:
                self.own['length']['writable'] = False
            return True
        elif prop.isdigit():
            index = int(int(prop) % 2**32)
            if index >= old_len and not old_len_desc['writable']:
                return False
            if not PyJs.define_own_property(self, prop, desc):
                return False
            if index >= old_len:
                old_len_desc['value'] = Js(index + 1)
            return True
        else:
            return PyJs.define_own_property(self, prop, desc)

    def to_list(self):
        return [
            self.get(str(e)) for e in xrange(self.get('length').to_uint32())
        ]

    def __repr__(self):
        return repr(self.to_python().to_list())


class PyJsUint8ClampedArray(PyJs):
    Class = 'Uint8ClampedArray'

    def __init__(self, arr=[], prototype=None):
        self.extensible = True
        self.prototype = prototype
        self.own = {
            'length': {
                'value': Js(0),
                'writable': True,
                'enumerable': False,
                'configurable': False
            }
        }

        for i, e in enumerate(arr):
            self.define_own_property(
                str(i), {
                    'value': Js(e),
                    'writable': True,
                    'enumerable': True,
                    'configurable': True
                })

    def define_own_property(self, prop, desc):
        old_len_desc = self.get_own_property('length')
        old_len = old_len_desc[
            'value'].value  #  value is js type so convert to py.
        if prop == 'length':
            if 'value' not in desc:
                return PyJs.define_own_property(self, prop, desc)
            new_len = desc['value'].to_uint32()
            if new_len != desc['value'].to_number().value:
                raise MakeError('RangeError', 'Invalid range!')
            new_desc = dict((k, v) for k, v in six.iteritems(desc))
            new_desc['value'] = Js(new_len)
            if new_len >= old_len:
                return PyJs.define_own_property(self, prop, new_desc)
            if not old_len_desc['writable']:
                return False
            if 'writable' not in new_desc or new_desc['writable'] == True:
                new_writable = True
            else:
                new_writable = False
                new_desc['writable'] = True
            if not PyJs.define_own_property(self, prop, new_desc):
                return False
            if new_len < old_len:
                # not very efficient for sparse arrays, so using different method for sparse:
                if old_len > 30 * len(self.own):
                    for ele in self.own.keys():
                        if ele.isdigit() and int(ele) >= new_len:
                            if not self.delete(
                                    ele
                            ):  # if failed to delete set len to current len and reject.
                                new_desc['value'] = Js(old_len + 1)
                                if not new_writable:
                                    new_desc['writable'] = False
                                PyJs.define_own_property(self, prop, new_desc)
                                return False
                    old_len = new_len
                else:  # standard method
                    while new_len < old_len:
                        old_len -= 1
                        if not self.delete(
                                str(int(old_len))
                        ):  # if failed to delete set len to current len and reject.
                            new_desc['value'] = Js(old_len + 1)
                            if not new_writable:
                                new_desc['writable'] = False
                            PyJs.define_own_property(self, prop, new_desc)
                            return False
            if not new_writable:
                self.own['length']['writable'] = False
            return True
        elif prop.isdigit():
            index = int(int(prop) % 2**32)
            if index >= old_len and not old_len_desc['writable']:
                return False
            if not PyJs.define_own_property(self, prop, desc):
                return False
            if index >= old_len:
                old_len_desc['value'] = Js(index + 1)
            return True
        else:
            return PyJs.define_own_property(self, prop, desc)

    def to_list(self):
        return [
            self.get(str(e)) for e in xrange(self.get('length').to_uint32())
        ]

    def __repr__(self):
        return repr(self.to_python().to_list())


class PyJsInt16Array(PyJs):
    Class = 'Int16Array'

    def __init__(self, arr=[], prototype=None):
        self.extensible = True
        self.prototype = prototype
        self.own = {
            'length': {
                'value': Js(0),
                'writable': True,
                'enumerable': False,
                'configurable': False
            }
        }

        for i, e in enumerate(arr):
            self.define_own_property(
                str(i), {
                    'value': Js(e),
                    'writable': True,
                    'enumerable': True,
                    'configurable': True
                })

    def define_own_property(self, prop, desc):
        old_len_desc = self.get_own_property('length')
        old_len = old_len_desc[
            'value'].value  #  value is js type so convert to py.
        if prop == 'length':
            if 'value' not in desc:
                return PyJs.define_own_property(self, prop, desc)
            new_len = desc['value'].to_uint32()
            if new_len != desc['value'].to_number().value:
                raise MakeError('RangeError', 'Invalid range!')
            new_desc = dict((k, v) for k, v in six.iteritems(desc))
            new_desc['value'] = Js(new_len)
            if new_len >= old_len:
                return PyJs.define_own_property(self, prop, new_desc)
            if not old_len_desc['writable']:
                return False
            if 'writable' not in new_desc or new_desc['writable'] == True:
                new_writable = True
            else:
                new_writable = False
                new_desc['writable'] = True
            if not PyJs.define_own_property(self, prop, new_desc):
                return False
            if new_len < old_len:
                # not very efficient for sparse arrays, so using different method for sparse:
                if old_len > 30 * len(self.own):
                    for ele in self.own.keys():
                        if ele.isdigit() and int(ele) >= new_len:
                            if not self.delete(
                                    ele
                            ):  # if failed to delete set len to current len and reject.
                                new_desc['value'] = Js(old_len + 1)
                                if not new_writable:
                                    new_desc['writable'] = False
                                PyJs.define_own_property(self, prop, new_desc)
                                return False
                    old_len = new_len
                else:  # standard method
                    while new_len < old_len:
                        old_len -= 1
                        if not self.delete(
                                str(int(old_len))
                        ):  # if failed to delete set len to current len and reject.
                            new_desc['value'] = Js(old_len + 1)
                            if not new_writable:
                                new_desc['writable'] = False
                            PyJs.define_own_property(self, prop, new_desc)
                            return False
            if not new_writable:
                self.own['length']['writable'] = False
            return True
        elif prop.isdigit():
            index = int(int(prop) % 2**32)
            if index >= old_len and not old_len_desc['writable']:
                return False
            if not PyJs.define_own_property(self, prop, desc):
                return False
            if index >= old_len:
                old_len_desc['value'] = Js(index + 1)
            return True
        else:
            return PyJs.define_own_property(self, prop, desc)

    def to_list(self):
        return [
            self.get(str(e)) for e in xrange(self.get('length').to_uint32())
        ]

    def __repr__(self):
        return repr(self.to_python().to_list())


class PyJsUint16Array(PyJs):
    Class = 'Uint16Array'

    def __init__(self, arr=[], prototype=None):
        self.extensible = True
        self.prototype = prototype
        self.own = {
            'length': {
                'value': Js(0),
                'writable': True,
                'enumerable': False,
                'configurable': False
            }
        }

        for i, e in enumerate(arr):
            self.define_own_property(
                str(i), {
                    'value': Js(e),
                    'writable': True,
                    'enumerable': True,
                    'configurable': True
                })

    def define_own_property(self, prop, desc):
        old_len_desc = self.get_own_property('length')
        old_len = old_len_desc[
            'value'].value  #  value is js type so convert to py.
        if prop == 'length':
            if 'value' not in desc:
                return PyJs.define_own_property(self, prop, desc)
            new_len = desc['value'].to_uint32()
            if new_len != desc['value'].to_number().value:
                raise MakeError('RangeError', 'Invalid range!')
            new_desc = dict((k, v) for k, v in six.iteritems(desc))
            new_desc['value'] = Js(new_len)
            if new_len >= old_len:
                return PyJs.define_own_property(self, prop, new_desc)
            if not old_len_desc['writable']:
                return False
            if 'writable' not in new_desc or new_desc['writable'] == True:
                new_writable = True
            else:
                new_writable = False
                new_desc['writable'] = True
            if not PyJs.define_own_property(self, prop, new_desc):
                return False
            if new_len < old_len:
                # not very efficient for sparse arrays, so using different method for sparse:
                if old_len > 30 * len(self.own):
                    for ele in self.own.keys():
                        if ele.isdigit() and int(ele) >= new_len:
                            if not self.delete(
                                    ele
                            ):  # if failed to delete set len to current len and reject.
                                new_desc['value'] = Js(old_len + 1)
                                if not new_writable:
                                    new_desc['writable'] = False
                                PyJs.define_own_property(self, prop, new_desc)
                                return False
                    old_len = new_len
                else:  # standard method
                    while new_len < old_len:
                        old_len -= 1
                        if not self.delete(
                                str(int(old_len))
                        ):  # if failed to delete set len to current len and reject.
                            new_desc['value'] = Js(old_len + 1)
                            if not new_writable:
                                new_desc['writable'] = False
                            PyJs.define_own_property(self, prop, new_desc)
                            return False
            if not new_writable:
                self.own['length']['writable'] = False
            return True
        elif prop.isdigit():
            index = int(int(prop) % 2**32)
            if index >= old_len and not old_len_desc['writable']:
                return False
            if not PyJs.define_own_property(self, prop, desc):
                return False
            if index >= old_len:
                old_len_desc['value'] = Js(index + 1)
            return True
        else:
            return PyJs.define_own_property(self, prop, desc)

    def to_list(self):
        return [
            self.get(str(e)) for e in xrange(self.get('length').to_uint32())
        ]

    def __repr__(self):
        return repr(self.to_python().to_list())


class PyJsInt32Array(PyJs):
    Class = 'Int32Array'

    def __init__(self, arr=[], prototype=None):
        self.extensible = True
        self.prototype = prototype
        self.own = {
            'length': {
                'value': Js(0),
                'writable': True,
                'enumerable': False,
                'configurable': False
            }
        }

        for i, e in enumerate(arr):
            self.define_own_property(
                str(i), {
                    'value': Js(e),
                    'writable': True,
                    'enumerable': True,
                    'configurable': True
                })

    def define_own_property(self, prop, desc):
        old_len_desc = self.get_own_property('length')
        old_len = old_len_desc[
            'value'].value  #  value is js type so convert to py.
        if prop == 'length':
            if 'value' not in desc:
                return PyJs.define_own_property(self, prop, desc)
            new_len = desc['value'].to_uint32()
            if new_len != desc['value'].to_number().value:
                raise MakeError('RangeError', 'Invalid range!')
            new_desc = dict((k, v) for k, v in six.iteritems(desc))
            new_desc['value'] = Js(new_len)
            if new_len >= old_len:
                return PyJs.define_own_property(self, prop, new_desc)
            if not old_len_desc['writable']:
                return False
            if 'writable' not in new_desc or new_desc['writable'] == True:
                new_writable = True
            else:
                new_writable = False
                new_desc['writable'] = True
            if not PyJs.define_own_property(self, prop, new_desc):
                return False
            if new_len < old_len:
                # not very efficient for sparse arrays, so using different method for sparse:
                if old_len > 30 * len(self.own):
                    for ele in self.own.keys():
                        if ele.isdigit() and int(ele) >= new_len:
                            if not self.delete(
                                    ele
                            ):  # if failed to delete set len to current len and reject.
                                new_desc['value'] = Js(old_len + 1)
                                if not new_writable:
                                    new_desc['writable'] = False
                                PyJs.define_own_property(self, prop, new_desc)
                                return False
                    old_len = new_len
                else:  # standard method
                    while new_len < old_len:
                        old_len -= 1
                        if not self.delete(
                                str(int(old_len))
                        ):  # if failed to delete set len to current len and reject.
                            new_desc['value'] = Js(old_len + 1)
                            if not new_writable:
                                new_desc['writable'] = False
                            PyJs.define_own_property(self, prop, new_desc)
                            return False
            if not new_writable:
                self.own['length']['writable'] = False
            return True
        elif prop.isdigit():
            index = int(int(prop) % 2**32)
            if index >= old_len and not old_len_desc['writable']:
                return False
            if not PyJs.define_own_property(self, prop, desc):
                return False
            if index >= old_len:
                old_len_desc['value'] = Js(index + 1)
            return True
        else:
            return PyJs.define_own_property(self, prop, desc)

    def to_list(self):
        return [
            self.get(str(e)) for e in xrange(self.get('length').to_uint32())
        ]

    def __repr__(self):
        return repr(self.to_python().to_list())


class PyJsUint32Array(PyJs):
    Class = 'Uint32Array'

    def __init__(self, arr=[], prototype=None):
        self.extensible = True
        self.prototype = prototype
        self.own = {
            'length': {
                'value': Js(0),
                'writable': True,
                'enumerable': False,
                'configurable': False
            }
        }

        for i, e in enumerate(arr):
            self.define_own_property(
                str(i), {
                    'value': Js(e),
                    'writable': True,
                    'enumerable': True,
                    'configurable': True
                })

    def define_own_property(self, prop, desc):
        old_len_desc = self.get_own_property('length')
        old_len = old_len_desc[
            'value'].value  #  value is js type so convert to py.
        if prop == 'length':
            if 'value' not in desc:
                return PyJs.define_own_property(self, prop, desc)
            new_len = desc['value'].to_uint32()
            if new_len != desc['value'].to_number().value:
                raise MakeError('RangeError', 'Invalid range!')
            new_desc = dict((k, v) for k, v in six.iteritems(desc))
            new_desc['value'] = Js(new_len)
            if new_len >= old_len:
                return PyJs.define_own_property(self, prop, new_desc)
            if not old_len_desc['writable']:
                return False
            if 'writable' not in new_desc or new_desc['writable'] == True:
                new_writable = True
            else:
                new_writable = False
                new_desc['writable'] = True
            if not PyJs.define_own_property(self, prop, new_desc):
                return False
            if new_len < old_len:
                # not very efficient for sparse arrays, so using different method for sparse:
                if old_len > 30 * len(self.own):
                    for ele in self.own.keys():
                        if ele.isdigit() and int(ele) >= new_len:
                            if not self.delete(
                                    ele
                            ):  # if failed to delete set len to current len and reject.
                                new_desc['value'] = Js(old_len + 1)
                                if not new_writable:
                                    new_desc['writable'] = False
                                PyJs.define_own_property(self, prop, new_desc)
                                return False
                    old_len = new_len
                else:  # standard method
                    while new_len < old_len:
                        old_len -= 1
                        if not self.delete(
                                str(int(old_len))
                        ):  # if failed to delete set len to current len and reject.
                            new_desc['value'] = Js(old_len + 1)
                            if not new_writable:
                                new_desc['writable'] = False
                            PyJs.define_own_property(self, prop, new_desc)
                            return False
            if not new_writable:
                self.own['length']['writable'] = False
            return True
        elif prop.isdigit():
            index = int(int(prop) % 2**32)
            if index >= old_len and not old_len_desc['writable']:
                return False
            if not PyJs.define_own_property(self, prop, desc):
                return False
            if index >= old_len:
                old_len_desc['value'] = Js(index + 1)
            return True
        else:
            return PyJs.define_own_property(self, prop, desc)

    def to_list(self):
        return [
            self.get(str(e)) for e in xrange(self.get('length').to_uint32())
        ]

    def __repr__(self):
        return repr(self.to_python().to_list())


class PyJsFloat32Array(PyJs):
    Class = 'Float32Array'

    def __init__(self, arr=[], prototype=None):
        self.extensible = True
        self.prototype = prototype
        self.own = {
            'length': {
                'value': Js(0),
                'writable': True,
                'enumerable': False,
                'configurable': False
            }
        }

        for i, e in enumerate(arr):
            self.define_own_property(
                str(i), {
                    'value': Js(e),
                    'writable': True,
                    'enumerable': True,
                    'configurable': True
                })

    def define_own_property(self, prop, desc):
        old_len_desc = self.get_own_property('length')
        old_len = old_len_desc[
            'value'].value  #  value is js type so convert to py.
        if prop == 'length':
            if 'value' not in desc:
                return PyJs.define_own_property(self, prop, desc)
            new_len = desc['value'].to_uint32()
            if new_len != desc['value'].to_number().value:
                raise MakeError('RangeError', 'Invalid range!')
            new_desc = dict((k, v) for k, v in six.iteritems(desc))
            new_desc['value'] = Js(new_len)
            if new_len >= old_len:
                return PyJs.define_own_property(self, prop, new_desc)
            if not old_len_desc['writable']:
                return False
            if 'writable' not in new_desc or new_desc['writable'] == True:
                new_writable = True
            else:
                new_writable = False
                new_desc['writable'] = True
            if not PyJs.define_own_property(self, prop, new_desc):
                return False
            if new_len < old_len:
                # not very efficient for sparse arrays, so using different method for sparse:
                if old_len > 30 * len(self.own):
                    for ele in self.own.keys():
                        if ele.isdigit() and int(ele) >= new_len:
                            if not self.delete(
                                    ele
                            ):  # if failed to delete set len to current len and reject.
                                new_desc['value'] = Js(old_len + 1)
                                if not new_writable:
                                    new_desc['writable'] = False
                                PyJs.define_own_property(self, prop, new_desc)
                                return False
                    old_len = new_len
                else:  # standard method
                    while new_len < old_len:
                        old_len -= 1
                        if not self.delete(
                                str(int(old_len))
                        ):  # if failed to delete set len to current len and reject.
                            new_desc['value'] = Js(old_len + 1)
                            if not new_writable:
                                new_desc['writable'] = False
                            PyJs.define_own_property(self, prop, new_desc)
                            return False
            if not new_writable:
                self.own['length']['writable'] = False
            return True
        elif prop.isdigit():
            index = int(int(prop) % 2**32)
            if index >= old_len and not old_len_desc['writable']:
                return False
            if not PyJs.define_own_property(self, prop, desc):
                return False
            if index >= old_len:
                old_len_desc['value'] = Js(index + 1)
            return True
        else:
            return PyJs.define_own_property(self, prop, desc)

    def to_list(self):
        return [
            self.get(str(e)) for e in xrange(self.get('length').to_uint32())
        ]

    def __repr__(self):
        return repr(self.to_python().to_list())


class PyJsFloat64Array(PyJs):
    Class = 'Float64Array'

    def __init__(self, arr=[], prototype=None):
        self.extensible = True
        self.prototype = prototype
        self.own = {
            'length': {
                'value': Js(0),
                'writable': True,
                'enumerable': False,
                'configurable': False
            }
        }

        for i, e in enumerate(arr):
            self.define_own_property(
                str(i), {
                    'value': Js(e),
                    'writable': True,
                    'enumerable': True,
                    'configurable': True
                })

    def define_own_property(self, prop, desc):
        old_len_desc = self.get_own_property('length')
        old_len = old_len_desc[
            'value'].value  #  value is js type so convert to py.
        if prop == 'length':
            if 'value' not in desc:
                return PyJs.define_own_property(self, prop, desc)
            new_len = desc['value'].to_uint32()
            if new_len != desc['value'].to_number().value:
                raise MakeError('RangeError', 'Invalid range!')
            new_desc = dict((k, v) for k, v in six.iteritems(desc))
            new_desc['value'] = Js(new_len)
            if new_len >= old_len:
                return PyJs.define_own_property(self, prop, new_desc)
            if not old_len_desc['writable']:
                return False
            if 'writable' not in new_desc or new_desc['writable'] == True:
                new_writable = True
            else:
                new_writable = False
                new_desc['writable'] = True
            if not PyJs.define_own_property(self, prop, new_desc):
                return False
            if new_len < old_len:
                # not very efficient for sparse arrays, so using different method for sparse:
                if old_len > 30 * len(self.own):
                    for ele in self.own.keys():
                        if ele.isdigit() and int(ele) >= new_len:
                            if not self.delete(
                                    ele
                            ):  # if failed to delete set len to current len and reject.
                                new_desc['value'] = Js(old_len + 1)
                                if not new_writable:
                                    new_desc['writable'] = False
                                PyJs.define_own_property(self, prop, new_desc)
                                return False
                    old_len = new_len
                else:  # standard method
                    while new_len < old_len:
                        old_len -= 1
                        if not self.delete(
                                str(int(old_len))
                        ):  # if failed to delete set len to current len and reject.
                            new_desc['value'] = Js(old_len + 1)
                            if not new_writable:
                                new_desc['writable'] = False
                            PyJs.define_own_property(self, prop, new_desc)
                            return False
            if not new_writable:
                self.own['length']['writable'] = False
            return True
        elif prop.isdigit():
            index = int(int(prop) % 2**32)
            if index >= old_len and not old_len_desc['writable']:
                return False
            if not PyJs.define_own_property(self, prop, desc):
                return False
            if index >= old_len:
                old_len_desc['value'] = Js(index + 1)
            return True
        else:
            return PyJs.define_own_property(self, prop, desc)

    def to_list(self):
        return [
            self.get(str(e)) for e in xrange(self.get('length').to_uint32())
        ]

    def __repr__(self):
        return repr(self.to_python().to_list())


ArrayPrototype = PyJsArray([], ObjectPrototype)

ArrayBufferPrototype = PyJsArrayBuffer([], ObjectPrototype)

Int8ArrayPrototype = PyJsInt8Array([], ObjectPrototype)

Uint8ArrayPrototype = PyJsUint8Array([], ObjectPrototype)

Uint8ClampedArrayPrototype = PyJsUint8ClampedArray([], ObjectPrototype)

Int16ArrayPrototype = PyJsInt16Array([], ObjectPrototype)

Uint16ArrayPrototype = PyJsUint16Array([], ObjectPrototype)

Int32ArrayPrototype = PyJsInt32Array([], ObjectPrototype)

Uint32ArrayPrototype = PyJsUint32Array([], ObjectPrototype)

Float32ArrayPrototype = PyJsFloat32Array([], ObjectPrototype)

Float64ArrayPrototype = PyJsFloat64Array([], ObjectPrototype)


class PyJsArguments(PyJs):
    Class = 'Arguments'

    def __init__(self, args, callee):
        self.own = {}
        self.extensible = True
        self.prototype = ObjectPrototype
        self.define_own_property(
            'length', {
                'value': Js(len(args)),
                'writable': True,
                'enumerable': False,
                'configurable': True
            })
        self.define_own_property(
            'callee', {
                'value': callee,
                'writable': True,
                'enumerable': False,
                'configurable': True
            })
        for i, e in enumerate(args):
            self.put(str(i), Js(e))

    def to_list(self):
        return [
            self.get(str(e)) for e in xrange(self.get('length').to_uint32())
        ]


#We can define function proto after number proto because func uses number in its init
FunctionPrototype = PyJsFunction(Empty, ObjectPrototype)
FunctionPrototype.own['name']['value'] = Js('')

# I will not rewrite RegExp engine from scratch. I will use re because its much faster.
# I have to only make sure that I am handling all the differences correctly.
REGEXP_DB = {}


class PyJsRegExp(PyJs):
    Class = 'RegExp'
    extensible = True

    def __init__(self, regexp, prototype=None):

        self.prototype = prototype
        self.glob = False
        self.ignore_case = 0
        self.multiline = 0
        # self._cache = {'str':'NoStringEmpty23093',
        #                'iterator': None,
        #                'lastpos': -1,
        #                'matches': {}}
        flags = ''
        if not regexp[-1] == '/':
            #contains some flags (allowed are i, g, m
            spl = regexp.rfind('/')
            flags = set(regexp[spl + 1:])
            self.value = regexp[1:spl]
            if 'g' in flags:
                self.glob = True
            if 'i' in flags:
                self.ignore_case = re.IGNORECASE
            if 'm' in flags:
                self.multiline = re.MULTILINE
        else:
            self.value = regexp[1:-1]

        try:
            if self.value in REGEXP_DB:
                self.pat = REGEXP_DB[regexp]
            else:
                comp = 'None'
                # we have to check whether pattern is valid.
                # also this will speed up matching later
                # todo critical fix patter conversion etc. ..!!!!!
                # ugly hacks porting js reg exp to py reg exp works in 99% of cases ;)
                possible_fixes = [(u'[]', u'[\0]'), (u'[^]', u'[^\0]'),
                                  (u'nofix1791', u'nofix1791')]
                reg = self.value
                for fix, rep in possible_fixes:
                    comp = REGEXP_CONVERTER._interpret_regexp(reg, flags)
                    #print 'reg -> comp', reg, '->', comp
                    try:
                        self.pat = re.compile(
                            comp, self.ignore_case | self.multiline)
                        #print reg, '->', comp
                        break
                    except:
                        reg = reg.replace(fix, rep)
                    # print 'Fix', fix, '->', rep, '=', reg
                else:
                    raise
                REGEXP_DB[regexp] = self.pat
        except:
            #print 'Invalid pattern but fuck it', self.value, comp
            raise MakeError(
                'SyntaxError',
                'Invalid RegExp pattern: %s -> %s' % (repr(self.value),
                                                      repr(comp)))
        # now set own properties:
        self.own = {
            'source': {
                'value': Js(self.value),
                'enumerable': False,
                'writable': False,
                'configurable': False
            },
            'global': {
                'value': Js(self.glob),
                'enumerable': False,
                'writable': False,
                'configurable': False
            },
            'ignoreCase': {
                'value': Js(bool(self.ignore_case)),
                'enumerable': False,
                'writable': False,
                'configurable': False
            },
            'multiline': {
                'value': Js(bool(self.multiline)),
                'enumerable': False,
                'writable': False,
                'configurable': False
            },
            'lastIndex': {
                'value': Js(0),
                'enumerable': False,
                'writable': True,
                'configurable': False
            }
        }

    def match(self, string, pos):
        '''string is of course py string'''
        return self.pat.match(string, pos)  # way easier :)
        # assert 0<=pos <= len(string)
        # if not pos:
        #     return re.match(self.pat, string)
        # else:
        #     if self._cache['str']==string:
        #         if pos>self._cache['lastpos']:
        #             for m in self._cache['iterator']:
        #                 start = m.start()
        #                 self._cache['lastpos'] = start
        #                 self._cache['matches'][start] = m
        #                 if start==pos:
        #                     return m
        #                 elif start>pos:
        #                     return None
        #             self._cache['lastpos'] = len(string)
        #             return None
        #         else:
        #             return self._cache['matches'].get(pos)
        #     else:
        #         self._cache['str'] = string
        #         self._cache['matches'] = {}
        #         self._cache['lastpos'] = -1
        #         self._cache['iterator'] = re.finditer(self.pat, string)
        #         return self.match(string, pos)


def JsRegExp(source):
    # Takes regexp literal!
    return PyJsRegExp(source, RegExpPrototype)


RegExpPrototype = PyJsRegExp('/(?:)/', ObjectPrototype)

####Exceptions:
default_attrs = {'writable': True, 'enumerable': False, 'configurable': True}


def fill_in_props(obj, props, default_desc):
    for prop, value in props.items():
        default_desc['value'] = Js(value)
        obj.define_own_property(prop, default_desc)


class PyJsError(PyJs):
    Class = 'Error'
    extensible = True

    def __init__(self, message=None, prototype=None):
        self.prototype = prototype
        self.own = {}
        if message is not None:
            self.put('message', Js(message).to_string())
            self.own['message']['enumerable'] = False


ErrorPrototype = PyJsError(Js(''), ObjectPrototype)


@Js
def Error(message):
    return PyJsError(None if message.is_undefined() else message,
                     ErrorPrototype)


Error.create = Error
err = {'name': 'Error', 'constructor': Error}
fill_in_props(ErrorPrototype, err, default_attrs)
Error.define_own_property(
    'prototype', {
        'value': ErrorPrototype,
        'enumerable': False,
        'writable': False,
        'configurable': False
    })


def define_error_type(name):
    TypeErrorPrototype = PyJsError(None, ErrorPrototype)

    @Js
    def TypeError(message):
        return PyJsError(None if message.is_undefined() else message,
                         TypeErrorPrototype)

    err = {'name': name, 'constructor': TypeError}
    fill_in_props(TypeErrorPrototype, err, default_attrs)
    TypeError.define_own_property(
        'prototype', {
            'value': TypeErrorPrototype,
            'enumerable': False,
            'writable': False,
            'configurable': False
        })
    ERRORS[name] = TypeError


ERRORS = {'Error': Error}
ERROR_NAMES = ['Eval', 'Type', 'Range', 'Reference', 'Syntax', 'URI']

for e in ERROR_NAMES:
    define_error_type(e + 'Error')

##############################################################################
# Import and fill prototypes here.


#this works only for data properties
def fill_prototype(prototype, Class, attrs, constructor=False):
    for i in dir(Class):
        e = getattr(Class, i)
        if six.PY2:
            if hasattr(e, '__func__'):
                temp = PyJsFunction(e.__func__, FunctionPrototype)
                attrs = dict((k, v) for k, v in attrs.iteritems())
                attrs['value'] = temp
                prototype.define_own_property(i, attrs)
        else:
            if hasattr(e, '__call__') and not i.startswith('__'):
                temp = PyJsFunction(e, FunctionPrototype)
                attrs = dict((k, v) for k, v in attrs.items())
                attrs['value'] = temp
                prototype.define_own_property(i, attrs)
        if constructor:
            attrs['value'] = constructor
            prototype.define_own_property('constructor', attrs)


PyJs.undefined = undefined
PyJs.Js = staticmethod(Js)

from .prototypes import jsfunction, jsobject, jsnumber, jsstring, jsboolean, jsarray, jsregexp, jserror, jsarraybuffer, jstypedarray

#Object proto
fill_prototype(ObjectPrototype, jsobject.ObjectPrototype, default_attrs)


#Define __proto__ accessor (this cant be done by fill_prototype since)
@Js
def __proto__():
    return this.prototype if this.prototype is not None else null


getter = __proto__


@Js
def __proto__(val):
    if val.is_object():
        this.prototype = val


setter = __proto__
ObjectPrototype.define_own_property('__proto__', {
    'set': setter,
    'get': getter,
    'enumerable': False,
    'configurable': True
})

#Function proto
fill_prototype(FunctionPrototype, jsfunction.FunctionPrototype, default_attrs)
#Number proto
fill_prototype(NumberPrototype, jsnumber.NumberPrototype, default_attrs)
#String proto
fill_prototype(StringPrototype, jsstring.StringPrototype, default_attrs)
#Boolean proto
fill_prototype(BooleanPrototype, jsboolean.BooleanPrototype, default_attrs)
#Array proto
fill_prototype(ArrayPrototype, jsarray.ArrayPrototype, default_attrs)
# ArrayBuffer proto
fill_prototype(ArrayBufferPrototype, jsarraybuffer.ArrayBufferPrototype,
               default_attrs)
# Int8Array proto
fill_prototype(Int8ArrayPrototype, jstypedarray.TypedArrayPrototype,
               default_attrs)
# Uint8Array proto
fill_prototype(Uint8ArrayPrototype, jstypedarray.TypedArrayPrototype,
               default_attrs)
# Uint8ClampedArray proto
fill_prototype(Uint8ClampedArrayPrototype, jstypedarray.TypedArrayPrototype,
               default_attrs)
# Int16Array proto
fill_prototype(Int16ArrayPrototype, jstypedarray.TypedArrayPrototype,
               default_attrs)
# Uint16Array proto
fill_prototype(Uint16ArrayPrototype, jstypedarray.TypedArrayPrototype,
               default_attrs)
# Int32Array proto
fill_prototype(Int32ArrayPrototype, jstypedarray.TypedArrayPrototype,
               default_attrs)
# Uint32Array proto
fill_prototype(Uint32ArrayPrototype, jstypedarray.TypedArrayPrototype,
               default_attrs)
# Float32Array proto
fill_prototype(Float32ArrayPrototype, jstypedarray.TypedArrayPrototype,
               default_attrs)
# Float64Array proto
fill_prototype(Float64ArrayPrototype, jstypedarray.TypedArrayPrototype,
               default_attrs)
#Error proto
fill_prototype(ErrorPrototype, jserror.ErrorPrototype, default_attrs)
#RegExp proto
fill_prototype(RegExpPrototype, jsregexp.RegExpPrototype, default_attrs)
# add exec to regexpfunction (cant add it automatically because of its name :(
RegExpPrototype.own['exec'] = RegExpPrototype.own['exec2']
del RegExpPrototype.own['exec2']

#########################################################################
# Constructors


# String
@Js
def String(st):
    if not len(arguments):
        return Js('')
    return arguments[0].to_string()


@Js
def string_constructor():
    temp = PyJsObject(prototype=StringPrototype)
    temp.Class = 'String'
    #temp.TYPE = 'String'
    if not len(arguments):
        temp.value = ''
    else:
        temp.value = arguments[0].to_string().value
        for i, ch in enumerate(temp.value):  # this will make things long...
            temp.own[str(i)] = {
                'value': Js(ch),
                'writable': False,
                'enumerable': True,
                'configurable': True
            }
    temp.own['length'] = {
        'value': Js(len(temp.value)),
        'writable': False,
        'enumerable': False,
        'configurable': False
    }
    return temp


String.create = string_constructor

# RegExp
REG_EXP_FLAGS = ('g', 'i', 'm')


@Js
def RegExp(pattern, flags):
    if pattern.Class == 'RegExp':
        if not flags.is_undefined():
            raise MakeError(
                'TypeError',
                'Cannot supply flags when constructing one RegExp from another'
            )
        # return unchanged
        return pattern
    #pattern is not a regexp
    if pattern.is_undefined():
        pattern = ''
    else:
        pattern = pattern.to_string().value
        # try:
        #     pattern = REGEXP_CONVERTER._unescape_string(pattern.to_string().value)
        # except:
        #     raise MakeError('SyntaxError', 'Invalid regexp')
    flags = flags.to_string().value if not flags.is_undefined() else ''
    for flag in flags:
        if flag not in REG_EXP_FLAGS:
            raise MakeError(
                'SyntaxError',
                'Invalid flags supplied to RegExp constructor "%s"' % flag)
    if len(set(flags)) != len(flags):
        raise MakeError(
            'SyntaxError',
            'Invalid flags supplied to RegExp constructor "%s"' % flags)
    pattern = '/%s/' % (pattern if pattern else '(?:)') + flags
    return JsRegExp(pattern)


RegExp.create = RegExp
PyJs.RegExp = RegExp

# Number


@Js
def Number():
    if len(arguments):
        return arguments[0].to_number()
    else:
        return Js(0)


@Js
def number_constructor():
    temp = PyJsObject(prototype=NumberPrototype)
    temp.Class = 'Number'
    #temp.TYPE = 'Number'
    if len(arguments):
        temp.value = arguments[0].to_number().value
    else:
        temp.value = 0
    return temp


Number.create = number_constructor

# Boolean


@Js
def Boolean(value):
    return value.to_boolean()


@Js
def boolean_constructor(value):
    temp = PyJsObject(prototype=BooleanPrototype)
    temp.Class = 'Boolean'
    #temp.TYPE = 'Boolean'
    temp.value = value.to_boolean().value
    return temp


Boolean.create = boolean_constructor

##############################################################################


def appengine(code):
    try:
        return translator.translate_js(code.decode('utf-8'))
    except:
        return traceback.format_exc()


builtins = ('true', 'false', 'null', 'undefined', 'Infinity', 'NaN')

scope = dict(zip(builtins, [eval(e) for e in builtins]))

JS_BUILTINS = dict((k, v) for k, v in scope.items())

# Fill in NUM_BANK
for e in xrange(-2**10, 2**14):
    NUM_BANK[e] = Js(e)

if __name__ == '__main__':
    print(ObjectPrototype.get('toString').callprop('call'))
    print(FunctionPrototype.own)
    a = null - Js(49404)
    x = a.put('ser', Js('der'))
    print(Js(0) or Js('p') and Js(4.0000000000050000001))
    FunctionPrototype.put('Chuj', Js(409))
    for e in FunctionPrototype:
        print('Obk', e.get('__proto__').get('__proto__').get('__proto__'), e)
    import code
    s = Js(4)
    b = Js(6)

    s2 = Js(4)
    o = ObjectPrototype
    o.put('x', Js(100))
    var = Scope(scope)
    e = code.InteractiveConsole(globals())
    #e.raw_input = interactor
    e.interact()
