from .code import Code
from .simplex import MakeError
from .opcodes import *
from .operations import *
from .trans_utils import *

SPECIAL_IDENTIFIERS = {'true', 'false', 'this'}


class ByteCodeGenerator:
    def __init__(self, exe):
        self.exe = exe

        self.declared_continue_labels = {}
        self.declared_break_labels = {}

        self.implicit_breaks = []
        self.implicit_continues = []

        self.declared_vars = []

        self.function_declaration_tape = []

        self.states = []

    def record_state(self):
        self.states.append(
            (self.declared_continue_labels, self.declared_break_labels,
             self.implicit_breaks, self.implicit_continues, self.declared_vars,
             self.function_declaration_tape))
        self.declared_continue_labels, self.declared_break_labels, \
        self.implicit_breaks, self.implicit_continues, \
        self.declared_vars, self.function_declaration_tape = {}, {}, [], [], [], []

    def restore_state(self):
        self.declared_continue_labels, self.declared_break_labels, \
        self.implicit_breaks, self.implicit_continues, \
        self.declared_vars, self.function_declaration_tape = self.states.pop()

    def ArrayExpression(self, elements, **kwargs):
        for e in elements:
            if e is None:
                self.emit('LOAD_NONE')
            else:
                self.emit(e)
        self.emit('LOAD_ARRAY', len(elements))

    def AssignmentExpression(self, operator, left, right, **kwargs):
        operator = operator[:-1]
        if left['type'] == 'MemberExpression':
            self.emit(left['object'])
            if left['computed']:
                self.emit(left['property'])
                self.emit(right)
                if operator:
                    self.emit('STORE_MEMBER_OP', operator)
                else:
                    self.emit('STORE_MEMBER')
            else:
                self.emit(right)
                if operator:
                    self.emit('STORE_MEMBER_DOT_OP', left['property']['name'],
                              operator)
                else:
                    self.emit('STORE_MEMBER_DOT', left['property']['name'])
        elif left['type'] == 'Identifier':
            if left['name'] in SPECIAL_IDENTIFIERS:
                raise MakeError('SyntaxError',
                                'Invalid left-hand side in assignment')
            self.emit(right)
            if operator:
                self.emit('STORE_OP', left['name'], operator)
            else:
                self.emit('STORE', left['name'])
        else:
            raise MakeError('SyntaxError',
                            'Invalid left-hand side in assignment')

    def BinaryExpression(self, operator, left, right, **kwargs):
        self.emit(left)
        self.emit(right)
        self.emit('BINARY_OP', operator)

    def BlockStatement(self, body, **kwargs):
        self._emit_statement_list(body)

    def BreakStatement(self, label, **kwargs):
        if label is None:
            self.emit('JUMP', self.implicit_breaks[-1])
        else:
            label = label.get('name')
            if label not in self.declared_break_labels:
                raise MakeError('SyntaxError',
                                'Undefined label \'%s\'' % label)
            else:
                self.emit('JUMP', self.declared_break_labels[label])

    def CallExpression(self, callee, arguments, **kwargs):
        if callee['type'] == 'MemberExpression':
            self.emit(callee['object'])
            if callee['computed']:
                self.emit(callee['property'])
                if arguments:
                    for e in arguments:
                        self.emit(e)
                    self.emit('LOAD_N_TUPLE', len(arguments))
                    self.emit('CALL_METHOD')
                else:
                    self.emit('CALL_METHOD_NO_ARGS')
            else:
                prop_name = to_key(callee['property'])
                if arguments:
                    for e in arguments:
                        self.emit(e)
                    self.emit('LOAD_N_TUPLE', len(arguments))
                    self.emit('CALL_METHOD_DOT', prop_name)
                else:
                    self.emit('CALL_METHOD_DOT_NO_ARGS', prop_name)
        else:
            self.emit(callee)
            if arguments:
                for e in arguments:
                    self.emit(e)
                self.emit('LOAD_N_TUPLE', len(arguments))
                self.emit('CALL')
            else:
                self.emit('CALL_NO_ARGS')

    def ClassBody(self, body, **kwargs):
        raise NotImplementedError('Not available in ECMA 5.1')

    def ClassDeclaration(self, id, superClass, body, **kwargs):
        raise NotImplementedError('Not available in ECMA 5.1')

    def ClassExpression(self, id, superClass, body, **kwargs):
        raise NotImplementedError('Classes not available in ECMA 5.1')

    def ConditionalExpression(self, test, consequent, alternate, **kwargs):
        alt = self.exe.get_new_label()
        end = self.exe.get_new_label()
        # ?
        self.emit(test)
        self.emit('JUMP_IF_FALSE', alt)
        # first val
        self.emit(consequent)
        self.emit('JUMP', end)
        # second val
        self.emit('LABEL', alt)
        self.emit(alternate)
        # end of ?: statement
        self.emit('LABEL', end)

    def ContinueStatement(self, label, **kwargs):
        if label is None:
            self.emit('JUMP', self.implicit_continues[-1])
        else:
            label = label.get('name')
            if label not in self.declared_continue_labels:
                raise MakeError('SyntaxError',
                                'Undefined label \'%s\'' % label)
            else:
                self.emit('JUMP', self.declared_continue_labels[label])

    def DebuggerStatement(self, **kwargs):
        self.EmptyStatement(**kwargs)

    def DoWhileStatement(self, body, test, **kwargs):
        continue_label = self.exe.get_new_label()
        break_label = self.exe.get_new_label()
        initial_do = self.exe.get_new_label()

        self.emit('JUMP', initial_do)
        self.emit('LABEL', continue_label)
        self.emit(test)
        self.emit('JUMP_IF_FALSE', break_label)
        self.emit('LABEL', initial_do)

        # translate the body, remember to add and afterwards remove implicit break/continue labels

        self.implicit_continues.append(continue_label)
        self.implicit_breaks.append(break_label)
        self.emit(body)
        self.implicit_continues.pop()
        self.implicit_breaks.pop()

        self.emit('JUMP', continue_label)  # loop back
        self.emit('LABEL', break_label)

    def EmptyStatement(self, **kwargs):
        # do nothing
        pass

    def ExpressionStatement(self, expression, **kwargs):
        # change the final stack value
        # pop the previous value and execute expression
        self.emit('POP')
        self.emit(expression)

    def ForStatement(self, init, test, update, body, **kwargs):
        continue_label = self.exe.get_new_label()
        break_label = self.exe.get_new_label()
        first_start = self.exe.get_new_label()

        if init is not None:
            self.emit(init)
            if init['type'] != 'VariableDeclaration':
                self.emit('POP')

        # skip first update and go straight to test
        self.emit('JUMP', first_start)

        self.emit('LABEL', continue_label)
        if update:
            self.emit(update)
            self.emit('POP')
        self.emit('LABEL', first_start)
        if test:
            self.emit(test)
            self.emit('JUMP_IF_FALSE', break_label)

        # translate the body, remember to add and afterwards to remove implicit break/continue labels

        self.implicit_continues.append(continue_label)
        self.implicit_breaks.append(break_label)
        self.emit(body)
        self.implicit_continues.pop()
        self.implicit_breaks.pop()

        self.emit('JUMP', continue_label)  # loop back
        self.emit('LABEL', break_label)

    def ForInStatement(self, left, right, body, **kwargs):
        # prepare the needed labels
        body_start_label = self.exe.get_new_label()
        continue_label = self.exe.get_new_label()
        break_label = self.exe.get_new_label()

        # prepare the name
        if left['type'] == 'VariableDeclaration':
            if len(left['declarations']) != 1:
                raise MakeError(
                    'SyntaxError',
                    ' Invalid left-hand side in for-in loop: Must have a single binding.'
                )
            self.emit(left)
            name = left['declarations'][0]['id']['name']
        elif left['type'] == 'Identifier':
            name = left['name']
        else:
            raise MakeError('SyntaxError',
                            'Invalid left-hand side in for-loop')

        # prepare the iterable
        self.emit(right)

        # emit ForIn Opcode
        self.emit('FOR_IN', name, body_start_label, continue_label,
                  break_label)

        # a special continue position
        self.emit('LABEL', continue_label)
        self.emit('NOP')

        self.emit('LABEL', body_start_label)
        self.implicit_continues.append(continue_label)
        self.implicit_breaks.append(break_label)
        self.emit('LOAD_UNDEFINED')
        self.emit(body)
        self.implicit_continues.pop()
        self.implicit_breaks.pop()
        self.emit('NOP')
        self.emit('LABEL', break_label)
        self.emit('NOP')

    def FunctionDeclaration(self, id, params, defaults, body, **kwargs):
        if defaults:
            raise NotImplementedError('Defaults not available in ECMA 5.1')

        # compile function
        self.record_state(
        )  # cleans translator state and appends it to the stack so that it can be later restored
        function_start = self.exe.get_new_label()
        function_declarations = self.exe.get_new_label()
        declarations_done = self.exe.get_new_label(
        )  # put jump to this place at the and of function tape!
        function_end = self.exe.get_new_label()

        # skip the function if encountered externally
        self.emit('JUMP', function_end)

        self.emit('LABEL', function_start)
        # call is made with empty stack so load undefined to fill it
        self.emit('LOAD_UNDEFINED')
        # declare all functions
        self.emit('JUMP', function_declarations)
        self.emit('LABEL', declarations_done)
        self.function_declaration_tape.append(LABEL(function_declarations))

        self.emit(body)
        self.ReturnStatement(None)

        self.function_declaration_tape.append(JUMP(declarations_done))
        self.exe.tape.extend(self.function_declaration_tape)

        self.emit('LABEL', function_end)
        declared_vars = self.declared_vars
        self.restore_state()

        # create function object and append to stack
        name = id.get('name')
        assert name is not None
        self.declared_vars.append(name)
        self.function_declaration_tape.append(
            LOAD_FUNCTION(function_start, tuple(p['name'] for p in params),
                          name, True, tuple(declared_vars)))
        self.function_declaration_tape.append(STORE(name))
        self.function_declaration_tape.append(POP())

    def FunctionExpression(self, id, params, defaults, body, **kwargs):
        if defaults:
            raise NotImplementedError('Defaults not available in ECMA 5.1')

        # compile function
        self.record_state(
        )  # cleans translator state and appends it to the stack so that it can be later restored
        function_start = self.exe.get_new_label()
        function_declarations = self.exe.get_new_label()
        declarations_done = self.exe.get_new_label(
        )  # put jump to this place at the and of function tape!
        function_end = self.exe.get_new_label()

        # skip the function if encountered externally
        self.emit('JUMP', function_end)

        self.emit('LABEL', function_start)
        # call is made with empty stack so load undefined to fill it
        self.emit('LOAD_UNDEFINED')
        # declare all functions
        self.emit('JUMP', function_declarations)
        self.emit('LABEL', declarations_done)
        self.function_declaration_tape.append(LABEL(function_declarations))

        self.emit(body)
        self.ReturnStatement(None)

        self.function_declaration_tape.append(JUMP(declarations_done))
        self.exe.tape.extend(self.function_declaration_tape)

        self.emit('LABEL', function_end)
        declared_vars = self.declared_vars
        self.restore_state()

        # create function object and append to stack
        name = id.get('name') if id else None
        self.emit('LOAD_FUNCTION', function_start,
                  tuple(p['name'] for p in params), name, False,
                  tuple(declared_vars))

    def Identifier(self, name, **kwargs):
        if name == 'true':
            self.emit('LOAD_BOOLEAN', 1)
        elif name == 'false':
            self.emit('LOAD_BOOLEAN', 0)
        elif name == 'undefined':
            self.emit('LOAD_UNDEFINED')
        else:
            self.emit('LOAD', name)

    def IfStatement(self, test, consequent, alternate, **kwargs):
        alt = self.exe.get_new_label()
        end = self.exe.get_new_label()
        # if
        self.emit(test)
        self.emit('JUMP_IF_FALSE', alt)
        # consequent
        self.emit(consequent)
        self.emit('JUMP', end)
        # alternate
        self.emit('LABEL', alt)
        if alternate is not None:
            self.emit(alternate)
        # end of if statement
        self.emit('LABEL', end)

    def LabeledStatement(self, label, body, **kwargs):
        label = label['name']
        if body['type'] in ('WhileStatement', 'DoWhileStatement',
                            'ForStatement', 'ForInStatement'):
            # Continue label available... Simply take labels defined by the loop.
            # It is important that they request continue label first
            self.declared_continue_labels[label] = self.exe._label_count + 1
            self.declared_break_labels[label] = self.exe._label_count + 2
            self.emit(body)
            del self.declared_break_labels[label]
            del self.declared_continue_labels[label]
        else:
            # only break label available
            lbl = self.exe.get_new_label()
            self.declared_break_labels[label] = lbl
            self.emit(body)
            self.emit('LABEL', lbl)
            del self.declared_break_labels[label]

    def Literal(self, value, **kwargs):
        if value is None:
            self.emit('LOAD_NULL')
        elif isinstance(value, bool):
            self.emit('LOAD_BOOLEAN', int(value))
        elif isinstance(value, basestring):
            self.emit('LOAD_STRING', unicode(value))
        elif isinstance(value, (float, int, long)):
            self.emit('LOAD_NUMBER', float(value))
        elif isinstance(value, tuple):
            self.emit('LOAD_REGEXP', *value)
        else:
            raise RuntimeError('Unsupported literal')

    def LogicalExpression(self, left, right, operator, **kwargs):
        end = self.exe.get_new_label()
        if operator == '&&':
            # AND
            self.emit(left)
            self.emit('JUMP_IF_FALSE_WITHOUT_POP', end)
            self.emit('POP')
            self.emit(right)
            self.emit('LABEL', end)
        elif operator == '||':
            # OR
            self.emit(left)
            self.emit('JUMP_IF_TRUE_WITHOUT_POP', end)
            self.emit('POP')
            self.emit(right)
            self.emit('LABEL', end)
        else:
            raise RuntimeError("Unknown logical expression: %s" % operator)

    def MemberExpression(self, computed, object, property, **kwargs):
        if computed:
            self.emit(object)
            self.emit(property)
            self.emit('LOAD_MEMBER')
        else:
            self.emit(object)
            self.emit('LOAD_MEMBER_DOT', property['name'])

    def NewExpression(self, callee, arguments, **kwargs):
        self.emit(callee)
        if arguments:
            n = len(arguments)
            for e in arguments:
                self.emit(e)
            self.emit('LOAD_N_TUPLE', n)
            self.emit('NEW')
        else:
            self.emit('NEW_NO_ARGS')

    def ObjectExpression(self, properties, **kwargs):
        data = []
        for prop in properties:
            self.emit(prop['value'])
            if prop['computed']:
                raise NotImplementedError(
                    'ECMA 5.1 does not support computed object properties!')
            data.append((to_key(prop['key']), prop['kind'][0]))
        self.emit('LOAD_OBJECT', tuple(data))

    def Program(self, body, **kwargs):
        old_tape_len = len(self.exe.tape)
        self.emit('LOAD_UNDEFINED')
        self.emit(body)
        # add function tape !
        self.exe.tape = self.exe.tape[:old_tape_len] + self.function_declaration_tape + self.exe.tape[old_tape_len:]

    def Pyimport(self, imp, **kwargs):
        raise NotImplementedError(
            'Not available for bytecode interpreter yet, use the Js2Py translator.'
        )

    def Property(self, kind, key, computed, value, method, shorthand,
                 **kwargs):
        raise NotImplementedError('Not available in ECMA 5.1')

    def RestElement(self, argument, **kwargs):
        raise NotImplementedError('Not available in ECMA 5.1')

    def ReturnStatement(self, argument, **kwargs):
        self.emit('POP')  # pop result of expression statements
        if argument is None:
            self.emit('LOAD_UNDEFINED')
        else:
            self.emit(argument)
        self.emit('RETURN')

    def SequenceExpression(self, expressions, **kwargs):
        for e in expressions:
            self.emit(e)
            self.emit('POP')
        del self.exe.tape[-1]

    def SwitchCase(self, test, consequent, **kwargs):
        raise NotImplementedError('Already implemented in SwitchStatement')

    def SwitchStatement(self, discriminant, cases, **kwargs):
        self.emit(discriminant)
        labels = [self.exe.get_new_label() for case in cases]
        tests = [case['test'] for case in cases]
        consequents = [case['consequent'] for case in cases]
        end_of_switch = self.exe.get_new_label()

        # translate test cases
        for test, label in zip(tests, labels):
            if test is not None:
                self.emit(test)
                self.emit('JUMP_IF_EQ', label)
            else:
                self.emit('POP')
                self.emit('JUMP', label)
        # this will be executed if none of the cases worked
        self.emit('POP')
        self.emit('JUMP', end_of_switch)

        # translate consequents
        self.implicit_breaks.append(end_of_switch)
        for consequent, label in zip(consequents, labels):
            self.emit('LABEL', label)
            self._emit_statement_list(consequent)
        self.implicit_breaks.pop()

        self.emit('LABEL', end_of_switch)

    def ThisExpression(self, **kwargs):
        self.emit('LOAD_THIS')

    def ThrowStatement(self, argument, **kwargs):
        # throw with the empty stack
        self.emit('POP')
        self.emit(argument)
        self.emit('THROW')

    def TryStatement(self, block, handler, finalizer, **kwargs):
        try_label = self.exe.get_new_label()
        catch_label = self.exe.get_new_label()
        finally_label = self.exe.get_new_label()
        end_label = self.exe.get_new_label()

        self.emit('JUMP', end_label)

        # try block
        self.emit('LABEL', try_label)
        self.emit('LOAD_UNDEFINED')
        self.emit(block)
        self.emit(
            'NOP'
        )  # needed to distinguish from break/continue vs some internal jumps

        # catch block
        self.emit('LABEL', catch_label)
        self.emit('LOAD_UNDEFINED')
        if handler:
            self.emit(handler['body'])
        self.emit('NOP')

        # finally block
        self.emit('LABEL', finally_label)
        self.emit('LOAD_UNDEFINED')
        if finalizer:
            self.emit(finalizer)
        self.emit('NOP')

        self.emit('LABEL', end_label)

        # give life to the code
        self.emit('TRY_CATCH_FINALLY', try_label, catch_label,
                  handler['param']['name'] if handler else None, finally_label,
                  bool(finalizer), end_label)

    def UnaryExpression(self, operator, argument, **kwargs):
        if operator == 'typeof' and argument[
                'type'] == 'Identifier':  # todo fix typeof
            self.emit('TYPEOF', argument['name'])
        elif operator == 'delete':
            if argument['type'] == 'MemberExpression':
                self.emit(argument['object'])
                if argument['property']['type'] == 'Identifier':
                    self.emit('LOAD_STRING',
                              unicode(argument['property']['name']))
                else:
                    self.emit(argument['property'])
                self.emit('DELETE_MEMBER')
            elif argument['type'] == 'Identifier':
                self.emit('DELETE', argument['name'])
            else:
                self.emit('LOAD_BOOLEAN', 1)
        elif operator in UNARY_OPERATIONS:
            self.emit(argument)
            self.emit('UNARY_OP', operator)
        else:
            raise MakeError('SyntaxError',
                            'Unknown unary operator %s' % operator)

    def UpdateExpression(self, operator, argument, prefix, **kwargs):
        incr = int(operator == "++")
        post = int(not prefix)
        if argument['type'] == 'MemberExpression':
            if argument['computed']:
                self.emit(argument['object'])
                self.emit(argument['property'])
                self.emit('POSTFIX_MEMBER', post, incr)
            else:
                self.emit(argument['object'])
                name = to_key(argument['property'])
                self.emit('POSTFIX_MEMBER_DOT', post, incr, name)
        elif argument['type'] == 'Identifier':
            name = to_key(argument)
            self.emit('POSTFIX', post, incr, name)
        else:
            raise MakeError('SyntaxError',
                            'Invalid left-hand side in assignment')

    def VariableDeclaration(self, declarations, kind, **kwargs):
        if kind != 'var':
            raise NotImplementedError(
                'Only var variable declaration is supported by ECMA 5.1')
        for d in declarations:
            self.emit(d)

    def LexicalDeclaration(self, declarations, kind, **kwargs):
        raise NotImplementedError('Not supported by ECMA 5.1')

    def VariableDeclarator(self, id, init, **kwargs):
        name = id['name']
        if name in SPECIAL_IDENTIFIERS:
            raise MakeError('Invalid left-hand side in assignment')
        self.declared_vars.append(name)
        if init is not None:
            self.emit(init)
            self.emit('STORE', name)
            self.emit('POP')

    def WhileStatement(self, test, body, **kwargs):
        continue_label = self.exe.get_new_label()
        break_label = self.exe.get_new_label()

        self.emit('LABEL', continue_label)
        self.emit(test)
        self.emit('JUMP_IF_FALSE', break_label)

        # translate the body, remember to add and afterwards remove implicit break/continue labels

        self.implicit_continues.append(continue_label)
        self.implicit_breaks.append(break_label)
        self.emit(body)
        self.implicit_continues.pop()
        self.implicit_breaks.pop()

        self.emit('JUMP', continue_label)  # loop back
        self.emit('LABEL', break_label)

    def WithStatement(self, object, body, **kwargs):
        beg_label = self.exe.get_new_label()
        end_label = self.exe.get_new_label()
        # scope
        self.emit(object)

        # now the body
        self.emit('JUMP', end_label)
        self.emit('LABEL', beg_label)
        self.emit('LOAD_UNDEFINED')
        self.emit(body)
        self.emit('NOP')
        self.emit('LABEL', end_label)

        # with statement implementation
        self.emit('WITH', beg_label, end_label)

    def _emit_statement_list(self, statements):
        for statement in statements:
            self.emit(statement)

    def emit(self, what, *args):
        ''' what can be either name of the op, or node, or a list of statements.'''
        if isinstance(what, basestring):
            return self.exe.emit(what, *args)
        elif isinstance(what, list):
            self._emit_statement_list(what)
        else:
            return getattr(self, what['type'])(**what)


import os, codecs


def path_as_local(path):
    if os.path.isabs(path):
        return path
    # relative to cwd
    return os.path.join(os.getcwd(), path)


def get_file_contents(path_or_file):
    if hasattr(path_or_file, 'read'):
        js = path_or_file.read()
    else:
        with codecs.open(path_as_local(path_or_file), "r", "utf-8") as f:
            js = f.read()
    return js


def main():
    from space import Space
    import fill_space

    from pyjsparser import parse
    import json
    a = ByteCodeGenerator(Code())

    s = Space()
    fill_space.fill_space(s, a)

    a.exe.space = s
    s.exe = a.exe
    con = get_file_contents('internals/esprima.js')
    d = parse(con + (
        ''';JSON.stringify(exports.parse(%s), 4, 4)''' % json.dumps(con)))
    # d = parse('''
    # function x(n) {
    #     log(n)
    #     return x(n+1)
    # }
    # x(0)
    # ''')

    # var v = 333333;
    # while (v) {
    #     v--
    #
    # }
    a.emit(d)
    print(a.declared_vars)
    print(a.exe.tape)
    print(len(a.exe.tape))

    a.exe.compile()

    def log(this, args):
        print(args[0])
        return 999

    print(a.exe.run(a.exe.space.GlobalObj))


if __name__ == '__main__':
    main()
