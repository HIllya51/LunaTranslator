from ..base import *

CONSTS = {
    'prototype': NumberPrototype,
    'MAX_VALUE': 1.7976931348623157e308,
    'MIN_VALUE': 5.0e-324,
    'NaN': NaN,
    'NEGATIVE_INFINITY': float('-inf'),
    'POSITIVE_INFINITY': float('inf')
}

fill_in_props(Number, CONSTS, {
    'enumerable': False,
    'writable': False,
    'configurable': False
})

NumberPrototype.define_own_property('constructor', {
    'value': Number,
    'enumerable': False,
    'writable': True,
    'configurable': True
})
