#include <windows.h>
#include<string>
using std::string;
#pragma comment( linker, "/subsystem:windows /entry:mainCRTStartup" )
//int main() {
//	WinExec("./LunaTranslator/LunaTranslator.exe", SW_SHOW);
// /*
//
//	STARTUPINFO StartInfo;
//	PROCESS_INFORMATION pinfo;
//	memset(&StartInfo, 0, sizeof(STARTUPINFO));
//	StartInfo.cb = sizeof(STARTUPINFO);
//
//	CreateProcess(L"./LunaTranslator/LunaTranslator.exe", NULL, NULL, NULL, FALSE, NORMAL_PRIORITY_CLASS, NULL, NULL, &StartInfo, &pinfo); */
//
//}
int main(int argc, char* argv[]) {
	string ss = "";
	for (int i = 1; i < argc; i += 1) {
		ss += argv[i];
		ss += " ";

	}
	WinExec(ss.c_str(), SW_SHOW);
	/*

	   STARTUPINFO StartInfo;
	   PROCESS_INFORMATION pinfo;
	   memset(&StartInfo, 0, sizeof(STARTUPINFO));
	   StartInfo.cb = sizeof(STARTUPINFO);

	   CreateProcess(L"./LunaTranslator/LunaTranslator.exe", NULL, NULL, NULL, FALSE, NORMAL_PRIORITY_CLASS, NULL, NULL, &StartInfo, &pinfo); */

}