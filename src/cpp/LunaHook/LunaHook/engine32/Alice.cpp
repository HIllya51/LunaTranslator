#include "Alice.h"

/********************************************************************************************
System40 hook:
  System40 is a game engine developed by Alicesoft.
  Afaik, there are 2 very different types of System40. Each requires a particular hook.

  Pattern 1: Either SACTDX.dll or SACT2.dll exports SP_TextDraw.
  The first relative call in this function draw text to some surface.
  Text pointer is return by last absolute indirect call before that.
  Split parameter is a little tricky. The first register pushed onto stack at the begining
  usually is used as font size later. According to instruction opcode map, push
  eax -- 50, ecx -- 51, edx -- 52, ebx --53, esp -- 54, ebp -- 55, esi -- 56, edi -- 57
  Split parameter value:
  eax - -8,   ecx - -C,  edx - -10, ebx - -14, esp - -18, ebp - -1C, esi - -20, edi - -24
  Just extract the low 4 bit and shift left 2 bit, then minus by -8,
  will give us the split parameter. e.g. push ebx 53->3 *4->C, -8-C=-14.
  Sometimes if split function is enabled, ITH will split text spoke by different
  character into different thread. Just open hook dialog and uncheck split parameter.
  Then click modify hook.

  Pattern 2: *engine.dll exports SP_SetTextSprite.
  At the entry point, EAX should be a pointer to some structure, character at +0x8.
  Before calling this function, the caller put EAX onto stack, we can also find this
  value on stack. But seems parameter order varies from game release. If a future
  game breaks the EAX rule then we need to disassemble the caller code to determine
  data offset dynamically.
********************************************************************************************/

static bool InsertAliceHook1(DWORD addr)
{
  if (!addr)
  {
    ConsoleOutput("AliceHook1: failed");
    return false;
  }
  for (DWORD i = addr, s = addr; i < s + 0x100; i++)
    if (*(BYTE *)i == 0xe8)
    { // Find the first relative call.
      DWORD j = i + 5 + *(DWORD *)(i + 1);
      while (true)
      { // Find the first register push onto stack.
        DWORD c = ::disasm((BYTE *)s);
        if (c == 1)
          break;
        s += c;
      }
      DWORD c = *(BYTE *)s;
      HookParam hp;
      hp.address = j;
      hp.offset = regoffset(eax);
      hp.split = -8 - ((c & 0xf) << 2);
      hp.type = USING_STRING | USING_SPLIT;
      // if (s>j) hp.type^=USING_SPLIT;
      ConsoleOutput("INSERT AliceHook1");

      // RegisterEngineType(ENGINE_SYS40);
      return NewHook(hp, "System40");
    }
  ConsoleOutput("AliceHook1: failed");
  return false;
}
static bool InsertAliceHook2(DWORD addr)
{
  if (!addr)
  {
    ConsoleOutput("AliceHook2: failed");
    return false;
  }
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(eax);
  hp.index = 0x8;
  hp.type = DATA_INDIRECT;
  ConsoleOutput("INSERT AliceHook2");
  return NewHook(hp, "System40");
  // RegisterEngineType(ENGINE_SYS40);
}

// jichi 8/23/2013 Move here from engine.cc
// Do not work for the latest Alice games
// jichi 5/13/2015: Looking for function entries in StoatSpriteEngine.dll
bool InsertAliceHook()
{
  bool ok = false;
  if (auto addr = Util::FindFunction("SP_TextDraw"))
  {

    ok |= InsertAliceHook1(addr);
  }
  // if (GetFunctionAddr("SP_SetTextSprite", &addr, &low, &high, 0) && addr) {
  //  InsertAliceHook2(addr);
  //  return true;
  //}
  if (auto addr = Util::FindFunction("SP_SetTextSprite"))
  { // Artikash 6/27/2018 not sure if this works

    ok |= InsertAliceHook2(addr);
  }
  // ConsoleOutput("AliceHook: failed");
  return ok;
}
namespace
{
  bool Sys42VM()
  {
    // https://vndb.org/r41279
    // Beat Blades Haruka
    auto vm = GetModuleHandle(L"Sys42VM.dll");
    if (!vm)
      return false;
    auto [s, e] = Util::QueryModuleLimits(vm);
    BYTE sig[] = {
        0x51, 0x56,
        0x8b, 0xf0,
        0x8b, 0x46, 0x04,
        0x85, 0xc0,
        0x74, 0x07,
        0x8b, 0x4e, 0x08,
        0x2b, 0xc8,
        0x75, 0x05,
        0xe8, XX4,
        0x8b, 0x76, 0x04,
        0x56,
        0x8b, 0x74, 0x24, 0x10,
        0xe8, XX4,
        0x5e, 0x59,
        0xc2, 0x04, 0x00};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), s, e);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = FULL_STRING | USING_STRING;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      auto a1 = context->eax;
      auto v3 = *(DWORD *)(a1 + 4);
      if (!v3 || *(DWORD *)(a1 + 8) == v3)
        return;
      buffer->from(*(const char **)(a1 + 4));
    };
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      if (endWith(buffer->viewA(), ".asd"))
        buffer->clear();
    };
    return NewHook(hp, "System42");
  }
}
bool Alice::attach_function_()
{

  return InsertAliceHook() | Sys42VM();
}