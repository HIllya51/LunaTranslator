from __future__ import unicode_literals

from ..conversions import *
from ..func_utils import *


class BooleanPrototype:
    def toString(this, args):
        if GetClass(this) != 'Boolean':
            raise MakeError('TypeError',
                            'Boolean.prototype.toString is not generic')
        if is_object(this):
            this = this.value
        return u'true' if this else u'false'

    def valueOf(this, args):
        if GetClass(this) != 'Boolean':
            raise MakeError('TypeError',
                            'Boolean.prototype.valueOf is not generic')
        if is_object(this):
            this = this.value
        return this
