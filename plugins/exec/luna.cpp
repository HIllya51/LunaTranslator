#include <windows.h>
#include <string>
#include <filesystem>
#pragma comment(linker, "/subsystem:windows /entry:mainCRTStartup")

int main()
{
	TCHAR szPath[MAX_PATH];
	GetModuleFileName(NULL, szPath, ARRAYSIZE(szPath));
	std::wstring moduleName = szPath;
	auto currpath = moduleName.substr(0, moduleName.rfind(L'\\'));
	auto exe = currpath + L".\\LunaTranslator\\LunaTranslator_main.exe";
	if (!std::filesystem::exists(exe))
	{
		MessageBoxW(0, (L"Can't find LunaTranslator\\LunaTranslator_main.exe, please download again."), L"Error", 0);
		return 0;
	}
	STARTUPINFO _1 = {};
	PROCESS_INFORMATION _2;
	CreateProcessW(exe.c_str(), NULL, NULL, NULL, FALSE, 0, NULL, currpath.c_str(), &_1, &_2);
	return 0;
}
