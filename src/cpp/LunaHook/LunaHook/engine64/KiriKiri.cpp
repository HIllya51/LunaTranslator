#include "KiriKiri.h"
bool InsertKiriKiriZHook()
{

	/*
	 * Sample games:
	 * RJ351843
	 */
	const BYTE bytes[] = {
		0xCC,												 // int 3
		0x4C, 0x89, 0x44, 0x24, 0x18,						 // mov [rsp+18],r8       <- hook here
		0x48, 0x89, 0x54, 0x24, 0x10,						 // mov [rsp+10],rdx
		0x53,												 // push rbx
		0x56,												 // push rsi
		0x57,												 // push rdi
		0x41, 0x54,											 // push r12
		0x41, 0x55,											 // push r13
		0x41, 0x56,											 // push r14
		0x41, 0x57,											 // push r15
		0x48, 0x83, 0xEC, 0x40,								 // sub rsp,40
		0x48, 0xC7, 0x44, 0x24, 0x30, 0xFE, 0xFF, 0xFF, 0xFF // mov qword ptr [rsp+30],FFFFFFFFFFFFFFFE
	};

	ULONG64 range = min(processStopAddress - processStartAddress, X64_MAX_REL_ADDR);
	for (auto addr : Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStartAddress + range))
	{
		HookParam hp;
		hp.address = addr + 1;
		hp.offset = regoffset(rcx);
		hp.index = 0x18;
		hp.type = CODEC_UTF16 | DATA_INDIRECT;
		return NewHook(hp, "KiriKiriZ");
	}
	return false;
}
bool Insertkrkrz64Hook()
{
	const BYTE BYTES[] = {
		0x41, 0x0F, 0xB7, 0x44, 0x24, 0x04,
		0x89, 0x43, 0x20,
		0x41, 0x0F, 0xB7, 0x44, 0x24, 0x06,
		0x89, 0x43, 0x24,
		0x41, 0x0F, 0xBF, 0x44, 0x24, 0x0C,
		0x89, 0x43, 0x14};
	auto addrs = Util::SearchMemory(BYTES, sizeof(BYTES), PAGE_EXECUTE_READ, processStartAddress, processStopAddress);
	ConsoleOutput("%p %p", processStartAddress, processStopAddress);
	for (auto addr : addrs)
	{
		ConsoleOutput("krkrz64 %p", addr);
		const BYTE funcstart[] = {0xcc, 0xcc, 0xcc, 0xcc};
		addr = reverseFindBytes(funcstart, sizeof(funcstart), addr - 0x1000, addr);
		if (!addr)
			continue;
		addr += 4;
		HookParam hp;
		hp.address = addr;
		hp.type = CODEC_UTF16 | DATA_INDIRECT;
		hp.offset = regoffset(rcx);
		hp.index = 0x18;
		ConsoleOutput("krkrz64 %p %x", addr);
		return NewHook(hp, "krkrz64");
	}

	ConsoleOutput("krkrz64 failed");
	return false;
}
bool KiriKiri::attach_function()
{
	return Insertkrkrz64Hook() || InsertKiriKiriZHook();
}
