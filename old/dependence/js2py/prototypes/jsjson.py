import json
from ..base import Js
indent = ''
# python 3 support
import six
if six.PY3:
    basestring = str
    long = int
    xrange = range
    unicode = str


def parse(text):
    reviver = arguments[1]
    s = text.to_string().value
    try:
        unfiltered = json.loads(s)
    except:
        raise this.MakeError('SyntaxError',
                             'Could not parse JSON string - Invalid syntax')
    unfiltered = to_js(this, unfiltered)
    if reviver.is_callable():
        root = this.Js({'': unfiltered})
        return walk(root, '', reviver)
    else:
        return unfiltered


def stringify(value, replacer, space):
    global indent
    stack = set([])
    indent = ''
    property_list = replacer_function = this.undefined
    if replacer.is_object():
        if replacer.is_callable():
            replacer_function = replacer
        elif replacer.Class == 'Array':
            property_list = []
            for e in replacer:
                v = replacer[e]
                item = this.undefined
                if v._type() == 'Number':
                    item = v.to_string()
                elif v._type() == 'String':
                    item = v
                elif v.is_object():
                    if v.Class in ('String', 'Number'):
                        item = v.to_string()
                if not item.is_undefined() and item.value not in property_list:
                    property_list.append(item.value)
    if space.is_object():
        if space.Class == 'Number':
            space = space.to_number()
        elif space.Class == 'String':
            space = space.to_string()
    if space._type() == 'Number':
        space = this.Js(min(10, space.to_int()))
        gap = max(int(space.value), 0) * ' '
    elif space._type() == 'String':
        gap = space.value[:10]
    else:
        gap = ''
    return this.Js(
        Str('', this.Js({
            '': value
        }), replacer_function, property_list, gap, stack, space))


def Str(key, holder, replacer_function, property_list, gap, stack, space):
    value = holder[key]
    if value.is_object():
        to_json = value.get('toJSON')
        if to_json.is_callable():
            value = to_json.call(value, (key, ))
    if not replacer_function.is_undefined():
        value = replacer_function.call(holder, (key, value))

    if value.is_object():
        if value.Class == 'String':
            value = value.to_string()
        elif value.Class == 'Number':
            value = value.to_number()
        elif value.Class == 'Boolean':
            value = value.to_boolean()
    if value.is_null():
        return 'null'
    elif value.Class == 'Boolean':
        return 'true' if value.value else 'false'
    elif value._type() == 'String':
        return Quote(value)
    elif value._type() == 'Number':
        if not value.is_infinity():
            return value.to_string()
        return 'null'
    if value.is_object() and not value.is_callable():
        if value.Class == 'Array':
            return ja(value, stack, gap, property_list, replacer_function,
                      space)
        else:
            return jo(value, stack, gap, property_list, replacer_function,
                      space)
    return None  # undefined


def jo(value, stack, gap, property_list, replacer_function, space):
    global indent
    if value in stack:
        raise value.MakeError('TypeError',
                              'Converting circular structure to JSON')
    stack.add(value)
    stepback = indent
    indent += gap
    if not property_list.is_undefined():
        k = property_list
    else:
        k = [e.value for e in value]
    partial = []
    for p in k:
        str_p = value.Js(
            Str(p, value, replacer_function, property_list, gap, stack, space))
        if not str_p.is_undefined():
            member = json.dumps(p) + ':' + (
                ' ' if gap else
                '') + str_p.value  # todo not sure here - what space character?
            partial.append(member)
    if not partial:
        final = '{}'
    else:
        if not gap:
            final = '{%s}' % ','.join(partial)
        else:
            sep = ',\n' + indent
            properties = sep.join(partial)
            final = '{\n' + indent + properties + '\n' + stepback + '}'
    stack.remove(value)
    indent = stepback
    return final


def ja(value, stack, gap, property_list, replacer_function, space):
    global indent
    if value in stack:
        raise value.MakeError('TypeError',
                              'Converting circular structure to JSON')
    stack.add(value)
    stepback = indent
    indent += gap
    partial = []
    length = len(value)
    for index in xrange(length):
        index = str(index)
        str_index = value.Js(
            Str(index, value, replacer_function, property_list, gap, stack,
                space))
        if str_index.is_undefined():
            partial.append('null')
        else:
            partial.append(str_index.value)
    if not partial:
        final = '[]'
    else:
        if not gap:
            final = '[%s]' % ','.join(partial)
        else:
            sep = ',\n' + indent
            properties = sep.join(partial)
            final = '[\n' + indent + properties + '\n' + stepback + ']'
    stack.remove(value)
    indent = stepback
    return final


def Quote(string):
    return string.Js(json.dumps(string.value))


def to_js(this, d):
    if isinstance(d, dict):
        return this.Js(dict((k, this.Js(v)) for k, v in six.iteritems(d)))
    return this.Js(d)


def walk(holder, name, reviver):
    val = holder.get(name)
    if val.Class == 'Array':
        for i in xrange(len(val)):
            i = unicode(i)
            new_element = walk(val, i, reviver)
            if new_element.is_undefined():
                val.delete(i)
            else:
                new_element.put(i, new_element)
    elif val.is_object():
        for key in val:
            new_element = walk(val, key, reviver)
            if new_element.is_undefined():
                val.delete(key)
            else:
                val.put(key, new_element)
    return reviver.call(holder, (name, val))


JSON = Js({})

JSON.define_own_property(
    'parse', {
        'value': Js(parse),
        'enumerable': False,
        'writable': True,
        'configurable': True
    })

JSON.define_own_property(
    'stringify', {
        'value': Js(stringify),
        'enumerable': False,
        'writable': True,
        'configurable': True
    })
