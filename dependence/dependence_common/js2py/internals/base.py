from __future__ import unicode_literals
import re

import datetime

from .desc import *
from .simplex import *
from .conversions import *

from pyjsparser import PyJsParser

import six
if six.PY2:
    from itertools import izip
else:
    izip = zip




def Type(obj):
    return obj.TYPE


# 8.6.2
class PyJs(object):
    TYPE = 'Object'
    IS_CONSTRUCTOR = False

    prototype = None
    Class = None
    extensible = True
    value = None

    own = {}

    def get_member(self, unconverted_prop):
        return self.get(to_string(unconverted_prop))

    def put_member(self, unconverted_prop, val):
        return self.put(to_string(unconverted_prop), val)

    def get(self, prop):
        assert type(prop) == unicode
        cand = self.get_property(prop)
        if cand is None:
            return undefined
        if is_data_descriptor(cand):
            return cand['value']
        if is_undefined(cand['get']):
            return undefined
        return cand['get'].call(self)

    def get_own_property(self, prop):
        assert type(prop) == unicode
        # takes py returns py
        return self.own.get(prop)

    def get_property(self, prop):
        assert type(prop) == unicode
        # take py returns py
        cand = self.get_own_property(prop)
        if cand:
            return cand
        if self.prototype is not None:
            return self.prototype.get_property(prop)

    def put(self, prop, val, throw=False):
        assert type(prop) == unicode
        # takes py, returns none
        if not self.can_put(prop):
            if throw:
                raise MakeError('TypeError', 'Could not define own property')
            return
        own_desc = self.get_own_property(prop)
        if is_data_descriptor(own_desc):
            self.own[prop]['value'] = val
            return
        desc = self.get_property(prop)
        if is_accessor_descriptor(desc):
            desc['set'].call(
                self, (val, ))  # calling setter on own or inherited element
        else:  # new property
            self.own[prop] = {
                'value': val,
                'writable': True,
                'configurable': True,
                'enumerable': True
            }

    def can_put(self, prop):  # to check
        assert type(prop) == unicode, type(prop)
        # takes py returns py
        desc = self.get_own_property(prop)
        if desc:  # if we have this property
            if is_accessor_descriptor(desc):
                return is_callable(
                    desc['set'])  # Check if setter method is defined
            else:  # data desc
                return desc['writable']
        if self.prototype is None:
            return self.extensible
        inherited = self.prototype.get_property(prop)
        if inherited is None:
            return self.extensible
        if is_accessor_descriptor(inherited):
            return not is_undefined(inherited['set'])
        elif self.extensible:
            return inherited['writable']  # weird...
        return False

    def has_property(self, prop):
        assert type(prop) == unicode
        # takes py returns Py
        return self.get_property(prop) is not None

    def delete(self, prop, throw=False):
        assert type(prop) == unicode
        # takes py, returns py
        desc = self.get_own_property(prop)
        if desc is None:
            return True
        if desc['configurable']:
            del self.own[prop]
            return True
        if throw:
            raise MakeError('TypeError', 'Could not define own property')
        return False

    def default_value(self, hint=None):
        order = ('valueOf', 'toString')
        if hint == 'String' or (hint is None and self.Class == 'Date'):
            order = ('toString', 'valueOf')
        for meth_name in order:
            method = self.get(meth_name)
            if method is not None and is_callable(method):
                cand = method.call(self, ())
                if is_primitive(cand):
                    return cand
        raise MakeError('TypeError',
                        'Cannot convert object to primitive value')

    def define_own_property(
            self, prop, desc,
            throw):  # Internal use only. External through Object
        assert type(prop) == unicode
        # takes Py, returns Py
        # prop must be a Py string. Desc is either a descriptor or accessor.
        # Messy method -  raw translation from Ecma spec to prevent any bugs. # todo check this
        current = self.get_own_property(prop)

        extensible = self.extensible
        if not current:  # We are creating a new OWN property
            if not extensible:
                if throw:
                    raise MakeError('TypeError',
                                    'Could not define own property')
                return False
            # extensible must be True
            if is_data_descriptor(desc) or is_generic_descriptor(desc):
                DEFAULT_DATA_DESC = {
                    'value': undefined,  # undefined
                    'writable': False,
                    'enumerable': False,
                    'configurable': False
                }
                DEFAULT_DATA_DESC.update(desc)
                self.own[prop] = DEFAULT_DATA_DESC
            else:
                DEFAULT_ACCESSOR_DESC = {
                    'get': undefined,  # undefined
                    'set': undefined,  # undefined
                    'enumerable': False,
                    'configurable': False
                }
                DEFAULT_ACCESSOR_DESC.update(desc)
                self.own[prop] = DEFAULT_ACCESSOR_DESC
            return True
        # therefore current exists!
        if not desc or desc == current:  # We don't need to change anything.
            return True
        configurable = current['configurable']
        if not configurable:  # Prevent changing params
            if desc.get('configurable'):
                if throw:
                    raise MakeError('TypeError',
                                    'Could not define own property')
                return False
            if 'enumerable' in desc and desc['enumerable'] != current[
                    'enumerable']:
                if throw:
                    raise MakeError('TypeError',
                                    'Could not define own property')
                return False
        if is_generic_descriptor(desc):
            pass
        elif is_data_descriptor(current) != is_data_descriptor(desc):
            # we want to change the current type of property
            if not configurable:
                if throw:
                    raise MakeError('TypeError',
                                    'Could not define own property')
                return False
            if is_data_descriptor(current):  # from data to setter
                del current['value']
                del current['writable']
                current['set'] = undefined  # undefined
                current['get'] = undefined  # undefined
            else:  # from setter to data
                del current['set']
                del current['get']
                current['value'] = undefined  # undefined
                current['writable'] = False
        elif is_data_descriptor(current) and is_data_descriptor(desc):
            if not configurable:
                if not current['writable'] and desc.get('writable'):
                    if throw:
                        raise MakeError('TypeError',
                                        'Could not define own property')
                    return False
            if not current['writable'] and 'value' in desc and current[
                    'value'] != desc['value']:
                if throw:
                    raise MakeError('TypeError',
                                    'Could not define own property')
                return False
        elif is_accessor_descriptor(current) and is_accessor_descriptor(desc):
            if not configurable:
                if 'set' in desc and desc['set'] != current['set']:
                    if throw:
                        raise MakeError('TypeError',
                                        'Could not define own property')
                    return False
                if 'get' in desc and desc['get'] != current['get']:
                    if throw:
                        raise MakeError('TypeError',
                                        'Could not define own property')
                    return False
        current.update(desc)
        return True

    def create(self, args, space):
        '''Generally not a constructor, raise an error'''
        raise MakeError('TypeError', '%s is not a constructor' % self.Class)


def get_member(
        self, prop, space
):  # general member getter, prop has to be unconverted prop. it is it can be any value
    typ = type(self)
    if typ not in PRIMITIVES:  # most likely getter for object
        return self.get_member(
            prop
        )  # <- object can implement this to support faster prop getting. ex array.
    elif typ == unicode:  # then probably a String
        if type(prop) == float and is_finite(prop):
            index = int(prop)
            if index == prop and 0 <= index < len(self):
                return self[index]
        s_prop = to_string(prop)
        if s_prop == 'length':
            return float(len(self))
        elif s_prop.isdigit():
            index = int(s_prop)
            if 0 <= index < len(self):
                return self[index]
        # use standard string prototype
        return space.StringPrototype.get(s_prop)
        # maybe an index
    elif typ == float:
        # use standard number prototype
        return space.NumberPrototype.get(to_string(prop))
    elif typ == bool:
        return space.BooleanPrototype.get(to_string(prop))
    elif typ is UNDEFINED_TYPE:
        raise MakeError('TypeError',
                        "Cannot read property '%s' of undefined" % prop)
    elif typ is NULL_TYPE:
        raise MakeError('TypeError',
                        "Cannot read property '%s' of null" % prop)
    else:
        raise RuntimeError('Unknown type! - ' + repr(typ))


def get_member_dot(self, prop, space):
    # dot member getter, prop has to be unicode
    typ = type(self)
    if typ not in PRIMITIVES:  # most likely getter for object
        return self.get(prop)
    elif typ == unicode:  # then probably a String
        if prop == 'length':
            return float(len(self))
        elif prop.isdigit():
            index = int(prop)
            if 0 <= index < len(self):
                return self[index]
        else:
            # use standard string prototype
            return space.StringPrototype.get(prop)
            # maybe an index
    elif typ == float:
        # use standard number prototype
        return space.NumberPrototype.get(prop)
    elif typ == bool:
        return space.BooleanPrototype.get(prop)
    elif typ in (UNDEFINED_TYPE, NULL_TYPE):
        raise MakeError('TypeError',
                        "Cannot read property '%s' of undefined" % prop)
    else:
        raise RuntimeError('Unknown type! - ' + repr(typ))


# Object


class PyJsObject(PyJs):
    TYPE = 'Object'
    Class = 'Object'

    def __init__(self, prototype=None):
        self.prototype = prototype
        self.own = {}

    def _init(self, props, vals):
        i = 0
        for prop, kind in props:
            if prop in self.own:  # just check... probably will not happen very often.
                if is_data_descriptor(self.own[prop]):
                    if kind != 'i':
                        raise MakeError(
                            'SyntaxError',
                            'Invalid object initializer! Duplicate property name "%s"'
                            % prop)
                else:
                    if kind == 'i' or (kind == 'g' and 'get' in self.own[prop]
                                       ) or (kind == 's'
                                             and 'set' in self.own[prop]):
                        raise MakeError(
                            'SyntaxError',
                            'Invalid object initializer! Duplicate setter/getter of prop: "%s"'
                            % prop)

            if kind == 'i':  # init
                self.own[prop] = {
                    'value': vals[i],
                    'writable': True,
                    'enumerable': True,
                    'configurable': True
                }
            elif kind == 'g':  # get
                self.define_own_property(prop, {
                    'get': vals[i],
                    'enumerable': True,
                    'configurable': True
                }, False)
            elif kind == 's':  # get
                self.define_own_property(prop, {
                    'get': vals[i],
                    'enumerable': True,
                    'configurable': True
                }, False)
            else:
                raise RuntimeError(
                    'Invalid property kind - %s. Expected one of i, g, s.' %
                    repr(kind))
            i += 1

    def _set_props(self, prop_descs):
        for prop, desc in six.iteritems(prop_descs):
            self.define_own_property(prop, desc)


# Array


# todo Optimise Array - extremely slow due to index conversions from str to int and back etc.
# solution - make get and put methods callable with any type of prop and handle conversions from inside
# if not array then use to_string(prop). In array if prop is integer then just use it
# also consider removal of these stupid writable, enumerable etc for ints.
class PyJsArray(PyJs):
    Class = 'Array'

    def __init__(self, length, prototype=None):
        self.prototype = prototype
        self.own = {
            'length': {
                'value': float(length),
                'writable': True,
                'enumerable': False,
                'configurable': False
            }
        }

    def _init(self, elements):
        for i, ele in enumerate(elements):
            if ele is None: continue
            self.own[unicode(i)] = {
                'value': ele,
                'writable': True,
                'enumerable': True,
                'configurable': True
            }

    def put(self, prop, val, throw=False):
        assert type(val) != int
        # takes py, returns none
        if not self.can_put(prop):
            if throw:
                raise MakeError('TypeError', 'Could not define own property')
            return
        own_desc = self.get_own_property(prop)
        if is_data_descriptor(own_desc):
            self.define_own_property(prop, {'value': val}, False)
            return
        desc = self.get_property(prop)
        if is_accessor_descriptor(desc):
            desc['set'].call(
                self, (val, ))  # calling setter on own or inherited element
        else:  # new property
            self.define_own_property(
                prop, {
                    'value': val,
                    'writable': True,
                    'configurable': True,
                    'enumerable': True
                }, False)

    def define_own_property(self, prop, desc, throw):
        assert type(desc.get('value')) != int
        old_len_desc = self.get_own_property('length')
        old_len = old_len_desc['value']  #  value is js type so convert to py.
        if prop == 'length':
            if 'value' not in desc:
                return PyJs.define_own_property(self, prop, desc, False)
            new_len = to_uint32(desc['value'])
            if new_len != to_number(desc['value']):
                raise MakeError('RangeError', 'Invalid range!')
            new_desc = dict((k, v) for k, v in six.iteritems(desc))
            new_desc['value'] = float(new_len)
            if new_len >= old_len:
                return PyJs.define_own_property(self, prop, new_desc, False)
            if not old_len_desc['writable']:
                return False
            if 'writable' not in new_desc or new_desc['writable'] == True:
                new_writable = True
            else:
                new_writable = False
                new_desc['writable'] = True
            if not PyJs.define_own_property(self, prop, new_desc, False):
                return False
            if new_len < old_len:
                # not very efficient for sparse arrays, so using different method for sparse:
                if old_len > 30 * len(self.own):
                    for ele in self.own.keys():
                        if ele.isdigit() and int(ele) >= new_len:
                            if not self.delete(
                                    ele
                            ):  # if failed to delete set len to current len and reject.
                                new_desc['value'] = old_len + 1.
                                if not new_writable:
                                    new_desc['writable'] = False
                                PyJs.define_own_property(
                                    self, prop, new_desc, False)
                                return False
                    old_len = new_len
                else:  # standard method
                    while new_len < old_len:
                        old_len -= 1
                        if not self.delete(
                                unicode(int(old_len))
                        ):  # if failed to delete set len to current len and reject.
                            new_desc['value'] = old_len + 1.
                            if not new_writable:
                                new_desc['writable'] = False
                            PyJs.define_own_property(self, prop, new_desc,
                                                     False)
                            return False
            if not new_writable:
                self.own['length']['writable'] = False
            return True

        elif prop.isdigit():
            index = to_uint32(prop)
            if index >= old_len and not old_len_desc['writable']:
                return False
            if not PyJs.define_own_property(self, prop, desc, False):
                return False
            if index >= old_len:
                old_len_desc['value'] = index + 1.
            return True
        else:
            return PyJs.define_own_property(self, prop, desc, False)

    def to_list(self):
        return [
            self.get(str(e)) for e in xrange(self.get('length').to_uint32())
        ]


# database with compiled patterns. Js pattern -> Py pattern.
REGEXP_DB = {}


class PyJsRegExp(PyJs):
    Class = 'RegExp'

    def __init__(self, body, flags, prototype=None):
        self.prototype = prototype
        self.glob = True if 'g' in flags else False
        self.ignore_case = re.IGNORECASE if 'i' in flags else 0
        self.multiline = re.MULTILINE if 'm' in flags else 0
        self.value = body

        if (body, flags) in REGEXP_DB:
            self.pat = REGEXP_DB[body, flags]
        else:
            comp = None
            try:
                # converting JS regexp pattern to Py pattern.
                possible_fixes = [(u'[]', u'[\0]'), (u'[^]', u'[^\0]'),
                                  (u'nofix1791', u'nofix1791')]
                reg = self.value
                for fix, rep in possible_fixes:
                    comp = PyJsParser()._interpret_regexp(reg, flags)
                    #print 'reg -> comp', reg, '->', comp
                    try:
                        self.pat = re.compile(
                            comp, self.ignore_case | self.multiline)
                        #print reg, '->', comp
                        break
                    except:
                        reg = reg.replace(fix, rep)
                    # print 'Fix', fix, '->', rep, '=', reg
                else:
                    raise Exception()
                REGEXP_DB[body, flags] = self.pat
            except:
                #print 'Invalid pattern...', self.value, comp
                raise MakeError(
                    'SyntaxError',
                    'Invalid RegExp pattern: %s -> %s' % (repr(self.value),
                                                          repr(comp)))
        # now set own properties:
        self.own = {
            'source': {
                'value': self.value,
                'enumerable': False,
                'writable': False,
                'configurable': False
            },
            'global': {
                'value': self.glob,
                'enumerable': False,
                'writable': False,
                'configurable': False
            },
            'ignoreCase': {
                'value': bool(self.ignore_case),
                'enumerable': False,
                'writable': False,
                'configurable': False
            },
            'multiline': {
                'value': bool(self.multiline),
                'enumerable': False,
                'writable': False,
                'configurable': False
            },
            'lastIndex': {
                'value': 0.,
                'enumerable': False,
                'writable': True,
                'configurable': False
            }
        }

    def match(self, string, pos):
        '''string is of course a py string'''
        return self.pat.match(string, int(pos))


class PyJsError(PyJs):
    Class = 'Error'
    extensible = True

    def __init__(self, message=None, prototype=None):
        self.prototype = prototype
        self.own = {}
        if message is not None:
            self.put('message', to_string(message))
            self.own['message']['enumerable'] = False


class PyJsDate(PyJs):
    Class = 'Date'
    UTCToLocal = None  # todo UTC to local should be imported!

    def __init__(self, value, prototype=None):
        self.value = value
        self.own = {}
        self.prototype = prototype

    # todo fix this problematic datetime part
    def to_local_dt(self):
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(
            seconds=self.UTCToLocal(self.value) // 1000)

    def to_utc_dt(self):
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(
            seconds=self.value // 1000)

    def local_strftime(self, pattern):
        if self.value is NaN:
            return 'Invalid Date'
        try:
            dt = self.to_local_dt()
        except:
            raise MakeError(
                'TypeError',
                'unsupported date range. Will fix in future versions')
        try:
            return dt.strftime(pattern)
        except:
            raise MakeError(
                'TypeError',
                'Could not generate date string from this date (limitations of python.datetime)'
            )

    def utc_strftime(self, pattern):
        if self.value is NaN:
            return 'Invalid Date'
        try:
            dt = self.to_utc_dt()
        except:
            raise MakeError(
                'TypeError',
                'unsupported date range. Will fix in future versions')
        try:
            return dt.strftime(pattern)
        except:
            raise MakeError(
                'TypeError',
                'Could not generate date string from this date (limitations of python.datetime)'
            )


# Scope class it will hold all the variables accessible to user
class Scope(PyJs):
    Class = 'Global'
    extensible = True
    IS_CHILD_SCOPE = True
    THIS_BINDING = None
    space = None
    exe = None

    # todo speed up!
    # in order to speed up this very important class the top scope should behave differently than
    # child scopes, child scope should not have this property descriptor thing because they cant be changed anyway
    # they are all confugurable= False

    def __init__(self, scope, space, parent=None):
        """Doc"""
        self.space = space
        self.prototype = parent
        if type(scope) is not dict:
            assert parent is not None, 'You initialised the WITH_SCOPE without a parent scope.'
            self.own = scope
            self.is_with_scope = True
        else:
            self.is_with_scope = False
        if parent is None:
            # global, top level scope
            self.own = {}
            for k, v in six.iteritems(scope):
                # set all the global items
                self.define_own_property(
                    k, {
                        'value': v,
                        'configurable': False,
                        'writable': False,
                        'enumerable': False
                    }, False)
        else:
            # not global, less powerful but faster closure.
            self.own = scope  # simple dictionary which maps name directly to js object.

        self.par = super(Scope, self)
        self.stack = []

    def register(self, var):
        # registered keeps only global registered variables
        if self.prototype is None:
            # define in global scope
            if var in self.own:
                self.own[var]['configurable'] = False
            else:
                self.define_own_property(
                    var, {
                        'value': undefined,
                        'configurable': False,
                        'writable': True,
                        'enumerable': True
                    }, False)
        elif var not in self.own:
            # define in local scope since it has not been defined yet
            self.own[var] = undefined  # default value

    def registers(self, vars):
        """register multiple variables"""
        for var in vars:
            self.register(var)

    def put(self, var, val, throw=False):
        if self.prototype is None:
            desc = self.own.get(var)  # global scope
            if desc is None:
                self.par.put(var, val, False)
            else:
                if desc['writable']:  # todo consider getters/setters
                    desc['value'] = val
        else:
            if self.is_with_scope:
                if self.own.has_property(var):
                    return self.own.put(var, val, throw=throw)
                else:
                    return self.prototype.put(var, val)
            # trying to put in local scope
            # we dont know yet in which scope we should place this var
            elif var in self.own:
                self.own[var] = val
                return val
            else:
                # try to put in the lower scope since we cant put in this one (var wasn't registered)
                return self.prototype.put(var, val)

    def get(self, var, throw=False):
        if self.prototype is not None:
            if self.is_with_scope:
                cand = None if not self.own.has_property(
                    var) else self.own.get(var)
            else:
                # fast local scope
                cand = self.own.get(var)
            if cand is None:
                return self.prototype.get(var, throw)
            return cand
        # slow, global scope
        if var not in self.own:
            # try in ObjectPrototype...
            if var in self.space.ObjectPrototype.own:
                return self.space.ObjectPrototype.get(var)
            if throw:
                raise MakeError('ReferenceError', '%s is not defined' % var)
            return undefined
        cand = self.own[var].get('value')
        return cand if cand is not None else self.own[var]['get'].call(self)

    def delete(self, var, throw=False):
        if self.prototype is not None:
            if self.is_with_scope:
                if self.own.has_property(var):
                    return self.own.delete(var)
            elif var in self.own:
                return False
            return self.prototype.delete(var)
        # we are in global scope here. Must exist and be configurable to delete
        if var not in self.own:
            # this var does not exist, why do you want to delete it???
            return True
        if self.own[var]['configurable']:
            del self.own[var]
            return True
        # not configurable, cant delete
        return False


def get_new_arguments_obj(args, space):
    obj = space.NewObject()
    obj.Class = 'Arguments'
    obj.define_own_property(
        'length', {
            'value': float(len(args)),
            'writable': True,
            'enumerable': False,
            'configurable': True
        }, False)
    for i, e in enumerate(args):
        obj.put(unicode(i), e)
    return obj


#Function
class PyJsFunction(PyJs):
    Class = 'Function'
    source = '{ [native code] }'
    IS_CONSTRUCTOR = True

    def __init__(self,
                 code,
                 ctx,
                 params,
                 name,
                 space,
                 is_declaration,
                 definitions,
                 prototype=None):
        self.prototype = prototype
        self.own = {}

        self.code = code
        if type(
                self.code
        ) == int:  # just a label pointing to the beginning of the code.
            self.is_native = False
        else:
            self.is_native = True  # python function

        self.ctx = ctx

        self.params = params
        self.arguments_in_params = 'arguments' in params
        self.definitions = definitions

        # todo remove this check later
        for p in params:
            assert p in self.definitions

        self.name = name
        self.space = space
        self.is_declaration = is_declaration

        #set own property length to the number of arguments
        self.own['length'] = {
            'value': float(len(params)),
            'writable': False,
            'enumerable': False,
            'configurable': False
        }

        if name:
            self.own['name'] = {
                'value': name,
                'writable': False,
                'enumerable': False,
                'configurable': True
            }

        if not self.is_native:  # set prototype for user defined functions
            # constructor points to this function
            proto = space.NewObject()
            proto.own['constructor'] = {
                'value': self,
                'writable': True,
                'enumerable': False,
                'configurable': True
            }
            self.own['prototype'] = {
                'value': proto,
                'writable': True,
                'enumerable': False,
                'configurable': False
            }
        # todo set up throwers on callee and arguments if in strict mode

    def call(self, this, args=()):
        ''' Dont use this method from inside bytecode to call other bytecode. '''
        if self.is_native:
            _args = SpaceTuple(
                args
            )  # we have to do that unfortunately to pass all the necessary info to the funcs
            _args.space = self.space
            return self.code(
                this, _args
            )  # must return valid js object - undefined, null, float, unicode, bool, or PyJs
        else:
            return self.space.exe._call(self, this,
                                        args)  # will run inside bytecode

    def has_instance(self, other):
        # I am not sure here so instanceof may not work lol.
        if not is_object(other):
            return False
        proto = self.get('prototype')
        if not is_object(proto):
            raise MakeError(
                'TypeError',
                'Function has non-object prototype in instanceof check')
        while True:
            other = other.prototype
            if not other:  # todo make sure that the condition is not None or null
                return False
            if other is proto:
                return True

    def create(self, args, space):
        proto = self.get('prototype')
        if not is_object(proto):
            proto = space.ObjectPrototype
        new = PyJsObject(prototype=proto)
        res = self.call(new, args)
        if is_object(res):
            return res
        return new

    def _generate_my_context(self, this, args):
        my_ctx = Scope(
            dict(izip(self.params, args)), self.space, parent=self.ctx)
        my_ctx.registers(self.definitions)
        my_ctx.THIS_BINDING = this
        if not self.arguments_in_params:
            my_ctx.own['arguments'] = get_new_arguments_obj(args, self.space)
        if not self.is_declaration and self.name and self.name not in my_ctx.own:
            my_ctx.own[
                self.
                name] = self  # this should be immutable binding but come on!
        return my_ctx


class SpaceTuple:
    def __init__(self, tup):
        self.tup = tup

    def __len__(self):
        return len(self.tup)

    def __getitem__(self, item):
        return self.tup[item]

    def __iter__(self):
        return iter(self.tup)
