#include"Circus1.h"
 /********************************************************************************************
CIRCUS hook:
  Game folder contains advdata folder. Used by CIRCUS games.
  Usually has font caching issues. But trace back from GetGlyphOutline gives a hook
  which generate repetition.
  If we study circus engine follow Freaka's video, we can easily discover that
  in the game main module there is a static buffer, which is filled by new text before
  it's drawing to screen. By setting a hardware breakpoint there we can locate the
  function filling the buffer. But we don't have to set hardware breakpoint to search
  the hook address if we know some characteristic instruction(cmp al,0x24) around there.
********************************************************************************************/
bool InsertCircusHook1() // jichi 10/2/2013: Change return type to bool
{
  for (DWORD i = processStartAddress + 0x1000; i < processStopAddress - 4; i++)
    if (*(WORD *)i == 0xa3c)  //cmp al, 0xA; je
      for (DWORD j = i; j < i + 0x100; j++) {
        BYTE c = *(BYTE *)j;
        if (c == 0xc3)
          break;
        if (c == 0xe8) {
          DWORD k = *(DWORD *)(j+1)+j+5;
          if (k > processStartAddress && k < processStopAddress) {
            HookParam hp;
            hp.address = k;
            hp.offset=get_stack(3);
            hp.split =get_reg(regs::esp);
            hp.type = DATA_INDIRECT|USING_SPLIT;
            ConsoleOutput("INSERT CIRCUS#1");
            
            //RegisterEngineType(ENGINE_CIRCUS);
            return NewHook(hp, "Circus1");
          }
        }
      }
      //break;
  //ConsoleOutput("Unknown CIRCUS engine");
  ConsoleOutput("CIRCUS1: failed");
  return false;
}
namespace{
  //C.D.C.D.2～シーディーシーディー2～
  //https://vndb.org/v947
  bool circus12()
  {
    BYTE sig[]={
      0x3C,0x24,
      0x0F,0x85,XX4,
      0x8A,0x47,0x01,
      0x47,
      0x3C,0x6E,
      0x75,XX,
      0xA0,XX4,
      0xB9,XX4,
      0x84,0xC0,
      0x0F,0x84,XX4,
      0x88,0x06,
      0x8A,0x41,0x01,
      0x46,
      0x41,
      0x84,0xC0,
      0x75,XX,
      0xE9,XX4,
      0x3C,0x66,
      0x75,XX
    };
    auto addr=MemDbg::findBytes(sig,sizeof(sig),processStartAddress,processStopAddress);
    if(!addr)return false;
    addr=MemDbg::findEnclosingAlignedFunction(addr,0x40);
    if(!addr)return false;
    HookParam hp;
    hp.address =addr;
    hp.offset=get_stack(2);
    hp.type = USING_STRING|EMBED_ABLE|EMBED_AFTER_NEW|EMBED_DYNA_SJIS;
    hp.embed_hook_font=F_GetGlyphOutlineA;
    return NewHook(hp, "Circus1");
  }
}
bool Circus1::attach_function() {
    
    return InsertCircusHook1()|circus12();
} 