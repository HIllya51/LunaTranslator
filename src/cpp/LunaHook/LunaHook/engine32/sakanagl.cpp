#include "sakanagl.h"

bool sakanagl::attach_function()
{
	// 年上お姉さんを独り占めしたい！
	// https://store.steampowered.com/app/2541470/__Possessing_My_Older_Sister/?l=japanese
	auto [minAddress, maxAddress] = Util::QueryModuleLimits(hmodule);
	BYTE bytes[] = {
		0x89, 0x01, 0x33, 0xc9, 0x85, 0xdb};
	auto addr = MemDbg::findBytes(bytes, sizeof(bytes), minAddress, maxAddress);

	HookParam hp;
	hp.address = (DWORD)addr;
	hp.offset = regoffset(edx);
	hp.type = USING_STRING | CODEC_UTF8 | EMBED_ABLE | EMBED_AFTER_OVERWRITE;
	return NewHook(hp, "sakanagldll");
}