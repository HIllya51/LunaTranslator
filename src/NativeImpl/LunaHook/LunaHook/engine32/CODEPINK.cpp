#include "CODEPINK.h"

static bool SEXFRIEND()
{
  // strstr
  BYTE bytes[] = {
      0x8b, 0x4c, 0x24, 0x08,
      0x57, 0x53, 0x56,
      0x8a, 0x11,
      0x8b, 0x7c, 0x24, 0x10,
      0x84, 0xd2,
      0x74, XX,
      0x8a, 0x71, 0x01,
      0x84, 0xf6,
      0x74, XX,
      0x8b, 0xf7,
      0x8b, 0x4c, 0x24, 0x14,
      0x8a, 0x07,
      0x46,
      0x38, 0xd0,
      0x74, XX,
      0x84, 0xc0,
      0x74, 0x0b};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = FULL_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    static int i = 0;
    if (i++ % 2)
      return buffer->clear();
    auto s = buffer->strA();
    s = re::sub(s, "(.+)@n@L15", "\x81\x79$1\x81\x7a");
    s = re::sub(s, "@n@L15");
    strReplace(s, "@n");
    strReplace(s, "\x87\x44", "!!");
    buffer->from(s);
  };
  return NewHook(hp, "SEXFRIEND");
}

static bool JOROSIN()
{
  char log[] = "font_no = %d";
  auto a = MemDbg::findBytes(log, sizeof(log), processStartAddress, processStopAddress);
  if (!a)
    return false;
  a = MemDbg::find_leaorpush_addr(a, processStartAddress, processStopAddress);
  if (!a)
    return false;
  a = MemDbg::findEnclosingAlignedFunction(a);
  if (!a)
    return false;
  HookParam hp;
  hp.address = a;
  hp.type = FULL_STRING;
  hp.offset = stackoffset(3);
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    auto s = buffer->strA();
    s = re::sub(s, "@F4@B05.*?@F0");
    s = re::sub(s, "@[A-Z][0-9]+");
    s = re::sub(s, "@n");
    buffer->from(s);
  };
  return NewHook(hp, "JOROSIN");
}

bool CODEPINK::attach_function()
{
  return SEXFRIEND() | JOROSIN();
}