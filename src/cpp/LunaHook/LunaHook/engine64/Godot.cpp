#include "Godot.h"
static bool _shaped_text_add_string()
{
	char _shaped_text_add_string[] = "_shaped_text_add_string";
	auto addr = MemDbg::findBytes(_shaped_text_add_string, sizeof(_shaped_text_add_string), processStartAddress, processStopAddress);
	if (!addr)
		return false;
	addr = MemDbg::find_leaorpush_addr(addr, processStartAddress, processStopAddress);
	if (!addr)
		return false;
	BYTE sig2[] = {0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54};
	addr = reverseFindBytes(sig2, sizeof(sig2), addr - 0x200, addr, 0, true);
	if (!addr)
		return false;
	const BYTE checkcodec_u16[] = {0x8B, 0x40, 0xFC, 0x83, 0xF8, 0x01, 0x83, 0xD0, 0xFF};
	const BYTE checkcodec_u32[] = {0x48, 0x8B, 0x40, 0xF8, 0x83, 0xF8, 0x01, 0x83, 0xD0, 0xFF};
	auto isu16 = MemDbg::findBytes(checkcodec_u16, sizeof(checkcodec_u16), addr, addr + 0x1000);
	auto isu32 = MemDbg::findBytes(checkcodec_u32, sizeof(checkcodec_u32), addr, addr + 0x1000);
	if (!isu16 && !isu32)
		return false;
	HookParam hp;
	hp.address = addr;
	hp.offset = regoffset(r8);
	if (isu16)
		hp.type = USING_STRING | CODEC_UTF16 | FULL_STRING | DATA_INDIRECT;
	else if (isu32)
		hp.type = USING_STRING | CODEC_UTF32 | FULL_STRING | DATA_INDIRECT;
	return NewHook(hp, "_shaped_text_add_string");
}
bool InsertGodotHook_X64()
{
	const BYTE bytes[] = {0x8B, 0x40, 0xFC, 0x83, 0xF8, 0x01, 0x83, 0xD0, 0xFF, 0x41, 0x39, 0xC6};

	ULONG64 range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
	for (auto addr : Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStartAddress + range))
	{
		HookParam myhp;
		myhp.address = addr;

		myhp.type = USING_STRING | CODEC_UTF16 | NO_CONTEXT; // /HQ 不使用上下文区分 把所有线程的文本都提取
		// myhp.padding = 0xc;//[esp+4]+padding
		//  data_offset
		myhp.offset = regoffset(rax);
		myhp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
		{
			int len = *(int *)(context->rax - 4);
			if (len != wcslen((wchar_t *)context->rax))
				return;
			buffer->from(context->rax, len * 2);
		};
		char nameForUser[HOOK_NAME_SIZE] = "RichTextLabel_add_text";

		return NewHook(myhp, nameForUser);
	}

	return false;
}
bool InsertGodotHook2_X64()
{

	/*
	 * Sample games:
	 * https://vndb.org/r109138
	 */
	const BYTE bytes[] = {
		0x48, 0x8B, 0x94, 0x24, XX4, // mov rdx,[rsp+000001C0]	<- hook here
		0x4C, 0x89, 0xE1,			 // mov rcx,r12
		0xE8, XX4,					 // call NULL-Windows.exe+D150
		0x49, 0x8B, 0x06,			 // mov rax,[r14]
		0x48, 0x85, 0xC0,			 // test rax,rax
		0x0F, 0x85, XX4				 // jne NULL-Windows.exe+A359D4

	};

	ULONG64 range = min(processStopAddress - processStartAddress, X64_MAX_REL_ADDR);
	for (auto addr : Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStartAddress + range))
	{
		HookParam hp;
		hp.address = addr;
		hp.offset = regoffset(rcx);
		hp.type = USING_STRING | CODEC_UTF16;
		return NewHook(hp, "Godot2_x64");
	}

	return false;
}
bool Godot::attach_function()
{
	auto _ = InsertGodotHook_X64();
	_ = InsertGodotHook2_X64() || _;
	return _ | _shaped_text_add_string();
}