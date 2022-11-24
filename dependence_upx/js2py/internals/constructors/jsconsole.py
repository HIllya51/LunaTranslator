from __future__ import unicode_literals

from js2py.internals.conversions import *
from js2py.internals.func_utils import *


class ConsoleMethods:
    def log(this, args):
        x = ' '.join(to_string(e) for e in args)
        print(x)
        return undefined
