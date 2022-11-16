from ..base import *
from ..conversions import *
from ..func_utils import *
from pyjsparser import parse
from ..byte_trans import ByteCodeGenerator, Code


def Function(this, args):
    # convert arguments to python list of strings
    a = list(map(to_string, tuple(args)))
    _body = u';'
    _args = ()
    if len(a):
        _body = u'%s;' % a[-1]
        _args = a[:-1]
    return executable_function(_body, _args, args.space, global_context=True)


def executable_function(_body, _args, space, global_context=True):
    func_str = u'(function (%s) { ; %s ; });' % (u', '.join(_args), _body)

    co = executable_code(
        code_str=func_str, space=space, global_context=global_context)
    return co()


# you can use this one lovely piece of function to compile and execute code on the fly! Watch out though as it may generate lots of code.
# todo tape cleanup? we dont know which pieces are needed and which are not so rather impossible without smarter machinery something like GC,
# a one solution would be to have a separate tape for functions
def executable_code(code_str, space, global_context=True):
    # parse first to check if any SyntaxErrors
    parsed = parse(code_str)

    old_tape_len = len(space.byte_generator.exe.tape)
    space.byte_generator.record_state()
    start = space.byte_generator.exe.get_new_label()
    skip = space.byte_generator.exe.get_new_label()
    space.byte_generator.emit('JUMP', skip)
    space.byte_generator.emit('LABEL', start)
    space.byte_generator.emit(parsed)
    space.byte_generator.emit('NOP')
    space.byte_generator.emit('LABEL', skip)
    space.byte_generator.emit('NOP')
    space.byte_generator.restore_state()

    space.byte_generator.exe.compile(
        start_loc=old_tape_len
    )  # dont read the code from the beginning, dont be stupid!

    ctx = space.GlobalObj if global_context else space.exe.current_ctx

    def ex_code():
        ret, status, token = space.byte_generator.exe.execute_fragment_under_context(
            ctx, start, skip)
        # todo Clean up the tape!
        # this is NOT a way to do that because the fragment may contain the executable code! We dont want to remove it
        #del space.byte_generator.exe.tape[old_tape_len:]
        if status == 0:
            return ret
        elif status == 3:
            raise token
        else:
            raise RuntimeError(
                'Unexpected return status during JIT execution: %d' % status)

    return ex_code


def _eval(this, args):
    code_str = to_string(get_arg(args, 0))
    return executable_code(code_str, args.space, global_context=True)()


def log(this, args):
    print(' '.join(map(to_string, args)))
    return undefined
