#include "Winters.h"

bool Winters::attach_function()
{
  // こんな魔法少女…アタシはレミィ
  // https://vndb.org/v11018
  const BYTE bytes[] = {
      0x4a,
      0x8b, 0xda,
      0xc1, 0xe3, 0x02,
      0x8d, 0x1c, 0x9b,
      0x8b, 0xcb,
      0x83, 0xc1, 0x11,
      0xba, 0x19, 0x00, 0x00, 0x00,
      0xe8, XX4};
  // ゴメンなさい・・・アタシのせいで
  // https://vndb.org/v4267
  const BYTE bytes2[] = {
      0x4a,
      0x8b, 0xda,
      0xc1, 0xe3, 0x03,
      0x8d, 0x1c, 0x5b,
      0x8b, 0xcb,
      0X41,
      0X81, 0XC1, 0X70, 0X01, 0X00, 0X00,
      0XBA, 0X27, 0X00, 0X00, 0X00,
      0xe8, XX4};
  auto off1 = sizeof(bytes);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
  {
    off1 = sizeof(bytes2);
    addr = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
  }
  if (!addr)
    return false;
  auto off = *(DWORD *)(addr + off1 - 4);
  auto target = off + addr + off1;
  HookParam hp;
  hp.address = target;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *)
  {
    static int idx = 0;
    if ((idx++) % 2)
      buffer->clear();
  };

  return NewHook(hp, "Winters");
}