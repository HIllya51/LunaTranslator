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

__all__ = [
    'PyJsParser', 'Node', 'WrappingNode', 'node_to_dict', 'parse',
    'translate_js', 'translate', 'syntax_tree_translate', 'DEFAULT_HEADER'
]
__author__ = 'Piotr Dabkowski'
__version__ = '2.2.0'
from pyjsparser import PyJsParser
from .translator import translate_js, trasnlate, syntax_tree_translate, DEFAULT_HEADER


def parse(javascript_code):
    """Returns syntax tree of javascript_code.

    Syntax tree has the same structure as syntax tree produced by esprima.js

       Same as PyJsParser().parse  For your convenience :) """
    p = PyJsParser()
    return p.parse(javascript_code)
