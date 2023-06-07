#pragma once
#ifndef _XXXXXXCOMMON

#include <winsock2.h>
#include<Windows.h>
extern SOCKET connectSocket ;
extern HINSTANCE g_instance;
extern int g_nCmdShow;
int WINAPI WinMain_pl();

int WINAPI WinMain_host(int);
BOOL CALLBACK EnumChildProc(HWND hwndChild, LPARAM lParam);

extern HFONT dfhFont;
#endif // !_XXXXXXCOMMON
