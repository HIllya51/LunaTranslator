#include "BKEngine.h"
// https://bke.bakery.moe/download.html
namespace
{
	bool _1()
	{
		BYTE sig[] = {0x64, 0xa3, 0x00, 0x00, 0x00, 0x00, 0x8b, 0xf1, 0x8b, 0x45, 0x08, 0x0f, 0x57, 0xc0, 0xc7, 0x06, 0x02, 0x00, 0x00, 0x00};
		auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
		if (!addr)
			return 0;
		addr = MemDbg::findEnclosingAlignedFunction(addr);
		if (!addr)
			return 0;
		HookParam hp;
		hp.address = addr;
		hp.type = CODEC_UTF16 | DATA_INDIRECT;
		hp.index = 0;
		hp.offset = stackoffset(1);

		return NewHook(hp, "BKEngine1");
	}
	bool _2()
	{
		BYTE sig[] = {0xb8, 0xff, 0x00, 0x00, 0x00, 0x66, 0x3b, 0x06, 0x1b, 0xc0, 0xf7, 0xd8, 0x40};
		auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
		if (!addr)
			return 0;
		addr = MemDbg::findEnclosingAlignedFunction(addr);
		if (!addr)
			return 0;
		HookParam hp;
		hp.address = addr;
		hp.type = CODEC_UTF16 | DATA_INDIRECT | NO_CONTEXT;
		hp.index = 0;
		hp.offset = stackoffset(1);

		return NewHook(hp, "BKEngine2");
	}
	bool _3()
	{
		BYTE sig[] = {0x6a, 0xff, 0x6a, 0x00, 0x56};
		std::unordered_map<DWORD, int> mp;
		DWORD maxaddr = 0;
		int maxi = 0;
		for (auto addr : Util::SearchMemory(sig, sizeof(sig), PAGE_EXECUTE, processStartAddress, processStopAddress))
		{
			addr = MemDbg::findEnclosingAlignedFunction(addr);
			if (!addr)
				continue;
			if (!mp.count(addr))
				mp[addr] = 0;
			mp[addr] += 1;
			if (mp[addr] > maxi)
			{
				maxi = mp[addr];
				maxaddr = addr;
			}
		}
		if (maxaddr == 0)
			return 0;

		HookParam hp;
		hp.address = maxaddr;
		hp.type = CODEC_UTF16 | USING_STRING;
		hp.offset = regoffset(edx);

		return NewHook(hp, "BKEngine3");
	}
}
bool BKEngine::attach_function()
{

	bool ok = _1();
	ok = _2() || ok;
	ok = _3() || ok;
	return ok;
}