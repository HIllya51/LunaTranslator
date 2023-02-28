# this is based on jsarray.py

from ..base import *
try:
    import numpy
except:
    pass


@Js
def Uint32Array():
    TypedArray = (PyJsInt8Array, PyJsUint8Array, PyJsUint8ClampedArray,
                  PyJsInt16Array, PyJsUint16Array, PyJsInt32Array,
                  PyJsUint32Array, PyJsFloat32Array, PyJsFloat64Array)
    a = arguments[0]
    if isinstance(a, PyJsNumber):  # length
        length = a.to_uint32()
        if length != a.value:
            raise MakeError('RangeError', 'Invalid array length')
        temp = Js(numpy.full(length, 0, dtype=numpy.uint32))
        temp.put('length', a)
        return temp
    elif isinstance(a, PyJsString):  # object (string)
        temp = Js(numpy.array(list(a.value), dtype=numpy.uint32))
        temp.put('length', Js(len(list(a.value))))
        return temp
    elif isinstance(a, PyJsArray) or isinstance(a, TypedArray) or isinstance(
            a, PyJsArrayBuffer):  # object (Array, TypedArray)
        array = a.to_list()
        array = [(int(item.value) if item.value != None else 0)
                 for item in array]
        if len(arguments) > 1:
            offset = int(arguments[1].value)
        else:
            offset = 0
        if len(arguments) > 2:
            length = int(arguments[2].value)
        else:
            length = len(array) - offset
        temp = Js(
            numpy.array(array[offset:offset + length], dtype=numpy.uint32))
        temp.put('length', Js(length))
        return temp
    elif isinstance(a, PyObjectWrapper):  # object (ArrayBuffer, etc)
        if len(a.obj) % 4 != 0:
            raise MakeError(
                'RangeError',
                'Byte length of Uint32Array should be a multiple of 4')
        if len(arguments) > 1:
            offset = int(arguments[1].value)
            if offset % 4 != 0:
                raise MakeError(
                    'RangeError',
                    'Start offset of Uint32Array should be a multiple of 4')
        else:
            offset = 0
        if len(arguments) > 2:
            length = int(arguments[2].value)
        else:
            length = int((len(a.obj) - offset) / 4)
        temp = Js(
            numpy.frombuffer(
                a.obj, dtype=numpy.uint32, count=length, offset=offset))
        temp.put('length', Js(length))
        return temp
    temp = Js(numpy.full(0, 0, dtype=numpy.uint32))
    temp.put('length', Js(0))
    return temp


Uint32Array.create = Uint32Array
Uint32Array.own['length']['value'] = Js(3)

Uint32Array.define_own_property(
    'prototype', {
        'value': Uint32ArrayPrototype,
        'enumerable': False,
        'writable': False,
        'configurable': False
    })

Uint32ArrayPrototype.define_own_property(
    'constructor', {
        'value': Uint32Array,
        'enumerable': False,
        'writable': True,
        'configurable': True
    })

Uint32ArrayPrototype.define_own_property('BYTES_PER_ELEMENT', {
    'value': Js(4),
    'enumerable': False,
    'writable': False,
    'configurable': False
})
