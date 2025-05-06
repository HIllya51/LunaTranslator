#include "Godot.h"

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

		ConsoleOutput("Insert: Godot_add_text_X64 Hook ");
		return NewHook(myhp, nameForUser);
	}

	ConsoleOutput("Godot_x64: pattern not found");
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
		ConsoleOutput("INSERT Godot2_x64 Hook ");
		return NewHook(hp, "Godot2_x64");
	}

	ConsoleOutput("Godot2_x64: pattern not found");
	return false;
}
bool Godot::attach_function()
{
	auto _ = InsertGodotHook_X64();
	_ = InsertGodotHook2_X64() || _;
	return _;
}