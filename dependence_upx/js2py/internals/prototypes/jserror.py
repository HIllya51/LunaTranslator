from __future__ import unicode_literals
from ..conversions import *
from ..func_utils import *


class ErrorPrototype:
    def toString(this, args):
        if Type(this) != 'Object':
            raise MakeError('TypeError',
                            'Error.prototype.toString called on non-object')
        name = this.get('name')
        name = u'Error' if is_undefined(name) else to_string(name)
        msg = this.get('message')
        msg = '' if is_undefined(msg) else to_string(msg)
        return name + (name and msg and ': ') + msg
