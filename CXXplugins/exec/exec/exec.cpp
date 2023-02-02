#include <windows.h>
#include<string> 
#pragma comment( linker, "/subsystem:windows /entry:mainCRTStartup" )
  
int main() { 
	ShellExecute(0, L"open", L".\\LunaTranslator\\LunaTranslator_main.exe ", L"", L"", SW_SHOW); 
	return 0;
}
 