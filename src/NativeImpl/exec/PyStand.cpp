
#include "PyStand.h"

#include <iomanip>
#include <sstream>
#include <chrono>
#include <ctime>
#include <filesystem>
#include <shlwapi.h>
#include <set>
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
#include "WjCryptLib_Sha256.h"
}

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

#ifndef WINXP
#define PYDLL L"python3.dll"
#else
#define PYDLL L"python34.dll"
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
	wchar_t path[MAX_PATH + 10];
	GetModuleFileNameW(GetModuleHandle(0), path, MAX_PATH);
	exepath = path;
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
	_argv.resize(argc);
	for (int i = 0; i < argc; i++)
	{
		_argv[i] = argvw[i];
	}
	LocalFree(argvw);

	_home = std::filesystem::path(exepath).parent_path().wstring();

	SetCurrentDirectoryW(_home.c_str());

	_runtime = (std::filesystem::path(_home) / rtp).wstring();

	if (_runtime.find(LR"(\AppData\Local\Temp\)") != _runtime.npos)
	{
		std::wstring msg = L"请先解压后再运行！\nPlease decompress before running!";
		MessageBoxW(NULL, msg.c_str(), L"ERROR", MB_OK);
		return false;
	}
	// check home
	if (!PathFileExistsW(_runtime.c_str()))
	{
		std::wstring msg = L"Missing embedded Python3 in:\n" + _runtime;
		MessageBoxW(NULL, msg.c_str(), L"ERROR", MB_OK);
		return false;
	}
	if (!PathFileExistsW((_runtime + L"\\" + PYDLL).c_str()))
	{
		std::wstring msg = std::wstring(L"Missing ") + PYDLL + L" in:\r\n" + _runtime;
		MessageBoxW(NULL, msg.c_str(), L"ERROR", MB_OK);
		return false;
	}

	if (!checkintegrity())
		return false;
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
	// python dll must be load under "runtime"
	SetCurrentDirectoryW(_runtime.c_str());
	// LoadLibrary

#ifdef WIN10ABOVE
	// win10版将runtime路径设为DLL搜索路径，优先使用自带的高级vcrt
	//  这样，即使将主exe静态编译，也能加载runtime中的vcrt
	SetDefaultDllDirectories(LOAD_LIBRARY_SEARCH_DEFAULT_DIRS);
	SetDllDirectoryW(_runtime.c_str());
#else
	WCHAR env[65535];
	GetEnvironmentVariableW(L"PATH", env, 65535);
	auto newenv = std::wstring(env) + L";" + _runtime;
#ifndef WINXP
	// win7版优先使用系统自带的，系统没有再用自带的
	;
#else
	// xp版把这些路径都加进去
	newenv += L";" + _runtime + L"Lib/site-packages/PyQt5";
#endif
	SetEnvironmentVariableW(L"PATH", newenv.c_str());
#endif

	std::wstring pydll = _runtime + L"\\" + PYDLL;
	_hDLL = (HINSTANCE)LoadLibraryW(pydll.c_str());
	if (_hDLL)
	{
		_Py_Main = (t_Py_Main)GetProcAddress(_hDLL, "Py_Main");
	}

	// restore director
	SetCurrentDirectoryW(_home.c_str());

	if (_hDLL == NULL)
	{
		std::wstring msg = L"Cannot load python3.dll from:\r\n" + _runtime;
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
	std::wstring test = _home + L"\\LunaTranslator\\main.py";
	if (!PathFileExistsW(test.c_str()))
	{
		std::wstring msg = L"Can't find :\r\n" + test;
		MessageBoxW(NULL, msg.c_str(), L"ERROR", MB_OK);
		return -1;
	}
	SetEnvironmentVariableW(L"PYSTAND_SCRIPT", test.c_str());
	SetEnvironmentVariableW(L"LUNA_EXE_NAME", exepath.c_str());
	return 0;
}

//---------------------------------------------------------------------
// init script
//---------------------------------------------------------------------
const auto init_script =
	LR"(
import os,functools, locale, sys
PYSTAND_SCRIPT = os.environ['PYSTAND_SCRIPT']
sys.path_origin = [n for n in sys.path]
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
SHA256_HASH Sha256Digest(const std::vector<uint8_t> &str)
{
	Sha256Context sha256Context;
	SHA256_HASH sha256Hash;
	uint16_t i;
	Sha256Initialise(&sha256Context);
	Sha256Update(&sha256Context, str.data(), str.size());
	Sha256Finalise(&sha256Context, &sha256Hash);
	return sha256Hash;
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

// 辅助函数：提取文件签名证书中的公钥数据
std::optional<std::vector<BYTE>> GetCertificatePublicKey(const wchar_t *filePath)
{
	HCERTSTORE hStore = NULL;
	HCRYPTMSG hMsg = NULL;
	DWORD dwEncoding = 0;
	DWORD dwContentType = 0;
	DWORD dwFormatType = 0;

	// 1. 从文件中查询加密对象（获取签名信息）
	BOOL bRes = CryptQueryObject(
		CERT_QUERY_OBJECT_FILE,
		filePath,
		CERT_QUERY_CONTENT_FLAG_PKCS7_SIGNED_EMBED,
		CERT_QUERY_FORMAT_FLAG_BINARY,
		0,
		&dwEncoding,
		&dwContentType,
		&dwFormatType,
		&hStore,
		&hMsg,
		NULL);

	if (!bRes)
		return {};

	// 2. 获取 Signer Info 的大小
	DWORD dwSignerInfoSize = 0;
	if (!CryptMsgGetParam(hMsg, CMSG_SIGNER_INFO_PARAM, 0, NULL, &dwSignerInfoSize))
	{
		if (hStore)
			CertCloseStore(hStore, 0);
		if (hMsg)
			CryptMsgClose(hMsg);
		return {};
	}

	// 3. 获取 Signer Info
	std::vector<BYTE> signerInfoBuf(dwSignerInfoSize);
	PCMSG_SIGNER_INFO pSignerInfo = (PCMSG_SIGNER_INFO)signerInfoBuf.data();
	std::vector<BYTE> result;
	if (CryptMsgGetParam(hMsg, CMSG_SIGNER_INFO_PARAM, 0, pSignerInfo, &dwSignerInfoSize))
	{

		// 4. 根据 Signer Info 中的 SerialNumber 和 Issuer 在 Store 中查找证书
		CERT_INFO CertInfo = {0};
		CertInfo.Issuer = pSignerInfo->Issuer;
		CertInfo.SerialNumber = pSignerInfo->SerialNumber;

		PCCERT_CONTEXT pCertContext = CertFindCertificateInStore(
			hStore,
			dwEncoding,
			0,
			CERT_FIND_SUBJECT_CERT,
			(PVOID)&CertInfo,
			NULL);

		if (pCertContext)
		{
			// ==============================================================
			// 核心部分：提取公钥信息 (SubjectPublicKeyInfo)
			// ==============================================================
			// PublicKey 位于 pCertContext->pCertInfo->SubjectPublicKeyInfo
			// 包含了算法 OID 和 公钥的二进制数据。
			// 我们需要比较整个 PublicKeyInfo 的编码数据，或者单独比较 PublicKey.pbData

			// 这里我们直接拷贝公钥的二进制流
			DWORD keyLen = pCertContext->pCertInfo->SubjectPublicKeyInfo.PublicKey.cbData;
			BYTE *keyPtr = pCertContext->pCertInfo->SubjectPublicKeyInfo.PublicKey.pbData;

			if (keyLen > 0 && keyPtr != NULL)
			{
				result.assign(keyPtr, keyPtr + keyLen);
			}

			CertFreeCertificateContext(pCertContext);
		}
	}

	if (hStore)
		CertCloseStore(hStore, 0);
	if (hMsg)
		CryptMsgClose(hMsg);

	return result;
}
bool VerifyFileSignature(const wchar_t *filePath)
{
	WINTRUST_FILE_INFO fileInfo = {0};
	fileInfo.cbStruct = sizeof(WINTRUST_FILE_INFO);
	fileInfo.pcwszFilePath = filePath;

	WINTRUST_DATA trustData = {0};
	trustData.cbStruct = sizeof(WINTRUST_DATA);
	trustData.dwUIChoice = WTD_UI_NONE;
	trustData.fdwRevocationChecks = WTD_REVOKE_NONE;
	trustData.dwUnionChoice = WTD_CHOICE_FILE;
	trustData.pFile = &fileInfo;
	trustData.dwStateAction = WTD_STATEACTION_VERIFY;
	// 只检查签名有效，不检查签名源
	trustData.dwProvFlags = WTD_REVOCATION_CHECK_NONE | WTD_HASH_ONLY_FLAG;
	GUID policyGuid = WINTRUST_ACTION_GENERIC_VERIFY_V2;
	LONG lStatus = WinVerifyTrust(NULL, &policyGuid, &trustData);

	trustData.dwStateAction = WTD_STATEACTION_CLOSE;
	WinVerifyTrust(NULL, &policyGuid, &trustData);

	return lStatus == ERROR_SUCCESS;
}

bool VerifyKeyMatchesSelf(const wchar_t *filePath, const std::optional<std::vector<uint8_t>> &selfKey)
{
	if (!VerifyFileSignature(filePath))
		return false;
	auto targetKey = GetCertificatePublicKey(filePath);
	if (!selfKey || !targetKey)
		return false;

	if (selfKey.value().size() != targetKey.value().size())
		return false;
	return memcmp(selfKey.value().data(), targetKey.value().data(), selfKey.value().size()) == 0;
}

std::set<const wchar_t *> PyStand::checkintegrity_(bool &succ)
{
	// 分别对python代码检查hash，对exe/dll检查签名
	std::set<const wchar_t *> collect;

	auto selfKey = GetCertificatePublicKey(exepath.c_str());
	if (selfKey)
	{
		if (!VerifyFileSignature(exepath.c_str()))
		{
			succ = false;
			return {};
		}
		for (auto &&fn : checksig)
		{
			// 验证是否签名，且必须和自己签名相同
			if (!fn)
				continue;
			if (!VerifyKeyMatchesSelf(fn, selfKey))
				collect.insert(fn);
		}
	}
	for (auto &&[fn, sig] : checkdigest)
	{
		if (!fn)
			continue;
		auto f = readFile(fn);
		if (!f)
		{
			collect.insert(fn);
			continue;
		}
		auto sigf = Sha256Digest(f.value());
		if (memcmp(sigf.bytes, sig.data(), sig.size()))
			collect.insert(fn);
	}
	return collect;
}
bool PyStand::checkintegrity()
{
	bool succ = true;
	auto invalidfiles = checkintegrity_(succ);
	if (!succ)
	{
		std::wstringstream ss;
		ss << L"主程序已被篡改，无法运行 ！";
		ss << L"\n";
		ss << L"The main program has been tampered with and cannot run!";
		MessageBoxW(0, ss.str().c_str(), L"Error", 0);
		return false;
	}
	if (invalidfiles.size())
	{
		// 检查到无效文件时，仍执行，但弹窗警告。
		std::wstringstream ss;
		ss << L"以下文件可能已被篡改，是否仍要运行？";
		ss << L"\n";
		ss << L"The following files may have been altered. Do you still want to run it?";
		int idx = 1;
		for (auto &f : invalidfiles)
		{
			// 前十个和最后一个显示名称，中间显示一个省略号
			if (idx == invalidfiles.size() || idx < 10)
			{
				ss << L"\n";
				ss << idx;
				ss << L". ";
				ss << f;
			}
			else if (idx == 10)
			{
				ss << L"\n";
				ss << L"...";
			}
			else if (idx > 10)
			{
			}
			idx++;
		}
		auto checked = MessageBoxW(0, ss.str().c_str(), L"Warning", MB_YESNO | MB_ICONQUESTION);
		if (checked != IDYES)
			return false;
	}
	return true;
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