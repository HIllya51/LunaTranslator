#include "Majiro.h"

/** jichi 12/28/2014: new Majiro hook pattern
 *
 *  Different function starts:
 *
 *  Old Majiro:
 *  enum { sub_esp = 0xec81 }; // caller pattern: sub esp = 0x81,0xec byte
 *
 *  New Majiro since [141128] [アトリエさくら] 流され妻、綾�“ネトラレ”��体験版
 *  003e9230   55               push ebp
 *  003e9231   8bec             mov ebp,esp
 *  003e9233   83ec 64          sub esp,0x64
 *
 *  Also, function addresses are fixed in old majiro, but floating in new majiro.
 *  In the old Majiro game, caller's address could be used as split.
 *  In the new Majiro game, the hooked function is invoked by the same caller.
 *
 *  Use a split instead.
 *  Sample stack values are as follows.
 *  - Old majiro: arg3 is text, arg1 is font name
 *  - New majiro: arg3 is text, arg4 is font name
 *
 *  Name:
 *  0038f164   003e8163  return to .003e8163 from .003e9230
 *  0038f168   00000000
 *  0038f16c   00000000
 *  0038f170   08b04dbc ; jichi: arg3, text
 *  0038f174   006709f0 ; jichi: arg4, font name
 *  0038f178   006dace8
 *  0038f17c   00000000
 *  0038f180   00000013
 *  0038f184   006fcba8
 *  0038f188   00000078 ; jichi: 0x24, alternative split
 *  0038f18c   00000078
 *  0038f190   00000018
 *  0038f194   00000002
 *  0038f198   08b04dbc
 *  0038f19c   006709f0
 *  0038f1a0   00000000
 *  0038f1a4   00000000
 *  0038f1a8   00000078
 *  0038f1ac   00000018
 *  0038f1b0   08aa0130
 *  0038f1b4   01b6b6c0
 *  0038f1b8   beff26e4
 *  0038f1bc   0038f1fc
 *  0038f1c0   004154af  return to .004154af from .00415400 ; jichi: 0x52, could be used as split
 *  0038f1c4   0000000e
 *  0038f1c8   000001ae
 *  0038f1cc   00000158
 *  0038f1d0   00000023
 *  0038f1d4   beff2680
 *  0038f1d8   0038f208
 *  0038f1dc   003ecfda  return to .003ecfda from .00415400
 *
 *  Scenario:
 *  0038e57c   003e8163  return to .003e8163 from .003e9230
 *  0038e580   00000000
 *  0038e584   00000000
 *  0038e588   0038ee4c  ; jichi: arg3, text
 *  0038e58c   004d5400  .004d5400 ; jichi: arg4, font name
 *  0038e590   006dace8
 *  0038e594   0038ee6d
 *  0038e598   004d7549  .004d7549
 *  0038e59c   00000000
 *  0038e5a0   00000180 ; jichi: 0x24, alternative hook
 *  0038e5a4   00000180
 *  0038e5a8   00000018
 *  0038e5ac   00000002
 *  0038e5b0   0038ee4c
 *  0038e5b4   004d5400  .004d5400
 *  0038e5b8   00000000
 *  0038e5bc   00000000
 *  0038e5c0   00000180
 *  0038e5c4   00000018
 *  0038e5c8   006a0180
 *  0038e5cc   0038e5f8
 *  0038e5d0   0041fc87  return to .0041fc87 from .0041fc99
 *  0038e5d4   0038e5f8
 *  0038e5d8   00418165  return to .00418165 from .0041fc81 ; jichi: used as split
 *  0038e5dc   004d7549  .004d7549
 *  0038e5e0   0038ee6d
 *  0038e5e4   0038e608
 *  0038e5e8   00419555  return to .00419555 from .0041814e
 *  0038e5ec   00000000
 *  0038e5f0   004d7549  .004d7549
 *  0038e5f4   0038ee6d
 *
 *  12/4/2014: Add split for furigana.
 *  Sample game: [141128] [チュアブルソフト] 残念な俺達�青春事情
 *  Following are memory values after arg4 (font name)
 *
 *  Surface: � *  00EC5400  82 6C 82 72 20 82 6F 83 53 83 56 83 62 83 4E 00  �� �ゴシヂ�.
 *  00EC5410  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
 *  00EC5420  01 00 00 00 00 00 00 00 1C 00 00 00 0D 00 00 00   ....... .......
 *  00EC5430 (2D)00 00 00 FF FF FF 00 00 00 00 02 00 00 00 00  -...���.... .... ; jichi: first byte as split in parenthesis
 *  00EC5440  00(00 00 00)60 F7 3F 00 F0 D8 FF FF 00 00 00 00  ....`・.   ....  ; jichi: first word without first byte as split
 *
 *  00EC5450  32 01 00 00 0C 00 00 00 A0 02 00 00 88 00 00 00  2 ......� ..・..
 *  00EC5460  00 00 00 00 01 00 00 00 00 00 00 00 32 01 00 00  .... .......2 ..
 *  00EC5470  14 00 00 00 01 00 00 00 82 6C 82 72 20 82 6F 83   ... ...�� �・ ; MS P Gothic
 *  00EC5480  53                                               S
 *
 *  Furigana: そ�
 *  00EC5400  82 6C 82 72 20 83 53 83 56 83 62 83 4E 00 4E 00  �� ゴシヂ�.N.
 *  00EC5410  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
 *  00EC5420  01 00 00 00 00 00 00 00 0E 00 00 00 06 00 00 00   ....... ... ...
 *  00EC5430 (16)00 00 00 FF FF FF 00 00 00 00 02 00 00 00 00   ...���.... ....
 *  00EC5440  00(00 00 00)60 F7 3F 00 F0 D8 FF FF 00 00 00 00  ....`・.   ....
 *
 *  00EC5450  32 01 00 00 0C 00 00 00 A0 02 00 00 88 00 00 00  2 ......� ..・..
 *  00EC5460  00 00 00 00 00 00 00 00 00 00 00 00 32 01 00 00  ............2 ..
 *  00EC5470  14 00 00 00 01 00 00 00 82 6C 82 72 20 82 6F 83   ... ...�� �・ ; MS P Gothic
 *  00EC5480  53                                               S
 *
 *  Furigana: そ�
 *  00EC5400  82 6C 82 72 20 82 6F 83 53 83 56 83 62 83 4E 00  �� �ゴシヂ�.
 *  00EC5410  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
 *  00EC5420  01 00 00 00 00 00 00 00 0E 00 00 00 06 00 00 00   ....... ... ...
 *  00EC5430 (2D)00 00 00 FF FF FF 00 00 00 00 02 00 00 00 00  -...���.... ....
 *  00EC5440  00(00 00 00)60 F7 3F 00 2B 01 00 00 06 00 00 00  ....`・.+ .. ...
 *
 *  00EC5450  32 01 00 00 0C 00 00 00 A0 02 00 00 88 00 00 00  2 ......� ..・..
 *  00EC5460  00 00 00 00 00 00 00 00 00 00 00 00 32 01 00 00  ............2 ..
 *  00EC5470  14 00 00 00 01 00 00 00 82 6C 82 72 20 82 6F 83   ... ...�� �・ ; MS P Gothic
 *  00EC5480  53                                               S
 *
 *  ---- need to split the above and below case
 *
 *  Text: � *  00EC5400  82 6C 82 72 20 82 6F 83 53 83 56 83 62 83 4E 00  �� �ゴシヂ�.
 *  00EC5410  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
 *  00EC5420  01 00 00 00 00 00 00 00 1C 00 00 00 0D 00 00 00   ....... .......
 *  00EC5430 (2D)00 00 00 FF FF FF 00 00 00 00 02 00 00 00 00  -...���.... .... ; jichi: first byte as split in parenthesis
 *  00EC5440  FF(FF FF FF)60 F7 3F 00 32 01 00 00 14 00 00 00  ����`・.2 .. ... ; jichi: first word without first byte as split
 *
 *  00EC5450  32 01 00 00 0C 00 00 00 A0 02 00 00 88 00 00 00  2 ......� ..・..
 *  00EC5460  00 00 00 00 01 00 00 00 00 00 00 00 32 01 00 00  .... .......2 ..
 *  00EC5470  14 00 00 00 00 00 00 00 82 6C 82 72 20 82 6F 83   .......�� �・ ; MS P Gothic
 *  00EC5480  53                                               S
 *
 *  Text: らには、一人の少女� *  00EC5400  82 6C 82 72 20 82 6F 83 53 83 56 83 62 83 4E 00  �� �ゴシヂ�.
 *  00EC5410  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
 *  00EC5420  01 00 00 00 00 00 00 00 1C 00 00 00 0D 00 00 00   ....... .......
 *  00EC5430 (2D)00 00 00 FF FF FF 00 00 00 00 02 00 00 00 00  -...���.... ....
 *  00EC5440  FF(FF FF FF)60 F7 3F 00 4D 01 00 00 14 00 00 00  ����`・.M .. ...
 *
 *  00EC5450  32 01 00 00 0C 00 00 00 A0 02 00 00 88 00 00 00  2 ......� ..・..
 *  00EC5460  00 00 00 00 01 00 00 00 00 00 00 00 32 01 00 00  .... .......2 ..
 *  00EC5470  14 00 00 00 00 00 00 00 82 6C 82 72 20 82 6F 83   .......�� �・ ; MS P Gothic
 *  00EC5480  53                                               S
 */

namespace
{ // unnamed

  // These values are the same as the assembly logic of ITH:
  //     ([eax+0x28] & 0xff) | (([eax+0x48] >> 1) & 0xffffff00)
  // 0x28 = 10 * 4, 0x48 = 18 / 4
  inline DWORD MajiroOldFontSplit(const DWORD *arg) // arg is supposed to be a string, though
  {
    return (arg[10] & 0xff) | ((arg[18] >> 1) & 0xffffff00);
  }

  // Remove lower bytes use 0xffffff00, which are different for furigana
  inline DWORD MajiroNewFontSplit(const DWORD *arg) // arg is supposed to be a string, though
  {
    return (arg[12] & 0xff) | (arg[16] & 0xffffff00);
  }

  void SpecialHookMajiro(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    DWORD arg3 = context->stack[3]; // text
    buffer->from((LPCSTR)arg3);
    // IsBadReadPtr is not needed for old Majiro game.
    // I am not sure if it is needed by new Majiro game.
    if (hp->user_value)
    {                                     // new majiro
      if (DWORD arg4 = context->stack[4]) // old majiro
        *split = MajiroNewFontSplit((LPDWORD)arg4);
      else
        *split = *(DWORD *)(context->base + 0x5c); // = 4 * 23, caller's caller
    }
    else if (DWORD arg1 = context->stack[1]) // old majiro
      *split = MajiroOldFontSplit((LPDWORD)arg1);
  }
} // unnamed namespace
bool InsertMajiroHook()
{
  // jichi 4/19/2014: There must be a function in Majiro game which contains 6 TextOutA.
  // That function draws all texts.
  //
  // jichi 11/28/2014: Add new function signature
  const DWORD funcs[] = {
      // caller patterns
      0xec81,     // sub esp = 0x81,0xec byte old majiro
      0x83ec8b55, // mov ebp,esp, sub esp,*  new majiro

      0x5348ec83
      // sub     esp, 48h, push    ebx
      // MOON CHILDe
      // https://vndb.org/v1568

  };
  enum
  {
    FunctionCount = sizeof(funcs) / sizeof(*funcs)
  };
  ULONG addr = MemDbg::findMultiCallerAddress((ULONG)::TextOutA, funcs, FunctionCount, processStartAddress, processStopAddress);
  // ULONG addr = MemDbg::findCallerAddress((ULONG)::TextOutA, 0x83ec8b55, processStartAddress, processStopAddress);
  if (!addr)
    return false;

  bool newMajiro = 0x55 == *(BYTE *)addr;
  BYTE checknew[] = {
      0x8D, 0x04, 0x8D, 0x00, 0x00, 0x00, 0x00,
      0x8B, 0x4D, 0x08,
      0x89, 0x45, XX,
      0x89, 0x4d, XX,
      0x38, 0x19,
      0x0f, 0x84, XX4};
  auto isverynew = newMajiro && MemDbg::findBytes(checknew, sizeof(checknew), addr, addr + 0x300);
  HookParam hp;
  hp.address = addr;
  if (isverynew)
  {
    // https://vndb.org/r128573
    // みずいろリメイク
    hp.offset = stackoffset(1);
    hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
    hp.embed_hook_font = F_TextOutA;
    return NewHook(hp, "Majiro2Ex");
  }
  hp.text_fun = SpecialHookMajiro;
  hp.user_value = newMajiro;
  if (newMajiro)
  {
    hp.type = NO_CONTEXT; // do not use return address for new majiro
    return NewHook(hp, "Majiro2");
  }
  else
  {
    return NewHook(hp, "Majiro");
  }
  // RegisterEngineType(ENGINE_MAJIRO);
}
bool InsertMajiroHook3x()
{
  const BYTE bytes[] = {
      0x8b,
      0x08,
      0x0f,
      0xbf,
      0x19,
      0x83,
      0xc1,
      0x02,
  };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);

  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr + 8;
  hp.offset = regoffset(ecx);
  hp.type = USING_STRING | NO_CONTEXT; //|EMBED_ABLE|EMBED_AFTER_OVERWRITE|EMBED_DYNA_SJIS;
  // 可以内嵌，但是必须保持「」，且DynamicEncoding编码的文字会被自动替换成引擎内的某的字符，导致可读性低。
  // hp.embed_hook_font=F_TextOutA|F_GetTextExtentPoint32A;
  // https://vndb.org/v17376
  // 私が好きなら「好き」って言って！
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto str = (char *)context->ecx;
    buffer->from(str);
    if ((str[0] == 0x81) && (str[1] == 0x79))
      *split = 0;
    else
      *split = 1;
  };
  return NewHook(hp, "majiro3");
}
bool InsertMajiro2Hookx()
{
  // Scarlett～スカーレット～
  const BYTE bytes[] = {
      0x83, 0xE2, 0x03, 0x03, 0xC2, 0xC1, 0xF8, 0x02, 0x81, 0xF9, 0x00, 0x01, 0x00, 0x00};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);

  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(2);
  hp.type = USING_STRING;
  return NewHook(hp, "majiro4");
}
bool InsertMajiro3Hook()
{

  /*
   * Sample games:
   * Narcissu 10th Anniversary Anthology Project
   * https://vndb.org/v10
   * https://vndb.org/v70
   * https://vndb.org/v18738
   * https://vndb.org/v18739
   * https://vndb.org/v18736
   */
  const BYTE bytes[] = {
      0xC1, 0xE9, 0x02, // shr ecx,02     << hook here
      0xF3, 0xA5,       // repe movsd
      0x8B, 0xCA,       // mov ecx,edx
      0x8D, 0x95, XX4   // lea edx,[ebp-00000404]
  };

  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(esi);
  hp.type = USING_STRING;
  return NewHook(hp, "Majiro3");
}
bool Majiro::attach_function()
{

  bool b1 = InsertMajiroHook();
  bool b2 = InsertMajiroHook3x();
  bool b3 = InsertMajiro2Hookx();
  bool b4 = InsertMajiro3Hook();
  return b1 || b2 || b3 || b4;
}