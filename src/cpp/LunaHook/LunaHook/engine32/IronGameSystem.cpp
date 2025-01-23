#include "IronGameSystem.h"

bool InsertIGSDynamicHook(LPVOID addr, hook_context *context)
{
  if (addr != GetGlyphOutlineW)
    return false;
  DWORD i;
  i = *(DWORD *)context->ebp;
  i = *(DWORD *)(i + 4);
  // if (SafeFillRange(L"mscorlib.ni.dll", &j, &k)) { // Artikash 6/30/2018: Dunno why addresses are needed
  while (*(BYTE *)i != 0xe8)
    i++;
  DWORD t = *(DWORD *)(i + 1) + i + 5;
  // if (t>j && t<k) {
  HookParam hp;
  hp.address = t;
  hp.offset = regoffset(edx);
  hp.split = regoffset(esp);
  hp.type = CODEC_UTF16 | USING_SPLIT;
  ConsoleOutput("INSERT IronGameSystem");

  // ConsoleOutput("IGS - Please set text(ヂ�ス� display speed(表示速度) to fastest(瞬�");
  // RegisterEngineType(ENGINE_IGS);
  return NewHook(hp, "IronGameSystem");
  //}
  //}
  ConsoleOutput("IGS: failed");
  return true; // jichi 12/25/2013: return true
}
void InsertIronGameSystemHook()
{
  PcHooks::hookGDIFunctions();
  // ConsoleOutput("Probably IronGameSystem. Wait for text.");
  trigger_fun = InsertIGSDynamicHook;
  ConsoleOutput("TRIGGER IronGameSystem");
}

bool IronGameSystem::attach_function()
{
  InsertIronGameSystemHook();
  return true;
}