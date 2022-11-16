__all__ = ['fix_js_args']

import types
from collections import namedtuple
import opcode
import six
import sys
import dis

if six.PY3:
    xrange = range
    chr = lambda x: x

# Opcode constants used for comparison and replacecment
LOAD_FAST = opcode.opmap['LOAD_FAST']
LOAD_GLOBAL = opcode.opmap['LOAD_GLOBAL']
STORE_FAST = opcode.opmap['STORE_FAST']


def fix_js_args(func):
    '''Use this function when unsure whether func takes this and arguments as its last 2 args.
       It will append 2 args if it does not.'''
    fcode = six.get_function_code(func)
    fargs = fcode.co_varnames[fcode.co_argcount - 2:fcode.co_argcount]
    if fargs == ('this', 'arguments') or fargs == ('arguments', 'var'):
        return func
    code = append_arguments(six.get_function_code(func), ('this', 'arguments'))

    return types.FunctionType(
        code,
        six.get_function_globals(func),
        func.__name__,
        closure=six.get_function_closure(func))


def append_arguments(code_obj, new_locals):
    co_varnames = code_obj.co_varnames  # Old locals
    co_names = code_obj.co_names  # Old globals
    co_names += tuple(e for e in new_locals if e not in co_names)
    co_argcount = code_obj.co_argcount  # Argument count
    co_code = code_obj.co_code  # The actual bytecode as a string

    # Make one pass over the bytecode to identify names that should be
    # left in code_obj.co_names.
    not_removed = set(opcode.hasname) - set([LOAD_GLOBAL])
    saved_names = set()
    for inst in instructions(code_obj):
        if inst[0] in not_removed:
            saved_names.add(co_names[inst[1]])

    # Build co_names for the new code object. This should consist of
    # globals that were only accessed via LOAD_GLOBAL
    names = tuple(
        name for name in co_names if name not in set(new_locals) - saved_names)

    # Build a dictionary that maps the indices of the entries in co_names
    # to their entry in the new co_names
    name_translations = dict(
        (co_names.index(name), i) for i, name in enumerate(names))

    # Build co_varnames for the new code object. This should consist of
    # the entirety of co_varnames with new_locals spliced in after the
    # arguments
    new_locals_len = len(new_locals)
    varnames = (
        co_varnames[:co_argcount] + new_locals + co_varnames[co_argcount:])

    # Build the dictionary that maps indices of entries in the old co_varnames
    # to their indices in the new co_varnames
    range1, range2 = xrange(co_argcount), xrange(co_argcount, len(co_varnames))
    varname_translations = dict((i, i) for i in range1)
    varname_translations.update((i, i + new_locals_len) for i in range2)

    # Build the dictionary that maps indices of deleted entries of co_names
    # to their indices in the new co_varnames
    names_to_varnames = dict(
        (co_names.index(name), varnames.index(name)) for name in new_locals)

    # Now we modify the actual bytecode
    modified = []
    for inst in instructions(code_obj):
        op, arg = inst.opcode, inst.arg
        # If the instruction is a LOAD_GLOBAL, we have to check to see if
        # it's one of the globals that we are replacing. Either way,
        # update its arg using the appropriate dict.
        if inst.opcode == LOAD_GLOBAL:
            if inst.arg in names_to_varnames:
                op = LOAD_FAST
                arg = names_to_varnames[inst.arg]
            elif inst.arg in name_translations:
                arg = name_translations[inst.arg]
            else:
                raise ValueError("a name was lost in translation")
        # If it accesses co_varnames or co_names then update its argument.
        elif inst.opcode in opcode.haslocal:
            arg = varname_translations[inst.arg]
        elif inst.opcode in opcode.hasname:
            arg = name_translations[inst.arg]
        modified.extend(write_instruction(op, arg))
    if six.PY2:
        code = ''.join(modified)
        args = (co_argcount + new_locals_len,
                code_obj.co_nlocals + new_locals_len, code_obj.co_stacksize,
                code_obj.co_flags, code, code_obj.co_consts, names, varnames,
                code_obj.co_filename, code_obj.co_name,
                code_obj.co_firstlineno, code_obj.co_lnotab,
                code_obj.co_freevars, code_obj.co_cellvars)
    else:
        code = bytes(modified)
        args = (co_argcount + new_locals_len, 0,
                code_obj.co_nlocals + new_locals_len, code_obj.co_stacksize,
                code_obj.co_flags, code, code_obj.co_consts, names, varnames,
                code_obj.co_filename, code_obj.co_name,
                code_obj.co_firstlineno, code_obj.co_lnotab,
                code_obj.co_freevars, code_obj.co_cellvars)

    # Done modifying codestring - make the code object
    if hasattr(code_obj, "replace"):
        # Python 3.8+
        return code_obj.replace(
            co_argcount=co_argcount + new_locals_len,
            co_nlocals=code_obj.co_nlocals + new_locals_len,
            co_code=code,
            co_names=names,
            co_varnames=varnames)
    else:
        return types.CodeType(*args)


def instructions(code_obj):
    # easy for python 3.4+
    if sys.version_info >= (3, 4):
        for inst in dis.Bytecode(code_obj):
            yield inst
    else:
        # otherwise we have to manually parse
        code = code_obj.co_code
        NewInstruction = namedtuple('Instruction', ('opcode', 'arg'))
        if six.PY2:
            code = map(ord, code)
        i, L = 0, len(code)
        extended_arg = 0
        while i < L:
            op = code[i]
            i += 1
            if op < opcode.HAVE_ARGUMENT:
                yield NewInstruction(op, None)
                continue
            oparg = code[i] + (code[i + 1] << 8) + extended_arg
            extended_arg = 0
            i += 2
            if op == opcode.EXTENDED_ARG:
                extended_arg = oparg << 16
                continue
            yield NewInstruction(op, oparg)


def write_instruction(op, arg):
    if sys.version_info < (3, 6):
        if arg is None:
            return [chr(op)]
        elif arg <= 65536:
            return [chr(op), chr(arg & 255), chr((arg >> 8) & 255)]
        elif arg <= 4294967296:
            return [
                chr(opcode.EXTENDED_ARG),
                chr((arg >> 16) & 255),
                chr((arg >> 24) & 255),
                chr(op),
                chr(arg & 255),
                chr((arg >> 8) & 255)
            ]
        else:
            raise ValueError("Invalid oparg: {0} is too large".format(oparg))
    else:  # python 3.6+ uses wordcode instead of bytecode and they already supply all the EXTENDEND_ARG ops :)
        if arg is None:
            return [chr(op), 0]
        return [chr(op), arg & 255]
        # the code below is for case when extended args are to be determined automatically
        # if op == opcode.EXTENDED_ARG:
        #     return []  # this will be added automatically
        # elif arg < 1 << 8:
        #     return [chr(op), arg]
        # elif arg < 1 << 32:
        #     subs = [1<<24, 1<<16, 1<<8]  # allowed op extension sizes
        #     for sub in subs:
        #         if arg >= sub:
        #             fit = int(arg / sub)
        #             return [chr(opcode.EXTENDED_ARG), fit]  + write_instruction(op, arg - fit * sub)
        # else:
        #     raise ValueError("Invalid oparg: {0} is too large".format(oparg))


def check(code_obj):
    old_bytecode = code_obj.co_code
    insts = list(instructions(code_obj))

    pos_to_inst = {}
    bytelist = []

    for inst in insts:
        pos_to_inst[len(bytelist)] = inst
        bytelist.extend(write_instruction(inst.opcode, inst.arg))
    if six.PY2:
        new_bytecode = ''.join(bytelist)
    else:
        new_bytecode = bytes(bytelist)
    if new_bytecode != old_bytecode:
        print(new_bytecode)
        print(old_bytecode)
        for i in range(min(len(new_bytecode), len(old_bytecode))):
            if old_bytecode[i] != new_bytecode[i]:
                while 1:
                    if i in pos_to_inst:
                        print(pos_to_inst[i])
                        print(pos_to_inst[i - 2])
                        print(list(map(chr, old_bytecode))[i - 4:i + 8])
                        print(bytelist[i - 4:i + 8])
                        break
            raise RuntimeError(
                'Your python version made changes to the bytecode')


check(six.get_function_code(check))

if __name__ == '__main__':
    x = 'Wrong'
    dick = 3000

    def func(a):
        print(x, y, z, a)
        print(dick)
        d = (x, )
        for e in (e for e in x):
            print(e)
        return x, y, z

    func2 = types.FunctionType(
        append_arguments(six.get_function_code(func), ('x', 'y', 'z')),
        six.get_function_globals(func),
        func.__name__,
        closure=six.get_function_closure(func))
    args = (2, 2, 3, 4), 3, 4
    assert func2(1, *args) == args
