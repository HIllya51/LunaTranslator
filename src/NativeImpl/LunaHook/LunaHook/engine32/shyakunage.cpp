#include "shyakunage.h"

bool shyakunage::attach_function()
{
	// しゃくなげ
	const BYTE bytes[] = {
		0x25, 0xff, 0xff, 0x00, 0x00, 0xc1, 0xe8, 0x04};
	auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
	if (!addr)
		return false;
	addr = MemDbg::findEnclosingAlignedFunction(addr);
	if (!addr)
		return false;
	HookParam hp;
	hp.address = addr;
	hp.offset = regoffset(edx);
	hp.type = USING_STRING;
	return NewHook(hp, "shyakunage");
}