#include "AB2Try.h"

/********************************************************************************************
AkabeiSoft2Try hook:
  Game folder contains YaneSDK.dll. Maybe we should call the engine Yane(屋� = roof)?
  This engine is based on .NET framework. This really makes it troublesome to locate a
  valid hook address. The problem is that the engine file merely contains bytecode for
  the CLR. Real meaningful object code is generated dynamically and the address is randomized.
  Therefore the easiest method is to brute force search whole address space. While it's not necessary
  to completely search the whole address space, since non-executable pages can be excluded first.
  The generated code sections do not belong to any module(exe/dll), hence they do not have
  a section name. So we can also exclude executable pages from all modules. At last, the code
  section should be long(>0x2000). The remain address space should be several MBs in size and
  can be examined in reasonable time(less than 0.1s for P8400 Win7x64).
  Characteristic sequence is 0F B7 44 50 0C, stands for movzx eax, word ptr [edx*2 + eax + C].
  Obviously this instruction extracts one unicode character from a string.
  A main shortcoming is that the code is not generated if it hasn't been used yet.
  So if you are in title screen this approach will fail.

********************************************************************************************/
namespace
{ // unnamed

  typedef struct _NSTRING
  {
    PVOID vfTable;
    DWORD lenWithNull;
    DWORD lenWithoutNull;
    WCHAR str[1];
  } NSTRING;

  // qsort correctly identifies overflow.
  int cmp(const void *a, const void *b)
  {
    return *(int *)a - *(int *)b;
  }

  void SpecialHookAB2Try(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    // DWORD test = *(DWORD*)(esp_base - 0x10);
    DWORD edx = context->edx;
    if (edx != 0)
      return;

    // NSTRING *s = *(NSTRING **)(esp_base - 8);
    if (const NSTRING *s = (NSTRING *)context->eax)
    {
      buffer->from(s->str, s->lenWithoutNull << 1);
      //*split = 0;
      *split = FIXED_SPLIT_VALUE; // 8/3/2014 jichi: change to single threads
    }
  }

  bool FindCharacteristInstruction()
  {
    const BYTE bytes[] = {0x0F, 0xB7, 0x44, 0x50, 0x0C, 0x89};
    for (auto addr : Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE_READWRITE))
    {
      // GROWL_DWORD(addr);
      HookParam hp;
      hp.address = addr;
      hp.text_fun = SpecialHookAB2Try;
      hp.type = USING_STRING | NO_CONTEXT | CODEC_UTF16;
      // ConsoleOutput("Please adjust text speed to fastest/immediate.");
      // RegisterEngineType(ENGINE_AB2T);
      return NewHook(hp, "AB2Try");
    }
    return false;
  }
} // unnamed namespace
bool AB2Try::attach_function()
{
  return FindCharacteristInstruction();
}