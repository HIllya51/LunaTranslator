from .opcodes import *
from .space import *
from .base import *


class Code:
    '''Can generate, store and run sequence of ops representing js code'''

    def __init__(self, is_strict=False, debug_mode=False):
        self.tape = []
        self.compiled = False
        self.label_locs = None
        self.is_strict = is_strict
        self.debug_mode = debug_mode

        self.contexts = []
        self.current_ctx = None
        self.return_locs = []
        self._label_count = 0
        self.label_locs = None

        # useful references
        self.GLOBAL_THIS = None
        self.space = None

        # dbg
        self.ctx_depth = 0


    def get_new_label(self):
        self._label_count += 1
        return self._label_count

    def emit(self, op_code, *args):
        ''' Adds op_code with specified args to tape '''
        self.tape.append(OP_CODES[op_code](*args))

    def compile(self, start_loc=0):
        ''' Records locations of labels and compiles the code '''
        self.label_locs = {} if self.label_locs is None else self.label_locs
        loc = start_loc
        while loc < len(self.tape):
            if type(self.tape[loc]) == LABEL:
                self.label_locs[self.tape[loc].num] = loc
                del self.tape[loc]
                continue
            loc += 1
        self.compiled = True

    def _call(self, func, this, args):
        ''' Calls a bytecode function func
            NOTE:  use !ONLY! when calling functions from native methods! '''
        assert not func.is_native
        # fake call - the the runner to return to the end of the file
        old_contexts = self.contexts
        old_return_locs = self.return_locs
        old_curr_ctx = self.current_ctx

        self.contexts = [FakeCtx()]
        self.return_locs = [len(self.tape)]  # target line after return

        # prepare my ctx
        my_ctx = func._generate_my_context(this, args)
        self.current_ctx = my_ctx

        # execute dunction
        ret = self.run(my_ctx, starting_loc=self.label_locs[func.code])

        # bring back old execution
        self.current_ctx = old_curr_ctx
        self.contexts = old_contexts
        self.return_locs = old_return_locs

        return ret

    def execute_fragment_under_context(self, ctx, start_label, end_label):
        ''' just like run but returns if moved outside of the specified fragment
            # 4 different exectution results
            # 0=normal, 1=return, 2=jump_outside, 3=errors
            # execute_fragment_under_context returns:
            # (return_value, typ, return_value/jump_loc/py_error)
            # IMPARTANT: It is guaranteed that the length of the ctx.stack is unchanged.
        '''
        old_curr_ctx = self.current_ctx
        self.ctx_depth += 1
        old_stack_len = len(ctx.stack)
        old_ret_len = len(self.return_locs)
        old_ctx_len = len(self.contexts)
        try:
            self.current_ctx = ctx
            return self._execute_fragment_under_context(
                ctx, start_label, end_label)
        except JsException as err:
            if self.debug_mode:
                self._on_fragment_exit("js errors")
            # undo the things that were put on the stack (if any) to ensure a proper error recovery
            del ctx.stack[old_stack_len:]
            del self.return_locs[old_ret_len:]
            del self.contexts[old_ctx_len :]
            return undefined, 3, err
        finally:
            self.ctx_depth -= 1
            self.current_ctx = old_curr_ctx
            assert old_stack_len == len(ctx.stack)

    def _get_dbg_indent(self):
        return self.ctx_depth * '  '

    def _on_fragment_exit(self, mode):
        print(self._get_dbg_indent() + 'ctx exit (%s)' % mode)

    def _execute_fragment_under_context(self, ctx, start_label, end_label):
        start, end = self.label_locs[start_label], self.label_locs[end_label]
        initial_len = len(ctx.stack)
        loc = start
        entry_level = len(self.contexts)
        # for e in self.tape[start:end]:
        #     print e
        if self.debug_mode:
            print(self._get_dbg_indent() + 'ctx entry (from:%d, to:%d)' % (start, end))
        while loc < len(self.tape):
            if len(self.contexts) == entry_level and loc >= end:
                if self.debug_mode:
                    self._on_fragment_exit('normal')
                assert loc == end
                delta_stack = len(ctx.stack) - initial_len
                assert delta_stack == +1, 'Stack change must be equal to +1! got %d' % delta_stack
                return ctx.stack.pop(), 0, None  # means normal return

            # execute instruction
            if self.debug_mode:
                print(self._get_dbg_indent() + str(loc), self.tape[loc])
            status = self.tape[loc].eval(ctx)

            # check status for special actions
            if status is not None:
                if type(status) == int:  # jump to label
                    loc = self.label_locs[status]
                    if len(self.contexts) == entry_level:
                        # check if jumped outside of the fragment and break if so
                        if not start <= loc < end:
                            if self.debug_mode:
                                self._on_fragment_exit('jump outside loc:%d label:%d' % (loc, status))
                            delta_stack = len(ctx.stack) - initial_len
                            assert delta_stack == +1, 'Stack change must be equal to +1! got %d' % delta_stack
                            return ctx.stack.pop(), 2, status  # jump outside
                    continue

                elif len(status) == 2:  # a call or a return!
                    # call: (new_ctx, func_loc_label_num)
                    if status[0] is not None:
                        # append old state to the stack
                        self.contexts.append(ctx)
                        self.return_locs.append(loc + 1)
                        # set new state
                        loc = self.label_locs[status[1]]
                        ctx = status[0]
                        self.current_ctx = ctx
                        continue

                    # return: (None, None)
                    else:
                        if len(self.contexts) == entry_level:
                            if self.debug_mode:
                                self._on_fragment_exit('return')
                            delta_stack = len(ctx.stack) - initial_len
                            assert delta_stack == +1, 'Stack change must be equal to +1! got %d' % delta_stack
                            return undefined, 1, ctx.stack.pop(
                            )  # return signal
                        return_value = ctx.stack.pop()
                        ctx = self.contexts.pop()
                        self.current_ctx = ctx
                        ctx.stack.append(return_value)

                        loc = self.return_locs.pop()
                        continue
            # next instruction
            loc += 1
        if self.debug_mode:
            self._on_fragment_exit('internal error - unexpected end of tape, will crash')
        assert False, 'Remember to add NOP at the end!'

    def run(self, ctx, starting_loc=0):
        loc = starting_loc
        self.current_ctx = ctx
        while loc < len(self.tape):
            # execute instruction
            if self.debug_mode:
                print(loc, self.tape[loc])
            status = self.tape[loc].eval(ctx)

            # check status for special actions
            if status is not None:
                if type(status) == int:  # jump to label
                    loc = self.label_locs[status]
                    continue

                elif len(status) == 2:  # a call or a return!
                    # call: (new_ctx, func_loc_label_num)
                    if status[0] is not None:
                        # append old state to the stack
                        self.contexts.append(ctx)
                        self.return_locs.append(loc + 1)
                        # set new state
                        loc = self.label_locs[status[1]]
                        ctx = status[0]
                        self.current_ctx = ctx
                        continue

                    # return: (None, None)
                    else:
                        return_value = ctx.stack.pop()
                        ctx = self.contexts.pop()
                        self.current_ctx = ctx
                        ctx.stack.append(return_value)

                        loc = self.return_locs.pop()
                        continue
            # next instruction
            loc += 1
        assert len(ctx.stack) == 1, ctx.stack
        return ctx.stack.pop()


class FakeCtx(object):
    def __init__(self):
        self.stack = []
