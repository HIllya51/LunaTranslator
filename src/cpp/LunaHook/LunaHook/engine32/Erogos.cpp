#include "Erogos.h"
static bool h1()
{
  // らぶフェチ～手コキ編～
  const BYTE bytes[] = {
      /*
       v4 = v1;
          v5 = byte_451BE0[v1];
          for ( byte_461CE2 = 0; v5; ++dword_461D0C )
          {
            v1 += 2;
            word_461D10[12 * v3] = v5 + ((unsigned __int8)byte_451BE1[v4] << 8);
      */
      0x66, 0x0f, 0xb6, 0x80, XX4,
      0x66, 0x0f, 0xb6, 0xc9,
      0x8d, 0x14, 0x52,
      0x66, 0x83, 0xc6, 0x02,
      0xc1, 0xe0, 0x08,
      0x03, 0xc1,
      0x66, 0x89, 0x04, 0xd5, XX4};

  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr + sizeof(bytes) - 8;
  hp.offset = regoffset(eax);
  hp.type = USING_CHAR;
  return NewHook(hp, "Erogos2");
}
bool Erogos::attach_function()
{
  // らぶフェチ ～マゾ編～
  // らぶフェチ～千聡編～
  HookParam hp;
  hp.address = (DWORD)TextOutA;
  hp.type = USING_STRING | USING_SPLIT;
  hp.split = stackoffset(4);
  hp.offset = stackoffset(4);
  hp.length_offset = 5;
  return h1() || NewHook(hp, "Erogos");
}