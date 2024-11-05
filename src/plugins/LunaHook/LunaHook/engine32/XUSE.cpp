#include"XUSE.h"

bool InsertXUSEHook2() { 
  //最果てのイマ -COMPLETE-
  ConsoleOutput("maybe XUSE2");
    
  BYTE bytes[] = {
    0x68,0x34,0x01,0x00,0x00
    //v39 = v16;
    //v40 = v15;  <-----  v15 ,eax
    //v41 = (const char*)operator new(0x134u);
  };
  auto succ=false;
  auto addrs = Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress);
  for (auto addr : addrs) {

    HookParam hp;
    hp.address = addr  ;
    hp.offset=get_reg(regs::eax);
    hp.type = CODEC_ANSI_BE|NO_CONTEXT | USING_SPLIT;
    hp.split = 0;
    ConsoleOutput("XUSE2 %p", addr);

    succ|=NewHook(hp, "XUSE2");
  }
  return succ;

}
bool InsertXUSEHook() {
  //詩乃先生の誘惑授業
  //憂ちゃんの新妻だいあり～
  ConsoleOutput("maybe XUSE");
  BYTE bytes[] = {
    0x6a,0x00,
    XX,
    0x6a,0x05,
    XX,
    XX,
    0xff,0x15,XX4,
    0x8b,0xf0,
    0x83,0xfe,0xff

  };
  auto succ=false;
  auto addrs = Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress);
  for(auto addr : addrs){ 

    HookParam hp;
    hp.address = addr + 7;
    hp.offset=get_reg(regs::edi);
    hp.type = CODEC_ANSI_BE | NO_CONTEXT | USING_SPLIT;
    hp.split = get_stack(3);

    ConsoleOutput("XUSE %p", addr);

    succ|=NewHook(hp, "XUSE");
  }
  return succ;

}

bool XUSE::attach_function() {  
     
    return  InsertXUSEHook() || InsertXUSEHook2();
} 