#include "Ages3ResT.h"

bool Ages3ResTHook()
{
  // 会直接提取多语言
  const BYTE bytes[] = {
      0x8d, 0x4f, XX,
      0xff, 0x15, XX4,
      XX,
      0x8d, 0x8f, XX4,
      0xff, 0x15, XX4,
      0x8d, XX, XX4,
      XX,
      0x8d, 0x8f, XX4,
      0xff, 0x15, XX4,
      0x8b, XX,
      0xff, 0x15, XX4};

  auto addrs = Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress);
  bool succ = false;
  for (auto addr : addrs)
  {
    ConsoleOutput("Ages3ResT %p", addr);
    addr = findfuncstart(addr);
    ConsoleOutput("Ages3ResT %p", addr);
    if (!addr)
      continue;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(3);
    hp.type = CODEC_UTF16 | USING_STRING | FULL_STRING;
    succ |= NewHook(hp, "Ages3ResT");
  }
  return succ;
}
bool Ages3ResTHook_1()
{
  /*
  if ( *(_BYTE *)(this + 1103) )
     {
       if ( a2 == 12305 )
         *(_BYTE *)(this + 1103) = 0;
     }
     else
     {
       v11 = a2;
       if ( a2 == 32 || a2 == 160 || a2 == 12288 )
       {
         if ( (*(_DWORD *)(this + 4 * *(_DWORD *)(this + 49744) + 8572) & 0x1000) != 0
           || *(_WORD *)(this + 8532) != *(_WORD *)(this + 12702) )
         {
           sub_448AF0(&a2);
           v22 = 0;
           v16 = *(__int16 *)(sub_5D5990(a2) + 308);
           v17 = sub_5D5990(a2);
           if ( v11 == 32 )
             *(_WORD *)(this + 8532) += *(_WORD *)(v17 + 310) + v16 / 2;
           else
             *(_WORD *)(this + 8532) += v16 + *(_WORD *)(v17 + 310);
           sub_406BF0(&a2);
         }
       }
  */
  BYTE sig1[] = {
      0x81, 0x7d, 0x08, 0x11, 0x30, 0x00, 0x00 // cmp [ebp+8],0x3011
  };
  BYTE sig2[] = {
      /*
      .text:005137F0                 mov     esi, [ebp+arg_0]
    .text:005137F3                 cmp     esi, 20h ; ' '
    .text:005137F6                 jz      loc_5138A9
    .text:005137FC                 cmp     esi, 0A0h
    .text:00513802                 jz      loc_5138A9
    .text:00513808                 cmp     esi, 3000h
    .text:0051380E                 jz      loc_5138A9
      */
      0x8b, 0x75, 0x08,
      0x83, 0xfe, 0x20,
      0x0f, 0x84, XX4,
      0x81, 0xfe, 0xa0, 0x00, 0x00, 0x00,
      0x0f, 0x84, XX4,
      0x81, 0xfe, 0x00, 0x30, 0x00, 0x00,
      0x0f, 0x84, XX4};
  auto addrs = Util::SearchMemory(sig2, sizeof(sig2), PAGE_EXECUTE, processStartAddress, processStopAddress);
  bool succ = false;
  for (auto addr2 : addrs)
  {
    ConsoleOutput("Ages3ResT2 %p", addr2);
    auto addr = findfuncstart(addr2);
    ConsoleOutput("Ages3ResT2 %p", addr);
    if (!addr)
      continue;
    if (!MemDbg::findBytes(sig1, sizeof(sig1), addr, addr2))
      continue;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = CODEC_UTF16 | USING_CHAR;
    succ |= NewHook(hp, "Ages3ResT2");
  }
  return succ;
}
bool Ages3ResT::attach_function()
{
  return Ages3ResTHook() | Ages3ResTHook_1();
}