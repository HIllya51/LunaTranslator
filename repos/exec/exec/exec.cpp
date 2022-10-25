#include <windows.h>
#include<string>
#include<thread>
using std::string;
#define BUFSIZE 4096
#pragma comment( linker, "/subsystem:windows /entry:mainCRTStartup" )
int main() { 
	
	 
	std::thread t1= std::thread([]() {
		
		while (true) { 
			HANDLE hPipe = CreateNamedPipe(L"\\\\.\\Pipe\\newsentence", PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT
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
	std::thread t2 = std::thread([]() {
		WinExec("./LunaTranslator/LunaTranslator.exe", SW_SHOW);
		 
		});
	t1.join();
	t2.join();
}
 