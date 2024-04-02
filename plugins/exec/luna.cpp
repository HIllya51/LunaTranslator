#include <windows.h>
#include <string>
#include <filesystem>
#pragma comment(linker, "/subsystem:windows /entry:mainCRTStartup")

int main()
{
	if (!std::filesystem::exists(L".\\LunaTranslator\\LunaTranslator_main.exe"))
	{
		MessageBoxW(0, L"Cant' find ./LunaTranslator/LunaTranslator_main.exe, please download again!", L"Error", 0);
		return 0;
	}
	STARTUPINFO _1 = {};
	PROCESS_INFORMATION _2;
	CreateProcessW(L".\\LunaTranslator\\LunaTranslator_main.exe", NULL, NULL, NULL, FALSE, 0, NULL, L".\\", &_1, &_2);
	return 0;
}
