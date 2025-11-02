#include "Ohgetsu.h"

namespace
{
  bool hook1()
  {
    // Silvery White ～君と出逢った理由～
    const BYTE bytes[] = {
        0x8b, XX, 0x10,
        0x8b, XX, 0x0C,
        0x8b, XX, 0x08,
        0x8b, XX,
        0xc1, XX, 02,
        0xf3, 0xa5,
        0x8b, XX,
        0x83, XX, 0x03,
        0xf3, 0xa4,
        0x8b, XX, 0x08,
        0x03, XX, 0x10,
        0xC6, XX, 0x00};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);

    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(2);
    hp.type = USING_STRING;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      auto text = (LPCSTR)context->stack[2];
      auto size = context->stack[3];
      *split = context->stack[0];
      buffer->from(text, size);
    };
    return NewHook(hp, "Ohgetsu");
  }
  bool hook2()
  {
    // Palmyra ～熱砂の海と美なる戦姫～
    const BYTE bytes[] = {
        0x8b,
        XX,
        0x08,
        0x0f,
        XX,
        0x08,
        0xC1,
        XX,
        0x08,
        0x8b,
        XX,
        0x08,
        0x0f,
        0xb6,
        0x42,
        0x01,
        0x0b,
        XX,

    };
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);

    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      *split = context->stack[0];
      buffer->from(context->stack[1], context->stack[2]);
    };
    return NewHook(hp, "Ohgetsu");
  }
  bool _3()
  {
    // それは舞い散る桜のように FullEffect
    auto addr = MemDbg::findCallerAddress((DWORD)GetGlyphOutlineA, 0xec81, processStartAddress, processStopAddress);
    if (!addr)
    {
      return false;
    }

    // reladdr = 0x48ff0;
    // reladdr = 0x48ff3;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = CODEC_ANSI_BE;

    return NewHook(hp, "Basil");
  }
  bool _4()
  {
    // それは舞い散る桜のように FullEffect
    const BYTE bytes[] = {
        0x3D,
        0x00,
        0x02,
        0xFF,
        0xFF,
        XX2,
        0x3D,
        0x01,
        0x02,
        0xFF,
        0xFF,
        XX2,
        0x3D,
        0x02,
        0x02,
        0xFF,
        0xFF,
        XX2,

    };
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);

    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(2);
    hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
    hp.embed_hook_font = F_GetGlyphOutlineA;
    return NewHook(hp, "Basil2");
  }
}
namespace
{
  bool _5()
  {
    // 仰せのままに★ご主人様！
    const BYTE bytes[] = {
        // memset(&byte_562568, 0, 0x20u);
        // memset(byte_562588, 0, sizeof(byte_562588));  ->RS@562588
        0x6a, 0x20,
        0x6a, 0x00,
        0x68, XX4,
        0xe8, XX4,
        0x83, 0xc4, 0x0c,
        0x68, 0x40, 0x01, 0x00, 0x00,
        0x6a, 0x00,
        0x68, XX4,
        0xe8, XX4};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);

    if (!addr)
      return false;
    addr = *(DWORD *)(addr + 25);
    if (IsBadReadPtr((LPVOID)addr, 10) != 0)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = DIRECT_READ;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
      StringCharReplacer(buffer, TEXTANDLEN("||"), '\n');
    };
    return NewHook(hp, "Ohgetsu");
  }
  bool _6()
  {
    // 仰せのままに★ご主人様！
    // 这个有人名，上面那个只有文本
    const BYTE bytes[] = {
        0x6a, 0x46,
        0x8b, 0x4d, 0xf4,
        0x6b, 0xc9, 0x46,
        0x81, 0xc1, XX4,
        0x51,
        0x8b, 0x55, 0xf4,
        0x83, 0xea, 0x05,
        0x6b, 0xd2, 0x46,
        0x81, 0xc2, XX4,
        0x52,
        0xe8};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = findfuncstart(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING;
    hp.length_offset = 2;
    hp.offset = stackoffset(1);
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
      StringCharReplacer(buffer, TEXTANDLEN("||"), '\n');
    };
    return NewHook(hp, "Ohgetsu");
  }
  bool _7()
  {
    return _6() || _5();
  }
}
bool Ohgetsu::attach_function()
{
  bool ok = _4();
  return hook1() || hook2() || _7() || _3() || ok;
}