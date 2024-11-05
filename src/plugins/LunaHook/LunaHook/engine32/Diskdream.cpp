#include"Diskdream.h"
 
bool Diskdream::attach_function() {
  //https://vndb.org/v3143
  //Endless Serenade
  char skip[]="FrameSkip = ";
  ULONG addr = MemDbg::findBytes(skip, sizeof(skip), processStartAddress, processStopAddress);
  if (!addr)  return false; 
  addr=MemDbg::findPushAddress(addr,processStartAddress, processStopAddress);
  if (!addr)  return false; 
  addr = findfuncstart(addr);
  if (!addr)  return false; 
  HookParam hp;
  hp.address = addr;
  hp.offset=get_reg(regs::edx);
  hp.type = USING_STRING; 
  hp.filter_fun = [](LPVOID data, size_t *size, HookParam *){
    if(*size==0)return false;
    return (bool)IsDBCSLeadByteEx(932,*(BYTE*)data);
  };
  return NewHook(hp, "Diskdream");
} 