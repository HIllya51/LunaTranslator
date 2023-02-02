// magpiecmdrunner.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <iostream>
#include<windows.h>
#include<thread>
#include<winuser.h>
#include<SIGNAL.h>
typedef BOOL (*Initialize)(
	UINT logLevel,
	const char* logFileName,
	int logArchiveAboveSize,
	int logMaxArchiveFiles
);
typedef const char* (* Run)(
	HWND hwndSrc,
	const char* effectsJson,
	UINT flags,
	UINT captureMode,
	float cursorZoomFactor,	// 负数和 0：和源窗口相同，正数：缩放比例
	UINT cursorInterpolationMode,	// 0：最近邻，1：双线性
	int adapterIdx,
	UINT multiMonitorUsage,	// 0：最近 1：相交 2：所有
	UINT cropLeft,
	UINT cropTop,
	UINT cropRight,
	UINT cropBottom
);
int main(int argc,char* argv[])
{
	FILE* fp;
	fopen_s(&fp, argv[1], "r");
	if (fp == 0)return 0;
	char cache[4096] = { 0 };
	char magpiepath[4096] = { 0 };
	HWND m_hWnd;
	char effect[4096] = { 0 };
	int flags, captureMode, CursorInterpolationMode, AdapterIdx, MultiMonitorUsage;
	float CursorZoomFactor;
	fgets(magpiepath, 4096, fp);
	magpiepath[strlen(magpiepath) - 1] = 0;
	printf("%s\n", magpiepath);
	fgets(cache, 4096, fp);
	sscanf_s(cache, "%lld\n", &m_hWnd); 
	fgets(effect, 4096, fp);
	effect[strlen(effect) - 1] = 0; 
	fgets(cache, 4096, fp);
	sscanf_s(cache, "%d,%d,%f,%d,%d,%d",
		&flags, &captureMode, &CursorZoomFactor, &CursorInterpolationMode, &AdapterIdx, &MultiMonitorUsage);

	fclose(fp); 
	SetForegroundWindow(m_hWnd);
	SetCurrentDirectoryA(magpiepath);
	HMODULE h = LoadLibrary(L".\\MagpieRT.dll");
	if (h == 0) return 0; 
	Initialize Initialize_f = (Initialize)GetProcAddress(h, "Initialize");
	Run Run_f = (Run)GetProcAddress(h, "Run");
	SetProcessDPIAware();
	Initialize_f(6, "./Runtime.log", 100000, 1);
	Run_f(m_hWnd, effect, flags, captureMode, CursorZoomFactor, CursorInterpolationMode, AdapterIdx, MultiMonitorUsage, 0, 0, 0, 0);
	
 
}
 