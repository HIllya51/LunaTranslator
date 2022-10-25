 
#include <stdio.h>
#include <thread>
#include <windows.h>
#include <thread>
#include<iostream>
#include <UIAutomation.h>

#define BUF_SIZE 256
typedef void(__stdcall* CodeCallback)(int code, WPARAM wparam, LPARAM lparam);
typedef void(__stdcall* MessageCallback)(const char* message);
static HHOOK cbtProcHook = NULL;
static HHOOK callWndProcHook = NULL;
typedef struct _MYHOOKDATA
{
	int code;
	WPARAM wparam;
	LPARAM lparam;
} MYHOOKDATA;

HANDLE _hmapFile;
HANDLE _event;
MYHOOKDATA* _payload;
BOOL _active;
HANDLE _threadHandle;
DWORD _threadId;
void SetFileMapping();
void DestroyFileMapping();
DWORD WINAPI MyThreadFunction(LPVOID lpParam);

#ifdef __cplusplus
extern "C" {  // only need to export C interface if
			  // used by C++ source code
#endif

	__declspec(dllexport) bool StartHooks(unsigned int threadId ); 
#ifdef __cplusplus
}
#endif


class wrapper {
private:
	CodeCallback _codeHandler;
	MessageCallback _messageHandler;
	unsigned int _threadId;
public:
	void Init(unsigned int threadId );
	bool Start(); 
	void SendManagedCode(int code, WPARAM wparam, LPARAM lparam); 
};

wrapper _Instance;

void wrapper::SendManagedCode(int code, WPARAM wparam, LPARAM lparam)
{
	
		printf("%d %lld %lld\n", code, wparam, lparam);
}
 

void wrapper::Init(unsigned int threadId )
{ 
	_threadId = threadId; 
	SetFileMapping();
}

bool wrapper::Start()
{ 
	HMODULE dll = LoadLibrary(L"inject.dll");
	if (dll == NULL) { 
		return false;
	} 
	HOOKPROC cbtProcAddress = (HOOKPROC)GetProcAddress(dll, "CbtProcCallback");
	if (cbtProcAddress == NULL) { 
		return false;
	}
	cbtProcHook = SetWindowsHookEx(WH_CBT, cbtProcAddress, dll, _threadId);
	if (cbtProcHook == NULL) { 
		return false;
	} 
	 
	HOOKPROC callWndProcAddress = (HOOKPROC)GetProcAddress(dll, "CallWndProcCallback");
	if (callWndProcAddress == NULL) { 
		return false;
	} 
	 
	callWndProcHook = SetWindowsHookEx(WH_CALLWNDPROC, callWndProcAddress, dll, _threadId);
	if (callWndProcHook == NULL) { 
		return false;
	} 
	return true;
}
 

void SetFileMapping()
{
	_hmapFile = CreateFileMapping(INVALID_HANDLE_VALUE,NULL,PAGE_READWRITE,	0,	BUF_SIZE,L"hsbmapping");
	if (_hmapFile == NULL)	{
		return;
	}  
	_payload = (MYHOOKDATA*)MapViewOfFile(_hmapFile, FILE_MAP_WRITE | FILE_MAP_READ, 0, 0, BUF_SIZE);
	_event = CreateEvent(NULL, false, false, L"hsbevent");
	_active = true;
	_threadHandle = CreateThread(NULL, 0, MyThreadFunction, NULL, 0, &_threadId);
}
 

DWORD WINAPI MyThreadFunction(LPVOID lpParam)
{
	while (_active)
	{
		WaitForSingleObject(_event, INFINITE);
		if (_active == false)
		{
		}
		else
		{
			_Instance.SendManagedCode(_payload->code, _payload->wparam, _payload->lparam);
		}
	}

	return 0;
}

bool StartHooks(unsigned int threadId )
{
	_Instance.Init(threadId );
	return _Instance.Start();
}
 
 
int main() {
	HANDLE h = GetCurrentProcess();
	DWORD _;
	DWORD pid = GetWindowThreadProcessId((HWND)h, &_); 
	std::cout << pid<<"\n";
	StartHooks(pid );
	
	system("pause");

}