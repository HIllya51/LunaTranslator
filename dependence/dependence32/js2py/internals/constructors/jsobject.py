from __future__ import unicode_literals
from ..conversions import *
from ..func_utils import *
from ..base import is_data_descriptor
import six


def Object(this, args):
    val = get_arg(args, 0)
    if is_null(val) or is_undefined(val):
        return args.space.NewObject()
    return to_object(val, args.space)


def ObjectCreate(args, space):
    if len(args):
        val = get_arg(args, 0)
        if is_object(val):
            #  Implementation dependent, but my will simply return :)
            return val
        elif type(val) in (NUMBER_TYPE, STRING_TYPE, BOOLEAN_TYPE):
            return to_object(val, space)
    return space.NewObject()


class ObjectMethods:
    def getPrototypeOf(this, args):
        obj = get_arg(args, 0)
        if not is_object(obj):
            raise MakeError('TypeError',
                            'Object.getPrototypeOf called on non-object')
        return null if obj.prototype is None else obj.prototype

    def getOwnPropertyDescriptor(this, args):
        obj = get_arg(args, 0)
        prop = get_arg(args, 1)
        if not is_object(obj):
            raise MakeError(
                'TypeError',
                'Object.getOwnPropertyDescriptor called on non-object')
        desc = obj.own.get(to_string(prop))
        return convert_to_js_type(desc, args.space)

    def getOwnPropertyNames(this, args):
        obj = get_arg(args, 0)
        if not is_object(obj):
            raise MakeError(
                'TypeError',
                'Object.getOwnPropertyDescriptor called on non-object')
        return args.space.ConstructArray(obj.own.keys())

    def create(this, args):
        obj = get_arg(args, 0)
        if not (is_object(obj) or is_null(obj)):
            raise MakeError('TypeError',
                            'Object prototype may only be an Object or null')
        temp = args.space.NewObject()
        temp.prototype = None if is_null(obj) else obj
        if len(args) > 1 and not is_undefined(args[1]):
            if six.PY2:
                args.tup = (args[1], )
                ObjectMethods.defineProperties.__func__(temp, args)
            else:
                args.tup = (args[1], )
                ObjectMethods.defineProperties(temp, args)
        return temp

    def defineProperty(this, args):
        obj = get_arg(args, 0)
        prop = get_arg(args, 1)
        attrs = get_arg(args, 2)
        if not is_object(obj):
            raise MakeError('TypeError',
                            'Object.defineProperty called on non-object')
        name = to_string(prop)
        if not obj.define_own_property(name, ToPropertyDescriptor(attrs),
                                       False):
            raise MakeError('TypeError', 'Cannot redefine property: %s' % name)
        return obj

    def defineProperties(this, args):
        obj = get_arg(args, 0)
        properties = get_arg(args, 1)
        if not is_object(obj):
            raise MakeError('TypeError',
                            'Object.defineProperties called on non-object')
        props = to_object(properties, args.space)
        for k, v in props.own.items():
            if not v.get('enumerable'):
                continue
            desc = ToPropertyDescriptor(props.get(unicode(k)))
            if not obj.define_own_property(unicode(k), desc, False):
                raise MakeError('TypeError',
                                'Failed to define own property: %s' % k)
        return obj

    def seal(this, args):
        obj = get_arg(args, 0)
        if not is_object(obj):
            raise MakeError('TypeError', 'Object.seal called on non-object')
        for desc in obj.own.values():
            desc['configurable'] = False
        obj.extensible = False
        return obj

    def freeze(this, args):
        obj = get_arg(args, 0)
        if not is_object(obj):
            raise MakeError('TypeError', 'Object.freeze called on non-object')
        for desc in obj.own.values():
            desc['configurable'] = False
            if is_data_descriptor(desc):
                desc['writable'] = False
        obj.extensible = False
        return obj

    def preventExtensions(this, args):
        obj = get_arg(args, 0)
        if not is_object(obj):
            raise MakeError('TypeError',
                            'Object.preventExtensions on non-object')
        obj.extensible = False
        return obj

    def isSealed(this, args):
        obj = get_arg(args, 0)
        if not is_object(obj):
            raise MakeError('TypeError',
                            'Object.isSealed called on non-object')
        if obj.extensible:
            return False
        for desc in obj.own.values():
            if desc.get('configurable'):
                return False
        return True

    def isFrozen(this, args):
        obj = get_arg(args, 0)
        if not is_object(obj):
            raise MakeError('TypeError',
                            'Object.isFrozen called on non-object')
        if obj.extensible:
            return False
        for desc in obj.own.values():
            if desc.get('configurable'):
                return False
            if is_data_descriptor(desc) and desc.get('writable'):
                return False
        return True

    def isExtensible(this, args):
        obj = get_arg(args, 0)
        if not is_object(obj):
            raise MakeError('TypeError',
                            'Object.isExtensible called on non-object')
        return obj.extensible

    def keys(this, args):
        obj = get_arg(args, 0)
        if not is_object(obj):
            raise MakeError('TypeError', 'Object.keys called on non-object')
        return args.space.ConstructArray([
            unicode(e) for e, d in six.iteritems(obj.own)
            if d.get('enumerable')
        ])


# some utility functions:


def ToPropertyDescriptor(obj):  # page 38 (50 absolute)
    if not is_object(obj):
        raise MakeError('TypeError',
                        'Can\'t convert non-object to property descriptor')
    desc = {}
    if obj.has_property('enumerable'):
        desc['enumerable'] = to_boolean(obj.get('enumerable'))
    if obj.has_property('configurable'):
        desc['configurable'] = to_boolean(obj.get('configurable'))
    if obj.has_property('value'):
        desc['value'] = obj.get('value')
    if obj.has_property('writable'):
        desc['writable'] = to_boolean(obj.get('writable'))
    if obj.has_property('get'):
        cand = obj.get('get')
        if not (is_undefined(cand) or is_callable(cand)):
            raise MakeError(
                'TypeError',
                'Invalid getter (it has to be a function or undefined)')
        desc['get'] = cand
    if obj.has_property('set'):
        cand = obj.get('set')
        if not (is_undefined(cand) or is_callable(cand)):
            raise MakeError(
                'TypeError',
                'Invalid setter (it has to be a function or undefined)')
        desc['set'] = cand
    if ('get' in desc or 'set' in desc) and ('value' in desc
                                             or 'writable' in desc):
        raise MakeError(
            'TypeError',
            'Invalid property.  A property cannot both have accessors and be writable or have a value.'
        )
    return desc
