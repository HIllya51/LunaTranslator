
#include "PyStand.h"

#include <iomanip>
#include <sstream>
#include <chrono>
#include <ctime>
#include<filesystem>
#include<shlwapi.h>
#include<atlbase.h>

inline SECURITY_ATTRIBUTES allAccess = std::invoke([] // allows non-admin processes to access kernel objects made by admin processes
                                                   {
	static SECURITY_DESCRIPTOR sd = {};
	InitializeSecurityDescriptor(&sd, SECURITY_DESCRIPTOR_REVISION);
	SetSecurityDescriptorDacl(&sd, TRUE, NULL, FALSE);
	return SECURITY_ATTRIBUTES{ sizeof(SECURITY_ATTRIBUTES), &sd, FALSE }; });
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
#ifndef WINXP
	// check python3.dll
	if (!PathFileExistsW((_runtime + L"\\python3.dll").c_str()))
	{
		std::wstring msg = L"Missing python3.dll in:\r\n" + _runtime;
		MessageBoxW(NULL, msg.c_str(), L"ERROR", MB_OK);
		return false;
	}
#else
	if (!PathFileExistsW((_runtime + L"\\python34.dll").c_str()))
	{
		std::wstring msg = L"Missing python34.dll in:\r\n" + _runtime;
		MessageBoxW(NULL, msg.c_str(), L"ERROR", MB_OK);
		return false;
	}
#endif
	// setup environment
	SetEnvironmentVariableW(L"PYSTAND", _pystand.c_str());
	SetEnvironmentVariableW(L"PYSTAND_HOME", _home.c_str());
	SetEnvironmentVariableW(L"PYSTAND_RUNTIME", _runtime.c_str());

	return true;
}
#ifndef WINXP
#define PYDLL L"python3.dll"
#else
#define PYDLL L"python34.dll"
#endif
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

#ifdef WIN10ABOVE
	//win10版将runtime路径设为DLL搜索路径，优先使用自带的高级vcrt
	// 这样，对于只需将主exe静态编译，其他的动态编译即可
	SetDllDirectoryW(runtime.c_str());
#else
	WCHAR env[65535];
	GetEnvironmentVariableW(L"PATH", env, 65535);
	auto newenv = std::wstring(env) + L";" + runtime;
	#ifndef WINXP
		// win7版优先使用系统自带的，系统没有再用自带的
		;
	#else
		// xp版把这些路径都加进去
		newenv += L";" + runtime +L"Lib/site-packages/PyQt5";
	#endif
	SetEnvironmentVariableW(L"PATH", newenv.c_str());
#endif

	std::wstring pydll = runtime + L"\\" + PYDLL;
	_hDLL = (HINSTANCE)LoadLibraryW(pydll.c_str());
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
		msg += pydll;
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

#ifdef WINXP
	auto Py_SetPath = (void (*)(const wchar_t *))GetProcAddress(_hDLL, "Py_SetPath");
	Py_SetPath(L"./files/runtime/Lib;./files/runtime/DLLs;./files/runtime/Lib/site-packages");
#endif
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
	test = _home + L"\\LunaTranslator\\main.py";
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
import os,functools, locale, sys
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


def fuckwrite(origin, message):
	try:
		if isinstance(message, str):
			code=locale.getpreferredencoding()
			origin(message.encode(encoding=code, errors='replace').decode(encoding=code, errors='replace'))
		else:
			origin(message)
	except:
		return
		import traceback, io
		sio = io.StringIO()
		traceback.print_exc(file = sio)
		os.MessageBox(sio.getvalue(), message)

try:
	fd = os.open('CONOUT$', os.O_RDWR | os.O_BINARY)
	fp = os.fdopen(fd, 'w')
	sys.stdout = fp
	sys.stderr = fp
	attached = True
	sys.stdout.write = functools.partial(fuckwrite,sys.stdout.write)
	sys.stderr.write = functools.partial(fuckwrite,sys.stderr.write)

except Exception as e:
    try:
        fp = open(os.devnull, 'w', errors='replace') # sometimes FileNotFound Error: [Errno 2]No such file or directory: 'nul'
        sys.stdout = fp
        sys.stderr = fp
        attached = False
    except:
        pass

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
		CHandle hMutex{CreateMutex(NULL, FALSE, L"LUNA_UPDATER_SINGLE")};
		if (GetLastError() == ERROR_ALREADY_EXISTS)
			return 0;
	}
	CHandle __handle{CreateMutexA(&allAccess, FALSE, "LUNA_UPDATER_BLOCK")};
	PyStand ps(L"files\\runtime");
	if (ps.DetectScript() != 0)
	{
		return 3;
	}
	// print cmd无法显示的字符时，如果使用cmd打开，不论debug还是普通，都会error31崩溃。如果双击打开debug，却不会崩溃
	// 但因为无法区分是使用cmd打开debug还是双击打开debug，所以干脆都这样吧。
	if (AttachConsole(ATTACH_PARENT_PROCESS))
	{
		freopen("CONOUT$", "w", stdout);
		freopen("CONOUT$", "w", stderr);
	}
	int hr = ps.RunString(init_script);
	return hr;
}

int WINAPI
WinMain(HINSTANCE hInst, HINSTANCE hPrevInst, LPSTR args, int show)
{
	return main();
}