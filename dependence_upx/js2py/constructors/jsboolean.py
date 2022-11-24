from ..base import *

BooleanPrototype.define_own_property('constructor', {
    'value': Boolean,
    'enumerable': False,
    'writable': True,
    'configurable': True
})

Boolean.define_own_property(
    'prototype', {
        'value': BooleanPrototype,
        'enumerable': False,
        'writable': False,
        'configurable': False
    })
