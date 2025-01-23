#include "Nitroplus.h"

bool InsertNitroplusHook()
{
	const BYTE bytes[] = {0xb0, 0x74, 0x53};
	DWORD addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
	if (!addr)
	{
		ConsoleOutput("Nitroplus: pattern not exist");
		return false;
	}
	enum : WORD
	{
		sub_esp = 0xec83
	}; // caller pattern: sub esp = 0x83,0xec
	BYTE b = *(BYTE *)(addr + 3) & 3;
	while (*(WORD *)addr != sub_esp)
		addr--;
	HookParam hp;
	hp.address = addr;
	hp.offset = -0x14 + (b << 2);
	hp.type = CODEC_ANSI_BE;
	ConsoleOutput("INSERT Nitroplus");
	return NewHook(hp, "Nitroplus");
	// RegisterEngineType(ENGINE_Nitroplus);
}
bool InsertNitroplus2Hook()
{

	/*
	 * Sample games:
	 * https://vndb.org/v428
	 */
	BYTE bytes[] = {
		0x8D, 0xB4, 0x29, XX4, // lea esi,[ecx+ebp+0000415C]
		0x74, 0x20,			   // je Django.exe+6126E
		0x8D, 0xBC, 0xBD, XX4, // lea edi,[ebp+edi*4+0006410C]
		0x8B, 0x56, 0xB0,	   // mov edx,[esi-50]
		0xE8, XX4			   // call Django.exe+51150      << hook here
	};
	enum
	{
		addr_offset = sizeof(bytes) - 5
	};
	ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
	if (!addr)
	{
		ConsoleOutput("Nitroplus2: pattern not found");
		return false;
	}
	HookParam hp;
	hp.address = addr + addr_offset;
	hp.offset = regoffset(edx);
	hp.type = CODEC_ANSI_BE;
	return NewHook(hp, "Nitroplus2");
}
namespace
{
	//	DRAMAtical Murder re:connect 普及版
	// https://vndb.org/v10895
	bool dmmdrc()
	{
		// BYTE sig[]={
		// 	0xc7,0x04,0x24,0x24,0x53,0x59,0x53,//$SYS
		// 	0xc7,0x44,0x24,0x04,0x54,0x45,0x4d,0x5f,//TEM_
		// 	0xc7,0x44,0x24,0x08,0x6c,0x61,0x73,0x74,//last
		// 	0xc7,0x44,0x24,0x0c,0x5f,0x74,0x65,0x78,//_tex
		// };
		BYTE sig[] = {
			0x8d, 0x89, XX4,
			0x8b, 0xc2,
			0xc1, 0xe8, 0x08,
			0x88, 0x01,
			0x88, 0x51, 0x01,
			0xc6, 0x41, 0x02, 0x00};
		ULONG addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
		if (!addr)
			return false;
		HookParam hp;
		hp.address = *(DWORD *)(addr + 2);
		hp.type = DIRECT_READ;
		auto succ = NewHook(hp, "dmmdrc");

		BYTE sig2[] = {
			0x68, 0x00, 0x02, 0x00, 0x00,
			0xba, XX4,
			0xe8, XX4};
		memcpy(sig2 + 6, (void *)(addr + 2), 4);
		addr = MemDbg::findBytes(sig2, sizeof(sig2), addr, addr + 0x100);
		if (addr)
		{
			HookParam hp;
			hp.address = addr + sizeof(sig2);
			hp.type = USING_STRING;
			hp.user_value = 0;
			hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
			{
				auto data = context->edx;
				auto l = strlen((char *)data);
				if (hp->user_value > l)
					hp->user_value = 0;
				data += hp->user_value;
				auto len = l - hp->user_value;
				hp->user_value = l;
				buffer->from(data, len);
			};
			succ |= NewHook(hp, "dmmdrc2");
		}
		return succ;
	}
}
bool Nitroplus::attach_function()
{

	return InsertNitroplusHook() || InsertNitroplus2Hook() || dmmdrc();
}

void NitroplusSysFilter(TextBuffer *buffer, HookParam *)
{
	auto text = reinterpret_cast<LPSTR>(buffer->buff);

	if (buffer->size <= 2)
		return buffer->clear();

	StringFilter(buffer, "\x81@", 2);
	CharReplacer(buffer, '\r', ' ');
	if (cpp_strnstr(text, "<", buffer->size))
	{
		StringFilterBetween(buffer, "<", 1, ">", 1);
	}
	while (buffer->size > 1 && ::isspace(*text))
	{
		::memmove(text, text + 1, --buffer->size);
	}
}

bool InsertNitroplusSysHook()
{

	/*
	 * Sample games:
	 * https://vndb.org/r76679
	 */
	const BYTE bytes[] = {
		0x0F, 0x84, XX4,		// je system.dll+5B8CA        <- hook here
		0xEB, 0x04,				// jmp system.dll+5A791
		0x8B, 0x44, 0x24, 0x20, // mov eax,[esp+20]
		0x8B, 0x4C, 0x24, 0x24	// mov ecx,[esp+24]
	};

	HMODULE module = GetModuleHandleW(L"system.dll");
	auto [minAddress, maxAddress] = Util::QueryModuleLimits(module);
	ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), minAddress, maxAddress);
	if (!addr)
		return false;

	HookParam hp;
	hp.address = addr;
	hp.offset = regoffset(eax);
	hp.type = USING_STRING;
	hp.filter_fun = NitroplusSysFilter;
	return NewHook(hp, "NitroplusSystem");
}
bool Nitroplusplus::attach_function()
{
	return InsertNitroplusSysHook();
}