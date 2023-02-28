from ..base import *

RegExpPrototype.define_own_property('constructor', {
    'value': RegExp,
    'enumerable': False,
    'writable': True,
    'configurable': True
})

RegExp.define_own_property(
    'prototype', {
        'value': RegExpPrototype,
        'enumerable': False,
        'writable': False,
        'configurable': False
    })
