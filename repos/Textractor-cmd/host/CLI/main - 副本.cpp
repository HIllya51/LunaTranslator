#include "../host.h"
#include "../hookcode.h"
#include <io.h>
#include <fcntl.h>
#include <iostream>
#include<string>
#define BUFSIZE 5 
#define PIPENAME L"\\\\.\\Pipe\\textractorcommand"
#define PIPENAME_output L"\\\\.\\Pipe\\textractoroutput"
HANDLE hPipe_output;
inline std::string WideStringToString1(const std::wstring& text)
{
	std::vector<char> buffer((text.size() + 1) * 4);
	WideCharToMultiByte(CP_UTF8, 0, text.c_str(), -1, buffer.data(), buffer.size(), nullptr, nullptr);
	return buffer.data();
}
int main()
{
	if (WaitNamedPipe(PIPENAME, NMPWAIT_WAIT_FOREVER) == FALSE)
		return 0;
	HANDLE hPipe = CreateFile(PIPENAME, GENERIC_READ | GENERIC_WRITE, 0,
		NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);

	if ((long)hPipe == -1)
		return 0;

	if (WaitNamedPipe(PIPENAME_output, NMPWAIT_WAIT_FOREVER) == FALSE)
		return 0;
	hPipe_output = CreateFile(PIPENAME_output, GENERIC_READ | GENERIC_WRITE, 0,
		NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);

	if ((long)hPipe == -1)
		return 0;
	_setmode(_fileno(stdout), _O_U16TEXT);
	_setmode(_fileno(stdin), _O_U16TEXT);
	wprintf_s(L"Usage: {'attach'|'detach'|hookcode} -Pprocessid\n");
	fflush(stdout);
	Host::Start([](auto) {}, [](auto) {}, [](auto&) {}, [](auto&) {}, [](TextThread& thread, std::wstring& output)
	{
			wchar_t buf[4096] = { 0 };
		
		 
		wsprintf(buf, L"[%I64X:%I32X:%I64X:%I64X:%I64X:%s:%s] %s\n",
			thread.handle,
			thread.tp.processId,
			thread.tp.addr,
			thread.tp.ctx,
			thread.tp.ctx2,
			thread.name.c_str(),
			HookCode::Generate(thread.hp, thread.tp.processId).c_str(),
			output.c_str()
		); 
		std::wstring sentence = std::wstring(buf);
		DWORD    dwWrite;
		std::string ss = WideStringToString1(sentence);
		WriteFile(hPipe_output, ss.data(), ss.length(), &dwWrite, NULL);

		int i = 0;  
		  
		wprintf_s( L"[%I64X:%I32X:%I64X:%I64X:%I64X:%s:%s] %s\n",
			thread.handle,
			thread.tp.processId,
			thread.tp.addr,
			thread.tp.ctx,
			thread.tp.ctx2,
			thread.name.c_str(),
			HookCode::Generate(thread.hp, thread.tp.processId).c_str(),
			output.c_str()
		);
		fflush(stdout);
		return false;
	});
	 /*
	wchar_t input[500] = {};
	while (fgetws(input, 500, stdin))
	{
		wchar_t command[500] = {};
		DWORD processId = 0;
		if (swscanf(input, L"%500s -P%d", command, &processId) != 2) ExitProcess(0);
		if (_wcsicmp(command, L"attach") == 0) Host::InjectProcess(processId);
		else if (_wcsicmp(command, L"detach") == 0) Host::DetachProcess(processId);
		else if (auto hp = HookCode::Parse(command)) Host::InsertHook(processId, hp.value());
		else ExitProcess(0);
	}
	ExitProcess(0);*/

	
	 
	//接收服务端发回的数据
	BOOL fSuccess = false;
	DWORD len = 0;
	char buffer[BUFSIZE];
	while (true) {
		std::string recvData = "";


		do
		{
			fSuccess = ReadFile(hPipe, buffer, BUFSIZE * sizeof(char), &len, NULL);
			char buffer2[BUFSIZE + 1] = { 0 };
			memcpy(buffer2, buffer, len);
			recvData.append(buffer2);
			if (!fSuccess || len < BUFSIZE)
				break;
		} while (true);
		//wprintf_s(StringToWideString(recvData).c_str());
		 
		wchar_t command[500] = {};
		DWORD processId = 0;
		if (swscanf(StringToWideString(recvData).c_str(), L"%500s -P%d", command, &processId) != 2) ExitProcess(0);
		if (_wcsicmp(command, L"attach") == 0) Host::InjectProcess(processId);
		else if (_wcsicmp(command, L"detach") == 0) Host::DetachProcess(processId);
		else if (_wcsicmp(command, L"exit") == 0) ExitProcess(0);
		else if (auto hp = HookCode::Parse(command)) Host::InsertHook(processId, hp.value());
		else {
			wprintf_s(L"[__hookcode__error__] %s\n", command);
			fflush(stdout);
		}
		 

	}
	
	FlushFileBuffers(hPipe);
	DisconnectNamedPipe(hPipe);
	CloseHandle(hPipe);
	 /*
	DisconnectNamedPipe(hPipe_output);
	CloseHandle(hPipe_output);*/
}
