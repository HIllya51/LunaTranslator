from ..base import *


@Js
def Array():
    if len(arguments) == 0 or len(arguments) > 1:
        return arguments.to_list()
    a = arguments[0]
    if isinstance(a, PyJsNumber):
        length = a.to_uint32()
        if length != a.value:
            raise MakeError('RangeError', 'Invalid array length')
        temp = Js([])
        temp.put('length', a)
        return temp
    return [a]


Array.create = Array
Array.own['length']['value'] = Js(1)


@Js
def isArray(arg):
    return arg.Class == 'Array'


Array.define_own_property('isArray', {
    'value': isArray,
    'enumerable': False,
    'writable': True,
    'configurable': True
})

Array.define_own_property(
    'prototype', {
        'value': ArrayPrototype,
        'enumerable': False,
        'writable': False,
        'configurable': False
    })

ArrayPrototype.define_own_property('constructor', {
    'value': Array,
    'enumerable': False,
    'writable': True,
    'configurable': True
})
