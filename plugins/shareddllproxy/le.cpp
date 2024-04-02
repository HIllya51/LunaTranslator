
#include <iostream>
#include <Windows.h>
#define SHIFT_JIS 932

int lewmain(int argc, wchar_t *argv[])
{
	std::wstring process = argv[1];
	std::wstring cmd = L"";
	for (int i = 1; i < argc; i++)
	{
		cmd += L"\"";
		cmd += argv[i];
		cmd += L"\" ";
	}
	auto cmd_x = new wchar_t[cmd.size() + 1];
	wcscpy(cmd_x, cmd.c_str());
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
		((LONG(__stdcall *)(decltype(&LEB), LPCWSTR appName, LPWSTR commandLine, LPCWSTR currentDir, void *, void *, PROCESS_INFORMATION *, void *, void *, void *, void *))
			 GetProcAddress(localeEmulator, "LeCreateProcess"))(&LEB, NULL, cmd_x, path.c_str(), NULL, NULL, &info, NULL, NULL, NULL, NULL);
	}
	return 1;
}
