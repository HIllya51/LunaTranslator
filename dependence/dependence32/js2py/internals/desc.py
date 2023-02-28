# todo make sure what they mean by desc undefined? None or empty? Answer: None :) it can never be empty but None is sometimes returned.

# I am implementing everything as dicts to speed up property creation

# Warning: value, get, set props of dest are PyJs types. Rest is Py!


def is_data_descriptor(desc):
    return desc and ('value' in desc or 'writable' in desc)


def is_accessor_descriptor(desc):
    return desc and ('get' in desc or 'set' in desc)


def is_generic_descriptor(
        desc
):  # generic means not the data and not the setter - therefore it must be one that changes only enum and conf
    return desc and not (is_data_descriptor(desc)
                         or is_accessor_descriptor(desc))


def from_property_descriptor(desc, space):
    if not desc:
        return {}
    obj = space.NewObject()
    if is_data_descriptor(desc):
        obj.define_own_property(
            'value', {
                'value': desc['value'],
                'writable': True,
                'enumerable': True,
                'configurable': True
            }, False)
        obj.define_own_property(
            'writable', {
                'value': desc['writable'],
                'writable': True,
                'enumerable': True,
                'configurable': True
            }, False)
    else:
        obj.define_own_property(
            'get', {
                'value': desc['get'],
                'writable': True,
                'enumerable': True,
                'configurable': True
            }, False)
        obj.define_own_property(
            'set', {
                'value': desc['set'],
                'writable': True,
                'enumerable': True,
                'configurable': True
            }, False)
    obj.define_own_property(
        'writable', {
            'value': desc['writable'],
            'writable': True,
            'enumerable': True,
            'configurable': True
        }, False)
    obj.define_own_property(
        'enumerable', {
            'value': desc['enumerable'],
            'writable': True,
            'enumerable': True,
            'configurable': True
        }, False)
    return obj


def to_property_descriptor(obj):
    if obj._type() != 'Object':
        raise TypeError()
    desc = {}
    for e in ('enumerable', 'configurable', 'writable'):
        if obj.has_property(e):
            desc[e] = obj.get(e).to_boolean().value
    if obj.has_property('value'):
        desc['value'] = obj.get('value')
    for e in ('get', 'set'):
        if obj.has_property(e):
            cand = obj.get(e)
            if not (cand.is_callable() or cand.is_undefined()):
                raise TypeError()
    if ('get' in desc or 'set' in desc) and ('value' in desc
                                             or 'writable' in desc):
        raise TypeError()
