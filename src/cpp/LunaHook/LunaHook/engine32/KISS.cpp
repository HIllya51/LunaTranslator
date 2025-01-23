#include "KISS.h"

bool InsertKissHook()
{

	/*
	 * Sample games:
	 * https://vndb.org/v1767
	 */
	const BYTE bytes[] = {
		0xC1, 0xE9, 0x02,		// shr ecx,02      <- hook here
		0xF3, 0xA5,				// repe movsd
		0x8B, 0xCA,				// mov ecx,edx
		0x55,					// push ebp
		0x83, 0xE1, 0x03,		// and ecx,03
		0xF3, 0xA4,				// repe movsb
		0x8D, 0x4C, 0x24, 0x18, // lea ecx,[esp+18]
		0xE8, XX4,				// call kano.exe+6310
		0x8B, 0x0D, XX4			// mov ecx,[kano.exe+211F8C]
	};

	ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
	ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
	if (!addr)
	{
		ConsoleOutput("Kiss: pattern not found");
		return false;
	}

	HookParam hp;
	hp.address = addr;
	hp.offset = regoffset(esi);
	hp.type = USING_STRING | NO_CONTEXT | EMBED_DYNA_SJIS | EMBED_ABLE | EMBED_AFTER_NEW;
	hp.embed_hook_font = F_GetTextExtentPoint32A | F_ExtTextOutA;
	ConsoleOutput("INSERT Kiss");
	return NewHook(hp, "Kiss");
}
bool KISS::attach_function()
{
	return InsertKissHook();
}