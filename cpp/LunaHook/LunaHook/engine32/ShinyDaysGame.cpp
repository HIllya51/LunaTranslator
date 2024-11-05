#include"ShinyDaysGame.h"


/** Game-specific engines */

//static char* ShinyDaysQueueString[0x10];
//static int ShinyDaysQueueStringLen[0x10];
//static int ShinyDaysQueueIndex, ShinyDaysQueueNext;
static void SpecialGameHookShinyDays(hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  static int ShinyDaysQueueStringLen;
  LPWSTR fun_str,text_str;
  DWORD l = 0;
  auto esp_base=stack->base;
  fun_str=(LPWSTR)stack->stack[0x13];
  auto esi=stack->stack[0x1C]+0x3C;
  auto edi=stack->stack[0x1D];
  if(esi<=edi){
    auto tu=(TextUnionW*)esi;
    text_str=(LPWSTR)tu->getText();
    l=tu->size*2;
  }
  if (::memcmp(fun_str, L"[PlayVoice]",0x18) == 0) {
    buffer->from(text_buffer,ShinyDaysQueueStringLen);
  }
  else if (::memcmp(fun_str, L"[PrintText]",0x18) == 0) {
    memcpy(text_buffer, text_str, l);
    ShinyDaysQueueStringLen = l;
  }
}
bool InsertShinyDaysGameHook()
{
  const BYTE bytes[] = {
    0xff,0x83,0x70,0x03,0x00,0x00,0x33,0xf6,
    0xc6,0x84,0x24,0x90,0x02,0x00,0x00,0x02
  };
  auto addr=MemDbg::findBytes(bytes, sizeof(bytes),processStartAddress,processStopAddress);
  if(addr==0)return false;
   
    HookParam hp;
    hp.address = addr + 0x8;
    hp.text_fun = SpecialGameHookShinyDays;
    hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
    hp.filter_fun=[](LPVOID data, size_t *size, HookParam *){
      auto text = reinterpret_cast<LPWSTR>(data);
      auto len = reinterpret_cast<size_t *>(size);
      StringCharReplacer(text,len,L"\\n",2,L'\n');
      return true;
    };
    ConsoleOutput("INSERT ShinyDays");
    return NewHook(hp, "ShinyDays");
    
}
 
bool ShinyDaysGame::attach_function() {  
    
    return InsertShinyDaysGameHook();
} 