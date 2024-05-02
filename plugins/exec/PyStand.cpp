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
#include "PyStand.h"


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
	if (CheckEnviron(runtime) == false)
	{
		exit(1);
	}
	if (LoadPython() == false)
	{
		exit(2);
	}
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
	if (argvw == NULL)
	{
		MessageBoxA(NULL, "Error in CommandLineToArgvW()", "ERROR", MB_OK);
		return false;
	}
	_argv.resize(argc);
	for (int i = 0; i < argc; i++)
	{
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
	for (; size > 0; size--)
	{
		if (path[size - 1] == L'/')
			break;
		if (path[size - 1] == L'\\')
			break;
	}
	path[size] = 0;
	SetCurrentDirectoryW(path);
	GetCurrentDirectoryW(MAX_PATH + 1, path);
	_home = path;
	SetCurrentDirectoryW(_cwd.c_str());

	// init: _runtime (embedded python directory)
	bool abspath = false;
	if (wcslen(rtp) >= 3)
	{
		if (rtp[1] == L':')
		{
			if (rtp[2] == L'/' || rtp[2] == L'\\')
				abspath = true;
		}
	}
	if (abspath == false)
	{
		_runtime = _home + L"\\" + rtp;
	}
	else
	{
		_runtime = rtp;
	}
	GetFullPathNameW(_runtime.c_str(), MAX_PATH + 1, path, NULL);
	_runtime = path;

	// check home
	std::wstring check = _runtime;
	if (!PathFileExistsW(check.c_str()))
	{
		std::wstring msg = L"Missing embedded Python3 in:\n" + check;
		MessageBoxW(NULL, msg.c_str(), L"ERROR", MB_OK);
		return false;
	}

	// check python3.dll
	std::wstring check2 = _runtime + L"\\python3.dll";
	if (!PathFileExistsW(check2.c_str()))
	{
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
	if (_hDLL)
	{
		_Py_Main = (t_Py_Main)GetProcAddress(_hDLL, "Py_Main");
	}

	// restore director
	SetCurrentDirectoryW(previous.c_str());

	if (_hDLL == NULL)
	{
		std::wstring msg = L"Cannot load python3.dll from:\r\n" + runtime;
		MessageBoxW(NULL, msg.c_str(), L"ERROR", MB_OK);
		return false;
	}
	else if (_Py_Main == NULL)
	{
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
	if (_Py_Main == NULL)
	{
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
	for (i = 1; i < (int)_argv.size(); i++)
	{
		_py_argv.push_back(_argv[i]);
	}
	// finalize arguments
	_py_args.resize(0);
	for (i = 0; i < (int)_py_argv.size(); i++)
	{
		_py_args.push_back((wchar_t *)_py_argv[i].c_str());
	}
	hr = _Py_Main((int)_py_args.size(), &_py_args[0]);
	return hr;
}

//---------------------------------------------------------------------
// LoadScript()
//---------------------------------------------------------------------
int PyStand::DetectScript()
{
	// init: _script (init script like PyStand.int or PyStand.py)
	int size = (int)_pystand.size() - 1;
	for (; size >= 0; size--)
	{
		if (_pystand[size] == L'.')
			break;
	}
	if (size < 0)
		size = (int)_pystand.size();
	std::wstring main = _pystand.substr(0, size);
	std::vector<const wchar_t *> exts;
	std::vector<std::wstring> scripts;
	_script.clear();

	std::wstring test;
	test = _home + L"\\LunaTranslator\\LunaTranslator_main.py";
	if (PathFileExistsW(test.c_str()))
	{
		_script = test;
	}
	if (_script.empty())
	{
		std::wstring msg = L"Can't find :\r\n" + test;
		MessageBoxW(NULL, msg.c_str(), L"ERROR", MB_OK);
		return -1;
	}
	SetEnvironmentVariableW(L"PYSTAND_SCRIPT", _script.c_str());
	
	std::vector<wchar_t> buffer(MAX_PATH);
	GetModuleFileNameW(GetModuleHandle(0), buffer.data(), MAX_PATH);
	SetEnvironmentVariableW(L"LUNA_EXE_NAME", buffer.data());
	
	return 0;
}

//---------------------------------------------------------------------
// init script
//---------------------------------------------------------------------
const auto init_script =
	L"import sys\n"
	L"import os\n"
	L"PYSTAND = os.environ['PYSTAND']\n"
	L"PYSTAND_HOME = os.environ['PYSTAND_HOME']\n"
	L"PYSTAND_RUNTIME = os.environ['PYSTAND_RUNTIME']\n"
	L"PYSTAND_SCRIPT = os.environ['PYSTAND_SCRIPT']\n"
	L"sys.path_origin = [n for n in sys.path]\n"
	L"sys.PYSTAND = PYSTAND\n"
	L"sys.PYSTAND_HOME = PYSTAND_HOME\n"
	L"sys.PYSTAND_SCRIPT = PYSTAND_SCRIPT\n"
	L"def MessageBox(msg, info = 'Message'):\n"
	L"    import ctypes\n"
	L"    ctypes.windll.user32.MessageBoxW(None, str(msg), str(info), 0)\n"
	L"    return 0\n"
	L"os.MessageBox = MessageBox\n"
#ifndef PYSTAND_CONSOLE
	L"try:\n"
	L"    fd = os.open('CONOUT$', os.O_RDWR | os.O_BINARY)\n"
	L"    fp = os.fdopen(fd, 'w')\n"
	L"    sys.stdout = fp\n"
	L"    sys.stderr = fp\n"
	L"    attached = True\n"
	L"except Exception as e:\n"
	L"    fp = open(os.devnull, 'w')\n"
	L"    sys.stdout = fp\n"
	L"    sys.stderr = fp\n"
	L"    attached = False\n"
#endif
	L"sys.argv = [os.environ['LUNA_EXE_NAME'] ,sys.argv[0], PYSTAND_SCRIPT] + sys.argv[1:]\n"
	L"text = open(PYSTAND_SCRIPT, 'rb').read()\n"
	L"environ = {'__file__': PYSTAND_SCRIPT, '__name__': '__main__'}\n"
	L"environ['__package__'] = None\n"
#ifndef PYSTAND_CONSOLE
	L"try:\n"
	L"    code = compile(text, PYSTAND_SCRIPT, 'exec')\n"
	L"    exec(code, environ)\n"
	L"except Exception:\n"
	L"    if attached:\n"
	L"        raise\n"
	L"    import traceback, io\n"
	L"    sio = io.StringIO()\n"
	L"    traceback.print_exc(file = sio)\n"
	L"    os.MessageBox(sio.getvalue(), 'Error')\n"
#else
	L"code = compile(text, PYSTAND_SCRIPT, 'exec')\n"
	L"exec(code, environ)\n"
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
	PyStand ps(L"LunaTranslator\\runtime");
	if (ps.DetectScript() != 0)
	{
		return 3;
	}
#ifndef PYSTAND_CONSOLE
	if (AttachConsole(ATTACH_PARENT_PROCESS))
	{
		freopen("CONOUT$", "w", stdout);
		freopen("CONOUT$", "w", stderr);
		int fd = _fileno(stdout);
		if (fd >= 0)
		{
			std::string fn = std::to_string(fd);
			SetEnvironmentVariableA("PYSTAND_STDOUT", fn.c_str());
		}
		fd = _fileno(stdin);
		if (fd >= 0)
		{
			std::string fn = std::to_string(fd);
			SetEnvironmentVariableA("PYSTAND_STDIN", fn.c_str());
		}
	}
#endif
	int hr = ps.RunString(init_script);
	// printf("finalize\n");
	return hr;
}
