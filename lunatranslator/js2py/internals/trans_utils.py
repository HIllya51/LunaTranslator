import six
if six.PY3:
    basestring = str
    long = int
    xrange = range
    unicode = str

def to_key(literal_or_identifier):
    ''' returns string representation of this object'''
    if literal_or_identifier['type'] == 'Identifier':
        return literal_or_identifier['name']
    elif literal_or_identifier['type'] == 'Literal':
        k = literal_or_identifier['value']
        if isinstance(k, float):
            return unicode(float_repr(k))
        elif 'regex' in literal_or_identifier:
            return compose_regex(k)
        elif isinstance(k, bool):
            return u'true' if k else u'false'
        elif k is None:
            return u'null'
        else:
            return unicode(k)


def compose_regex(val):
    reg, flags = val
    # reg = REGEXP_CONVERTER._unescape_string(reg)
    return u'/%s/%s' % (reg, flags)


def float_repr(f):
    if int(f) == f:
        return unicode(repr(int(f)))
    return unicode(repr(f))
