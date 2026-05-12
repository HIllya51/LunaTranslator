#include "PiAS.h"

static bool h2()
{
  // 人形の匣 ～愛のディテール～
  // https://vndb.org/v10758

  BYTE bytes2[] = {
      0x8b, 0x44, 0x24, 0x0c,
      0x83, 0xec, XX,
      0x85, 0xc0,
      XX, XX, XX, XX,
      0x75, XX,
      0xb8, 0xff, 0x0f, 0x00, 0x00,
      XX, XX, XX, XX,
      0x83, 0xc4, XX,
      0xc3,
      0x8b, 0x7c, 0x24, XX,
      0x8b, 0x4c, 0x24, XX,
      0x8b, 0xc7,
      0x81, 0xe1, 0xff, 0xff, 0x00, 0x00,
      0x0f, 0xaf, 0xc7,
      0x0f, 0xaf, 0xc1,
      0x99,
      0x83, 0xe2, 0x07,
      0x03, 0xc2,
      0x8b, 0xe8,
      0xc1, 0xfd, 0x03,
      0x83, 0xff, 0x18,
      0x74, XX,
      0x83, 0xff, 0x08,
      0x75, XX};
  auto addr = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = CODEC_UTF16 | USING_CHAR;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    static auto charset = StringToWideString(LoadResData(L"PiAS", L"CHARSET"));
    buffer->from_t<WORD>(charset[(WORD)context->stack[1]]);
  };
  return NewHook(hp, "PiAS");
}
static bool h1()
{
  // https://vndb.org/v10757
  // 堕ちた天使が詩う歌

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

bool PiAS::attach_function()
{
  return h1() || h2();
}
