#include "PiAS.h"

// https://vndb.org/v10757
// 堕ちた天使が詩う歌

bool PiAS::attach_function()
{
  BYTE bytes2[] = {
      0x8b, 0x45, XX,
      0xc1, 0xe0, 0x05,
      0x8b, 0x4d, XX,
      0x8d, 0x54, 0x01, 0x02,
      0x69, 0xd2, 0x80, 0x02, 0x00, 0x00,
      0x8b, 0x45, XX,
      0x03, 0xc2,
      0x8b, 0x4d, XX,
      0x8d, 0x14, 0xc8,
      0xa1, XX4,
      0xc6, 0x44, 0x10, 0x02, 0x01};
  auto addr = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = findfuncstart(addr, 0x400);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING | CODEC_UTF16 | FULL_STRING;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    static auto charset = StringToWideString(LoadResData(L"PiAS", L"CHARSET"));
    std::wstring wss;
    for (auto i = 0; i < context->stack[2]; i++)
    {
      wss += charset[*(WORD *)(context->stack[1] + 2 * i)];
    }
    buffer->from(wss);
  };
  return NewHook(hp, "PiAS");
}