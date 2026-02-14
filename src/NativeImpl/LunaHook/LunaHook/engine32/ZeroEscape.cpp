#include "ZeroEscape.h"

static bool ze2()
{
  wchar_t aDS[] = L"[%d] %s";
  auto addr = MemDbg::findBytes(aDS, sizeof(aDS), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findPushAddress(addr, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0x80);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING | CODEC_UTF8 | FULL_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    static int i = 0;
    if (i++ % 2)
      return buffer->clear();
    auto s = buffer->strA();
    s = re::sub(s, R"(\[.*?\])");
    s = re::sub(s, R"(<\w>)");
    s = re::sub(s, R"(\n)");
    buffer->from(s);
  };
  return NewHook(hp, "ZeroEscape");
}

static bool ze1()
{
  // sprintf
  BYTE sig[] = {
      0x55, 0x8b, 0xec,
      0x83, 0xec, 0x20,
      0x53, 0x57,
      0x33, 0xdb,
      0x8d, 0x7d, 0xe4,
      0x6a, 0x07,
      0x33, 0xc0,
      0x89, 0x5d, 0xe0,
      0x59,
      0xf3, 0xab,
      0x39, 0x45, 0x0c,
      0x75, 0x15,
      0xe8, XX4,
      0xc7, 0x00, 0x16, 0x00, 0x00, 0x00,
      0xe8, XX4,
      0x83, 0xc8, 0xff,
      0xeb, XX};
  auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(3);
  hp.type = USING_STRING | FULL_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    auto s = buffer->strA();
    s = re::sub(s, R"(\x87\x53[a-z0-9]*)");
    s = re::sub(s, R"(\x81\xa5)");
    buffer->from(s);
  };
  return NewHook(hp, "ZeroEscape");
}

bool ZeroEscape::attach_function()
{
  // Zero Escape: The Nonary Games
  // https://store.steampowered.com/app/477740/Zero_Escape_The_Nonary_Games/

  return ze2() || ze1();
}