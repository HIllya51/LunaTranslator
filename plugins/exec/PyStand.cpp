//=====================================================================
//
// PyStand.cpp - 
//
// Created by skywind on 2022/02/03
// Last Modified: 2023/03/17 20:06
//
//=====================================================================
#ifdef _MSC_VER
#define _CRT_SECURE_NO_WARNINGS 1
#endif

#include <shlwapi.h>
#include <string>
#include <string.h>
#include <winbase.h>
#include <wincon.h>

#include "PyStand.h"

#ifdef _MSC_VER
#pragma comment(lib, "shlwapi.lib")
#endif


//---------------------------------------------------------------------
// dtor
//---------------------------------------------------------------------
PyStand::~PyStand()
{
	FreeLibrary(_hDLL);
}


//---------------------------------------------------------------------
// ctor
//---------------------------------------------------------------------
PyStand::PyStand(const wchar_t *runtime)
{
	_hDLL = NULL;
	_Py_Main = NULL;
	if (CheckEnviron(runtime) == false) {
		exit(1);
	}
	if (LoadPython() == false) {
		exit(2);
	}
}


//---------------------------------------------------------------------
// ctor for ansi
//---------------------------------------------------------------------
PyStand::PyStand(const char *runtime)
{
	_hDLL = NULL;
	_Py_Main = NULL;
	std::wstring rtp = Ansi2Unicode(runtime);
	if (CheckEnviron(rtp.c_str()) == false) {
		exit(1);
	}
	if (LoadPython() == false) {
		exit(2);
	}
}


//---------------------------------------------------------------------
// char to wchar_t
//---------------------------------------------------------------------
std::wstring PyStand::Ansi2Unicode(const char *text)
{
	int len = (int)strlen(text);
	std::wstring wide;
	int require = MultiByteToWideChar(CP_ACP, 0, text, len, NULL, 0);
	if (require > 0) {
		wide.resize(require);
		MultiByteToWideChar(CP_ACP, 0, text, len, &wide[0], require);
	}
	return wide;
}


//---------------------------------------------------------------------
// init: _args, _argv, _cwd, _pystand, _home, _runtime, 
//---------------------------------------------------------------------
bool PyStand::CheckEnviron(const wchar_t *rtp)
{
	// init: _args, _argv
	LPWSTR *argvw;
	int argc;
	_args = GetCommandLineW();
	argvw = CommandLineToArgvW(_args.c_str(), &argc);
	if (argvw == NULL) {
		MessageBoxA(NULL, "Error in CommandLineToArgvW()", "ERROR", MB_OK);
		return false;
	}
	_argv.resize(argc);
	for (int i = 0; i < argc; i++) {
		_argv[i] = argvw[i];
	}
	LocalFree(argvw);

	// init: _cwd (current working directory)
	wchar_t path[MAX_PATH + 10];
	GetCurrentDirectoryW(MAX_PATH + 1, path);
	_cwd = path;

	// init: _pystand (full path of PyStand.exe)
	GetModuleFileNameW(NULL, path, MAX_PATH + 1);
#if 0
	wsprintf(path, L"e:\\github\\tools\\pystand\\pystand.exe");
#endif
	_pystand = path;

	// init: _home
	int size = (int)wcslen(path);
	for (; size > 0; size--) {
		if (path[size - 1] == L'/') break;
		if (path[size - 1] == L'\\') break;
	}
	path[size] = 0;
	SetCurrentDirectoryW(path);
	GetCurrentDirectoryW(MAX_PATH + 1, path);
	_home = path;
	SetCurrentDirectoryW(_cwd.c_str());

	// init: _runtime (embedded python directory)
	bool abspath = false;
	if (wcslen(rtp) >= 3) {
		if (rtp[1] == L':') {
			if (rtp[2] == L'/' || rtp[2] == L'\\')
				abspath = true;
		}
	}
	if (abspath == false) {
		_runtime = _home + L"\\" + rtp;
	}
	else {
		_runtime = rtp;
	}
	GetFullPathNameW(_runtime.c_str(), MAX_PATH + 1, path, NULL);
	_runtime = path;

	// check home
	std::wstring check = _runtime;
	if (!PathFileExistsW(check.c_str())) {
		std::wstring msg = L"Missing embedded Python3 in:\n" + check;
		MessageBoxW(NULL, msg.c_str(), L"ERROR", MB_OK);
		return false;
	}

	// check python3.dll
	std::wstring check2 = _runtime + L"\\python3.dll";
	if (!PathFileExistsW(check2.c_str())) {
		std::wstring msg = L"Missing python3.dll in:\r\n" + check;
		MessageBoxW(NULL, msg.c_str(), L"ERROR", MB_OK);
		return false;
	}

	// setup environment
	SetEnvironmentVariableW(L"PYSTAND", _pystand.c_str());
	SetEnvironmentVariableW(L"PYSTAND_HOME", _home.c_str());
	SetEnvironmentVariableW(L"PYSTAND_RUNTIME", _runtime.c_str());

	// unnecessary to init PYSTAND_SCRIPT here.
#if 0
	SetEnvironmentVariableW(L"PYSTAND_SCRIPT", _script.c_str());
#endif

#if 0
	wprintf(L"%s - %s\n", _pystand.c_str(), path);
	MessageBoxW(NULL, _pystand.c_str(), _home.c_str(), MB_OK);
#endif

	return true;
}


//---------------------------------------------------------------------
// load python
//---------------------------------------------------------------------
bool PyStand::LoadPython()
{
	std::wstring runtime = _runtime;
	std::wstring previous;

	// save current directory
	wchar_t path[MAX_PATH + 10];
	GetCurrentDirectoryW(MAX_PATH + 1, path);
	previous = path;

	// python dll must be load under "runtime"
	SetCurrentDirectoryW(runtime.c_str());
	// LoadLibrary
	_hDLL = (HINSTANCE)LoadLibraryA("python3.dll");
	if (_hDLL) {
		_Py_Main = (t_Py_Main)GetProcAddress(_hDLL, "Py_Main");
	}	

	// restore director
	SetCurrentDirectoryW(previous.c_str());

	if (_hDLL == NULL) {
		std::wstring msg = L"Cannot load python3.dll from:\r\n" + runtime;
		MessageBoxW(NULL, msg.c_str(), L"ERROR", MB_OK);
		return false;
	}
	else if (_Py_Main == NULL) {
		std::wstring msg = L"Cannot find Py_Main() in:\r\n";
		msg += runtime + L"\\python3.dll";
		MessageBoxW(NULL, msg.c_str(), L"ERROR", MB_OK);
		return false;
	}
	return true;
}


//---------------------------------------------------------------------
// run string
//---------------------------------------------------------------------
int PyStand::RunString(const wchar_t *script)
{
	if (_Py_Main == NULL) {
		return -1;
	}
	int hr = 0;
	int i;
	_py_argv.resize(0);
	// init arguments
	_py_argv.push_back(_argv[0]);
	_py_argv.push_back(L"-I");
	_py_argv.push_back(L"-s");
	_py_argv.push_back(L"-S");
	_py_argv.push_back(L"-c");
	_py_argv.push_back(script);
	for (i = 1; i < (int)_argv.size(); i++) {
		_py_argv.push_back(_argv[i]);
	}
	// finalize arguments
	_py_args.resize(0);
	for (i = 0; i < (int)_py_argv.size(); i++) {
		_py_args.push_back((wchar_t*)_py_argv[i].c_str());
	}
	hr = _Py_Main((int)_py_args.size(), &_py_args[0]);
	return hr;
}


//---------------------------------------------------------------------
// run ansi string
//---------------------------------------------------------------------
int PyStand::RunString(const char *script)
{
	std::wstring text = Ansi2Unicode(script);
	return RunString(text.c_str());
}



//---------------------------------------------------------------------
// static init script
//---------------------------------------------------------------------
#ifndef PYSTAND_STATIC_NAME
#define PYSTAND_STATIC_NAME "LunaTranslator\\LunaTranslator_main.py"
#endif


//---------------------------------------------------------------------
// LoadScript()
//---------------------------------------------------------------------
int PyStand::DetectScript()
{
	// init: _script (init script like PyStand.int or PyStand.py)
	int size = (int)_pystand.size() - 1;
	for (; size >= 0; size--) {
		if (_pystand[size] == L'.') break;
	}
	if (size < 0) size = (int)_pystand.size();
	std::wstring main = _pystand.substr(0, size);
	std::vector<const wchar_t*> exts;
	std::vector<std::wstring> scripts;
	_script.clear();
#if !(PYSTAND_DISABLE_STATIC)
	std::wstring test;
	test = _home + L"\\" + Ansi2Unicode(PYSTAND_STATIC_NAME);
	if (PathFileExistsW(test.c_str())) {
		_script = test;
	}
#endif
	if (_script.empty()) {
		exts.push_back(L".int");
		exts.push_back(L".py");
		exts.push_back(L".pyw");
		for (int i = 0; i < (int)exts.size(); i++) {
			std::wstring test = main + exts[i];
			scripts.push_back(test);
			if (PathFileExistsW(test.c_str())) {
				_script = test;
				break;
			}
		}
		if (_script.size() == 0) {
			std::wstring msg = L"Can't find either of:\r\n";
			for (int j = 0; j < (int)scripts.size(); j++) {
				msg += scripts[j] + L"\r\n";
			}
			MessageBoxW(NULL, msg.c_str(), L"ERROR", MB_OK);
			return -1;
		}
	}
	SetEnvironmentVariableW(L"PYSTAND_SCRIPT", _script.c_str());
	return 0;
}


//---------------------------------------------------------------------
// init script
//---------------------------------------------------------------------
const char *init_script = 
"import sys\n"
"import os\n"
"PYSTAND = os.environ['PYSTAND']\n"
"PYSTAND_HOME = os.environ['PYSTAND_HOME']\n"
"PYSTAND_RUNTIME = os.environ['PYSTAND_RUNTIME']\n"
"PYSTAND_SCRIPT = os.environ['PYSTAND_SCRIPT']\n"
"sys.path_origin = [n for n in sys.path]\n"
"sys.PYSTAND = PYSTAND\n"
"sys.PYSTAND_HOME = PYSTAND_HOME\n"
"sys.PYSTAND_SCRIPT = PYSTAND_SCRIPT\n"
"def MessageBox(msg, info = 'Message'):\n"
"    import ctypes\n"
"    ctypes.windll.user32.MessageBoxW(None, str(msg), str(info), 0)\n"
"    return 0\n"
"os.MessageBox = MessageBox\n"
#ifndef PYSTAND_CONSOLE
"try:\n"
"    fd = os.open('CONOUT$', os.O_RDWR | os.O_BINARY)\n"
"    fp = os.fdopen(fd, 'w')\n"
"    sys.stdout = fp\n"
"    sys.stderr = fp\n"
"    attached = True\n"
"except Exception as e:\n"
"    fp = open(os.devnull, 'w')\n"
"    sys.stdout = fp\n"
"    sys.stderr = fp\n"
"    attached = False\n"
#endif
"sys.argv = [PYSTAND_SCRIPT] + sys.argv[1:]\n"
"text = open(PYSTAND_SCRIPT, 'rb').read()\n"
"environ = {'__file__': PYSTAND_SCRIPT, '__name__': '__main__'}\n"
"environ['__package__'] = None\n"
#ifndef PYSTAND_CONSOLE
"try:\n"
"    code = compile(text, PYSTAND_SCRIPT, 'exec')\n"
"    exec(code, environ)\n"
"except Exception:\n"
"    if attached:\n"
"        raise\n"
"    import traceback, io\n"
"    sio = io.StringIO()\n"
"    traceback.print_exc(file = sio)\n"
"    os.MessageBox(sio.getvalue(), 'Error')\n"
#else
"code = compile(text, PYSTAND_SCRIPT, 'exec')\n"
"exec(code, environ)\n"
#endif
"";


//---------------------------------------------------------------------
// main
//---------------------------------------------------------------------

//! flag: -static
//! src: 
//! link: stdc++, shlwapi, resource.o
//! prebuild: windres resource.rc -o resource.o
//! mode: win
//! int: objs

#ifdef PYSTAND_CONSOLE
int main()
#else
int WINAPI 
WinMain(HINSTANCE hInst, HINSTANCE hPrevInst, LPSTR args, int show)
#endif
{
	PyStand ps("LunaTranslator\\runtime");
	if (ps.DetectScript() != 0) {
		return 3;
	}
#ifndef PYSTAND_CONSOLE
	if (AttachConsole(ATTACH_PARENT_PROCESS)) {
		freopen("CONOUT$", "w", stdout);
		freopen("CONOUT$", "w", stderr);
		int fd = _fileno(stdout);
		if (fd >= 0) {
			std::string fn = std::to_string(fd);
			SetEnvironmentVariableA("PYSTAND_STDOUT", fn.c_str());
		}
		fd = _fileno(stdin);
		if (fd >= 0) {
			std::string fn = std::to_string(fd);
			SetEnvironmentVariableA("PYSTAND_STDIN", fn.c_str());
		}
	}
#endif
	int hr = ps.RunString(init_script);
	// printf("finalize\n");
	return hr;
}


