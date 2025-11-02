#include "SYSD.h"

bool InsertSysdHook()
{

	/*
	 * Sample games:
	 * https://vndb.org/v2069
	 */
	const BYTE bytes[] = {
		0xC1, 0xE9, 0x02,			 // shr ecx,02      <- hook here
		0xF3, 0xA5,					 // repe movsd
		0x8B, 0xCA,					 // mov ecx,edx
		0x83, 0xE1, 0x03,			 // and ecx,03
		0xF3, 0xA4,					 // repe movsb
		0x5F,						 // pop edi
		0xB8, 0x01, 0x00, 0x00, 0x00 // mov eax,00000001
	};

	ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
	ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
	if (!addr)
	{
		ConsoleOutput("Sysd: pattern not found");
		return false;
	}

	HookParam hp;
	hp.address = addr;
	hp.offset = regoffset(esi);
	hp.index = 0;
	hp.padding = 0x12;
	hp.split = stackoffset(2);
	hp.split_index = 0;
	hp.type = USING_STRING | NO_CONTEXT | USING_SPLIT;
	hp.filter_fun = [](TextBuffer *buffer, HookParam *)
	{
		CharFilter(buffer, '\n');
	};
	ConsoleOutput("INSERT Sysd");
	return NewHook(hp, "Sysd");
}

bool SYSD::attach_function()
{
	return InsertSysdHook();
}