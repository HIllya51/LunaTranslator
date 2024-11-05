
#include "PyStand.h"

#include <iomanip>
#include <sstream>
#include <chrono>
#include <ctime>

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

	wchar_t path[MAX_PATH + 10];

	// init: _pystand (full path of PyStand.exe)
	GetModuleFileNameW(NULL, path, MAX_PATH + 1);
#if 0
	wsprintf(path, L"e:\\github\\tools\\pystand\\pystand.exe");
#endif
	_pystand = path;
	_home = std::filesystem::path(path).parent_path().wstring();

	SetCurrentDirectoryW(_home.c_str());

	_runtime = (std::filesystem::path(_home) / rtp).wstring();

	// check home
	if (!PathFileExistsW(_runtime.c_str()))
	{
		std::wstring msg = L"Missing embedded Python3 in:\n" + _runtime;
		MessageBoxW(NULL, msg.c_str(), L"ERROR", MB_OK);
		return false;
	}

	// check python3.dll
	if (!PathFileExistsW((_runtime + L"\\python3.dll").c_str()))
	{
		std::wstring msg = L"Missing python3.dll in:\r\n" + _runtime;
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
	LR"(
import sys
import os
PYSTAND = os.environ['PYSTAND']
PYSTAND_HOME = os.environ['PYSTAND_HOME']
PYSTAND_RUNTIME = os.environ['PYSTAND_RUNTIME']
PYSTAND_SCRIPT = os.environ['PYSTAND_SCRIPT']
sys.path_origin = [n for n in sys.path]
sys.PYSTAND = PYSTAND
sys.PYSTAND_HOME = PYSTAND_HOME
sys.PYSTAND_SCRIPT = PYSTAND_SCRIPT
def MessageBox(msg, info = 'Message'):
    import ctypes
    ctypes.windll.user32.MessageBoxW(None, str(msg), str(info), 0)
    return 0
os.MessageBox = MessageBox
#sys.stdout=sys.stderr
sys.path.insert(0, './LunaTranslator')
)"
#ifndef PYSTAND_CONSOLE
	LR"(
try:
	fd = os.open('CONOUT$', os.O_RDWR | os.O_BINARY)
	fp = os.fdopen(fd, 'w')
	sys.stdout = fp
	sys.stderr = fp
	attached = True
except Exception as e:
    try:
        fp = open(os.devnull, 'w', errors='ignore') # sometimes FileNotFound Error: [Errno 2]No such file or directory: 'nul'
        sys.stdout = fp
        sys.stderr = fp
        attached = False
    except:
        pass
)"
#endif
	LR"(
sys.argv = [PYSTAND_SCRIPT] + sys.argv[1:]
text = open(PYSTAND_SCRIPT, 'rb').read()
environ = {'__file__': PYSTAND_SCRIPT, '__name__': '__main__'}
environ['__package__'] = None
)"
#ifndef PYSTAND_CONSOLE
	LR"(
try:
    code = compile(text, PYSTAND_SCRIPT, 'exec')
    exec(code, environ)
except Exception:
    if attached:
        raise
    import traceback, io
    sio = io.StringIO()
    traceback.print_exc(file = sio)
    os.MessageBox(sio.getvalue(), 'Error')
)"
#else
	LR"(
code = compile(text, PYSTAND_SCRIPT, 'exec')
exec(code, environ)
)"
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

int main()
{
	{
		// 当更新进行时，禁止启动
		AutoHandle hMutex = CreateMutex(NULL, FALSE, L"LUNA_UPDATER_SINGLE");
		if (GetLastError() == ERROR_ALREADY_EXISTS)
			return 0;
	}
	auto __handle = AutoHandle(CreateMutexA(&allAccess, FALSE, "LUNA_UPDATER_BLOCK"));
	PyStand ps(L"files\\runtime");
	if (ps.DetectScript() != 0)
	{
		return 3;
	}
#ifndef PYSTAND_CONSOLE
	// winmain下的stderr没有任何卵用，对于崩溃时的stderr根本显示不出来，所以还是用控制台来保存log吧。
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
#else
	SetConsoleOutputCP(CP_UTF8);
	/*
	auto getCurrentTimestamp = []
	{
		auto now = std::chrono::system_clock::now();
		std::time_t now_time_t = std::chrono::system_clock::to_time_t(now);
		std::tm now_tm = *std::localtime(&now_time_t);
		std::ostringstream oss;
		oss << std::put_time(&now_tm, "log_%Y-%m-%d-%H-%M-%S.txt");
		return oss.str();
	};
	auto curr = getCurrentTimestamp();
	freopen(curr.c_str(), "a", stderr);
	*/
#endif
	int hr = ps.RunString(init_script);
	return hr;
}

int WINAPI
WinMain(HINSTANCE hInst, HINSTANCE hPrevInst, LPSTR args, int show)
{
	return main();
}