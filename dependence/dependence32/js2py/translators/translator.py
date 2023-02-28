import pyjsparser
import pyjsparser.parser
from . import translating_nodes

import hashlib
import re

# Enable Js2Py exceptions and pyimport in parser
pyjsparser.parser.ENABLE_PYIMPORT = True

# the re below is how we'll recognise numeric constants.
# it finds any 'simple numeric that is not preceded with an alphanumeric character
# the numeric can be a float (so a dot is found) but
# it does not recognise notation such as 123e5, 0xFF, infinity or NaN
CP_NUMERIC_RE = re.compile(r'(?<![a-zA-Z0-9_"\'])([0-9\.]+)')
CP_NUMERIC_PLACEHOLDER = '__PyJsNUM_%i_PyJsNUM__'
CP_NUMERIC_PLACEHOLDER_REVERSE_RE = re.compile(
    CP_NUMERIC_PLACEHOLDER.replace('%i', r'([0-9\.]+)'))

# the re below is how we'll recognise string constants
# it finds a ' or ", then reads until the next matching ' or "
# this re only services simple cases, it can not be used when
# there are escaped quotes in the expression

#CP_STRING_1 = re.compile(r'(["\'])(.*?)\1') # this is how we'll recognise string constants

CP_STRING = '"([^\\\\"]+|\\\\([bfnrtv\'"\\\\]|[0-3]?[0-7]{1,2}|x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}))*"|\'([^\\\\\']+|\\\\([bfnrtv\'"\\\\]|[0-3]?[0-7]{1,2}|x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}))*\''
CP_STRING_RE = re.compile(
    CP_STRING)  # this is how we'll recognise string constants
CP_STRING_PLACEHOLDER = '__PyJsSTR_%i_PyJsSTR__'
CP_STRING_PLACEHOLDER_REVERSE_RE = re.compile(
    CP_STRING_PLACEHOLDER.replace('%i', r'([0-9\.]+)'))

cache = {}

# This crap is still needed but I removed it for speed reasons. Have to think ofa  better idea
# import js2py.pyjs, sys
# # Redefine builtin objects... Do you have a better idea?
# for m in list(sys.modules):
# 	if m.startswith('js2py'):
# 		del sys.modules[m]
# del js2py.pyjs
# del js2py

DEFAULT_HEADER = u'''from js2py.pyjs import *
# setting scope
var = Scope( JS_BUILTINS )
set_global_object(var)

# Code follows:
'''


def dbg(x):
    """does nothing, legacy dummy function"""
    return ''

# Another way of doing that would be with my auto esprima translation but its much slower:
# parsed = esprima.parse(js).to_dict()
def pyjsparser_parse_fn(code):
    parser = pyjsparser.PyJsParser()
    return parser.parse(code)

def translate_js(js, HEADER=DEFAULT_HEADER, use_compilation_plan=False, parse_fn=pyjsparser_parse_fn):
    """js has to be a javascript source code.
       returns equivalent python code."""
    if use_compilation_plan and not '//' in js and not '/*' in js:
        return translate_js_with_compilation_plan(js, HEADER=HEADER)

    parsed = parse_fn(js)
    translating_nodes.clean_stacks()
    return HEADER + translating_nodes.trans(
        parsed)  # syntax tree to python code


class match_unumerator(object):
    """This class ise used """
    matchcount = -1

    def __init__(self, placeholder_mask):
        self.placeholder_mask = placeholder_mask
        self.matches = []

    def __call__(self, match):
        self.matchcount += 1
        self.matches.append(match.group(0))
        return self.placeholder_mask % self.matchcount

    def __repr__(self):
        return '\n'.join(self.placeholder_mask % counter + '=' + match
                         for counter, match in enumerate(self.matches))

    def wrap_up(self, output):
        for counter, value in enumerate(self.matches):
            output = output.replace(
                "u'" + self.placeholder_mask % (counter) + "'", value, 1)
        return output


def get_compilation_plan(js):
    match_increaser_str = match_unumerator(CP_STRING_PLACEHOLDER)
    compilation_plan = re.sub(CP_STRING, match_increaser_str, js)

    match_increaser_num = match_unumerator(CP_NUMERIC_PLACEHOLDER)
    compilation_plan = re.sub(CP_NUMERIC_RE, match_increaser_num,
                              compilation_plan)
    # now put quotes, note that just patching string replaces is somewhat faster than
    # using another re:
    compilation_plan = compilation_plan.replace(
        '__PyJsNUM_', '"__PyJsNUM_').replace('_PyJsNUM__', '_PyJsNUM__"')
    compilation_plan = compilation_plan.replace(
        '__PyJsSTR_', '"__PyJsSTR_').replace('_PyJsSTR__', '_PyJsSTR__"')

    return match_increaser_str, match_increaser_num, compilation_plan


def translate_js_with_compilation_plan(js, HEADER=DEFAULT_HEADER):
    """js has to be a javascript source code.
       returns equivalent python code.

       compile plans only work with the following restrictions:
       - only enabled for oneliner expressions
       - when there are comments in the js code string substitution is disabled
       - when there nested escaped quotes string substitution is disabled, so

       cacheable:
       Q1 == 1 && name == 'harry'

       not cacheable:
       Q1 == 1 && name == 'harry' // some comment

       not cacheable:
       Q1 == 1 && name == 'o\'Reilly'

       not cacheable:
       Q1 == 1 && name /* some comment */ == 'o\'Reilly'
       """

    match_increaser_str, match_increaser_num, compilation_plan = get_compilation_plan(
        js)

    cp_hash = hashlib.md5(compilation_plan.encode('utf-8')).digest()
    try:
        python_code = cache[cp_hash]['proto_python_code']
    except:
        parser = pyjsparser.PyJsParser()
        parsed = parser.parse(compilation_plan)  # js to esprima syntax tree
        # Another way of doing that would be with my auto esprima translation but its much slower and causes import problems:
        # parsed = esprima.parse(js).to_dict()
        translating_nodes.clean_stacks()
        python_code = translating_nodes.trans(
            parsed)  # syntax tree to python code
        cache[cp_hash] = {
            'compilation_plan': compilation_plan,
            'proto_python_code': python_code,
        }

    python_code = match_increaser_str.wrap_up(python_code)
    python_code = match_increaser_num.wrap_up(python_code)

    return HEADER + python_code


def trasnlate(js, HEADER=DEFAULT_HEADER):
    """js has to be a javascript source code.
       returns equivalent python code.

       Equivalent to translate_js"""
    return translate_js(js, HEADER)


syntax_tree_translate = translating_nodes.trans

if __name__ == '__main__':
    PROFILE = False
    import js2py
    import codecs

    def main():
        with codecs.open("esprima.js", "r", "utf-8") as f:
            d = f.read()
            r = js2py.translate_js(d)

            with open('res.py', 'wb') as f2:
                f2.write(r)
            exec (r, {})

    if PROFILE:
        import cProfile
        cProfile.run('main()', sort='tottime')
    else:
        main()
