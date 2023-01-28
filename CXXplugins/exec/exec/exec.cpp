#include <windows.h>
#include<string>
#include<thread>
#include<tlhelp32.h>
using std::string;
#define BUFSIZE 4096
#pragma comment( linker, "/subsystem:windows /entry:mainCRTStartup" )
bool is_existing_file(const wchar_t* path)
{
	HANDLE hfile(NULL); // 文件句柄

	// 重新设置错误代码，避免发生意外
	::SetLastError(ERROR_SUCCESS);

	// 直接打开文件
	hfile = ::CreateFileW //
	(
		path,
		FILE_READ_EA,
		FILE_SHARE_READ | FILE_SHARE_WRITE,
		NULL,
		OPEN_EXISTING, // 打开一个存在的文件
		0,
		NULL //
	);

	DWORD error = ::GetLastError();

#ifdef DEBUG
	printf("hfile: %p\n", hfile);
	printf("lastError: %lu\n", error);
#endif

	if (hfile == NULL || hfile == INVALID_HANDLE_VALUE)
	{
		// 打开文件失败，检查错误代码
		// 注意：有时候即使文件存在，也可能会打开失败，如拒绝访问的情况
		return error != ERROR_PATH_NOT_FOUND &&
			error != ERROR_FILE_NOT_FOUND;
	}
	else
	{
		// 打开成功，文件存在

		// 记得关闭句柄释放资源
		::CloseHandle(hfile);
		hfile = NULL;

		return true;
	}
} 
static UINT64 getCurrentMilliSecTimestamp() {
	FILETIME file_time;
	GetSystemTimeAsFileTime(&file_time);
	UINT64 time = ((UINT64)file_time.dwLowDateTime) + ((UINT64)file_time.dwHighDateTime << 32);

	// This magic number is the number of 100 nanosecond intervals since January 1, 1601 (UTC)
	// until 00:00:00 January 1, 1970
	static const UINT64 EPOCH = ((UINT64)116444736000000000ULL);

	return (UINT64)((time - EPOCH) / 10000LL);
}
int main() { 
	//if (is_existing_file(L"./files/single.txt")) {
	//	
	//	LPCWSTR pwszProcName = NULL;
	//	HANDLE hProcess = NULL;
	//	HANDLE hProcSnap = INVALID_HANDLE_VALUE;
	//	PROCESSENTRY32W pe32w;

	//	hProcSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
	//	if (hProcSnap != INVALID_HANDLE_VALUE) {

	//		ZeroMemory(&pe32w, sizeof(PROCESSENTRY32W));
	//		pe32w.dwSize = sizeof(PROCESSENTRY32W);
	//		if (Process32FirstW(hProcSnap, &pe32w)) {
	//			//wprintf(L"PID \t	ProcessName\t\n");
	//			do {
	//				//wprintf(L"%u \t	%s\t\n", pe32w.th32ProcessID, pe32w.szExeFile);
	//				if (wcscmp(pe32w.szExeFile, L"LunaTranslator_main.exe") == 0) {
	//					exit(0);
	//				}

	//			} while (Process32NextW(hProcSnap, &pe32w));
	//		}

	//		
	//	}

	//	 
	//}
	/*fopen_s(&f,"./files/single.txt", "r");
		if (f) {
			CreateMutex(NULL, 1, L"keepSingletonmutex");
			if (GetLastError() == 183) {
				exit(1);
			}

	}*/
	
	UINT64 tm = getCurrentMilliSecTimestamp();
	wchar_t buffw[32];
	swprintf_s(buffw, 32, L"%lld", tm);
	std::wstring starttimew= std::wstring(buffw);

	char buff[32];
	sprintf_s(buff, 32,  "%lld", tm);
	std::string starttime = std::string(buff);
	std::thread t1= std::thread([starttimew]() {
		
		while (true) { 
			HANDLE hPipe = CreateNamedPipe((std::wstring(L"\\\\.\\Pipe\\newsentence")+starttimew).c_str(), PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT
				, PIPE_UNLIMITED_INSTANCES, 0, 0, NMPWAIT_WAIT_FOREVER, 0);
			if (ConnectNamedPipe(hPipe, NULL) == NULL) {
				continue;
			}
			//printf("connected\n");
			BOOL fSuccess = false;
			DWORD len = 0;
			char buffer[BUFSIZE];
			string recvData = "";
			do
			{
				fSuccess = ReadFile(hPipe, buffer, BUFSIZE * sizeof(char), &len, NULL);
				char buffer2[BUFSIZE + 1] = { 0 };
				memcpy(buffer2, buffer, len);
				recvData.append(buffer2);
				if (!fSuccess || len < BUFSIZE)
					break;
			} while (true);
			printf(recvData.c_str());
			if (strcmp(recvData.c_str(), "end") == 0) {
				break;
			}
			//WinExec("taskkill /IM voice2.exe /F", SW_HIDE);
			//WinExec("./files/voiceroid2/voice2.exe C:/dataH/Yukari2 C:/tmp/LunaTranslator/files/voiceroid2/aitalked.dll yukari_emo_44 1 1.05 C:/tmp/LunaTranslator/ttscache/1.wav  86 111 105 99 101 82 111 105 100 50 32", SW_HIDE);
			WinExec(recvData.c_str(), SW_HIDE);
			printf("exec\n");
		}

		});
	std::thread t2 = std::thread([starttime]() {
		WinExec((std::string("./LunaTranslator/LunaTranslator_main.exe ")+starttime).c_str(), SW_SHOW);
		 
		});
	t1.join();
	t2.join();
}
 