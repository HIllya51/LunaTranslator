#include "ArcSystemWorks.h"

bool ArcSystemWorks::attach_function()
{
  // https://vndb.org/v18642
  // 月英学園 -kou-
  BYTE bytes2[] = {
      0x6a, 0x00,
      0x6a, 0x00,
      0x6a, 0x00,
      0x6a, 0x00,
      0x6a, 0x00,
      0x6a, 0x00,
      0x6a, 0x00,
      0x8d, XX, XX,
      0x51,
      0x6a, 0x01,
      0x6a, 0x00,
      0x6a, 0x00,
      0x6a, 0x00,
      0x6a, 0x00,
      0x6a, 0xff,
      0x8d, XX, XX,
      0x52,
      0x8d, XX, XX,
      0x50,
      0x8d, XX, XX,
      0x51,
      0xba, 0x1c, 0x00, 0x00, 0x00,
      0x6b, 0xd2, 0x00,
      0x8b, XX, XX,
      0x8d, XX, XX, XX,
      0x51,
      0x51,
      0xf3, XX4,
      0xf3, XX4,
      0x68, 0x00, 0x04, 0x00, 0x00,
      0x8d, XX, XX4,
      0x52,
      0x6a, 0x00,
      0x8b, XX, XX,
      0x50,
      0xb9, 0x1c, 0x00, 0x00, 0x00,
      0x6b, 0xc9, 0x00,
      0x8b, XX, XX,
      0x8d, XX2, XX4,
      0xe8, XX4,
      0x50,
      0xe8};
  auto addr = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr + sizeof(bytes2) - 1;
  hp.type = USING_STRING | CODEC_UTF16 | NO_CONTEXT | FULL_STRING;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto stack = (DWORD *)(context->esp);
    buffer->from((WCHAR *)stack[1]);
  };
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    std::wstring result = buffer->strW();
    result = re::sub(result, L"<ruby>(.*?)<.*?/ruby>", L"$1");
    buffer->from(result);
  };
  return NewHook(hp, "ArcSystemWorks");
}