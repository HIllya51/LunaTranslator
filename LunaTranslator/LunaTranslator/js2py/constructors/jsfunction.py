from ..base import *
try:
    from ..translators.translator import translate_js
except:
    pass


@Js
def Function():
    # convert arguments to python list of strings
    a = [e.to_string().value for e in arguments.to_list()]
    body = ';'
    args = ()
    if len(a):
        body = '%s;' % a[-1]
        args = a[:-1]
    # translate this function to js inline function
    js_func = '(function (%s) {%s})' % (','.join(args), body)
    # now translate js inline to python function
    py_func = translate_js(js_func, '')
    # add set func scope to global scope
    # a but messy solution but works :)
    globals()['var'] = PyJs.GlobalObject
    # define py function and return it
    temp = executor(py_func, globals())
    temp.source = '{%s}' % body
    temp.func_name = 'anonymous'
    return temp


def executor(f, glob):
    exec (f, globals())
    return globals()['PyJs_anonymous_0_']


#new statement simply calls Function
Function.create = Function

#set constructor property inside FunctionPrototype

fill_in_props(FunctionPrototype, {'constructor': Function}, default_attrs)

#attach prototype to Function constructor
Function.define_own_property(
    'prototype', {
        'value': FunctionPrototype,
        'enumerable': False,
        'writable': False,
        'configurable': False
    })
#Fix Function length (its 0 and should be 1)
Function.own['length']['value'] = Js(1)
