from .operations import *
from .base import get_member, get_member_dot, PyJsFunction, Scope


class OP_CODE(object):
    _params = []

    # def eval(self, ctx):
    #     raise

    def __repr__(self):
        return self.__class__.__name__ + str(
            tuple([getattr(self, e) for e in self._params]))


# --------------------- UNARY ----------------------


class UNARY_OP(OP_CODE):
    _params = ['operator']

    def __init__(self, operator):
        self.operator = operator

    def eval(self, ctx):
        val = ctx.stack.pop()
        ctx.stack.append(UNARY_OPERATIONS[self.operator](val))


# special unary operations


class TYPEOF(OP_CODE):
    _params = ['identifier']

    def __init__(self, identifier):
        self.identifier = identifier

    def eval(self, ctx):
        # typeof something_undefined  does not throw reference error
        val = ctx.get(self.identifier,
                      False)  # <= this makes it slightly different!
        ctx.stack.append(typeof_uop(val))


class POSTFIX(OP_CODE):
    _params = ['cb', 'ca', 'identifier']

    def __init__(self, post, incr, identifier):
        self.identifier = identifier
        self.cb = 1 if incr else -1
        self.ca = -self.cb if post else 0

    def eval(self, ctx):
        target = to_number(ctx.get(self.identifier)) + self.cb
        ctx.put(self.identifier, target)
        ctx.stack.append(target + self.ca)


class POSTFIX_MEMBER(OP_CODE):
    _params = ['cb', 'ca']

    def __init__(self, post, incr):
        self.cb = 1 if incr else -1
        self.ca = -self.cb if post else 0

    def eval(self, ctx):
        name = ctx.stack.pop()
        left = ctx.stack.pop()

        target = to_number(get_member(left, name, ctx.space)) + self.cb
        if type(left) not in PRIMITIVES:
            left.put_member(name, target)

        ctx.stack.append(target + self.ca)


class POSTFIX_MEMBER_DOT(OP_CODE):
    _params = ['cb', 'ca', 'prop']

    def __init__(self, post, incr, prop):
        self.cb = 1 if incr else -1
        self.ca = -self.cb if post else 0
        self.prop = prop

    def eval(self, ctx):
        left = ctx.stack.pop()

        target = to_number(get_member_dot(left, self.prop,
                                          ctx.space)) + self.cb
        if type(left) not in PRIMITIVES:
            left.put(self.prop, target)

        ctx.stack.append(target + self.ca)


class DELETE(OP_CODE):
    _params = ['name']

    def __init__(self, name):
        self.name = name

    def eval(self, ctx):
        ctx.stack.append(ctx.delete(self.name))


class DELETE_MEMBER(OP_CODE):
    def eval(self, ctx):
        prop = to_string(ctx.stack.pop())
        obj = to_object(ctx.stack.pop(), ctx)
        ctx.stack.append(obj.delete(prop, False))


# --------------------- BITWISE ----------------------


class BINARY_OP(OP_CODE):
    _params = ['operator']

    def __init__(self, operator):
        self.operator = operator

    def eval(self, ctx):
        right = ctx.stack.pop()
        left = ctx.stack.pop()
        ctx.stack.append(BINARY_OPERATIONS[self.operator](left, right))


# &&, || and conditional are implemented in bytecode

# --------------------- JUMPS ----------------------


# simple label that will be removed from code after compilation. labels ID will be translated
# to source code position.
class LABEL(OP_CODE):
    _params = ['num']

    def __init__(self, num):
        self.num = num


# I implemented interpreter in the way that when an integer is returned by eval operation the execution will jump
# to the location of the label (it is loc = label_locations[label])


class BASE_JUMP(OP_CODE):
    _params = ['label']

    def __init__(self, label):
        self.label = label


class JUMP(BASE_JUMP):
    def eval(self, ctx):
        return self.label


class JUMP_IF_TRUE(BASE_JUMP):
    def eval(self, ctx):
        val = ctx.stack.pop()
        if to_boolean(val):
            return self.label


class JUMP_IF_EQ(BASE_JUMP):
    # this one is used in switch statement - compares last 2 values using === operator and jumps popping both if true else pops last.
    def eval(self, ctx):
        cmp = ctx.stack.pop()
        if strict_equality_op(ctx.stack[-1], cmp):
            ctx.stack.pop()
            return self.label


class JUMP_IF_TRUE_WITHOUT_POP(BASE_JUMP):
    def eval(self, ctx):
        val = ctx.stack[-1]
        if to_boolean(val):
            return self.label


class JUMP_IF_FALSE(BASE_JUMP):
    def eval(self, ctx):
        val = ctx.stack.pop()
        if not to_boolean(val):
            return self.label


class JUMP_IF_FALSE_WITHOUT_POP(BASE_JUMP):
    def eval(self, ctx):
        val = ctx.stack[-1]
        if not to_boolean(val):
            return self.label


class POP(OP_CODE):
    def eval(self, ctx):
        # todo remove this check later
        assert len(ctx.stack), 'Popped from empty stack!'
        del ctx.stack[-1]


# class REDUCE(OP_CODE):
#     def eval(self, ctx):
#         assert len(ctx.stack)==2
#         ctx.stack[0] = ctx.stack[1]
#         del ctx.stack[1]

# --------------- LOADING --------------


class LOAD_NONE(OP_CODE):  # be careful with this :)
    _params = []

    def eval(self, ctx):
        ctx.stack.append(None)


class LOAD_N_TUPLE(
        OP_CODE
):  # loads the tuple composed of n last elements on stack. elements are popped.
    _params = ['n']

    def __init__(self, n):
        self.n = n

    def eval(self, ctx):
        tup = tuple(ctx.stack[-self.n:])
        del ctx.stack[-self.n:]
        ctx.stack.append(tup)


class LOAD_UNDEFINED(OP_CODE):
    def eval(self, ctx):
        ctx.stack.append(undefined)


class LOAD_NULL(OP_CODE):
    def eval(self, ctx):
        ctx.stack.append(null)


class LOAD_BOOLEAN(OP_CODE):
    _params = ['val']

    def __init__(self, val):
        assert val in (0, 1)
        self.val = bool(val)

    def eval(self, ctx):
        ctx.stack.append(self.val)


class LOAD_STRING(OP_CODE):
    _params = ['val']

    def __init__(self, val):
        assert isinstance(val, basestring)
        self.val = unicode(val)

    def eval(self, ctx):
        ctx.stack.append(self.val)


class LOAD_NUMBER(OP_CODE):
    _params = ['val']

    def __init__(self, val):
        assert isinstance(val, (float, int, long))
        self.val = float(val)

    def eval(self, ctx):
        ctx.stack.append(self.val)


class LOAD_REGEXP(OP_CODE):
    _params = ['body', 'flags']

    def __init__(self, body, flags):
        self.body = body
        self.flags = flags

    def eval(self, ctx):
        # we have to generate a new regexp - they are mutable
        ctx.stack.append(ctx.space.NewRegExp(self.body, self.flags))


class LOAD_FUNCTION(OP_CODE):
    _params = ['start', 'params', 'name', 'is_declaration', 'definitions']

    def __init__(self, start, params, name, is_declaration, definitions):
        assert type(start) == int
        self.start = start  # its an ID of label pointing to the beginning of the function bytecode
        self.params = params
        self.name = name
        self.is_declaration = bool(is_declaration)
        self.definitions = tuple(set(definitions + params))

    def eval(self, ctx):
        ctx.stack.append(
            ctx.space.NewFunction(self.start, ctx, self.params, self.name,
                                  self.is_declaration, self.definitions))


class LOAD_OBJECT(OP_CODE):
    _params = [
        'props'
    ]  # props are py string pairs (prop_name, kind): kind can be either i, g or s. (init, get, set)

    def __init__(self, props):
        self.num = len(props)
        self.props = props

    def eval(self, ctx):
        obj = ctx.space.NewObject()
        if self.num:
            obj._init(self.props, ctx.stack[-self.num:])
            del ctx.stack[-self.num:]

        ctx.stack.append(obj)


class LOAD_ARRAY(OP_CODE):
    _params = ['num']

    def __init__(self, num):
        self.num = num

    def eval(self, ctx):
        arr = ctx.space.NewArray(self.num)
        if self.num:
            arr._init(ctx.stack[-self.num:])
            del ctx.stack[-self.num:]
        ctx.stack.append(arr)


class LOAD_THIS(OP_CODE):
    def eval(self, ctx):
        ctx.stack.append(ctx.THIS_BINDING)


class LOAD(OP_CODE):  # todo check!
    _params = ['identifier']

    def __init__(self, identifier):
        self.identifier = identifier

    # 11.1.2
    def eval(self, ctx):
        ctx.stack.append(ctx.get(self.identifier, throw=True))


class LOAD_MEMBER(OP_CODE):
    def eval(self, ctx):
        prop = ctx.stack.pop()
        obj = ctx.stack.pop()
        ctx.stack.append(get_member(obj, prop, ctx.space))


class LOAD_MEMBER_DOT(OP_CODE):
    _params = ['prop']

    def __init__(self, prop):
        self.prop = prop

    def eval(self, ctx):
        obj = ctx.stack.pop()
        ctx.stack.append(get_member_dot(obj, self.prop, ctx.space))


# --------------- STORING --------------


class STORE(OP_CODE):
    _params = ['identifier']

    def __init__(self, identifier):
        self.identifier = identifier

    def eval(self, ctx):
        value = ctx.stack[-1]  # don't pop
        ctx.put(self.identifier, value)


class STORE_MEMBER(OP_CODE):
    def eval(self, ctx):
        value = ctx.stack.pop()
        name = ctx.stack.pop()
        left = ctx.stack.pop()

        typ = type(left)
        if typ in PRIMITIVES:
            prop = to_string(name)
            if typ == NULL_TYPE:
                raise MakeError('TypeError',
                                "Cannot set property '%s' of null" % prop)
            elif typ == UNDEFINED_TYPE:
                raise MakeError('TypeError',
                                "Cannot set property '%s' of undefined" % prop)
            # just ignore...
        else:
            left.put_member(name, value)

        ctx.stack.append(value)


class STORE_MEMBER_DOT(OP_CODE):
    _params = ['prop']

    def __init__(self, prop):
        self.prop = prop

    def eval(self, ctx):
        value = ctx.stack.pop()
        left = ctx.stack.pop()

        typ = type(left)
        if typ in PRIMITIVES:
            if typ == NULL_TYPE:
                raise MakeError('TypeError',
                                "Cannot set property '%s' of null" % self.prop)
            elif typ == UNDEFINED_TYPE:
                raise MakeError(
                    'TypeError',
                    "Cannot set property '%s' of undefined" % self.prop)
            # just ignore...
        else:
            left.put(self.prop, value)
        ctx.stack.append(value)


class STORE_OP(OP_CODE):
    _params = ['identifier', 'op']

    def __init__(self, identifier, op):
        self.identifier = identifier
        self.op = op

    def eval(self, ctx):
        value = ctx.stack.pop()
        new_value = BINARY_OPERATIONS[self.op](ctx.get(self.identifier), value)
        ctx.put(self.identifier, new_value)
        ctx.stack.append(new_value)


class STORE_MEMBER_OP(OP_CODE):
    _params = ['op']

    def __init__(self, op):
        self.op = op

    def eval(self, ctx):
        value = ctx.stack.pop()
        name = ctx.stack.pop()
        left = ctx.stack.pop()

        typ = type(left)
        if typ in PRIMITIVES:
            if typ is NULL_TYPE:
                raise MakeError(
                    'TypeError',
                    "Cannot set property '%s' of null" % to_string(name))
            elif typ is UNDEFINED_TYPE:
                raise MakeError(
                    'TypeError',
                    "Cannot set property '%s' of undefined" % to_string(name))
            ctx.stack.append(BINARY_OPERATIONS[self.op](get_member(
                left, name, ctx.space), value))
            return
        else:
            ctx.stack.append(BINARY_OPERATIONS[self.op](get_member(
                left, name, ctx.space), value))
            left.put_member(name, ctx.stack[-1])


class STORE_MEMBER_DOT_OP(OP_CODE):
    _params = ['prop', 'op']

    def __init__(self, prop, op):
        self.prop = prop
        self.op = op

    def eval(self, ctx):
        value = ctx.stack.pop()
        left = ctx.stack.pop()

        typ = type(left)
        if typ in PRIMITIVES:
            if typ == NULL_TYPE:
                raise MakeError('TypeError',
                                "Cannot set property '%s' of null" % self.prop)
            elif typ == UNDEFINED_TYPE:
                raise MakeError(
                    'TypeError',
                    "Cannot set property '%s' of undefined" % self.prop)
            ctx.stack.append(BINARY_OPERATIONS[self.op](get_member_dot(
                left, self.prop, ctx.space), value))
            return
        else:
            ctx.stack.append(BINARY_OPERATIONS[self.op](get_member_dot(
                left, self.prop, ctx.space), value))
            left.put(self.prop, ctx.stack[-1])


# --------------- CALLS --------------


def bytecode_call(ctx, func, this, args):
    if type(func) is not PyJsFunction:
        raise MakeError('TypeError', "%s is not a function" % Type(func))
    if func.is_native:  # call to built-in function or method
        ctx.stack.append(func.call(this, args))
        return None

    # therefore not native. we have to return (new_context, function_label) to instruct interpreter to call
    return func._generate_my_context(this, args), func.code


class CALL(OP_CODE):
    def eval(self, ctx):
        args = ctx.stack.pop()
        func = ctx.stack.pop()

        return bytecode_call(ctx, func, ctx.space.GlobalObj, args)


class CALL_METHOD(OP_CODE):
    def eval(self, ctx):
        args = ctx.stack.pop()
        prop = ctx.stack.pop()
        base = ctx.stack.pop()

        func = get_member(base, prop, ctx.space)

        return bytecode_call(ctx, func, base, args)


class CALL_METHOD_DOT(OP_CODE):
    _params = ['prop']

    def __init__(self, prop):
        self.prop = prop

    def eval(self, ctx):
        args = ctx.stack.pop()
        base = ctx.stack.pop()

        func = get_member_dot(base, self.prop, ctx.space)

        return bytecode_call(ctx, func, base, args)


class CALL_NO_ARGS(OP_CODE):
    def eval(self, ctx):
        func = ctx.stack.pop()

        return bytecode_call(ctx, func, ctx.space.GlobalObj, ())


class CALL_METHOD_NO_ARGS(OP_CODE):
    def eval(self, ctx):
        prop = ctx.stack.pop()
        base = ctx.stack.pop()

        func = get_member(base, prop, ctx.space)

        return bytecode_call(ctx, func, base, ())


class CALL_METHOD_DOT_NO_ARGS(OP_CODE):
    _params = ['prop']

    def __init__(self, prop):
        self.prop = prop

    def eval(self, ctx):
        base = ctx.stack.pop()

        func = get_member_dot(base, self.prop, ctx.space)

        return bytecode_call(ctx, func, base, ())


class NOP(OP_CODE):
    def eval(self, ctx):
        pass


class RETURN(OP_CODE):
    def eval(
            self, ctx
    ):  # remember to load the return value on stack before using RETURN op.
        return (None, None)


class NEW(OP_CODE):
    def eval(self, ctx):
        args = ctx.stack.pop()
        constructor = ctx.stack.pop()
        if type(constructor) in PRIMITIVES or not hasattr(
                constructor, 'create'):
            raise MakeError('TypeError',
                            '%s is not a constructor' % Type(constructor))
        ctx.stack.append(constructor.create(args, space=ctx.space))


class NEW_NO_ARGS(OP_CODE):
    def eval(self, ctx):
        constructor = ctx.stack.pop()
        if type(constructor) in PRIMITIVES or not hasattr(
                constructor, 'create'):
            raise MakeError('TypeError',
                            '%s is not a constructor' % Type(constructor))
        ctx.stack.append(constructor.create((), space=ctx.space))


# --------------- EXCEPTIONS --------------


class THROW(OP_CODE):
    def eval(self, ctx):
        raise MakeError(None, None, ctx.stack.pop())


class TRY_CATCH_FINALLY(OP_CODE):
    _params = [
        'try_label', 'catch_label', 'catch_variable', 'finally_label',
        'finally_present', 'end_label'
    ]

    def __init__(self, try_label, catch_label, catch_variable, finally_label,
                 finally_present, end_label):
        self.try_label = try_label
        self.catch_label = catch_label
        self.catch_variable = catch_variable
        self.finally_label = finally_label
        self.finally_present = finally_present
        self.end_label = end_label

    def eval(self, ctx):
        # 4 different exectution results
        # 0=normal, 1=return, 2=jump_outside, 3=errors
        # execute_fragment_under_context returns:
        # (return_value, typ, jump_loc/error)

        ctx.stack.pop()

        # execute try statement
        try_status = ctx.space.exe.execute_fragment_under_context(
            ctx, self.try_label, self.catch_label)

        errors = try_status[1] == 3

        # catch
        if errors and self.catch_variable is not None:
            # generate catch block context...
            catch_context = Scope({
                self.catch_variable:
                try_status[2].get_thrown_value(ctx.space)
            }, ctx.space, ctx)
            catch_context.THIS_BINDING = ctx.THIS_BINDING
            catch_status = ctx.space.exe.execute_fragment_under_context(
                catch_context, self.catch_label, self.finally_label)
        else:
            catch_status = None

        # finally
        if self.finally_present:
            finally_status = ctx.space.exe.execute_fragment_under_context(
                ctx, self.finally_label, self.end_label)
        else:
            finally_status = None

        # now return controls
        other_status = catch_status or try_status
        if finally_status is None or (finally_status[1] == 0
                                      and other_status[1] != 0):
            winning_status = other_status
        else:
            winning_status = finally_status

        val, typ, spec = winning_status
        if typ == 0:  # normal
            ctx.stack.append(val)
            return
        elif typ == 1:  # return
            ctx.stack.append(spec)
            return None, None  # send return signal
        elif typ == 2:  # jump outside
            ctx.stack.append(val)
            return spec
        elif typ == 3:
            # throw is made with empty stack as usual
            raise spec
        else:
            raise RuntimeError('Invalid return code')


# ------------ WITH + ITERATORS ----------


class WITH(OP_CODE):
    _params = ['beg_label', 'end_label']

    def __init__(self, beg_label, end_label):
        self.beg_label = beg_label
        self.end_label = end_label

    def eval(self, ctx):
        obj = to_object(ctx.stack.pop(), ctx.space)

        with_context = Scope(
            obj, ctx.space, ctx)  # todo actually use the obj to modify the ctx
        with_context.THIS_BINDING = ctx.THIS_BINDING
        status = ctx.space.exe.execute_fragment_under_context(
            with_context, self.beg_label, self.end_label)

        val, typ, spec = status

        if typ != 3:  # exception
            ctx.stack.pop()

        if typ == 0:  # normal
            ctx.stack.append(val)
            return
        elif typ == 1:  # return
            ctx.stack.append(spec)
            return None, None  # send return signal
        elif typ == 2:  # jump outside
            ctx.stack.append(val)
            return spec
        elif typ == 3:  # exception
            # throw is made with empty stack as usual
            raise spec
        else:
            raise RuntimeError('Invalid return code')


class FOR_IN(OP_CODE):
    _params = ['name', 'body_start_label', 'continue_label', 'break_label']

    def __init__(self, name, body_start_label, continue_label, break_label):
        self.name = name
        self.body_start_label = body_start_label
        self.continue_label = continue_label
        self.break_label = break_label

    def eval(self, ctx):
        iterable = ctx.stack.pop()
        if is_null(iterable) or is_undefined(iterable):
            ctx.stack.pop()
            ctx.stack.append(undefined)
            return self.break_label

        obj = to_object(iterable, ctx.space)

        for e in sorted(obj.own):
            if not obj.own[e]['enumerable']:
                continue

            ctx.put(
                self.name, e
            )  # JS would have been so much nicer if this was ctx.space.put(self.name, obj.get(e))

            # evaluate the body
            status = ctx.space.exe.execute_fragment_under_context(
                ctx, self.body_start_label, self.break_label)

            val, typ, spec = status

            if typ != 3:  # exception
                ctx.stack.pop()

            if typ == 0:  # normal
                ctx.stack.append(val)
                continue
            elif typ == 1:  # return
                ctx.stack.append(spec)
                return None, None  # send return signal
            elif typ == 2:  # jump outside
                # now have to figure out whether this is a continue or something else...
                ctx.stack.append(val)
                if spec == self.continue_label:
                    # just a continue, perform next iteration as normal
                    continue
                return spec  # break or smth, go there and finish the iteration
            elif typ == 3:  # exception
                # throw is made with empty stack as usual
                raise spec
            else:
                raise RuntimeError('Invalid return code')

        return self.break_label


# all opcodes...
OP_CODES = {}
g = ''
for g in globals():
    try:
        if not issubclass(globals()[g], OP_CODE) or g is 'OP_CODE':
            continue
    except:
        continue
    OP_CODES[g] = globals()[g]
