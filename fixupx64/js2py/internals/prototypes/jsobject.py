from __future__ import unicode_literals
from ..conversions import *
from ..func_utils import *


class ObjectPrototype:
    def toString(this, args):
        if type(this) == UNDEFINED_TYPE:
            return u'[object Undefined]'
        elif type(this) == NULL_TYPE:
            return u'[object Null]'
        return u'[object %s]' % GetClass(to_object(this, args.space))

    def valueOf(this, args):
        return to_object(this, args.space)

    def toLocaleString(this, args):
        o = to_object(this, args.space)
        toString = o.get(u'toString')
        if not is_callable(toString):
            raise MakeError('TypeError', 'toString of this is not callcable')
        else:
            return toString.call(this, args)

    def hasOwnProperty(this, args):
        prop = get_arg(args, 0)
        o = to_object(this, args.space)
        return o.get_own_property(to_string(prop)) is not None

    def isPrototypeOf(this, args):
        # a bit stupid specification because of object conversion that will cause invalid values for primitives
        # for example Object.prototype.isPrototypeOf.call((5).__proto__, 5) gives false
        obj = get_arg(args, 0)
        if not is_object(obj):
            return False
        o = to_object(this, args.space)
        while 1:
            obj = obj.prototype
            if obj is None or is_null(obj):
                return False
            if obj is o:
                return True

    def propertyIsEnumerable(this, args):
        prop = get_arg(args, 0)
        o = to_object(this, args.space)
        cand = o.own.get(to_string(prop))
        return cand is not None and cand.get('enumerable')
