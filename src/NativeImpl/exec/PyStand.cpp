
#include "PyStand.h"

#include <iomanip>
#include <sstream>
#include <chrono>
#include <ctime>
#include <filesystem>
#include <shlwapi.h>
#include <optional>
#include <atlbase.h>
#include <fstream>
#include <wincrypt.h>
#include <wintrust.h>
#include <softpub.h>
#include <array>
#include "../common.hpp"
#include "checksigs.hpp"
extern "C"
{
#include "WjCryptLib_Sha512.h"
}
#pragma comment(lib, "wintrust.lib")

#ifdef WIN10ABOVE
#define RUNTIME L"runtime31264"
#else
#ifdef WINXP
#define RUNTIME L"runtime3432"
#else
#ifdef _WIN64
#define RUNTIME L"runtime3764"
#else
#define RUNTIME L"runtime3732"
#endif
#endif
#endif
#define FILES L"files\\"
#define FILESRUNTIME FILES RUNTIME

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
	// win10版将runtime路径设为DLL搜索路径，优先使用自带的高级vcrt
	//  这样，即使将主exe静态编译，也能加载runtime中的vcrt
	SetDefaultDllDirectories(LOAD_LIBRARY_SEARCH_DEFAULT_DIRS);
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
	newenv += L";" + runtime + L"Lib/site-packages/PyQt5";
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
	std::wstring path = std::wstring(FILESRUNTIME) + L"\\Lib;" + FILESRUNTIME + L"\\DLLs;" + FILESRUNTIME + L"\\Lib\\site-packages";
	Py_SetPath(path.c_str());
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
SHA512_HASH Sha512Digest(const std::vector<uint8_t> &str)
{
	Sha512Context sha512Context;
	SHA512_HASH sha512Hash;
	uint16_t i;
	Sha512Initialise(&sha512Context);
	Sha512Update(&sha512Context, str.data(), str.size());
	Sha512Finalise(&sha512Context, &sha512Hash);
	return sha512Hash;
}
std::optional<std::vector<uint8_t>> readFile(const std::wstring &filename)
{
	std::ifstream file(filename, std::ios::binary);
	if (!file)
		return {};
	// 使用迭代器读取文件内容到vector
	std::vector<uint8_t> buffer(
		(std::istreambuf_iterator<char>(file)),
		std::istreambuf_iterator<char>());

	return buffer;
}

bool VerifyFileSignature(const wchar_t *filePath)
{
	WINTRUST_FILE_INFO fileInfo = {0};
	fileInfo.cbStruct = sizeof(WINTRUST_FILE_INFO);
	fileInfo.pcwszFilePath = filePath;
	fileInfo.hFile = NULL;
	fileInfo.pgKnownSubject = NULL;

	WINTRUST_DATA trustData = {0};
	trustData.cbStruct = sizeof(WINTRUST_DATA);
	trustData.pPolicyCallbackData = NULL;
	trustData.pSIPClientData = NULL;
	trustData.dwUIChoice = WTD_UI_NONE;
	trustData.fdwRevocationChecks = WTD_REVOKE_NONE;
	trustData.dwUnionChoice = WTD_CHOICE_FILE;
	trustData.pFile = &fileInfo;
	trustData.dwStateAction = WTD_STATEACTION_VERIFY;
	trustData.hWVTStateData = NULL;
	trustData.pwszURLReference = NULL;
	trustData.dwProvFlags = WTD_REVOCATION_CHECK_NONE;
	trustData.dwUIContext = 0;

	GUID policyGuid = WINTRUST_ACTION_GENERIC_VERIFY_V2;
	LONG result = WinVerifyTrust(NULL, &policyGuid, &trustData);

	trustData.dwStateAction = WTD_STATEACTION_CLOSE;
	WinVerifyTrust(NULL, &policyGuid, &trustData);

	return result == ERROR_SUCCESS;
}
std::vector<const wchar_t *> checkintegrity_()
{
	// 分别对python代码检查hash，对exe/dll检查签名
	std::vector<const wchar_t *> collect;
	for (auto &&[fn, sig] : checkdigest)
	{
		if (!fn)
			continue;
		auto f = readFile(fn);
		if (!f)
		{
			collect.push_back(fn);
			continue;
		}
		auto sigf = Sha512Digest(f.value());
		if (memcmp(sigf.bytes, sig.data(), sig.size()))
			collect.push_back(fn);
	}
	for (auto &&fn : checksig)
	{
		if (!fn)
			continue;
		if (!VerifyFileSignature(fn))
			collect.push_back(fn);
	}
	return collect;
}
void checkintegrity()
{
	auto invalidfiles = checkintegrity_();
	if (invalidfiles.size())
	{
		// 检查到无效文件时，仍执行，但弹窗警告。
		std::wstringstream ss;
		ss << L"以下文件可能已被篡改，请注意甄别文件来源";
		ss << L"\n";
		ss << L"The following files may have been altered. Please verify their origin.";
		int idx = 1;
		for (auto &f : invalidfiles)
		{
			ss << L"\n";
			ss << idx;
			ss << L". ";
			ss << f;
			idx++;
		}
		MessageBoxW(0, ss.str().c_str(), L"Warning", 0);
	}
}
int main()
{
	{
		// 当更新进行时，禁止启动
		CHandle hMutex{CreateMutex(NULL, FALSE, L"LUNA_UPDATER_SINGLE")};
		if (GetLastError() == ERROR_ALREADY_EXISTS)
			return 0;
	}
	CHandle __handle{CreateMutexA(&allAccess, FALSE, "LUNA_UPDATER_BLOCK")};

	PyStand ps(FILESRUNTIME);
	if (ps.DetectScript() != 0)
	{
		return 3;
	}
	checkintegrity();
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