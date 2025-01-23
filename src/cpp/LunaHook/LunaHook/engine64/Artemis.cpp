#include "Artemis.h"

bool InsertArtemisHook()
{

	/*
	 * Sample games:
	 * https://vndb.org/v45247
	 */
	const BYTE bytes[] = {
		0xCC,							   // int 3
		0x40, 0x57,						   // push rdi          <- hook here
		0x48, 0x83, 0xEC, 0x40,			   // sub rsp,40
		0x48, 0xC7, 0x44, 0x24, 0x30, XX4, // mov qword ptr [rsp+30],FFFFFFFFFFFFFFFE
		0x48, 0x89, 0x5C, 0x24, 0x50	   // mov [rsp+50],rbx
	};

	for (auto addr : Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress))
	{
		HookParam hp;
		hp.address = addr + 1;
		hp.offset = regoffset(rdx);
		hp.type = USING_STRING | CODEC_UTF8 | NO_CONTEXT;
		ConsoleOutput("INSERT Artemis Hook ");
		return NewHook(hp, "Artemis");
	}

	ConsoleOutput("Artemis: pattern not found");
	return false;
}
bool Artemis64()
{

	const BYTE BYTES[] = {
		0x48, 0x89, 0x5C, 0x24, 0x20, 0x55, 0x56, 0x57, 0x41, 0x54, 0x41, 0x55, 0x41, 0x56, 0x41, 0x57, 0x48, 0x83, 0xec, 0x60
		//__int64 __fastcall sub_14017A760(__int64 a1, char *a2, char **a3)
		// FLIP FLOP IO
	};
	auto addrs = Util::SearchMemory(BYTES, sizeof(BYTES), PAGE_EXECUTE_READ, processStartAddress, processStopAddress);
	for (auto addr : addrs)
	{
		char info[1000] = {};
		ConsoleOutput("InsertArtemis64Hook %p", addr);
		HookParam hp;
		hp.address = addr;
		hp.type = CODEC_UTF8 | USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW;
		hp.offset = regoffset(rdx); // rdx
		return NewHook(hp, "Artemis64");
	}

	ConsoleOutput("InsertArtemis64Hook failed");
	return false;
}

bool Artemis64x()
{
	// https://vndb.org/v50832
	// きら☆かの 体验版

	/*
	__int64 __fastcall sub_1401B13F0(__int64 a1, unsigned __int64 a2, char **a3)
	v4 = (char *)a2;
	v9 = *v4;
	 if ( (unsigned __int8)(v9 + 95) <= 0x53u || (_BYTE)v9 == 0x8E )
	  else if ( v8 == 2 && (v9 & 0x80u) != 0 )
		else if ( ((unsigned __int8)v9 ^ 0x20u) - 161 < 0x3C )
		if ( (unsigned __int8)(a2 - 65) > 0x19u && (unsigned __int8)(a2 - 97) > 0x19u )
		 if ( (unsigned __int8)(*v4 + 95) > 0x53u && *v4 != -114 )
	*/

	// else if ( ((unsigned __int8)v9 ^ 0x20u) - 161 < 0x3C )
	/*
	.text:00000001401B1477                 movzx   eax, dl
.text:00000001401B147A                 xor     eax, 20h
.text:00000001401B147D                 sub     eax, 0A1h
.text:00000001401B1482                 cmp     eax, 3Ch ; '<'
.text:00000001401B1485                 jnb     loc_1401B1510
	*/

	const BYTE BYTES[] = {
		0x0f, 0xb6, 0xc2,
		0x83, 0xf0, 0x20,
		0x2d, 0xa1, 0x00, 0x00, 0x00,
		0x83, 0xf8, 0x3c,
		0x0f, 0x83, XX4

	};
	auto succ = false;
	auto addrs = Util::SearchMemory(BYTES, sizeof(BYTES), PAGE_EXECUTE_READ, processStartAddress, processStopAddress);
	for (auto addr : addrs)
	{
		BYTE start[] = {0xCC, 0xCC, 0x48, 0x89};
		addr = reverseFindBytes(start, sizeof(start), addr - 0x200, addr);
		if (!addr)
			continue;
		HookParam hp;
		hp.address = addr + 2;
		hp.type = CODEC_UTF8 | USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | USING_SPLIT | NO_CONTEXT;
		hp.offset = regoffset(rdx);
		hp.split = regoffset(rcx);
		succ |= NewHook(hp, "Artemis64x");
	}

	return succ;
}
bool Artemis::attach_function()
{
	bool b1 = Artemis64();
	b1 = InsertArtemisHook() || b1;
	return b1 || Artemis64x();
}