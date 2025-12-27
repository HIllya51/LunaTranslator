#include "AGES7.h"
namespace
{
  // Muv-Luv Alternative - Total Eclipse
  // https://vndb.org/v7052
  bool _1()
  {
    // HSN65001#-44@234699:te-win64vc14-release.exe
    BYTE b1[] = {
        0x48, XX2, 0xb0, 0xfe, 0xff, 0xff,
        0x4c, XX2, 0xb8, 0x01, 0x00, 0x00

    };
    auto addr = MemDbg::findBytes(b1, sizeof(b1), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | CODEC_UTF8 | NO_CONTEXT;
    hp.offset = regoffset(rdi);
    auto succ = NewHook(hp, "Ages7_1");
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (addr)
    {
      hp.address = addr;
      hp.type = USING_STRING | CODEC_UTF8 | NO_CONTEXT;
      hp.offset = regoffset(rbx);
      succ |= NewHook(hp, "Ages7_3");
    }
    return succ;
  }
  bool _2()
  {
    // HSN65001#-44@2346AC:te-win64vc14-release.exe
    BYTE b1[] = {
        0x48, XX2, 0x10,
        0x48, XX2, 0xb0, 0x01, 0x00, 0x00,
        XX2, 0xc0, 0x08, 0x00, 0x00};
    auto addr = MemDbg::findBytes(b1, sizeof(b1), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | CODEC_UTF8 | NO_CONTEXT;
    hp.offset = regoffset(rdi);
    auto suc = NewHook(hp, "Ages7_2");
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (addr)
    {
      hp.address = addr;
      hp.type = USING_STRING | CODEC_UTF8 | NO_CONTEXT;
      hp.offset = regoffset(rbx);
      suc |= NewHook(hp, "Ages7_3");
    }
    return suc;
  }
  bool _3()
  {
    // HSN65001#-14@3D9814:te-win64vc14-release.exe
    BYTE b1[] = {
        0x48, 0x8b, 0x1b,
        0x48, 0x8b, 0x01,
        0x48, 0x8b, 0xd3,
        0xff, 0x10,
        0x48, 0x8b, 0x45, 0xc8,
        0x48, 0x8b, 0x4d, 0xc0,
        0x48, 0x2b, 0xc1,
        0x48, 0xc1, 0xf8, 0x03,
        0x48, 0x85, 0xc0};
    auto addr = MemDbg::findBytes(b1, sizeof(b1), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr + 3;
    hp.type = USING_STRING | CODEC_UTF8 | NO_CONTEXT;
    hp.offset = regoffset(rbx);
    return NewHook(hp, "Ages7_4");
  }
  bool all()
  {
    auto _ = _1();
    _ = _2() || _;
    _ = _3() || _;
    return _;
  }
  bool h4()
  {
    // 君が望む永遠 ～Enhanced Edition R～ Ver 1.1.27
    BYTE b1[] = {
        0x49, 0x8b, 0x8d, XX4,
        0x4c, 0x8d, XX, XX,
        0x48, 0x83, XX, XX, 0x10,
        0x4c, 0x0f, XX, XX, XX,
        0x48, 0x81, 0xc1, XX4,
        0x48, 0x8d, 0x54, XX, XX,
        0xe8, XX4,
        0x0f, 0x10, 0x00,
        0x0f, 0x29, XX, XX,
        0x4c, 0x8d, XX, XX,
        0x48, 0x83, XX, XX, 0x10,
        0x4c, 0x0f, XX, XX, XX,
        0x49, 0x8b, 0x8d, XX4,
        0x48, 0x81, 0xc1, XX4,
        0x48, 0x8d, 0x55, XX,
        0xe8, XX4};
    auto addr = MemDbg::findBytes(b1, sizeof(b1), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr + 7 + 4 + 5 + 5 + 7 + 5;
    hp.type = USING_STRING | CODEC_UTF8 | FULL_STRING;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      std::string name = (char *)context->r8;
      std::string text = (char *)context->rdi;
      strReplace(text, "\\w");
      strReplace(text, "\\p");
      strReplace(text, "\\n", "\n");
      buffer->from(name + text);
    };
    return NewHook(hp, "Ages7_5");
  }
}
bool AGES7::attach_function()
{
  return all() || h4();
}