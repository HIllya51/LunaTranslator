# this is based on jsarray.py

from ..base import *
try:
    import numpy
except:
    pass


@Js
def Int32Array():
    TypedArray = (PyJsInt8Array, PyJsUint8Array, PyJsUint8ClampedArray,
                  PyJsInt16Array, PyJsUint16Array, PyJsInt32Array,
                  PyJsUint32Array, PyJsFloat32Array, PyJsFloat64Array)
    a = arguments[0]
    if isinstance(a, PyJsNumber):  # length
        length = a.to_uint32()
        if length != a.value:
            raise MakeError('RangeError', 'Invalid array length')
        temp = Js(numpy.full(length, 0, dtype=numpy.int32))
        temp.put('length', a)
        return temp
    elif isinstance(a, PyJsString):  # object (string)
        temp = Js(numpy.array(list(a.value), dtype=numpy.int32))
        temp.put('length', Js(len(list(a.value))))
        return temp
    elif isinstance(a, PyJsArray) or isinstance(a, TypedArray) or isinstance(
            a, PyJsArrayBuffer):  # object (Array, TypedArray)
        array = a.to_list()
        array = [(int(item.value) if item.value != None else 0)
                 for item in array]
        temp = Js(numpy.array(array, dtype=numpy.int32))
        temp.put('length', Js(len(array)))
        return temp
    elif isinstance(a, PyObjectWrapper):  # object (ArrayBuffer, etc)
        if len(a.obj) % 4 != 0:
            raise MakeError(
                'RangeError',
                'Byte length of Int32Array should be a multiple of 4')
        if len(arguments) > 1:
            offset = int(arguments[1].value)
            if offset % 4 != 0:
                raise MakeError(
                    'RangeError',
                    'Start offset of Int32Array should be a multiple of 4')
        else:
            offset = 0
        if len(arguments) > 2:
            length = int(arguments[2].value)
        else:
            length = int((len(a.obj) - offset) / 4)
        array = numpy.frombuffer(
            a.obj, dtype=numpy.int32, count=length, offset=offset)
        temp = Js(array)
        temp.put('length', Js(length))
        temp.buff = array
        return temp
    temp = Js(numpy.full(0, 0, dtype=numpy.int32))
    temp.put('length', Js(0))
    return temp


Int32Array.create = Int32Array
Int32Array.own['length']['value'] = Js(3)

Int32Array.define_own_property(
    'prototype', {
        'value': Int32ArrayPrototype,
        'enumerable': False,
        'writable': False,
        'configurable': False
    })

Int32ArrayPrototype.define_own_property(
    'constructor', {
        'value': Int32Array,
        'enumerable': False,
        'writable': True,
        'configurable': True
    })

Int32ArrayPrototype.define_own_property('BYTES_PER_ELEMENT', {
    'value': Js(4),
    'enumerable': False,
    'writable': False,
    'configurable': False
})
