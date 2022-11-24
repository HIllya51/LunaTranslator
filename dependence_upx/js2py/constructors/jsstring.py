from ..base import *
# python 3 support
import six
if six.PY3:
    unichr = chr


@Js
def fromCharCode():
    args = arguments.to_list()
    res = u''
    for e in args:
        res += unichr(e.to_uint16())
    return this.Js(res)


fromCharCode.own['length']['value'] = Js(1)

String.define_own_property(
    'fromCharCode', {
        'value': fromCharCode,
        'enumerable': False,
        'writable': True,
        'configurable': True
    })

String.define_own_property(
    'prototype', {
        'value': StringPrototype,
        'enumerable': False,
        'writable': False,
        'configurable': False
    })

StringPrototype.define_own_property('constructor', {
    'value': String,
    'enumerable': False,
    'writable': True,
    'configurable': True
})
