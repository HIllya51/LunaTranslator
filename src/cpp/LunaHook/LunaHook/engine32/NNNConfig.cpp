#include "NNNConfig.h"
bool NNNConfig::attach_function()
{
	// blackcyc
	// 夢幻廻廊
	// 復讐の女仕官ハイネ ～肢体に刻まれる淫欲のプログラム～
	// https://vndb.org/v24955
	const BYTE bytes[] = {
		0x68, 0xE8, 0x03, 0x00, 0x00, 0x6a, 0x00};
	auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
	if (!addr)
		return false;

	addr = addr + sizeof(bytes);
	for (int i = 0; i < 5; i++)
	{
		if (*(BYTE *)addr == 0xe8)
		{
			addr += 1;
			break;
		}
		addr += 1;
	}
	uintptr_t offset = *(uintptr_t *)(addr);
	uintptr_t funcaddr = offset + addr + 4;
	const BYTE check[] = {0x83, 0xEC, 0x1C};
	auto checkoffset = MemDbg::findBytes(check, sizeof(check), funcaddr, funcaddr + 0x20);

	if (checkoffset == 0)
		offset = stackoffset(5);
	else
		offset = stackoffset(6);
	HookParam hp;
	hp.address = funcaddr;
	hp.offset = offset;
	hp.type = USING_STRING;
	hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
	{
		// 当前文本可以过滤重复，上一条文本会按照换行符切分不停刷新。
		auto data = context->stack[hp->offset / 4];
		static std::unordered_map<uintptr_t, std::string> everythreadlast;
		if (everythreadlast.find(context->retaddr) == everythreadlast.end())
			everythreadlast[context->retaddr] = "";
		auto thisstr = std::string((char *)data);
		if (everythreadlast[context->retaddr] == thisstr)
			return;
		everythreadlast[context->retaddr] = thisstr;
		auto len = everythreadlast[context->retaddr].size();
		buffer->from(data, len);
	};
	return NewHook(hp, "NNNhook");
}