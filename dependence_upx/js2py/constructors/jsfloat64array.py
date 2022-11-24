# this is based on jsarray.py

from ..base import *
try:
    import numpy
except:
    pass


@Js
def Float64Array():
    TypedArray = (PyJsInt8Array, PyJsUint8Array, PyJsUint8ClampedArray,
                  PyJsInt16Array, PyJsUint16Array, PyJsInt32Array,
                  PyJsUint32Array, PyJsFloat32Array, PyJsFloat64Array)
    a = arguments[0]
    if isinstance(a, PyJsNumber):  # length
        length = a.to_uint32()
        if length != a.value:
            raise MakeError('RangeError', 'Invalid array length')
        temp = Js(numpy.full(length, 0, dtype=numpy.float64))
        temp.put('length', a)
        return temp
    elif isinstance(a, PyJsString):  # object (string)
        temp = Js(numpy.array(list(a.value), dtype=numpy.float64))
        temp.put('length', Js(len(list(a.value))))
        return temp
    elif isinstance(a, PyJsArray) or isinstance(a, TypedArray) or isinstance(
            a, PyJsArrayBuffer):  # object (Array, TypedArray)
        array = a.to_list()
        array = [(int(item.value) if item.value != None else 0)
                 for item in array]
        temp = Js(numpy.array(array, dtype=numpy.float64))
        temp.put('length', Js(len(array)))
        return temp
    elif isinstance(a, PyObjectWrapper):  # object (ArrayBuffer, etc)
        if len(a.obj) % 8 != 0:
            raise MakeError(
                'RangeError',
                'Byte length of Float64Array should be a multiple of 8')
        if len(arguments) > 1:
            offset = int(arguments[1].value)
            if offset % 8 != 0:
                raise MakeError(
                    'RangeError',
                    'Start offset of Float64Array should be a multiple of 8')
        else:
            offset = 0
        if len(arguments) > 2:
            length = int(arguments[2].value)
        else:
            length = int((len(a.obj) - offset) / 8)
        array = numpy.frombuffer(
            a.obj, dtype=numpy.float64, count=length, offset=offset)
        temp = Js(array)
        temp.put('length', Js(length))
        temp.buff = array
        return temp
    temp = Js(numpy.full(0, 0, dtype=numpy.float64))
    temp.put('length', Js(0))
    return temp


Float64Array.create = Float64Array
Float64Array.own['length']['value'] = Js(3)

Float64Array.define_own_property(
    'prototype', {
        'value': Float64ArrayPrototype,
        'enumerable': False,
        'writable': False,
        'configurable': False
    })

Float64ArrayPrototype.define_own_property(
    'constructor', {
        'value': Float64Array,
        'enumerable': False,
        'writable': True,
        'configurable': True
    })

Float64ArrayPrototype.define_own_property('BYTES_PER_ELEMENT', {
    'value': Js(8),
    'enumerable': False,
    'writable': False,
    'configurable': False
})
