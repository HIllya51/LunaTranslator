#include "sakanagl.h"

bool sakanagl::attach_function()
{
	// 年上お姉さんを独り占めしたい！
	// https://store.steampowered.com/app/2541470/__Possessing_My_Older_Sister/?l=japanese
	HMODULE module = GetModuleHandleW(L"sakanagl.dll");
	if (module == 0)
		return false;
	auto [minAddress, maxAddress] = Util::QueryModuleLimits(module);
	BYTE bytes[] = {
		0x89, 0x01, 0x33, 0xc9, 0x85, 0xdb};
	auto addr = MemDbg::findBytes(bytes, sizeof(bytes), minAddress, maxAddress);

	ConsoleOutput("sakanagldll %p", addr);
	HookParam hp;
	hp.address = (DWORD)addr;
	hp.offset = regoffset(edx);
	hp.type = USING_STRING | CODEC_UTF8 | EMBED_ABLE | EMBED_AFTER_OVERWRITE;
	return NewHook(hp, "sakanagldll");
}