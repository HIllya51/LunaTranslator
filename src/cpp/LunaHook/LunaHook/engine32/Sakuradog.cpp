#include "Sakuradog.h"

bool Sakuradog::attach_function()
{
  // 綾瀬家のオンナ～淫華の血脈～

  auto entry = Util::FindImportEntry(processStartAddress, (DWORD)GetGlyphOutlineA);
  if (entry == 0)
    return false;
  BYTE bytes2[] = {
      0x57,
      0x50,
      0x6a, 0x06,
      0x56,
      0x53,
      0xff, 0x15, XX4};
  memcpy(bytes2 + sizeof(bytes2) - 4, &entry, 4);
  auto addr = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr + 6;
  hp.offset = regoffset(esi);
  hp.split = 0xe4;
  hp.type = CODEC_ANSI_BE | USING_SPLIT | NO_CONTEXT;
  return NewHook(hp, "Sakuradog");
}