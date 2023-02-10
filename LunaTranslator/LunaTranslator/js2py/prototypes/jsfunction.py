# python 3 support
import six
if six.PY3:
    basestring = str
    long = int
    xrange = range
    unicode = str


class FunctionPrototype:
    def toString():
        if not this.is_callable():
            raise TypeError('toString is not generic!')
        args = ', '.join(this.code.__code__.co_varnames[:this.argcount])
        return 'function %s(%s) ' % (this.func_name, args) + this.source

    def call():
        arguments_ = arguments
        if not len(arguments):
            obj = this.Js(None)
        else:
            obj = arguments[0]
        if len(arguments) <= 1:
            args = ()
        else:
            args = tuple([arguments_[e] for e in xrange(1, len(arguments_))])
        return this.call(obj, args)

    def apply():
        if not len(arguments):
            obj = this.Js(None)
        else:
            obj = arguments[0]
        if len(arguments) <= 1:
            args = ()
        else:
            appl = arguments[1]
            args = tuple([appl[e] for e in xrange(len(appl))])
        return this.call(obj, args)

    def bind(thisArg):
        arguments_ = arguments
        target = this
        if not target.is_callable():
            raise this.MakeError(
                'Object must be callable in order to be used with bind method')
        if len(arguments) <= 1:
            args = ()
        else:
            args = tuple([arguments_[e] for e in xrange(1, len(arguments_))])
        return this.PyJsBoundFunction(target, thisArg, args)
