from __future__ import unicode_literals
from ..conversions import *
from ..func_utils import *
from ..operations import strict_equality_op

import six

if six.PY3:
    xrange = range
    import functools

ARR_STACK = set({})


class ArrayPrototype:
    def toString(this, args):
        arr = to_object(this, args.space)
        func = arr.get('join')
        if not is_callable(func):
            return u'[object %s]' % GetClass(arr)
        return func.call(this, ())

    def toLocaleString(this, args):
        array = to_object(this, args.space)
        arr_len = js_arr_length(array)
        # separator is simply a comma ','
        if not arr_len:
            return ''
        res = []
        for i in xrange(arr_len):
            element = array.get(unicode(i))
            if is_undefined(element) or is_null(element):
                res.append('')
            else:
                cand = to_object(element, args.space)
                str_func = cand.get('toLocaleString')
                if not is_callable(str_func):
                    raise MakeError(
                        'TypeError',
                        'toLocaleString method of item at index %d is not callable'
                        % i)
                res.append(to_string(str_func.call(cand, ())))
        return ','.join(res)

    def concat(this, args):
        array = to_object(this, args.space)
        items = [array]
        items.extend(tuple(args))
        A = []
        for E in items:
            if GetClass(E) == 'Array':
                k = 0
                e_len = js_arr_length(E)
                while k < e_len:
                    if E.has_property(unicode(k)):
                        A.append(E.get(unicode(k)))
                    k += 1
            else:
                A.append(E)
        return args.space.ConstructArray(A)

    def join(this, args):
        ARR_STACK.add(this)
        array = to_object(this, args.space)
        separator = get_arg(args, 0)
        arr_len = js_arr_length(array)
        separator = ',' if is_undefined(separator) else to_string(separator)
        elems = []
        for e in xrange(arr_len):
            elem = array.get(unicode(e))
            if elem in ARR_STACK:
                s = ''
            else:
                s = to_string(elem)
            elems.append(
                s if not (is_undefined(elem) or is_null(elem)) else '')
        res = separator.join(elems)
        ARR_STACK.remove(this)
        return res

    def pop(this, args):  #todo check
        array = to_object(this, args.space)
        arr_len = js_arr_length(array)
        if not arr_len:
            array.put('length', float(arr_len))
            return undefined
        ind = unicode(arr_len - 1)
        element = array.get(ind)
        array.delete(ind)
        array.put('length', float(arr_len - 1))
        return element

    def push(this, args):
        array = to_object(this, args.space)
        arr_len = js_arr_length(array)
        to_put = tuple(args)
        i = arr_len
        for i, e in enumerate(to_put, arr_len):
            array.put(unicode(i), e, True)
        array.put('length', float(arr_len + len(to_put)), True)
        return float(i)

    def reverse(this, args):
        array = to_object(this, args.space)
        vals = js_array_to_list(array)
        has_props = [
            array.has_property(unicode(e))
            for e in xrange(js_arr_length(array))
        ]
        vals.reverse()
        has_props.reverse()
        for i, val in enumerate(vals):
            if has_props[i]:
                array.put(unicode(i), val)
            else:
                array.delete(unicode(i))
        return array

    def shift(this, args):
        array = to_object(this, args.space)
        arr_len = js_arr_length(array)
        if not arr_len:
            array.put('length', 0.)
            return undefined
        first = array.get('0')
        for k in xrange(1, arr_len):
            from_s, to_s = unicode(k), unicode(k - 1)
            if array.has_property(from_s):
                array.put(to_s, array.get(from_s))
            else:
                array.delete(to_s)
        array.delete(unicode(arr_len - 1))
        array.put('length', float(arr_len - 1))
        return first

    def slice(this, args):  # todo check
        array = to_object(this, args.space)
        start = get_arg(args, 0)
        end = get_arg(args, 1)
        arr_len = js_arr_length(array)
        relative_start = to_int(start)
        k = max((arr_len + relative_start), 0) if relative_start < 0 else min(
            relative_start, arr_len)
        relative_end = arr_len if is_undefined(end) else to_int(end)
        final = max((arr_len + relative_end), 0) if relative_end < 0 else min(
            relative_end, arr_len)
        res = []
        n = 0
        while k < final:
            pk = unicode(k)
            if array.has_property(pk):
                res.append(array.get(pk))
            k += 1
            n += 1
        return args.space.ConstructArray(res)

    def sort(
            this, args
    ):  # todo: this assumes array continous (not sparse) - fix for sparse arrays
        cmpfn = get_arg(args, 0)
        if not GetClass(this) in ('Array', 'Arguments'):
            return to_object(this, args.space)  # do nothing
        arr_len = js_arr_length(this)
        if not arr_len:
            return this
        arr = [
            (this.get(unicode(e)) if this.has_property(unicode(e)) else None)
            for e in xrange(arr_len)
        ]
        if not is_callable(cmpfn):
            cmpfn = None
        cmp = lambda a, b: sort_compare(a, b, cmpfn)
        if six.PY3:
            key = functools.cmp_to_key(cmp)
            arr.sort(key=key)
        else:
            arr.sort(cmp=cmp)
        for i in xrange(arr_len):
            if arr[i] is None:
                this.delete(unicode(i))
            else:
                this.put(unicode(i), arr[i])
        return this

    def splice(this, args):
        # 1-8
        array = to_object(this, args.space)
        start = get_arg(args, 0)
        deleteCount = get_arg(args, 1)
        arr_len = js_arr_length(this)
        relative_start = to_int(start)
        actual_start = max(
            (arr_len + relative_start), 0) if relative_start < 0 else min(
                relative_start, arr_len)
        actual_delete_count = min(
            max(to_int(deleteCount), 0), arr_len - actual_start)
        k = 0
        A = args.space.NewArray(0)
        # 9
        while k < actual_delete_count:
            if array.has_property(unicode(actual_start + k)):
                A.put(unicode(k), array.get(unicode(actual_start + k)))
            k += 1
        # 10-11
        items = list(args)[2:]
        items_len = len(items)
        # 12
        if items_len < actual_delete_count:
            k = actual_start
            while k < (arr_len - actual_delete_count):
                fr = unicode(k + actual_delete_count)
                to = unicode(k + items_len)
                if array.has_property(fr):
                    array.put(to, array.get(fr))
                else:
                    array.delete(to)
                k += 1
            k = arr_len
            while k > (arr_len - actual_delete_count + items_len):
                array.delete(unicode(k - 1))
                k -= 1
        # 13
        elif items_len > actual_delete_count:
            k = arr_len - actual_delete_count
            while k > actual_start:
                fr = unicode(k + actual_delete_count - 1)
                to = unicode(k + items_len - 1)
                if array.has_property(fr):
                    array.put(to, array.get(fr))
                else:
                    array.delete(to)
                k -= 1
        # 14-17
        k = actual_start
        while items:
            E = items.pop(0)
            array.put(unicode(k), E)
            k += 1
        array.put('length', float(arr_len - actual_delete_count + items_len))
        return A

    def unshift(this, args):
        array = to_object(this, args.space)
        arr_len = js_arr_length(array)
        argCount = len(args)
        k = arr_len
        while k > 0:
            fr = unicode(k - 1)
            to = unicode(k + argCount - 1)
            if array.has_property(fr):
                array.put(to, array.get(fr))
            else:
                array.delete(to)
            k -= 1
        items = tuple(args)
        for j, e in enumerate(items):
            array.put(unicode(j), e)
        array.put('length', float(arr_len + argCount))
        return float(arr_len + argCount)

    def indexOf(this, args):
        array = to_object(this, args.space)
        searchElement = get_arg(args, 0)
        arr_len = js_arr_length(array)
        if arr_len == 0:
            return -1.
        if len(args) > 1:
            n = to_int(args[1])
        else:
            n = 0
        if n >= arr_len:
            return -1.
        if n >= 0:
            k = n
        else:
            k = arr_len - abs(n)
            if k < 0:
                k = 0
        while k < arr_len:
            if array.has_property(unicode(k)):
                elementK = array.get(unicode(k))
                if strict_equality_op(searchElement, elementK):
                    return float(k)
            k += 1
        return -1.

    def lastIndexOf(this, args):
        array = to_object(this, args.space)
        searchElement = get_arg(args, 0)
        arr_len = js_arr_length(array)
        if arr_len == 0:
            return -1.
        if len(args) > 1:
            n = to_int(args[1])
        else:
            n = arr_len - 1
        if n >= 0:
            k = min(n, arr_len - 1)
        else:
            k = arr_len - abs(n)
        while k >= 0:
            if array.has_property(unicode(k)):
                elementK = array.get(unicode(k))
                if strict_equality_op(searchElement, elementK):
                    return float(k)
            k -= 1
        return -1.

    def every(this, args):
        array = to_object(this, args.space)
        callbackfn = get_arg(args, 0)
        arr_len = js_arr_length(array)
        if not is_callable(callbackfn):
            raise MakeError('TypeError', 'callbackfn must be a function')
        T = get_arg(args, 1)
        k = 0
        while k < arr_len:
            if array.has_property(unicode(k)):
                kValue = array.get(unicode(k))
                if not to_boolean(
                        callbackfn.call(T, (kValue, float(k), array))):
                    return False
            k += 1
        return True

    def some(this, args):
        array = to_object(this, args.space)
        callbackfn = get_arg(args, 0)
        arr_len = js_arr_length(array)
        if not is_callable(callbackfn):
            raise MakeError('TypeError', 'callbackfn must be a function')
        T = get_arg(args, 1)
        k = 0
        while k < arr_len:
            if array.has_property(unicode(k)):
                kValue = array.get(unicode(k))
                if to_boolean(callbackfn.call(T, (kValue, float(k), array))):
                    return True
            k += 1
        return False

    def forEach(this, args):
        array = to_object(this, args.space)
        callbackfn = get_arg(args, 0)
        arr_len = js_arr_length(array)
        if not is_callable(callbackfn):
            raise MakeError('TypeError', 'callbackfn must be a function')
        _this = get_arg(args, 1)
        k = 0
        while k < arr_len:
            sk = unicode(k)
            if array.has_property(sk):
                kValue = array.get(sk)
                callbackfn.call(_this, (kValue, float(k), array))
            k += 1
        return undefined

    def map(this, args):
        array = to_object(this, args.space)
        callbackfn = get_arg(args, 0)
        arr_len = js_arr_length(array)
        if not is_callable(callbackfn):
            raise MakeError('TypeError', 'callbackfn must be a function')
        _this = get_arg(args, 1)
        k = 0
        A = args.space.NewArray(0)
        while k < arr_len:
            Pk = unicode(k)
            if array.has_property(Pk):
                kValue = array.get(Pk)
                mappedValue = callbackfn.call(_this, (kValue, float(k), array))
                A.define_own_property(
                    Pk, {
                        'value': mappedValue,
                        'writable': True,
                        'enumerable': True,
                        'configurable': True
                    }, False)
            k += 1
        return A

    def filter(this, args):
        array = to_object(this, args.space)
        callbackfn = get_arg(args, 0)
        arr_len = js_arr_length(array)
        if not is_callable(callbackfn):
            raise MakeError('TypeError', 'callbackfn must be a function')
        _this = get_arg(args, 1)
        k = 0
        res = []
        while k < arr_len:
            if array.has_property(unicode(k)):
                kValue = array.get(unicode(k))
                if to_boolean(
                        callbackfn.call(_this, (kValue, float(k), array))):
                    res.append(kValue)
            k += 1
        return args.space.ConstructArray(res)

    def reduce(this, args):
        array = to_object(this, args.space)
        callbackfn = get_arg(args, 0)
        arr_len = js_arr_length(array)
        if not is_callable(callbackfn):
            raise MakeError('TypeError', 'callbackfn must be a function')
        if not arr_len and len(args) < 2:
            raise MakeError('TypeError',
                            'Reduce of empty array with no initial value')
        k = 0
        accumulator = undefined
        if len(args) > 1:  # initial value present
            accumulator = args[1]
        else:
            kPresent = False
            while not kPresent and k < arr_len:
                kPresent = array.has_property(unicode(k))
                if kPresent:
                    accumulator = array.get(unicode(k))
                k += 1
            if not kPresent:
                raise MakeError('TypeError',
                                'Reduce of empty array with no initial value')
        while k < arr_len:
            if array.has_property(unicode(k)):
                kValue = array.get(unicode(k))
                accumulator = callbackfn.call(
                    undefined, (accumulator, kValue, float(k), array))
            k += 1
        return accumulator

    def reduceRight(this, args):
        array = to_object(this, args.space)
        callbackfn = get_arg(args, 0)
        arr_len = js_arr_length(array)
        if not is_callable(callbackfn):
            raise MakeError('TypeError', 'callbackfn must be a function')
        if not arr_len and len(args) < 2:
            raise MakeError('TypeError',
                            'Reduce of empty array with no initial value')
        k = arr_len - 1
        accumulator = undefined

        if len(args) > 1:  # initial value present
            accumulator = args[1]
        else:
            kPresent = False
            while not kPresent and k >= 0:
                kPresent = array.has_property(unicode(k))
                if kPresent:
                    accumulator = array.get(unicode(k))
                k -= 1
            if not kPresent:
                raise MakeError('TypeError',
                                'Reduce of empty array with no initial value')
        while k >= 0:
            if array.has_property(unicode(k)):
                kValue = array.get(unicode(k))
                accumulator = callbackfn.call(
                    undefined, (accumulator, kValue, float(k), array))
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
    if is_undefined(a):
        if is_undefined(b):
            return 0
        return 1
    if is_undefined(b):
        if is_undefined(a):
            return 0
        return -1
    if comp is not None:
        res = comp.call(undefined, (a, b))
        return to_int(res)
    x, y = to_string(a), to_string(b)
    if x < y:
        return -1
    elif x > y:
        return 1
    return 0
