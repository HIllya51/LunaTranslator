# The MIT License
#
# Copyright 2014, 2015 Piotr Dabkowski
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the 'Software'),
# to deal in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so, subject
# to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
#  OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
""" This module allows you to translate and execute Javascript in pure python.
    Basically its implementation of ECMAScript 5.1 in pure python.

    Use eval_js method to execute javascript code and get resulting python object (builtin if possible).

    EXAMPLE:
    >>> import js2py
    >>> add = js2py.eval_js('function add(a, b) {return a + b}')
    >>> add(1, 2) + 3
    6
    >>> add('1', 2, 3)
    u'12'
    >>> add.constructor
    function Function() { [python code] }


    Or use EvalJs to execute many javascript code fragments under same context - you would be able to get any
    variable from the context!

    >>> js = js2py.EvalJs()
    >>> js.execute('var a = 10; function f(x) {return x*x};')
    >>> js.f(9)
    81
    >>> js.a
    10

    Also you can use its console method to play with interactive javascript console.


    Use parse_js to parse (syntax tree is just like in esprima.js) and translate_js to trasnlate JavaScript.

    Finally, you can use pyimport statement from inside JS code to import and use python libraries.

    >>> js2py.eval_js('pyimport urllib; urllib.urlopen("https://www.google.com")')

    NOTE: This module is still not fully finished:

          Date and JSON builtin objects are not implemented
          Array prototype is not fully finished (will be soon)

    Other than that everything should work fine.

"""

__author__ = 'Piotr Dabkowski'
__all__ = [
    'EvalJs', 'translate_js', 'import_js', 'eval_js', 'parse_js',
    'translate_file', 'run_file', 'disable_pyimport', 'eval_js6',
    'translate_js6', 'PyJsException', 'get_file_contents',
    'write_file_contents', 'require'
]

from .base import PyJsException
from .evaljs import *
from .translators import parse as parse_js
from .node_import import require
