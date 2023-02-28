# this is based on jsarray.py

import six
try:
    import numpy
except:
    pass

if six.PY3:
    xrange = range
    import functools


def to_arr(this):
    """Returns Python array from Js array"""
    return [this.get(str(e)) for e in xrange(len(this))]


ARR_STACK = set({})


class TypedArrayPrototype:
    def toString():
        # this function is wrong
        func = this.get('join')
        if not func.is_callable():

            @this.Js
            def func():
                return '[object %s]' % this.Class

        return func.call(this, ())

    def toLocaleString(locales=None, options=None):
        array = this.to_object()
        arr_len = array.get("length").to_uint32()
        # separator is simply a comma ','
        if not arr_len:
            return ''
        res = []
        for i in xrange(arr_len):
            element = array[str(i)]
            if element.is_undefined() or element.is_null():
                res.append('')
            else:
                cand = element.to_object()
                str_func = element.get('toLocaleString')
                if not str_func.is_callable():
                    raise this.MakeError(
                        'TypeError',
                        'toLocaleString method of item at index %d is not callable'
                        % i)
                res.append(element.callprop('toLocaleString').value)
        return ','.join(res)

    def join(separator):
        ARR_STACK.add(this)
        array = this.to_object()
        arr_len = array.get("length").to_uint32()
        separator = ',' if separator.is_undefined() else separator.to_string(
        ).value
        elems = []
        for e in xrange(arr_len):
            elem = array.get(str(e))
            if elem in ARR_STACK:
                s = ''
            else:
                s = elem.to_string().value
            elems.append(
                s if not (elem.is_undefined() or elem.is_null()) else '')
        res = separator.join(elems)
        ARR_STACK.remove(this)
        return res

    def reverse():
        array = this.to_object()  # my own algorithm
        vals = to_arr(array)
        has_props = [array.has_property(str(e)) for e in xrange(len(array))]
        vals.reverse()
        has_props.reverse()
        for i, val in enumerate(vals):
            if has_props[i]:
                array.put(str(i), val)
            else:
                array.delete(str(i))
        return array

    def slice(start, end):  # todo check
        array = this.to_object()
        arr_len = array.get("length").to_uint32()
        relative_start = start.to_int()
        k = max((arr_len + relative_start), 0) if relative_start < 0 else min(
            relative_start, arr_len)
        relative_end = arr_len if end.is_undefined() else end.to_int()
        final = max((arr_len + relative_end), 0) if relative_end < 0 else min(
            relative_end, arr_len)
        res = []
        n = 0
        while k < final:
            pk = str(k)
            if array.has_property(pk):
                res.append(array.get(pk))
            k += 1
            n += 1
        return res

    def sort(cmpfn):
        if not this.Class in ('Array', 'Arguments'):
            return this.to_object()  # do nothing
        arr = []
        for i in xrange(len(this)):
            arr.append(this.get(six.text_type(i)))

        if not arr:
            return this
        if not cmpfn.is_callable():
            cmpfn = None
        cmp = lambda a, b: sort_compare(a, b, cmpfn)
        if six.PY3:
            key = functools.cmp_to_key(cmp)
            arr.sort(key=key)
        else:
            arr.sort(cmp=cmp)
        for i in xrange(len(arr)):
            this.put(six.text_type(i), arr[i])

        return this

    def indexOf(searchElement):
        array = this.to_object()
        arr_len = array.get("length").to_uint32()
        if arr_len == 0:
            return -1
        if len(arguments) > 1:
            n = arguments[1].to_int()
        else:
            n = 0
        if n >= arr_len:
            return -1
        if n >= 0:
            k = n
        else:
            k = arr_len - abs(n)
            if k < 0:
                k = 0
        while k < arr_len:
            if array.has_property(str(k)):
                elementK = array.get(str(k))
                if searchElement.strict_equality_comparison(elementK):
                    return k
            k += 1
        return -1

    def lastIndexOf(searchElement):
        array = this.to_object()
        arr_len = array.get("length").to_uint32()
        if arr_len == 0:
            return -1
        if len(arguments) > 1:
            n = arguments[1].to_int()
        else:
            n = arr_len - 1
        if n >= 0:
            k = min(n, arr_len - 1)
        else:
            k = arr_len - abs(n)
        while k >= 0:
            if array.has_property(str(k)):
                elementK = array.get(str(k))
                if searchElement.strict_equality_comparison(elementK):
                    return k
            k -= 1
        return -1

    def every(callbackfn):
        array = this.to_object()
        arr_len = array.get("length").to_uint32()
        if not callbackfn.is_callable():
            raise this.MakeError('TypeError', 'callbackfn must be a function')
        T = arguments[1]
        k = 0
        while k < arr_len:
            if array.has_property(str(k)):
                kValue = array.get(str(k))
                if not callbackfn.call(
                        T, (kValue, this.Js(k), array)).to_boolean().value:
                    return False
            k += 1
        return True

    def some(callbackfn):
        array = this.to_object()
        arr_len = array.get("length").to_uint32()
        if not callbackfn.is_callable():
            raise this.MakeError('TypeError', 'callbackfn must be a function')
        T = arguments[1]
        k = 0
        while k < arr_len:
            if array.has_property(str(k)):
                kValue = array.get(str(k))
                if callbackfn.call(
                        T, (kValue, this.Js(k), array)).to_boolean().value:
                    return True
            k += 1
        return False

    def forEach(callbackfn):
        array = this.to_object()
        arr_len = array.get("length").to_uint32()
        if not callbackfn.is_callable():
            raise this.MakeError('TypeError', 'callbackfn must be a function')
        T = arguments[1]
        k = 0
        while k < arr_len:
            if array.has_property(str(k)):
                kValue = array.get(str(k))
                callbackfn.call(T, (kValue, this.Js(k), array))
            k += 1

    def map(callbackfn):
        array = this.to_object()
        arr_len = array.get("length").to_uint32()
        if not callbackfn.is_callable():
            raise this.MakeError('TypeError', 'callbackfn must be a function')
        T = arguments[1]
        A = this.Js([])
        k = 0
        while k < arr_len:
            Pk = str(k)
            if array.has_property(Pk):
                kValue = array.get(Pk)
                mappedValue = callbackfn.call(T, (kValue, this.Js(k), array))
                A.define_own_property(
                    Pk, {
                        'value': mappedValue,
                        'writable': True,
                        'enumerable': True,
                        'configurable': True
                    })
            k += 1
        return A

    def filter(callbackfn):
        array = this.to_object()
        arr_len = array.get("length").to_uint32()
        if not callbackfn.is_callable():
            raise this.MakeError('TypeError', 'callbackfn must be a function')
        T = arguments[1]
        res = []
        k = 0
        while k < arr_len:
            if array.has_property(str(k)):
                kValue = array.get(str(k))
                if callbackfn.call(
                        T, (kValue, this.Js(k), array)).to_boolean().value:
                    res.append(kValue)
            k += 1
        return res  # converted to js array automatically

    def reduce(callbackfn):
        array = this.to_object()
        arr_len = array.get("length").to_uint32()
        if not callbackfn.is_callable():
            raise this.MakeError('TypeError', 'callbackfn must be a function')
        if not arr_len and len(arguments) < 2:
            raise this.MakeError(
                'TypeError', 'Reduce of empty array with no initial value')
        k = 0
        if len(arguments) > 1:  # initial value present
            accumulator = arguments[1]
        else:
            kPresent = False
            while not kPresent and k < arr_len:
                kPresent = array.has_property(str(k))
                if kPresent:
                    accumulator = array.get(str(k))
                k += 1
            if not kPresent:
                raise this.MakeError(
                    'TypeError', 'Reduce of empty array with no initial value')
        while k < arr_len:
            if array.has_property(str(k)):
                kValue = array.get(str(k))
                accumulator = callbackfn.call(
                    this.undefined, (accumulator, kValue, this.Js(k), array))
            k += 1
        return accumulator

    def reduceRight(callbackfn):
        array = this.to_object()
        arr_len = array.get("length").to_uint32()
        if not callbackfn.is_callable():
            raise this.MakeError('TypeError', 'callbackfn must be a function')
        if not arr_len and len(arguments) < 2:
            raise this.MakeError(
                'TypeError', 'Reduce of empty array with no initial value')
        k = arr_len - 1
        if len(arguments) > 1:  # initial value present
            accumulator = arguments[1]
        else:
            kPresent = False
            while not kPresent and k >= 0:
                kPresent = array.has_property(str(k))
                if kPresent:
                    accumulator = array.get(str(k))
                k -= 1
            if not kPresent:
                raise this.MakeError(
                    'TypeError', 'Reduce of empty array with no initial value')
        while k >= 0:
            if array.has_property(str(k)):
                kValue = array.get(str(k))
                accumulator = callbackfn.call(
                    this.undefined, (accumulator, kValue, this.Js(k), array))
            k -= 1
        return accumulator


def sort_compare(a, b, comp):
    if a is None:
        if b is None:
            return 0
        return 1
    if b is None:
        if a is None:
            return 0
        return -1
    if a.is_undefined():
        if b.is_undefined():
            return 0
        return 1
    if b.is_undefined():
        if a.is_undefined():
            return 0
        return -1
    if comp is not None:
        res = comp.call(a.undefined, (a, b))
        return res.to_int()
    x, y = a.to_string(), b.to_string()
    if x < y:
        return -1
    elif x > y:
        return 1
    return 0
