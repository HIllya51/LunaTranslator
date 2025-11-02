#include "Footy2.h"
bool insertstrcpyhook()
{
  const BYTE bytes[] = {
      0x3B, 0xD8, 0x72, 0x45, 0x83, 0xF9, 0x10, 0x72, 0x04, 0x8B, 0x16, 0xEB, 0x02};
  auto addrs = Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress);
  const BYTE funcstart[] = {
      0x55, 0x8b, 0xec, 0x53, 0x8b, 0x5d, 0x08};
  bool succ = false;
  for (auto addr : addrs)
  {
    addr = reverseFindBytes(funcstart, sizeof(funcstart), addr - 0x100, addr);
    if (!addr)
      continue;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING;
    ConsoleOutput("strcpy %p", addr);
    succ |= NewHook(hp, "strcpy");
  }
  return false;
}
bool Footy2::attach_function()
{
  // ガールズ・ブック・メイカー -幸せのリブレット-

  return insertstrcpyhook();
}