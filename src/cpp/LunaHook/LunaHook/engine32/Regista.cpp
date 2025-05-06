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
		const BYTE bytes[] = {
			// old不是很好，old是strcmp，有很多乱七八糟的，这个是脚本的一些控制字符判断和shiftjis范围判断。
			0x80, 0xF9, 0x81,
			XX2,
			0x80, 0xF9, 0x9F,
			XX2,
			0x80, 0xF9, 0xE0,
			XX2,
			0x80, 0xF9, 0xFC};
		auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
		ConsoleOutput("%p", addr);
		if (!addr)
			return false;
		const BYTE start[] = {
			0xCC, 0xCC, 0xCC, 0xCC};
		addr = reverseFindBytes(start, sizeof(start), addr - 0x40, addr);
		if (!addr)
			return false;
		HookParam hp;
		hp.address = addr + 4;
		hp.offset = regoffset(edx);
		hp.type = USING_STRING;
		return NewHook(hp, "Regista");
	}
}

bool Regista::attach_function()
{
	return _2() || old();
}