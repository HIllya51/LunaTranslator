// cleproc.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <iostream>
#include<Windows.h>
#define  SHIFT_JIS  932

#pragma comment( linker, "/subsystem:windows /entry:wmainCRTStartup" )
int wmain(int argc,wchar_t *argv[])
{
	std::wstring process = argv[1];
	
	std::wstring path = std::wstring(process).erase(process.rfind(L'\\'));
	 
	PROCESS_INFORMATION info = {};
	if (HMODULE localeEmulator = LoadLibraryW(L"LoaderDll"))
	{
		
		// https://github.com/xupefei/Locale-Emulator/blob/aa99dec3b25708e676c90acf5fed9beaac319160/LEProc/LoaderWrapper.cs#L252
		struct
		{
			ULONG AnsiCodePage = SHIFT_JIS;
			ULONG OemCodePage = SHIFT_JIS;
			ULONG LocaleID = LANG_JAPANESE;
			ULONG DefaultCharset = SHIFTJIS_CHARSET;
			ULONG HookUiLanguageApi = FALSE;
			WCHAR DefaultFaceName[LF_FACESIZE] = {};
			TIME_ZONE_INFORMATION Timezone;
			ULONG64 Unused = 0;
		} LEB;
		GetTimeZoneInformation(&LEB.Timezone);
		((LONG(__stdcall*)(decltype(&LEB), LPCWSTR appName, LPWSTR commandLine, LPCWSTR currentDir, void*, void*, PROCESS_INFORMATION*, void*, void*, void*, void*))
			GetProcAddress(localeEmulator, "LeCreateProcess"))(&LEB, process.c_str(), NULL, path.c_str(), NULL, NULL, &info, NULL, NULL, NULL, NULL);
	}
}

// 运行程序: Ctrl + F5 或调试 >“开始执行(不调试)”菜单
// 调试程序: F5 或调试 >“开始调试”菜单

// 入门使用技巧: 
//   1. 使用解决方案资源管理器窗口添加/管理文件
//   2. 使用团队资源管理器窗口连接到源代码管理
//   3. 使用输出窗口查看生成输出和其他消息
//   4. 使用错误列表窗口查看错误
//   5. 转到“项目”>“添加新项”以创建新的代码文件，或转到“项目”>“添加现有项”以将现有代码文件添加到项目
//   6. 将来，若要再次打开此项目，请转到“文件”>“打开”>“项目”并选择 .sln 文件
