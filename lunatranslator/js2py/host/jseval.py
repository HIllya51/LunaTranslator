from ..base import *
import inspect
try:
    from js2py.translators.translator import translate_js
except:
    pass


@Js
def Eval(code):
    local_scope = inspect.stack()[3][0].f_locals['var']
    global_scope = this.GlobalObject
    # todo fix scope - we have to behave differently if called through variable other than eval
    # we will use local scope (default)
    globals()['var'] = local_scope
    try:
        py_code = translate_js(code.to_string().value, '')
    except SyntaxError as syn_err:
        raise MakeError('SyntaxError', str(syn_err))
    lines = py_code.split('\n')
    # a simple way to return value from eval. Will not work in complex cases.
    has_return = False
    for n in xrange(len(lines)):
        line = lines[len(lines) - n - 1]
        if line.strip():
            if line.startswith(' '):
                break
            elif line.strip() == 'pass':
                continue
            elif any(
                    line.startswith(e)
                    for e in ['return ', 'continue ', 'break', 'raise ']):
                break
            else:
                has_return = True
                cand = 'EVAL_RESULT = (%s)\n' % line
                try:
                    compile(cand, '', 'exec')
                except SyntaxError:
                    break
                lines[len(lines) - n - 1] = cand
                py_code = '\n'.join(lines)
                break
    #print py_code
    executor(py_code)
    if has_return:
        return globals()['EVAL_RESULT']


def executor(code):
    exec (code, globals())
