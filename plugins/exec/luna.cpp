#include <windows.h>
#include<string> 
#pragma comment( linker, "/subsystem:windows /entry:mainCRTStartup" )
  
int main() { 
	STARTUPINFO _1 = {};
	PROCESS_INFORMATION _2;
	CreateProcessW( L".\\LunaTranslator\\LunaTranslator_main.exe",NULL,NULL,NULL,FALSE,0,NULL, L".\\",&_1,&_2);
	return 0;
}
 