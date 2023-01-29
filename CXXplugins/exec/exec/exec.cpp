#include <windows.h>
#include<string>
#include<thread> 
using std::string;
#define BUFSIZE 4096
#pragma comment( linker, "/subsystem:windows /entry:mainCRTStartup" )
 
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
			if (strcmp(recvData.c_str(), "end") == 0) {
				break;
			}
			//WinExec("taskkill /IM voice2.exe /F", SW_HIDE);
			//WinExec("./files/voiceroid2/voice2.exe C:/dataH/Yukari2 C:/tmp/LunaTranslator/files/voiceroid2/aitalked.dll yukari_emo_44 1 1.05 C:/tmp/LunaTranslator/ttscache/1.wav  86 111 105 99 101 82 111 105 100 50 32", SW_HIDE);
			WinExec(recvData.c_str(), SW_HIDE); 
		}

		});
	std::thread t2 = std::thread([starttime]() {
		WinExec((std::string("./LunaTranslator/LunaTranslator_main.exe ")+starttime).c_str(), SW_SHOW);
		 
		});
	t1.join();
	t2.join();
}
 