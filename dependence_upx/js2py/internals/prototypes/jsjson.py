from __future__ import unicode_literals
from ..conversions import *
from ..func_utils import *
from ..operations import strict_equality_op
import json

indent = ''
# python 3 support
import six
if six.PY3:
    basestring = str
    long = int
    xrange = range
    unicode = str


def parse(this, args):
    text, reviver = get_arg(args, 0), get_arg(args, 1)
    s = to_string(text)
    try:
        unfiltered = json.loads(s)
    except:
        raise MakeError(
            'SyntaxError',
            'JSON.parse could not parse JSON string - Invalid syntax')
    unfiltered = to_js(unfiltered, args.space)
    if is_callable(reviver):
        root = args.space.ConstructObject({'': unfiltered})
        return walk(root, '', reviver)
    else:
        return unfiltered


def stringify(this, args):
    global indent
    value, replacer, space = get_arg(args, 0), get_arg(args, 1), get_arg(
        args, 2)
    stack = set([])
    indent = ''
    property_list = replacer_function = undefined
    if is_object(replacer):
        if is_callable(replacer):
            replacer_function = replacer
        elif replacer.Class == 'Array':
            property_list = []
            for e in replacer:
                v = replacer[e]
                item = undefined
                typ = Type(v)
                if typ == 'Number':
                    item = to_string(v)
                elif typ == 'String':
                    item = v
                elif typ == 'Object':
                    if GetClass(v) in ('String', 'Number'):
                        item = to_string(v)
                if not is_undefined(item) and item not in property_list:
                    property_list.append(item)
    if is_object(space):
        if GetClass(space) == 'Number':
            space = to_number(space)
        elif GetClass(space) == 'String':
            space = to_string(space)
    if Type(space) == 'Number':
        space = min(10, to_int(space))
        gap = max(int(space), 0) * ' '
    elif Type(space) == 'String':
        gap = space[:10]
    else:
        gap = ''
    return Str('', args.space.ConstructObject({
        '': value
    }), replacer_function, property_list, gap, stack, space)


def Str(key, holder, replacer_function, property_list, gap, stack, space):
    value = holder.get(key)
    if is_object(value):
        to_json = value.get('toJSON')
        if is_callable(to_json):
            value = to_json.call(value, (key, ))
    if not is_undefined(replacer_function):
        value = replacer_function.call(holder, (key, value))

    if is_object(value):
        if value.Class == 'String':
            value = to_string(value)
        elif value.Class == 'Number':
            value = to_number(value)
        elif value.Class == 'Boolean':
            value = to_boolean(value)
    typ = Type(value)
    if is_null(value):
        return 'null'
    elif typ == 'Boolean':
        return 'true' if value else 'false'
    elif typ == 'String':
        return Quote(value)
    elif typ == 'Number':
        if not is_infinity(value):
            return to_string(value)
        return 'null'
    if is_object(value) and not is_callable(value):
        if value.Class == 'Array':
            return ja(value, stack, gap, property_list, replacer_function,
                      space)
        else:
            return jo(value, stack, gap, property_list, replacer_function,
                      space)
    return undefined


def jo(value, stack, gap, property_list, replacer_function, space):
    global indent
    if value in stack:
        raise MakeError('TypeError', 'Converting circular structure to JSON')
    stack.add(value)
    stepback = indent
    indent += gap
    if not is_undefined(property_list):
        k = property_list
    else:
        k = [unicode(e) for e, d in value.own.items() if d.get('enumerable')]
    partial = []
    for p in k:
        str_p = Str(p, value, replacer_function, property_list, gap, stack,
                    space)
        if not is_undefined(str_p):
            member = json.dumps(p) + ':' + (
                ' ' if gap else
                '') + str_p  # todo not sure here - what space character?
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
        raise MakeError('TypeError', 'Converting circular structure to JSON')
    stack.add(value)
    stepback = indent
    indent += gap
    partial = []
    length = js_arr_length(value)
    for index in xrange(length):
        index = unicode(index)
        str_index = Str(index, value, replacer_function, property_list, gap,
                        stack, space)
        if is_undefined(str_index):
            partial.append('null')
        else:
            partial.append(str_index)
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
    return json.dumps(string)


def to_js(d, _args_space):
    return convert_to_js_type(d, _args_space)


def walk(holder, name, reviver):
    val = holder.get(name)
    if GetClass(val) == 'Array':
        for i in xrange(js_arr_length(val)):
            i = unicode(i)
            new_element = walk(val, i, reviver)
            if is_undefined(new_element):
                val.delete(i)
            else:
                new_element.put(i, new_element)
    elif is_object(val):
        for key in [
                unicode(e) for e, d in val.own.items() if d.get('enumerable')
        ]:
            new_element = walk(val, key, reviver)
            if is_undefined(new_element):
                val.delete(key)
            else:
                val.put(key, new_element)
    return reviver.call(holder, (name, val))
