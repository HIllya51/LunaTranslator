from __future__ import unicode_literals

from ..conversions import *
from ..func_utils import *

# python 3 support
import six
if six.PY3:
    basestring = str
    long = int
    xrange = range
    unicode = str

# todo fix apply and bind


class FunctionPrototype:
    def toString(this, args):
        if not is_callable(this):
            raise MakeError('TypeError',
                            'Function.prototype.toString is not generic')

        args = u', '.join(map(unicode, this.params))
        return u'function %s(%s) { [native code] }' % (this.name if this.name
                                                       else u'', args)

    def call(this, args):
        if not is_callable(this):
            raise MakeError('TypeError',
                            'Function.prototype.call is not generic')
        _this = get_arg(args, 0)
        _args = tuple(args)[1:]
        return this.call(_this, _args)

    def apply(this, args):
        if not is_callable(this):
            raise MakeError('TypeError',
                            'Function.prototype.apply is not generic')
        _args = get_arg(args, 1)
        if not is_object(_args):
            raise MakeError(
                'TypeError',
                'argList argument to Function.prototype.apply must an Object')
        _this = get_arg(args, 0)
        return this.call(_this, js_array_to_tuple(_args))

    def bind(this, args):
        if not is_callable(this):
            raise MakeError('TypeError',
                            'Function.prototype.bind is not generic')
        bound_this = get_arg(args, 0)
        bound_args = tuple(args)[1:]

        def bound(dummy_this, extra_args):
            return this.call(bound_this, bound_args + tuple(extra_args))

        js_bound = args.space.NewFunction(bound, this.ctx, (), u'', False, ())
        js_bound.put(u'length',
                     float(max(len(this.params) - len(bound_args), 0.)))
        js_bound.put(u'name', u'boundFunc')
        return js_bound
