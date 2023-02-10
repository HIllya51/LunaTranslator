# this is based on jsarray.py

from ..base import *
try:
    import numpy
except:
    pass


@Js
def Uint8Array():
    TypedArray = (PyJsInt8Array, PyJsUint8Array, PyJsUint8ClampedArray,
                  PyJsInt16Array, PyJsUint16Array, PyJsInt32Array,
                  PyJsUint32Array, PyJsFloat32Array, PyJsFloat64Array)
    a = arguments[0]
    if isinstance(a, PyJsNumber):  # length
        length = a.to_uint32()
        if length != a.value:
            raise MakeError('RangeError', 'Invalid array length')
        temp = Js(numpy.full(length, 0, dtype=numpy.uint8))
        temp.put('length', a)
        return temp
    elif isinstance(a, PyJsString):  # object (string)
        temp = Js(numpy.array(list(a.value), dtype=numpy.uint8))
        temp.put('length', Js(len(list(a.value))))
        return temp
    elif isinstance(a, PyJsArray) or isinstance(a, TypedArray) or isinstance(
            a, PyJsArrayBuffer):  # object (Array, TypedArray)
        array = a.to_list()
        array = [(int(item.value) if item.value != None else 0)
                 for item in array]
        temp = Js(numpy.array(array, dtype=numpy.uint8))
        temp.put('length', Js(len(array)))
        return temp
    elif isinstance(a, PyObjectWrapper):  # object (ArrayBuffer, etc)
        if len(arguments) > 1:
            offset = int(arguments[1].value)
        else:
            offset = 0
        if len(arguments) > 2:
            length = int(arguments[2].value)
        else:
            length = int(len(a.obj) - offset)
        array = numpy.frombuffer(
            a.obj, dtype=numpy.uint8, count=length, offset=offset)
        temp = Js(array)
        temp.put('length', Js(length))
        temp.buff = array
        return temp
    temp = Js(numpy.full(0, 0, dtype=numpy.uint8))
    temp.put('length', Js(0))
    return temp


Uint8Array.create = Uint8Array
Uint8Array.own['length']['value'] = Js(3)

Uint8Array.define_own_property(
    'prototype', {
        'value': Uint8ArrayPrototype,
        'enumerable': False,
        'writable': False,
        'configurable': False
    })

Uint8ArrayPrototype.define_own_property(
    'constructor', {
        'value': Uint8Array,
        'enumerable': False,
        'writable': True,
        'configurable': True
    })

Uint8ArrayPrototype.define_own_property('BYTES_PER_ELEMENT', {
    'value': Js(1),
    'enumerable': False,
    'writable': False,
    'configurable': False
})
