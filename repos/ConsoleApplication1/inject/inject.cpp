
#include <stdio.h>
#include <windows.h>
extern "C" __declspec(dllexport) LRESULT CALLBACK CbtProcCallback(int code, WPARAM wparam, LPARAM lparam);
extern "C" __declspec(dllexport) LRESULT CALLBACK CallWndProcCallback(int code, WPARAM wparam, LPARAM lparam);
typedef struct _MYHOOKDATA
{
	int code;
	WPARAM wparam;
	LPARAM lparam;
} MYHOOKDATA;

#define BUF_SIZE 256
HANDLE _hmapFile;
HANDLE _event;
MYHOOKDATA* _payload;
void SetFileMapping();
void DestroyFileMapping();
void SendPayload(int code, WPARAM wparam, LPARAM lparam);
LRESULT CALLBACK CbtProcCallback(int code, WPARAM wparam, LPARAM lparam)
{
	if (code >= 0)
	{
		// Only send the code if you are about to MAXIMIZE
		SendPayload(code, wparam, lparam);
		if (code == HCBT_MINMAX)
		{
			if (lparam == SW_MAXIMIZE)
			{
				// Do something
				SendPayload(0, wparam, lparam);
			}
		}
	}

	return CallNextHookEx(NULL, code, wparam, lparam);
}

LRESULT CALLBACK CallWndProcCallback(int code, WPARAM wparam, LPARAM lparam)
{	
	CWPSTRUCT* message = (CWPSTRUCT*)lparam;
	if (message->message == WM_ACTIVATEAPP) {
		SendPayload(99, wparam, lparam);
		//SendPayload(code, wparam, lparam);
	}
	
	if (code >= 0)
	{
		if (code == HC_ACTION)
		{
			// LPARAM contains a pointer to a CWPSTRUCT that contains details about the message
			
			if (message->message == WM_MOVING)
			{
				// Do something
				SendPayload(1, wparam, lparam);
			}
			else if (message->message == WM_EXITSIZEMOVE)
			{
				// Do something
				SendPayload(2, wparam, lparam);
			}
		}
	}

	return CallNextHookEx(NULL, code, wparam, lparam);
}

void SetFileMapping()
{
	_hmapFile = CreateFileMapping(
		INVALID_HANDLE_VALUE,
		NULL,
		PAGE_READWRITE,
		0,
		BUF_SIZE,
		L"hsbmapping");
	if (_hmapFile == NULL)
	{
		return;
	}

	_payload = (MYHOOKDATA*)MapViewOfFile(_hmapFile, FILE_MAP_READ | FILE_MAP_WRITE, 0, 0, BUF_SIZE);
	_event = CreateEvent(NULL, false, false, L"hsbevent");
}

void DestroyFileMapping()
{
	if (_payload != 0)
	{
		UnmapViewOfFile(_payload);
	}

	CloseHandle(_hmapFile);
}
int testadd(int a, int b) {
	return a + b;
}
void SendPayload(int code, WPARAM wparam, LPARAM lparam)
{
	_payload->code = code;
	_payload->wparam = wparam;
	_payload->lparam = lparam;
	 
	SetEvent(_event);
}