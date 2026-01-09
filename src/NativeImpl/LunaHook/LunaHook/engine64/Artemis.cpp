#include "Artemis.h"
namespace
{
	void filtercommon(TextBuffer *buffer, HookParam *hp)
	{
		Utf8TypeChecker(buffer, hp);
		auto s = buffer->strA();
		if (hp->type & CODEC_UTF8)
		{
			if (s == u8"「」（）『』")
				return buffer->clear();
			else if (s == u8"　")
				return buffer->clear();
			else if (s == u8"「」（）『』")
				return buffer->clear();
		}
		else
		{
			if (s == "\x81\x75\x81\x76\x81\x69\x81\x6a\x81\x77\x81\x78")
				return buffer->clear();
			else if (s == "\x81\x40")
				return buffer->clear();
			else if (s == "\x81\x75\x81\x76\x81\x69\x81\x6a\x81\x77\x81\x78")
				return buffer->clear();
		}
		if (re::match(s, "\\d+"))
			return buffer->clear();
	}
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
		hp.type = CODEC_UTF8 | USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | NO_CONTEXT;
		hp.offset = regoffset(rdx);
		hp.filter_fun = filtercommon;
		succ |= NewHook(hp, "Artemis64x");
	}

	return succ;
}
bool InsertArtemisHook()
{
	const BYTE bytes[] = {
		0x41, 0x0f, 0xb6, 0xc1,
		0x83, 0xf0, 0x20,
		0x2d, 0xa1, 0x00, 0x00, 0x00,
		0x41, 0x8b, XX,
		0x83, 0xf8, 0x3c,
		0x0f, 0x92, 0xc1,
		0xeb, XX,
		0x83, 0xf8, 0x01,
		0x75, 0x1a,
		0x41, 0x8d, 0x41, 0x5f,
		0x3c, 0x53,
		0x76, XX,
		0x41, 0x80, 0xf9, 0x8e,
		0x74, XX};
	auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
	if (!addr)
		return false;
	addr = MemDbg::findEnclosingAlignedFunction(addr);
	if (!addr)
		return false;
	HookParam hp;
	hp.address = addr;
	hp.offset = regoffset(r8);
	hp.type = USING_STRING | CODEC_UTF8 | NO_CONTEXT;
	hp.filter_fun = Utf8TypeChecker;
	return NewHook(hp, "Artemis");
}
bool InsertArtemisHook2()
{
	// 妹(姉)は兄(弟)の性癖を歪ませたい！
	// きら☆かの
	const BYTE bytes[] = {
		0x48, 0x89, 0x5c, 0x24, 0x20,
		0x55, 0x56, 0x57,
		0x48, 0x83, 0xec, XX,
		0x48, 0x8b, 0x05, XX4,
		0x48, 0x33, 0xc4,
		0x48, 0x89, 0x44, 0x24, XX,
		// v4 = *a1;
		// if ( *a2 == 10 )
		0x48,
		0x8b, 0xfa,
		0x48, 0x8b, 0xd9,
		0x48, 0x8b, 0x01,
		0x80, 0x3a, 0x0a,
		0x75, 0x0d};
	auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
	if (!addr)
		return false;
	HookParam hp;
	hp.address = addr;
	hp.offset = regoffset(rdx);
	hp.type = USING_STRING | CODEC_UTF8 | NO_CONTEXT;
	hp.filter_fun = Utf8TypeChecker;
	return NewHook(hp, "Artemis");
}
bool Artemis::attach_function()
{
	// 后两者能提取到rubytext
	return Artemis64x() | (InsertArtemisHook() || InsertArtemisHook2());
}