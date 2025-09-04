#include "Regista.h"
namespace
{
	// ルートダブル -Before Crime * After Days-
	bool old()
	{
		const BYTE bytes[] = {
			0x8a, 0x10, 0x83, 0xC0, 0x04, 0x83, 0xc1, 0x04, 0x84, 0xd2, 0x74};
		auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
		ConsoleOutput("%p", addr);
		if (!addr)
			return false;

		addr = findfuncstart(addr, 0x40);
		ConsoleOutput("%p", addr);
		if (!addr)
			return false;
		HookParam hp;
		hp.address = addr;
		hp.offset = stackoffset(1);
		hp.type = DATA_INDIRECT;
		hp.index = 0;
		return NewHook(hp, "Regista");
	}
	bool _2()
	{
		bool succ = false;
		const BYTE bytes[] = {
			// old不是很好，old是strcmp，有很多乱七八糟的，这个是脚本的一些控制字符判断和shiftjis范围判断。
			0x80, 0xF9, 0x81,
			XX2,
			0x80, 0xF9, 0x9F,
			XX2,
			0x80, 0xF9, 0xE0,
			XX2,
			0x80, 0xF9, 0xFC};
		for (auto addr : Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress))
		{
			const BYTE start[] = {
				0xCC, 0xCC, 0xCC, 0xCC};
			addr = reverseFindBytes(start, sizeof(start), addr - 0x40, addr, 4);
			if (!addr)
				continue;
			const BYTE check[] = {
				0x8b, 0x15, XX4, // mov     edx, dword_3EA6904
				0x8a, 0x0a,		 // mov     cl, [edx]
			};
			if (MatchPattern(addr, check, sizeof(check)))
				addr += 6;
			HookParam hp;
			hp.address = addr;
			hp.offset = regoffset(edx);
			hp.type = USING_STRING;
			hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
			{
				// ……黒く、冷たい銃口と、%Nもっと冷たい、黒い瞳が……
				auto s = buffer->strA();
				s = re::sub(s, "%[Nn]");
				buffer->from(s);
			};
			succ |= NewHook(hp, "Regista2");
		}
		return succ;
	}
}

bool Regista::attach_function()
{
	return _2() || old();
}