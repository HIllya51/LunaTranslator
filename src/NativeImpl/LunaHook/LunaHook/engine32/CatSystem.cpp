#include "CatSystem.h"
// jichi 5/10/2014
// See also: http://bbs.sumisora.org/read.php?tid=11044704&fpage=2
//
// Old engine:  グリザイアの迷宮
// 0053cc4e   cc               int3
// 0053cc4f   cc               int3
// 0053cc50   6a ff            push -0x1    ; jichi: hook here
// 0053cc52   68 6b486000      push .0060486b
// 0053cc57   64:a1 00000000   mov eax,dword ptr fs:[0]
// 0053cc5d   50               push eax
// 0053cc5e   81ec 24020000    sub esp,0x224
// 0053cc64   a1 f8647600      mov eax,dword ptr ds:[0x7664f8]
// 0053cc69   33c4             xor eax,esp
// 0053cc6b   898424 20020000  mov dword ptr ss:[esp+0x220],eax
// 0053cc72   53               push ebx
// 0053cc73   55               push ebp
// 0053cc74   56               push esi
// 0053cc75   57               push edi
//
// Stack:
// 0544e974   0053d593  return to .0053d593 from .0053cc50
// 0544e978   045cc820
// 0544e97c   00008dc5  : jichi: text
// 0544e980   00000016
// 0544e984   0452f2e4
// 0544e988   00000000
// 0544e98c   00000001
// 0544e990   0544ea94
// 0544e994   04513840
// 0544e998   0452f2b8
// 0544e99c   04577638
// 0544e9a0   04620450
// 0544e9a4   00000080
// 0544e9a8   00000080
// 0544e9ac   004914f3  return to .004914f3 from .0055c692
//
// Registers:
// edx 0
// ebx 00000016
//
//
// New engine: イノセントガール
// Stack:
// 051ae508   0054e9d1  return to .0054e9d1 from .0054e310
// 051ae50c   04361650
// 051ae510   00008ca9  ; jichi: text
// 051ae514   0000001a
// 051ae518   04343864
// 051ae51c   00000000
// 051ae520   00000001
// 051ae524   051ae62c
// 051ae528   041edc20
// 051ae52c   04343830
// 051ae530   0434a8b0
// 051ae534   0434a7f0
// 051ae538   00000080
// 051ae53c   00000080
// 051ae540   3f560000
// 051ae544   437f8000
// 051ae548   4433e000
// 051ae54c   16f60c00
// 051ae550   051ae650
// 051ae554   042c4c20
// 051ae558   0000002c
// 051ae55c   00439bc5  return to .00439bc5 from .0043af60
//
// Registers & stack:
// Scenario:
// eax 04361650
// ecx 04357640
// edx 04343864
// ebx 0000001a
// esp 051ae508
// ebp 00008169
// esi 04357640
// edi 051ae62c
// eip 0054e310 .0054e310
//
// 051ae508   0054e9d1  return to .0054e9d1 from .0054e310
// 051ae50c   04361650
// 051ae510   00008169
// 051ae514   0000001a
// 051ae518   04343864
// 051ae51c   00000000
// 051ae520   00000001
// 051ae524   051ae62c
// 051ae528   041edc20
// 051ae52c   04343830
// 051ae530   0434a8b0
// 051ae534   0434a7f0
// 051ae538   00000080
// 051ae53c   00000080
// 051ae540   3f560000
// 051ae544   437f8000
// 051ae548   4433e000
// 051ae54c   16f60c00
// 051ae550   051ae650
// 051ae554   042c4c20
// 051ae558   0000002c
//
// Name:
//
// eax 04362430
// ecx 17025230
// edx 0430b6e4
// ebx 0000001a
// esp 051ae508
// ebp 00008179
// esi 17025230
// edi 051ae62c
// eip 0054e310 .0054e310
//
// 051ae508   0054e9d1  return to .0054e9d1 from .0054e310
// 051ae50c   04362430
// 051ae510   00008179
// 051ae514   0000001a
// 051ae518   0430b6e4
// 051ae51c   00000000
// 051ae520   00000001
// 051ae524   051ae62c
// 051ae528   041edae0
// 051ae52c   0430b6b0
// 051ae530   0434a790
// 051ae534   0434a910
// 051ae538   00000080
// 051ae53c   00000080
// 051ae540   3efa0000
// 051ae544   4483f000
// 051ae548   44322000
// 051ae54c   16f60aa0
// 051ae550   051ae650
// 051ae554   042c4c20
// 051ae558   0000002c

static void SpecialHookCatSystem3(hook_context *context, HookParam *, uintptr_t *data, uintptr_t *split, size_t *len)
{
  // DWORD ch = *data = *(DWORD *)(esp_base + hp->offset); // arg2
  DWORD ch = *data = context->stack[2];
  *len = LeadByteTable[(ch >> 8) & 0xff]; // CODEC_ANSI_BE
  *split = context->edx >> 16;
}

bool InsertCatSystemHook()
{
  // DWORD search=0x95EB60F;
  // DWORD j,i=SearchPattern(processStartAddress,processStopAddress-processStartAddress,&search,4);
  // if (i==0) return;
  // i+=processStartAddress;
  // for (j=i-0x100;i>j;i--)
  //   if (*(DWORD*)i==0xcccccccc) break;
  // if (i==j) return;
  // hp.address=i+4;
  // hp.offset=regoffset(eax);
  // hp.index=4;
  // hp.type =CODEC_ANSI_BE|DATA_INDIRECT|USING_SPLIT|SPLIT_INDIRECT;
  // hp.length_offset=1;

  enum
  {
    beg = 0xff6acccc
  }; // jichi 7/12/2014: beginning of the function
  enum
  {
    addr_offset = 2
  }; // skip two leading 0xcc
  ULONG addr = MemDbg::findCallerAddress((ULONG)::GetTextMetricsA, beg, processStartAddress, processStopAddress);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr + addr_offset; // skip 1 push?
  hp.offset = stackoffset(2);      // text character is in arg2

  // jichi 12/23/2014: Modify split for new catsystem
  bool newEngine = Util::CheckFile(L"cs2conf.dll");
  if (newEngine)
  {
    // hp.text_fun = SpecialHookCatSystem3; // type not needed
    // NewHook(hp, "CatSystem3");
    // ConsoleOutput("INSERT CatSystem3");
    hp.type = CODEC_ANSI_BE | USING_SPLIT;
    hp.split = regoffset(esi);
    return NewHook(hp, "CatSystem3new");
  }
  else
  {
    BYTE check[] = {0x66, 0x83, 0xff, 0x20, // 0x20
                    0x0f, 0x84, XX4,
                    0xb8, 0x40, 0x81, 0x00, 0x00, // 0x8140
                    0x66, 0x3b, 0xf8};
    BYTE check2[] = {
        0X6A, 0XFF,
        0X68, XX4,
        0X64, 0XA1, 0, 0, 0, 0,
        0X50,
        0X81, 0XEC, XX4,
        0XA1, XX4,
        0X33, 0XC4,
        0X89, 0X84, 0X24, XX4,
        XX, XX, XX,
        0XA1, XX4,
        0X33, 0XC4,
        XX,
        0X8D, 0X84, 0X24, XX4,
        0X64, 0XA3, 0, 0, 0, 0,
        0X8B, 0XF9};
    hp.type = CODEC_ANSI_BE | USING_SPLIT;
    if (MemDbg::findBytes(check, sizeof(check), addr, addr + 0x100))
    {
      hp.split = stackoffset(1);
      hp.offset = regoffset(edx);
    }
    else if (MatchPattern(hp.address, check2, sizeof(check2)))
    {
      // 結い橋R
      // https://vndb.org/v5588
      hp.offset = regoffset(ecx);
      // hp.split = stackoffset(1);
      hp.type &= ~USING_SPLIT;
    }
    else
    {
      hp.split = regoffset(edx);
    }
    return NewHook(hp, "CatSystem2");
  }
}
bool InsertCatSystem2Hook()
{

  /*
   * Sample games:
   * https://vndb.org/v26987
   */
  const BYTE bytes[] = {
      0x38, 0x08,                              // cmp [eax],cl
      0x0F, 0x84, XX4,                         // je cs2.exe+23E490
      0x66, 0x66, 0x0F, 0x1F, 0x84, 0x00, XX4, // nop word ptr [eax+eax+00000000]
      0x4F,                                    // dec edi
      0xC7, 0x85, XX4, XX4,                    // mov [ebp-000005A0],00000000
      0x33, 0xF6,                              // xor esi,esi
      0xC7, 0x85, XX4, XX4,                    // mov [ebp-0000057C],00000000
      0x85, 0xFF                               // test edi,edi
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(eax);
  hp.type = USING_STRING | CODEC_UTF8;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    auto _ = re::sub(buffer->strA(), R"(\[(.+?)/.+\])", "$1");
    strReplace(_, "\\@");
    buffer->from(_);
  };
  hp.lineSeparator = L"\\n";
  return NewHook(hp, "CatSystem2new");
}
namespace
{ // unnamed
  namespace Patch
  {

    namespace Private
    {
      // String in ecx
      // bool __fastcall isLeadByteChar(const char *s, DWORD edx)
      // bool  isLeadByteChar(hook_context*s,void* data, size_t* len,uintptr_t*role)
      // {
      //   auto pc=(CHAR*)s->ecx;

      //   s->eax=(bool)((pc)&&dynsjis::isleadbyte(*pc));
      //   return false;

      //   //return dynsjis::isleadstr(s); // no idea why this will cause Grisaia3 to hang
      //   //return ::IsDBCSLeadByte(HIBYTE(testChar));
      // }
      bool isLeadByteChar(char *s)
      {
        return s && dynsjis::isleadchar(*s);

        // return dynsjis::isleadstr(s); // no idea why this will cause Grisaia3 to hang
        // return ::IsDBCSLeadByte(HIBYTE(testChar));
      }
      __declspec(naked) bool thiscallisLeadByteChar()
      {
        __asm {
            push ecx 
            call isLeadByteChar
            pop ecx
            ret
        }
      }

    } // namespace Private

    /**
     *  Sample game: ゆきこいめると
     *
     *  This function is found by searching the following instruction:
     *  00511C8E   3C 81            CMP AL,0x81
     *
     *  This function is very similar to that in LC-ScriptEngine.
     *
     *  Return 1 if the first byte in arg1 is leading byte else 0.
     *
     *  00511C7C   CC               INT3
     *  00511C7D   CC               INT3
     *  00511C7E   CC               INT3
     *  00511C7F   CC               INT3
     *  00511C80   8B4C24 04        MOV ECX,DWORD PTR SS:[ESP+0x4]
     *  00511C84   85C9             TEST ECX,ECX
     *  00511C86   74 2F            JE SHORT .00511CB7
     *  00511C88   8A01             MOV AL,BYTE PTR DS:[ECX]
     *  00511C8A   84C0             TEST AL,AL
     *  00511C8C   74 29            JE SHORT .00511CB7
     *  00511C8E   3C 81            CMP AL,0x81
     *  00511C90   72 04            JB SHORT .00511C96
     *  00511C92   3C 9F            CMP AL,0x9F
     *  00511C94   76 08            JBE SHORT .00511C9E
     *  00511C96   3C E0            CMP AL,0xE0
     *  00511C98   72 1D            JB SHORT .00511CB7
     *  00511C9A   3C EF            CMP AL,0xEF
     *  00511C9C   77 19            JA SHORT .00511CB7
     *  00511C9E   8A41 01          MOV AL,BYTE PTR DS:[ECX+0x1]
     *  00511CA1   3C 40            CMP AL,0x40
     *  00511CA3   72 04            JB SHORT .00511CA9
     *  00511CA5   3C 7E            CMP AL,0x7E
     *  00511CA7   76 08            JBE SHORT .00511CB1
     *  00511CA9   3C 80            CMP AL,0x80
     *  00511CAB   72 0A            JB SHORT .00511CB7
     *  00511CAD   3C FC            CMP AL,0xFC
     *  00511CAF   77 06            JA SHORT .00511CB7
     *  00511CB1   B8 01000000      MOV EAX,0x1
     *  00511CB6   C3               RETN
     *  00511CB7   33C0             XOR EAX,EAX
     *  00511CB9   C3               RETN
     *  00511CBA   CC               INT3
     *  00511CBB   CC               INT3
     *  00511CBC   CC               INT3
     *  00511CBD   CC               INT3
     *
     *  Sample game: Grisaia3 グリザイアの楽園
     *  0050747F   CC               INT3
     *  00507480   8B4C24 04        MOV ECX,DWORD PTR SS:[ESP+0x4]  ; jichi: text in arg1
     *  00507484   85C9             TEST ECX,ECX
     *  00507486   74 2F            JE SHORT .005074B7
     *  00507488   8A01             MOV AL,BYTE PTR DS:[ECX]
     *  0050748A   84C0             TEST AL,AL
     *  0050748C   74 29            JE SHORT .005074B7
     *  0050748E   3C 81            CMP AL,0x81
     *  00507490   72 04            JB SHORT .00507496
     *  00507492   3C 9F            CMP AL,0x9F
     *  00507494   76 08            JBE SHORT .0050749E
     *  00507496   3C E0            CMP AL,0xE0
     *  00507498   72 1D            JB SHORT .005074B7
     *  0050749A   3C EF            CMP AL,0xEF
     *  0050749C   77 19            JA SHORT .005074B7
     *  0050749E   8A41 01          MOV AL,BYTE PTR DS:[ECX+0x1]
     *  005074A1   3C 40            CMP AL,0x40
     *  005074A3   72 04            JB SHORT .005074A9
     *  005074A5   3C 7E            CMP AL,0x7E
     *  005074A7   76 08            JBE SHORT .005074B1
     *  005074A9   3C 80            CMP AL,0x80
     *  005074AB   72 0A            JB SHORT .005074B7
     *  005074AD   3C FC            CMP AL,0xFC
     *  005074AF   77 06            JA SHORT .005074B7
     *  005074B1   B8 01000000      MOV EAX,0x1
     *  005074B6   C3               RETN
     *  005074B7   33C0             XOR EAX,EAX
     *  005074B9   C3               RETN
     *  005074BA   CC               INT3
     *  005074BB   CC               INT3
     *  005074BC   CC               INT3
     *  005074BD   CC               INT3
     *
     *  Sample game: Grisaia1 グリザイアの果実
     *  0041488A   CC               INT3
     *  0041488B   CC               INT3
     *  0041488C   CC               INT3
     *  0041488D   CC               INT3
     *  0041488E   CC               INT3
     *  0041488F   CC               INT3
     *  00414890   85C9             TEST ECX,ECX    ; jichi: text in ecx
     *  00414892   74 2F            JE SHORT Grisaia.004148C3
     *  00414894   8A01             MOV AL,BYTE PTR DS:[ECX]
     *  00414896   84C0             TEST AL,AL
     *  00414898   74 29            JE SHORT Grisaia.004148C3
     *  0041489A   3C 81            CMP AL,0x81
     *  0041489C   72 04            JB SHORT Grisaia.004148A2
     *  0041489E   3C 9F            CMP AL,0x9F
     *  004148A0   76 08            JBE SHORT Grisaia.004148AA
     *  004148A2   3C E0            CMP AL,0xE0
     *  004148A4   72 1D            JB SHORT Grisaia.004148C3
     *  004148A6   3C EF            CMP AL,0xEF
     *  004148A8   77 19            JA SHORT Grisaia.004148C3
     *  004148AA   8A41 01          MOV AL,BYTE PTR DS:[ECX+0x1]
     *  004148AD   3C 40            CMP AL,0x40
     *  004148AF   72 04            JB SHORT Grisaia.004148B5
     *  004148B1   3C 7E            CMP AL,0x7E
     *  004148B3   76 08            JBE SHORT Grisaia.004148BD
     *  004148B5   3C 80            CMP AL,0x80
     *  004148B7   72 0A            JB SHORT Grisaia.004148C3
     *  004148B9   3C FC            CMP AL,0xFC
     *  004148BB   77 06            JA SHORT Grisaia.004148C3
     *  004148BD   B8 01000000      MOV EAX,0x1
     *  004148C2   C3               RETN
     *  004148C3   33C0             XOR EAX,EAX
     *  004148C5   C3               RETN
     *  004148C6   CC               INT3
     *  004148C7   CC               INT3
     *  004148C8   CC               INT3
     */

    ULONG patchEncoding(ULONG startAddress, ULONG stopAddress)
    {
      const uint8_t bytes[] = {
          0x74, 0x29, // 00511c8c   74 29            je short .00511cb7
          0x3c, 0x81  // 00511c8e   3c 81            cmp al,0x81
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return false;
      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        return false;
      for (auto p = addr; p - addr < 20; p += ::disasm((LPCVOID)p))
        if (*(WORD *)p == 0xc985) // 00414890   85C9             TEST ECX,ECX    ; jichi: text in ecx
          return addr;            // winhook::replace_fun(p, (ULONG)Private::isLeadByteChar);
      return 0;
    }

  } // namespace Patch

  /**
   *  Sample game: ゆきこいめると
   *
   *  Example prefix to skip:
   *  03751294  81 40 5C 70 63 81 75 83 7B 83 4E 82 CC 8E AF 82  　\pc「ボクの識・
   *
   *  033CF370  5C 6E 81 40 5C 70 63 8C 4A 82 E8 95 D4 82 BB 82  \n　\pc繰り返そ・
   *  033CF380  A4 81 41 96 7B 93 96 82 C9 81 41 82 B1 82 CC 8B  ､、本当に、この・
   *  033CF390  47 90 DF 82 CD 81 41 83 8D 83 4E 82 C8 82 B1 82  G節は、ロクなこ・
   *  033CF3A0  C6 82 AA 82 C8 82 A2 81 42 00 AA 82 C8 82 A2 81  ﾆがない。.ｪない・
   *  033CF3B0  42 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  B...............
   *  033CF3C0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
   *  033CF3D0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
   *  033CF3E0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
   *  033CF3F0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
   *  033CF400  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
   *
   *  Sample choice texts:
   *
   *  str 155 選択肢
   *
   *  0 op01 最初から始める
   *
   *  1 select_go_tar たるひ初キスシーンを見る
   */
  template <typename strT>
  strT ltrim(strT text)
  {
    strT lastText = nullptr;
    while (*text && text != lastText)
    {
      lastText = text;
      if (text[0] == 0x20)
        text++;
      if ((UINT8)text[0] == 0x81 && (UINT8)text[1] == 0x40) // skip space \u3000 (0x8140 in sjis)
        text += 2;
      if (text[0] == '\\')
      {
        text++;
        while (::islower(text[0]) || text[0] == '@')
          text++;
      }
    }
    while ((signed char)text[0] > 0 && text[0] != '[') // skip all leading ascii characters except "[" needed for ruby
      text++;
    return text;
  }

  // Remove trailing '\@'
  size_t rtrim(LPCSTR text)
  {
    size_t size = ::strlen(text);
    while (size >= 2 && text[size - 2] == '\\' && (UINT8)text[size - 1] <= 127)
      size -= 2;
    return size;
  }

  namespace ScenarioHook
  {
    namespace Private
    {

      bool isOtherText(LPCSTR text)
      {
        /* Sample game: ゆきこいめると */
        return ::strcmp(text, "\x91\x49\x91\xf0\x8e\x88") == 0; /* 選択肢 */
      }

      /**
       *  Sample game: 果つることなき未来ヨリ
       *
       *  Sample ecx:
       *
       *  03283A88    24 00 CD 02 76 16 02 00 24 00 CD 02 58 00 CD 02  $.ﾍv.$.ﾍX.ﾍ
       *  03283A98    BD 2D 01 00 1C 1C 49 03 14 65 06 00 14 65 06 00  ｽ-.Ie.e.
       *                                      this is ID,  this is the same ID: 0x066514
       *  03283AA8    80 64 06 00 20 8C 06 00 24 00 6C 0D 00 00 10 00  d. ・.$.l....
       *              this is ID: 0x066480
       *  03283AB8    C8 F1 C2 00 21 00 00 00 48 A9 75 00 E8 A9 96 00  ﾈ.!...Hｩu.隧・
       *  03283AC8    00 00 00 00 48 80 4F 03 00 00 00 00 CC CC CC CC  ....HO....ﾌﾌﾌﾌ
       *  03283AD8    CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC  ﾌﾌﾌﾌﾌﾌﾌﾌﾌﾌﾌﾌﾌﾌﾌﾌ
       */
      // struct ClassArgument // for ecx
      //{
      //   DWORD unknown[7],
      //         split1,   // 0x20 - 9
      //         split2;   // 0x20
      //   // split1 - split2 is always 0x94
      //   DWORD split() const { return split1 - split2; } //
      // };

      static bool containsNamePunct_(const char *text)
      {
        static const char *puncts[] = {
            "\x81\x41" /* 、 */
            ,
            "\x81\x43" /* ， */
            ,
            "\x81\x42" /* 。 */
            //, "\x81\x48" /* ？ */
            ,
            "\x81\x49" /* ！ */
            ,
            "\x81\x63" /* … */
            ,
            "\x81\x64" /* ‥ */

            //, "\x81\x79" /* 【 */
            //, "\x81\x7a" /* 】 */
            ,
            "\x81\x75" /* 「 */
            ,
            "\x81\x76" /* 」 */
            ,
            "\x81\x77" /* 『 */
            ,
            "\x81\x78" /* 』 */
            //, "\x81\x69" /* （ */
            //, "\x81\x6a" /* ） */
            //, "\x81\x6f" /* ｛ */
            //, "\x81\x70" /* ｝ */
            //, "\x81\x71" /* 〈 */
            //, "\x81\x72" /* 〉 */
            ,
            "\x81\x6d" /* ［ */
            ,
            "\x81\x6e" /* ］ */
            //, "\x81\x83", /* ＜ */
            //, "\x81\x84", /* ＞ */
            ,
            "\x81\x65" /* ‘ */
            ,
            "\x81\x66" /* ’ */
            ,
            "\x81\x67" /* “ */
            ,
            "\x81\x68" /* ” */
        };
        for (size_t i = 0; i < ARRAYSIZE(puncts); i++)
          if (::strstr(text, puncts[i]))
            return true;

        if (::strstr(text, "\x81\x48")                      /* ？ */
            && !::strstr(text, "\x81\x48\x81\x48\x81\x48")) /* ？？？ */
          return true;
        return false;
      }
      bool guessIsNameText(const char *text, size_t size)
      {
        enum
        {
          MaximumNameSize = 0x10
        };
        if (!size)
          size = ::strlen(text);
        return size < MaximumNameSize && !containsNamePunct_(text);
      }
      LPSTR trimmedText;
      size_t trimmedSize;
      void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
      {
        // static std::unordered_set<uint64_t> hashes_;
        auto text = (LPSTR)s->eax; // arg1
        if (!text || !*text || all_ascii(text))
          return;
        // Alternatively, if do not skip ascii chars, edx is always 0x4ef74 for Japanese texts
        // if (s->edx != 0x4ef74)
        //  return true;
        trimmedText = ltrim(text);
        if (!trimmedText || !*trimmedText)
          return;
        trimmedSize = rtrim(trimmedText);
        *role = Engine::OtherRole;
        // DOUT(QString::fromLocal8Bit((LPCSTR)s->esi));
        // auto splitText = (LPCSTR)s->esi;
        // if (::strcmp(splitText, "MES_SETNAME")) // This is for scenario text with voice
        // if (::strcmp(splitText, "MES_SETFACE"))
        // if (::strcmp(splitText, "pcm")) // first scenario or history without text
        //   return true;
        // auto retaddr = s->stack[1]; // caller
        // auto retaddr = s->stack[13]; // parent caller
        // auto split = *(DWORD *)s->esi;
        // auto split = s->esi - s->eax;
        // DOUT(split);
        // auto self = (ClassArgument *)s->ecx;
        // auto split = self->split();
        // enum { sig = 0 };
        auto self = s->ecx;
        if (!Engine::isAddressWritable(self)) // old cs2 game such as Grisaia
          self = s->stack[2];                 // arg1
        ULONG groupId = self;
        if (Engine::isAddressWritable(self))
          groupId = *(DWORD *)(self + 0x20);
        {
          static ULONG minimumGroupId_ = -1; // I assume scenario thread to have minimum groupId

          // if (session_.addText(groupId, Engine::hashCharArray(text))) {
          if (groupId <= minimumGroupId_)
          {
            minimumGroupId_ = groupId;

            *role = Engine::ScenarioRole;
            if (isOtherText(text))
              *role = Engine::OtherRole;
            else if (::isdigit(text[0]))
              *role = Engine::ChoiceRole;
            else if (trimmedText == text && !trimmedText[trimmedSize] // no prefix and suffix
                     && guessIsNameText(trimmedText, trimmedSize))
              *role = Engine::NameRole;
          }
        }

        std::string oldData(trimmedText, trimmedSize);
        strReplace(oldData, "\\n", "\n");
        buffer->from(oldData);
      }
      void hookafter(hook_context *s, TextBuffer buffer)
      {
        auto newData = buffer.strA();
        strReplace(newData, "\n", "\\n");
        if (trimmedText[trimmedSize])
          newData.append(trimmedText + trimmedSize);
        ::strcpy(trimmedText, newData.c_str());
      }
    } // namespace Private

    /**
     *  Sample game: 果つることなき未来ヨリ
     *
     *  Debugging message:
     *  - Hook to GetGlyphOutlineA
     *  - Find "MES_SHOW" address on the stack
     *    Alternatively, find the address of "fes.int/flow.fes" immediately after the game is launched
     *  - Use hardware breakpoint to find out when "MES_SHOW" is overridden
     *    Only stop when text is written by valid scenario text.
     *
     *  00503ADE   CC               INT3
     *  00503ADF   CC               INT3
     *  00503AE0   8B4424 0C        MOV EAX,DWORD PTR SS:[ESP+0xC]
     *  00503AE4   8B4C24 04        MOV ECX,DWORD PTR SS:[ESP+0x4]
     *  00503AE8   56               PUSH ESI
     *  00503AE9   FF30             PUSH DWORD PTR DS:[EAX]
     *  00503AEB   E8 102F1600      CALL Hatsumir.00666A00	; jichi: text in eax after this call
     *  00503AF0   BE 18058900      MOV ESI,Hatsumir.00890518                ; ASCII "fes.int/flow.fes"
     *  00503AF5   8BC8             MOV ECX,EAX ; jichi: esi is the target location
     *  00503AF7   2BF0             SUB ESI,EAX
     *  00503AF9   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
     *  00503B00   8A11             MOV DL,BYTE PTR DS:[ECX]
     *  00503B02   8D49 01          LEA ECX,DWORD PTR DS:[ECX+0x1]
     *  00503B05   88540E FF        MOV BYTE PTR DS:[ESI+ECX-0x1],DL    ; jichi: target location modified here
     *  00503B09   84D2             TEST DL,DL
     *  00503B0B  ^75 F3            JNZ SHORT Hatsumir.00503B00
     *  00503B0D   8B4C24 0C        MOV ECX,DWORD PTR SS:[ESP+0xC]
     *  00503B11   50               PUSH EAX
     *  00503B12   68 18058900      PUSH Hatsumir.00890518                   ; ASCII "fes.int/flow.fes"
     *  00503B17   8B89 B4000000    MOV ECX,DWORD PTR DS:[ECX+0xB4]
     *  00503B1D   E8 EE030B00      CALL Hatsumir.005B3F10
     *  00503B22   B8 02000000      MOV EAX,0x2
     *  00503B27   5E               POP ESI
     *  00503B28   C2 1000          RETN 0x10
     *  00503B2B   CC               INT3
     *  00503B2C   CC               INT3
     *  00503B2D   CC               INT3
     *  00503B2E   CC               INT3
     *
     *  EAX 0353B1A0    ; jichi: text here
     *  ECX 00D86D08
     *  EDX 0004EF74
     *  EBX 00012DB2
     *  ESP 0525EBAC
     *  EBP 0525ED6C
     *  ESI 00D86D08
     *  EDI 00000000
     *  EIP 00503AF0 Hatsumir.00503AF0
     *
     *  0525EBAC   00D86D08
     *  0525EBB0   0066998E  RETURN to Hatsumir.0066998E
     *  0525EBB4   00D86D08
     *  0525EBB8   00B16188
     *  0525EBBC   035527D8
     *  0525EBC0   0525EBE4
     *  0525EBC4   00B16188
     *  0525EBC8   00D86D08
     *  0525EBCC   0525F62B  ASCII "ript.kcs"
     *  0525EBD0   00000004
     *  0525EBD4   00000116
     *  0525EBD8   00000003
     *  0525EBDC   00000003
     *  0525EBE0   00665C08  RETURN to Hatsumir.00665C08
     *  0525EBE4   CCCCCCCC
     *  0525EBE8   0525F620  ASCII "kcs.int/sscript.kcs"
     *  0525EBEC   00694D94  Hatsumir.00694D94
     *  0525EBF0   004B278F  RETURN to Hatsumir.004B278F from Hatsumir.00666CA0
     *  0525EBF4   B3307379
     *  0525EBF8   0525ED04
     *  0525EBFC   00B16188
     *  0525EC00   0525ED04
     *  0525EC04   00B16188
     *  0525EC08   00CC5440
     *  0525EC0C   02368938
     *  0525EC10   0069448C  ASCII "%s/%s"
     *  0525EC14   00B45B18  ASCII "kcs.int"
     *  0525EC18   00000001
     *  0525EC1C   023741E0
     *  0525EC20   0000000A
     *  0525EC24   0049DBB3  RETURN to Hatsumir.0049DBB3 from Hatsumir.00605A84
     *  0525EC28   72637373
     *  0525EC2C   2E747069
     *  0525EC30   0073636B  Hatsumir.0073636B
     *  0525EC34   0525ED04
     *  0525EC38   0053ECDE  RETURN to Hatsumir.0053ECDE from Hatsumir.004970C0
     *  0525EC3C   0525EC80
     *  0525EC40   023D9FB8
     *
     *  Alternative ruby hook:
     *  It will hook to the beginning of the Ruby processing function, which is not better than the current approach.
     *  http://lab.aralgood.com/index.php?mid=board_lecture&search_target=title_content&search_keyword=CS&document_srl=1993027
     *
     *  Sample game: Grisaia3 グリザイアの楽園
     *
     *  004B00CB   CC               INT3
     *  004B00CC   CC               INT3
     *  004B00CD   CC               INT3
     *  004B00CE   CC               INT3
     *  004B00CF   CC               INT3
     *  004B00D0   8B4424 0C        MOV EAX,DWORD PTR SS:[ESP+0xC]
     *  004B00D4   8B08             MOV ECX,DWORD PTR DS:[EAX]
     *  004B00D6   56               PUSH ESI
     *  004B00D7   51               PUSH ECX
     *  004B00D8   8B4C24 0C        MOV ECX,DWORD PTR SS:[ESP+0xC]
     *  004B00DC   E8 7F191300      CALL .005E1A60
     *  004B00E1   BE D0E87B00      MOV ESI,.007BE8D0
     *  004B00E6   8BC8             MOV ECX,EAX
     *  004B00E8   2BF0             SUB ESI,EAX
     *  004B00EA   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
     *  004B00F0   8A11             MOV DL,BYTE PTR DS:[ECX]
     *  004B00F2   88140E           MOV BYTE PTR DS:[ESI+ECX],DL
     *  004B00F5   41               INC ECX
     *  004B00F6   84D2             TEST DL,DL
     *  004B00F8  ^75 F6            JNZ SHORT .004B00F0
     *  004B00FA   8B5424 0C        MOV EDX,DWORD PTR SS:[ESP+0xC]
     *  004B00FE   8B8A B4000000    MOV ECX,DWORD PTR DS:[EDX+0xB4]
     *  004B0104   50               PUSH EAX
     *  004B0105   68 D0E87B00      PUSH .007BE8D0
     *  004B010A   E8 818D0600      CALL .00518E90
     *  004B010F   B8 02000000      MOV EAX,0x2
     *  004B0114   5E               POP ESI
     *  004B0115   C2 1000          RETN 0x10
     *  004B0118   CC               INT3
     *  004B0119   CC               INT3
     *  004B011A   CC               INT3
     *  004B011B   CC               INT3
     *  004B011C   CC               INT3
     *
     *  Sample game: Grisaia1 グリザイアの果実
     *  00498579   CC               INT3
     *  0049857A   CC               INT3
     *  0049857B   CC               INT3
     *  0049857C   CC               INT3
     *  0049857D   CC               INT3
     *  0049857E   CC               INT3
     *  0049857F   CC               INT3
     *  00498580   8B4424 0C        MOV EAX,DWORD PTR SS:[ESP+0xC]
     *  00498584   8B08             MOV ECX,DWORD PTR DS:[EAX]  ; jichi: ecx is no longer a pointer
     *  00498586   8B4424 04        MOV EAX,DWORD PTR SS:[ESP+0x4]
     *  0049858A   56               PUSH ESI
     *  0049858B   E8 10920500      CALL Grisaia.004F17A0
     *  00498590   BE D89C7600      MOV ESI,Grisaia.00769CD8                 ; ASCII "bgm01"
     *  00498595   8BC8             MOV ECX,EAX
     *  00498597   2BF0             SUB ESI,EAX
     *  00498599   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
     *  004985A0   8A11             MOV DL,BYTE PTR DS:[ECX]
     *  004985A2   88140E           MOV BYTE PTR DS:[ESI+ECX],DL
     *  004985A5   41               INC ECX
     *  004985A6   84D2             TEST DL,DL
     *  004985A8  ^75 F6            JNZ SHORT Grisaia.004985A0
     *  004985AA   8B4C24 0C        MOV ECX,DWORD PTR SS:[ESP+0xC]
     *  004985AE   8B91 B4000000    MOV EDX,DWORD PTR DS:[ECX+0xB4]
     *  004985B4   50               PUSH EAX
     *  004985B5   68 D89C7600      PUSH Grisaia.00769CD8                    ; ASCII "bgm01"
     *  004985BA   52               PUSH EDX
     *  004985BB   E8 701C0600      CALL Grisaia.004FA230
     *  004985C0   B8 02000000      MOV EAX,0x2
     *  004985C5   5E               POP ESI
     *  004985C6   C2 1000          RETN 0x10
     *  004985C9   CC               INT3
     *  004985CA   CC               INT3
     *  004985CB   CC               INT3
     *  004985CC   CC               INT3
     *  004985CD   CC               INT3
     */
    bool attach(ULONG startAddress, ULONG stopAddress, bool utf8)
    {
      const uint8_t bytes[] = {
          0xe8, XX4,  // 004b00dc   e8 7f191300      call .005e1a60 ; jichi: hook after here
          0xbe, XX4,  // 004b00e1   be d0e87b00      mov esi,.007be8d0
          0x8b, 0xc8, // 004b00e6   8bc8             mov ecx,eax
          0x2b, 0xf0  // 004b00e8   2bf0             sub esi,eax
                      // XX2, XX, 0x00,0x00,0x00 // 004b00ea   8d9b 00000000    lea ebx,dword ptr ds:[ebx]
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return false;
      HookParam hp;
      hp.address = addr + 5;
      hp.type = USING_STRING | EMBED_ABLE | NO_CONTEXT;
      if (utf8)
        hp.type |= CODEC_UTF8;
      else
      {
        hp.type |= EMBED_DYNA_SJIS;

        auto p = Patch::patchEncoding(startAddress, stopAddress);
        if (p)
        {
          hp.type |= EMBED_DYNA_SJIS;
          hp.embed_hook_font = F_GetGlyphOutlineA;
          if (*(WORD *)p == 0xc985)
            patch_fun_ptrs = {{(void *)p, (PVOID)(ULONG)Patch::Private::thiscallisLeadByteChar}};
          else
            patch_fun_ptrs = {{(void *)p, (PVOID)(ULONG)Patch::Private::isLeadByteChar}};
        }
      }
      hp.text_fun = Private::hookBefore;
      hp.embed_fun = Private::hookafter;
      hp.embed_hook_font = F_GetGlyphOutlineA;
      hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
      {
        buffer->from(re::sub(buffer->strA(), R"(\[(.+?)/.+\])", "$1"));
      };

      return NewHook(hp, "EmbedCS2");
    }
  }
} // namespace ScenarioHook
namespace
{
  bool cs2()
  {
    // https://vndb.org/v26537
    const uint8_t bytes[] = {/*
    .text:0065C10F                 cmp     bx, 20h ; ' '
.text:0065C113                 jz      loc_65C5A6
.text:0065C119                 mov     ecx, 8140h
.text:0065C11E                 cmp     bx, cx
.text:0065C121                 jnz     short loc_65C140
.text:0065C123                 jmp     loc_65C5A6
.text:0065C128 ; ---------------------------------------------------------------------------
.text:0065C128
.text:0065C128 loc_65C128:                             ; CODE XREF: sub_65C080+8D↑j
.text:0065C128                 cmp     bx, 20h ; ' '
.text:0065C12C                 jz      loc_65C5A6
.text:0065C132                 mov     ecx, 3000h
.text:0065C137                 cmp     bx, cx
.text:0065C13A                 jz      loc_65C5A6
if ( a9 )
  {
    if ( a3 == 32 || a3 == 12288 )
      return 1;
  }
  else if ( a3 == 32 || a3 == 0x8140 )
  {
    return 1;
  }
*/
                             0x66, 0x83, 0xfb, 0x20,
                             0x0f, 0x84, XX4,
                             0xB9, 0x40, 0x81, 0x00, 0x00,
                             0x66, 0x3B, 0xD9,
                             0x75, XX,

                             0xe9, XX4,

                             0x66, 0x83, 0xfb, 0x20,
                             0x0f, 0x84, XX4,
                             0xB9, 0x00, 0x30, 0x00, 0x00,
                             0x66, 0x3B, 0xD9,
                             0x0f, 0x84, XX4

    };
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_CHAR;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      if (context->stack[8])
      {
        hp->type |= CODEC_UTF16;
        hp->type &= ~CODEC_ANSI_BE;
      }
      else
      {
        hp->type |= CODEC_ANSI_BE;
        hp->type &= ~CODEC_UTF16;
      }
      auto c = context->stack[2];
      buffer->from_t<wchar_t>(c);
    };
    return NewHook(hp, "catsystem");
  }
}
bool CatSystem::attach_function()
{
  bool utf8 = false;
  auto b1 = InsertCatSystemHook();
  if (!b1)
  {
    b1 |= InsertCatSystem2Hook();
    utf8 = true;
  }
  auto embed = ScenarioHook::attach(processStartAddress, processStopAddress, utf8);
  b1 = b1 || cs2();
  b1 |= embed;
  return b1;
}