#include "EME.h"

/********************************************************************************************
EMEHook hook: (Contributed by Freaka)
  EmonEngine is used by LoveJuice company and TakeOut. Earlier builds were apparently
  called Runrun engine. String parsing varies a lot depending on the font settings and
  speed setting. E.g. without antialiasing (which very early versions did not have)
  uses TextOutA, fast speed triggers different functions then slow/normal. The user can
  set his own name and some odd control characters are used (0x09 for line break, 0x0D
  for paragraph end) which is parsed and put together on-the-fly while playing so script
  can't be read directly.
********************************************************************************************/
bool InsertEMEHook()
{
  ULONG addr = MemDbg::findCallAddress((ULONG)::IsDBCSLeadByte, processStartAddress, processStopAddress);
  // no needed as first call to IsDBCSLeadByte is correct, but sig could be used for further verification
  // WORD sig = 0x51C3;
  // while (c && (*(WORD*)(c-2)!=sig))
  //{
  //  //-0x1000 as FindCallOrJmpAbs always uses an offset of 0x1000
  //  c = Util::FindCallOrJmpAbs((DWORD)IsDBCSLeadByte,processStopAddress-c-0x1000+4,c-0x1000+4,false);
  //}
  if (!addr)
  {
    ConsoleOutput("EME: pattern does not exist");
    return false;
  }
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(eax);
  hp.type = NO_CONTEXT | DATA_INDIRECT | USING_CHAR;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *)
  {
    auto xx = buffer->strA();
    strReplace(xx, "	");
    buffer->from(xx);
  };
  return NewHook(hp, "EmonEngine");
}
namespace
{

  bool takeout()
  {
    // https://vndb.org/v6187
    // みちくさ～Loitering on the way～

    PcHooks::hookGDIFunctions();
    trigger_fun = [](LPVOID addr, hook_context *context)
    {
      if (addr != (LPVOID)GetGlyphOutlineA)
        return false;
      auto caller = context->retaddr;
      auto add = MemDbg::findEnclosingAlignedFunction(caller);
      if (!add)
        return true;
      HookParam hp;
      hp.address = add;

      hp.type = USING_STRING;
      hp.offset = stackoffset(4);
      hp.filter_fun = [](TextBuffer *buffer, HookParam *)
      {
        auto xx = buffer->strA();
        strReplace(xx, "	");
        static lru_cache<std::string> last(10);
        if (last.touch(xx))
          buffer->clear();
        else
          buffer->from(xx);
      };
      return NewHook(hp, "takeout");
    };
    return false;
  }
}
namespace
{
  /*
  v8 = (BYTE *)(*(_DWORD *)(this + 64) + v7);
  if ( *v8 == 9 )
  {
    *v8 = 0;
    v9 = *(_DWORD *)(this + 68);
    ++*(_WORD *)(this + 74);
    *(_WORD *)(this + 72) = 0;
    *(_DWORD *)(this + 68) = v9 + 1;
    sub_413920(String1, 1);
    return 1;
  }
  else
  {
    if ( IsDBCSLeadByte(*v8) )
  */
  bool emeengine()
  {
    BYTE sig[] = {
        /*
        .text:0042D05C                 mov     cl, [eax]
  .text:0042D05E                 cmp     cl, 9
  .text:0042D061                 jnz     short loc_42D08E
        */
        0x8A, 0x08,
        0x80, 0xF9, 0x09,
        0x75, XX};
    BYTE tgt[] = {
        /*
        .text:0042D08E                 push    ecx             ; TestChar
  .text:0042D08F                 call    ds:IsDBCSLeadByte
        */
        0x51,
        0xFF, 0x15, XX4};
    auto __IsDBCSLeadByte = Util::FindImportEntry(processStartAddress, (DWORD)IsDBCSLeadByte);
    if (!__IsDBCSLeadByte)
      return false;
    *(DWORD *)(tgt + 3) = __IsDBCSLeadByte;
    for (auto addr : Util::SearchMemory(sig, sizeof(sig), PAGE_EXECUTE_READWRITE, processStartAddress, processStopAddress))
    {
      auto off = *(BYTE *)(addr + sizeof(sig) - 1);
      auto target = addr + sizeof(sig) + off;
      if (memcmp((void *)target, tgt, sizeof(tgt)) != 0)
        continue;
      HookParam hp;
      hp.address = addr;
      hp.offset = regoffset(eax);
      hp.type = NO_CONTEXT | DATA_INDIRECT | USING_CHAR;
      hp.filter_fun = [](TextBuffer *buffer, HookParam *)
      {
        auto xx = buffer->strA();
        strReplace(xx, "	");
        buffer->from(xx);
      };
      return NewHook(hp, "EmonEngine2");
    }
    return InsertEMEHook();
  }
}
bool EME::attach_function()
{

  return emeengine() | takeout();
}