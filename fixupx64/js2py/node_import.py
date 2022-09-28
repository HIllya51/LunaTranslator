__all__ = ['require']

import subprocess, os, codecs, glob
from .evaljs import translate_js, DEFAULT_HEADER
from .translators.friendly_nodes import is_valid_py_name
import six
import tempfile
import hashlib
import random

DID_INIT = False
DIRNAME = tempfile.mkdtemp()
PY_NODE_MODULES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'py_node_modules')


def _init():
    global DID_INIT
    if DID_INIT:
        return
    assert subprocess.call(
        'node -v', shell=True, cwd=DIRNAME
    ) == 0, 'You must have node installed! run: brew install node'
    assert subprocess.call(
        'cd %s;npm install babel-core babel-cli babel-preset-es2015 babel-polyfill babelify browserify browserify-shim'
        % repr(DIRNAME),
        shell=True,
        cwd=DIRNAME) == 0, 'Could not link required node_modules'
    DID_INIT = True


ADD_TO_GLOBALS_FUNC = '''
;function addToGlobals(name, obj) {
    if (!Object.prototype.hasOwnProperty('_fake_exports')) {
        Object.prototype._fake_exports = {};
    }
    Object.prototype._fake_exports[name] = obj;
};

'''
# subprocess.call("""node -e 'require("browserify")'""", shell=True)
GET_FROM_GLOBALS_FUNC = '''
;function getFromGlobals(name) {
    if (!Object.prototype.hasOwnProperty('_fake_exports')) {
        throw Error("Could not find any value named "+name);
    }
    if (Object.prototype._fake_exports.hasOwnProperty(name)) {
        return Object.prototype._fake_exports[name];
    } else {
        throw Error("Could not find any value named "+name);
    }
};

'''


def _get_module_py_name(module_name):
    return module_name.replace('-', '_')


def _get_module_var_name(module_name):
    cand =  _get_module_py_name(module_name).rpartition('/')[-1]
    if not is_valid_py_name(cand):
        raise ValueError(
            "Invalid Python module name %s (generated from %s). Unsupported/invalid npm module specification?" % (
                repr(cand), repr(module_name)))
    return cand


def _get_and_translate_npm_module(module_name, include_polyfill=False, update=False, maybe_version_str=""):
    assert isinstance(module_name, str), 'module_name must be a string!'

    py_name = _get_module_py_name(module_name)
    module_filename = '%s.py' % py_name
    var_name = _get_module_var_name(module_name)
    if not os.path.exists(os.path.join(PY_NODE_MODULES_PATH,
                                       module_filename)) or update:
        _init()
        module_hash = hashlib.sha1(module_name.encode("utf-8")).hexdigest()[:15]
        version = random.randrange(10000000000000)
        in_file_name = 'in_%s_%d.js' % (module_hash, version)
        out_file_name = 'out_%s_%d.js' % (module_hash, version)
        code = ADD_TO_GLOBALS_FUNC
        if include_polyfill:
            code += "\n;require('babel-polyfill');\n"
        code += """
        var module_temp_love_python = require(%s);
        addToGlobals(%s, module_temp_love_python);
        """ % (repr(module_name), repr(module_name))
        with open(os.path.join(DIRNAME, in_file_name), 'wb') as f:
            f.write(code.encode('utf-8') if six.PY3 else code)

        pkg_name = module_name.partition('/')[0]
        if maybe_version_str:
            pkg_name += '@' + maybe_version_str
        # make sure the module is installed
        assert subprocess.call(
            'cd %s;npm install %s' % (repr(DIRNAME), pkg_name),
            shell=True,
            cwd=DIRNAME
        ) == 0, 'Could not install the required module: ' + pkg_name

        # convert the module
        assert subprocess.call(
            '''node -e "(require('browserify')('./%s').bundle(function (err,data) {if (err) {console.log(err);throw new Error(err);};fs.writeFile('%s', require('babel-core').transform(data, {'presets': require('babel-preset-es2015')}).code, ()=>{});}))"'''
            % (in_file_name, out_file_name),
            shell=True,
            cwd=DIRNAME,
        ) == 0, 'Error when converting module to the js bundle'

        os.remove(os.path.join(DIRNAME, in_file_name))
        with codecs.open(os.path.join(DIRNAME, out_file_name), "r",
                         "utf-8") as f:
            js_code = f.read()
        print("Bundled JS library dumped at: %s" % os.path.join(DIRNAME, out_file_name))
        if len(js_code) < 50:
            raise RuntimeError("Candidate JS bundle too short - likely browserify issue.")
        js_code += GET_FROM_GLOBALS_FUNC
        js_code += ';var %s = getFromGlobals(%s);%s' % (
            var_name, repr(module_name), var_name)
        print('Please wait, translating...')
        py_code = translate_js(js_code)

        dirname = os.path.dirname(
            os.path.join(PY_NODE_MODULES_PATH, module_filename))
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        with open(os.path.join(PY_NODE_MODULES_PATH, module_filename),
                  'wb') as f:
            f.write(py_code.encode('utf-8') if six.PY3 else py_code)
    else:
        with codecs.open(
                os.path.join(PY_NODE_MODULES_PATH, module_filename), "r",
                "utf-8") as f:
            py_code = f.read()
    return py_code


def require(module_name, include_polyfill=True, update=False, context=None):
    """
    Installs the provided npm module, exports a js bundle via browserify, converts to ECMA 5.1 via babel and
    finally translates the generated JS bundle to Python via Js2Py.
    Returns a pure python object that behaves like the installed module. Nice!

    :param module_name: Name of the npm module to require. For example 'esprima'. Supports specific versions via @
        specification. Eg: 'crypto-js@3.3'.
    :param include_polyfill: Whether the babel-polyfill should be included as part of the translation. May be needed
    for some modules that use unsupported features of JS6 such as Map or typed arrays.
    :param update: Whether to force update the translation. Otherwise uses a cached version if exists.
    :param context: Optional context in which the translated module should be executed in. If provided, the
        header (js2py imports) will be skipped as it is assumed that the context already has all the necessary imports.
    :return: The JsObjectWrapper containing the translated module object. Can be used like a standard python object.
    """
    module_name, maybe_version = (module_name+"@@@").split('@')[:2]

    py_code = _get_and_translate_npm_module(module_name, include_polyfill=include_polyfill, update=update,
                                            maybe_version_str=maybe_version)
    # this is a bit hacky but we need to strip the default header from the generated code...
    if context is not None:
        if not py_code.startswith(DEFAULT_HEADER):
            # new header version? retranslate...
            assert not update, "Unexpected header."
            py_code = _get_and_translate_npm_module(module_name, include_polyfill=include_polyfill, update=True)
            assert py_code.startswith(DEFAULT_HEADER), "Unexpected header."
        py_code = py_code[len(DEFAULT_HEADER):]
    context = {} if context is None else context
    exec(py_code, context)
    return context['var'][_get_module_var_name(module_name)].to_py()
