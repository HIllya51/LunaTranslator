#include"FrontWing.h"


bool FrontWing::attach_function() { 
  const BYTE bytes[] = {
    //v55 = (int)(__CFADD__(v54 * v13, 0x80000000) + v54 * v13 + 0x80000000 + 0x80000000) >> 1;
   0x05,0x00,0x00,0x00,0x80,0x15,0x00,0x00,0x00,0x80,0xD1,0xF8,0x85,0xC0
  };
    
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (addr == 0)return false;
  addr=MemDbg::findEnclosingAlignedFunction(addr);
  if(addr==0)return false;
  HookParam hp;
  hp.address = addr;
  hp.offset=stackoffset(1);
  hp.type = USING_STRING;
  return NewHook(hp, "FrontWing");
} 