from .base import *
from .constructors.jsmath import Math
from .constructors.jsdate import Date
from .constructors.jsobject import Object
from .constructors.jsfunction import Function
from .constructors.jsstring import String
from .constructors.jsnumber import Number
from .constructors.jsboolean import Boolean
from .constructors.jsregexp import RegExp
from .constructors.jsarray import Array
from .constructors.jsarraybuffer import ArrayBuffer
from .constructors.jsint8array import Int8Array
from .constructors.jsuint8array import Uint8Array
from .constructors.jsuint8clampedarray import Uint8ClampedArray
from .constructors.jsint16array import Int16Array
from .constructors.jsuint16array import Uint16Array
from .constructors.jsint32array import Int32Array
from .constructors.jsuint32array import Uint32Array
from .constructors.jsfloat32array import Float32Array
from .constructors.jsfloat64array import Float64Array
from .prototypes.jsjson import JSON
from .host.console import console
from .host.jseval import Eval
from .host.jsfunctions import parseFloat, parseInt, isFinite, \
    isNaN, escape, unescape, encodeURI, decodeURI, encodeURIComponent, decodeURIComponent

# Now we have all the necessary items to create global environment for script
__all__ = [
    'Js', 'PyJsComma', 'PyJsStrictEq', 'PyJsStrictNeq', 'PyJsException',
    'PyJsBshift', 'Scope', 'PyExceptionToJs', 'JsToPyException', 'JS_BUILTINS',
    'appengine', 'set_global_object', 'JsRegExp', 'PyJsException',
    'PyExceptionToJs', 'JsToPyException', 'PyJsSwitchException'
]

# these were defined in base.py
builtins = (
    'true',
    'false',
    'null',
    'undefined',
    'Infinity',
    'NaN',
    'console',
    'String',
    'Number',
    'Boolean',
    'RegExp',
    'Math',
    'Date',
    'Object',
    'Function',
    'Array',
    'Int8Array',
    'Uint8Array',
    'Uint8ClampedArray',
    'Int16Array',
    'Uint16Array',
    'Int32Array',
    'Uint32Array',
    'Float32Array',
    'Float64Array',
    'ArrayBuffer',
    'parseFloat',
    'parseInt',
    'isFinite',
    'isNaN',
    'escape',
    'unescape',
    'encodeURI',
    'decodeURI',
    'encodeURIComponent',
    'decodeURIComponent',
)

#Array, Function, JSON,   Error is done later :)
# also some built in functions like eval...


def set_global_object(obj):
    obj.IS_CHILD_SCOPE = False
    this = This({})
    this.own = obj.own
    this.prototype = obj.prototype
    PyJs.GlobalObject = this
    # make this available
    obj.register('this')
    obj.put('this', this)
    # also add window and set it to be a global object for compatibility
    obj.register('window')
    obj.put('window', this)


scope = dict(zip(builtins, [globals()[e] for e in builtins]))
# Now add errors:
for name, error in ERRORS.items():
    scope[name] = error
#add eval
scope['eval'] = Eval
scope['JSON'] = JSON
JS_BUILTINS = dict((k, v) for k, v in scope.items())
