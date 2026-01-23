#include "sakanagl.h"
namespace
{
	bool h1(uintptr_t minAddress, uintptr_t maxAddress)
	{
		// 猫猫旅行社 ももいろ町おこしプロジェクト！
		BYTE bytes[] = {
			0x49, 0x23, 0xc5,
			0x4c, 0x89, 0xbc, 0x24, XX4,
			0x48, 0x8b, 0x58, 0x38,
			0xe8, XX4, // u8->u32(?,?,u8)->len
			0x8b, 0x4b, 0x10,
			0x4c, 0x63, 0xe0,
			0x41, 0x03, 0xcc,
			0x8d, 0x2c, 0x8d, 0x04, 0x00, 0x00, 0x00,
			0x8b, 0xcd,
			0xe8, XX4, // new string<char32_t>
			0x4c, 0x63, 0x43, 0x10,
			0x48, 0x8b, 0xc8,
			0x48, 0x8b, 0x53, 0x20,
			0x4c, 0x8b, 0xf8,
			0x49, 0xc1, 0xe0, 0x02, // size*4
			0xe8, XX4,				// memmove
		};
		auto addr = MemDbg::findBytes(bytes, sizeof(bytes), minAddress, maxAddress);
		if (!addr)
			return false;
		HookParam hp;
		hp.address = addr + 3 + 8 + 4;
		static char32_t **str;
		hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
		{
			str = (char32_t **)context->r8;
		};
		if (!NewHook(hp, "sakanagldll"))
			return false;
		hp.address = addr + 3 + 8 + 4 + 5;
		hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
		{
			buffer->from(std::u32string_view(*str, context->rax));
		};
		hp.type = USING_STRING | CODEC_UTF32 | EMBED_ABLE;
		hp.embed_fun = [](hook_context *context, TextBuffer buffer, HookParam *)
		{
			context->rax = buffer.viewU().size();
			*str = allocateString(buffer.viewU());
		};
		return NewHook(hp, "sakanagldll");
	}
}
bool sakanagl::attach_function()
{
	// 年上お姉さんを独り占めしたい！
	// https://store.steampowered.com/app/2541470/__Possessing_My_Older_Sister/?l=japanese
	auto [minAddress, maxAddress] = Util::QueryModuleLimits(hmodule);
	return h1(minAddress, maxAddress);
}