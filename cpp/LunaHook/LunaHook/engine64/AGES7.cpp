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
    if (addr = MemDbg::findEnclosingAlignedFunction(addr))
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
    if (addr = MemDbg::findEnclosingAlignedFunction(addr))
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
}
bool AGES7::attach_function()
{
  return all();
}