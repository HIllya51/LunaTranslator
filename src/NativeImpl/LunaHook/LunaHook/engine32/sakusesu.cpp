#include "sakusesu.h"

bool sakusesu::attach_function()
{

  // if ((unsigned __int8)v1 >= 0x20u)
  //	{
  //	  if ((unsigned __int8)v1 >= 0x80u)
  //	  {
  //		if ((unsigned __int8)v1 >= 0xA0u)
  //		{
  //		  if ((unsigned __int8)v1 < 0xC0u)
  const BYTE bytesa0[] = {
      0x3C, 0xA0, 0x73};
  const BYTE bytesc0[] = {
      0x3C, 0xc0, 0x73};
  const BYTE bytes80[] = {
      0x3C, 0x80, 0x73};
  auto succ = false;
  for (auto bs : {bytesa0, bytes80, bytesc0})
  {
    auto addr = MemDbg::findBytes(bs, 3, processStartAddress, processStopAddress);
    if (!addr)
      continue;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      continue;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING;
    succ |= NewHook(hp, "sakusesu");
    for (auto xrefaddr : findxref_reverse(addr, addr - 0x10000, addr + 0x10000))
    {
      xrefaddr = MemDbg::findEnclosingAlignedFunction(xrefaddr);
      if (xrefaddr == 0)
        continue;
      HookParam hp;
      hp.address = xrefaddr;
      hp.offset = stackoffset(1);
      hp.type = USING_STRING;
      succ |= NewHook(hp, "sakusesu");
    }
  }
  return succ;
}