
#include "../hookcode.h"
#include <io.h>
#include <fcntl.h>
#include <iostream>
#include<string>
int wmain(int argc, wchar_t* argv[])
{ 
	_setmode(_fileno(stdout), _O_U16TEXT);
	_setmode(_fileno(stdin), _O_U16TEXT);
	//wprintf_s(argv[1]);
	//wprintf_s(L"\n");
	if (auto hp = HookCode::Parse(argv[1])) {
		
		wprintf_s(L"1");
	}
	else {
		wprintf_s(L"0");
	}
}
