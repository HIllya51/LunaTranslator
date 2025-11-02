#include "V8.h"
#include "v8/v8.h"
#if 0
/**
*  Artikash 7/15/2018: Insert Tyranobuilder hook
*  Sample game: https://vndb.org/v22252: /HWN-8:-1C@233A54:yuika_t.exe
*  Artikash 9/11/2018: This is more than just Tyranobuilder. It's actually a hook for the V8 JavaScript runtime
*  Sample game: https://www.freem.ne.jp/win/game/9672: /HQ8@2317A0:Prison.exe This new hook seems more reliable
*  Nevermind both of those, just hook v8::String::Write https://v8docs.nodesource.com/node-0.8/d2/db3/classv8_1_1_string.html
*  v8::String::Write - 55                    - push ebp
*  v8::String::Write+1- 8B EC                 - mov ebp,esp
*  v8::String::Write+3- 8B 45 14              - mov eax,[ebp+14]
*  v8::String::Write+6- 8B 55 10              - mov edx,[ebp+10]
*  v8::String::Write+9- 50                    - push eax
*  v8::String::Write+A- 8B 45 0C              - mov eax,[ebp+0C]
*  v8::String::Write+D- 52                    - push edx
*  v8::String::Write+E- 8B 55 08              - mov edx,[ebp+08]
*  v8::String::Write+11- 50                   - push eax
*  v8::String::Write+12- 52                   - push edx
*  v8::String::Write+13- 51                   - push ecx
*  v8::String::Write+14- E8 B7C7FFFF          - call 6EF630 ; actual writing happens in this function, hooking after is possible
*  v8::String::Write+19- 83 C4 14             - add esp,14 { 20 }
*  v8::String::Write+1C- 5D                   - pop ebp
*  v8::String::Write+1D- C2 1000              - ret 0010 { 16 }
*/
void SpecialHookV8String(hook_context*, HookParam *hp, uintptr_t* data, uintptr_t* split, size_t* len)
{
	DWORD ecx = *data;
	DWORD strPtr = *(DWORD*)ecx;
	*data = strPtr + 0xb;
	*len = *(short*)(strPtr + 7);
	if(wcslen((wchar_t*)*data)*2<*len)*len=0;
	
	//if (*len < 12) *split = 1; // To ensure this is caught by cyclic repetition detection, split if there's 6+ wide chars
	//*split = *(DWORD*)((BYTE*)hp->split + dwDatabase);
}

bool InsertV8Hook(HMODULE module)
{
	auto [minAddress, maxAddress] = Util::QueryModuleLimits(module);
	for (const auto& pattern : Array<const BYTE[3]>{ { 0x55, 0x8b, 0xec }, { 0x55, 0x89, 0xe5 } })
	{
		int matches = Util::SearchMemory(pattern, sizeof(pattern), PAGE_EXECUTE, minAddress, maxAddress).size(), requiredRecords = matches * 20;
		if (matches > 10'000 && requiredRecords > spDefault.maxRecords)
		{
			memcpy(spDefault.pattern, pattern, spDefault.length = sizeof(pattern));
			spDefault.maxRecords = requiredRecords;
		}
	}
	std::tie(spDefault.minAddress, spDefault.maxAddress) = std::tuple{ minAddress, maxAddress };
	ConsoleOutput("JavaScript hook is known to be low quality: try searching for hooks if you don't like it");
	HookParam hp;
	hp.address = (DWORD)GetProcAddress(module, "?Write@String@v8@@QBEHPAGHHH@Z");
	hp.offset=regoffset(ecx);
	hp.type = CODEC_UTF16 | USING_STRING;
	hp.text_fun = SpecialHookV8String;
	auto succ=NewHook(hp, "JavaScript");
	const BYTE bytes[] = {
		0x83, 0xc4, XX, // add esp,XX
		0x5d, // pop ebp
		0xc2 // ret
	};
	if (DWORD addr = MemDbg::findBytes(bytes, sizeof(bytes), hp.address, hp.address + 0x30))
	{
		hp.address = addr;
		hp.offset = 0x8 + *(BYTE*)(addr + 2); // second argument + amount that the stack pointer is offset from arguments
		hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
		hp.length_offset = (0x10 + *(BYTE*)(addr + 2)) / 4; // fourth argument + amount that the stack pointer is offset from arguments
		hp.text_fun = nullptr;
		succ|=NewHook(hp, "JavaScript2");
	}
	return succ;
}
bool hookv8addr(HMODULE module) {
	if (GetProcAddress(module, "?Write@String@v8@@QBEHPAGHHH@Z")==0)false;
	auto [minAddress, maxAddress] = Util::QueryModuleLimits(module);
	const BYTE bytes[] = {
		0x89,0xc1,
		0x0f,0xb7,0xd8,
		0x81,0xe1,0x00,0xfc,0x00,0x00,
		0x81,0xf9,0x00,0xd8,0x00,0x00
	};
	ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), minAddress, maxAddress);
	if (!addr) {
		return false;
	}
	HookParam hp;
	hp.address = addr;

	hp.offset=regoffset(eax);

	hp.type = CODEC_UTF16 | NO_CONTEXT; 

	return NewHook(hp, "electronW");
}

#endif
bool V8::attach_function_()
{

	return tryhookv8();
}
