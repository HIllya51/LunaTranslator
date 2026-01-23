#include "QLIE.h"
/**
 * jichi 8/18/2013:  QLIE identified by GameData/data0.pack
 *
 * The old hook cannot recognize new games.
 */

namespace
{ // unnamed QLIE

  /**
  * Artikash 8/1/2018: new QLIE hook. old one misses on https://vndb.org/v22308 and https://vndb.org/v19182
  * ExtTextOut hook misses characters because of font caching
  * Method to find H-code: trace call stack from ExtTextOut until missing characters from default hook are found
  * /HW-1C*0:-20@base address of pattern
  * characterizing pattern:
  kimimeza.exe+100D9C - 55                    - push ebp
  kimimeza.exe+100D9D - 8B EC                 - mov ebp,esp
  kimimeza.exe+100D9F - 83 C4 E4              - add esp,-1C { 228 }
  kimimeza.exe+100DA2 - 53                    - push ebx
  kimimeza.exe+100DA3 - 56                    - push esi
  kimimeza.exe+100DA4 - 57                    - push edi
  kimimeza.exe+100DA5 - 33 D2                 - xor edx,edx
  kimimeza.exe+100DA7 - 89 55 FC              - mov [ebp-04],edx
  */
  bool InsertQLIE3Hook()
  {
    const BYTE bytes[] =
        {
            0x55,
            0x8b, 0xec,
            0x83, 0xc4, 0xe4,
            0x53,
            0x56,
            0x57,
            0x33, 0xd2,
            0x89, 0x55, 0xfc};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
    {
      ConsoleOutput("QLIE3: pattern not found");
      // ConsoleOutput("Not QLIE2");
      return false;
    }

    HookParam hp;
    hp.type = CODEC_UTF16 | DATA_INDIRECT | USING_SPLIT;
    hp.offset = regoffset(esi);
    hp.split = regoffset(edi);
    hp.address = addr;

    ConsoleOutput("INSERT QLIE3");
    return NewHook(hp, "QLiE3");
  }
  /**
   * jichi 8/18/2013: new QLIE hook
   * See: http://www.hongfire.com/forum/showthread.php/420362-QLIE-engine-Hcode
   *
   * Ins:
   * 55 8B EC 53 8B 5D 1C
   * - 55         push ebp    ; hook here
   * - 8bec       mov ebp, esp
   * - 53         push ebx
   * - 8B5d 1c    mov ebx, dword ptr ss:[ebp+1c]
   *
   * /HBN14*0@4CC2C4
   * - addr: 5030596  (0x4cc2c4)
   * - text_fun: 0x0
   * - function: 0
   * - hook_len: 0
   * - ind: 0
   * - length_offset: 1
   * - module: 0
   * - off: 20    (0x14)
   * - recover_len: 0
   * - split: 0
   * - split_ind: 0
   * - type: 1032 (0x408)
   */
  bool InsertQLIE2Hook()
  {
    const BYTE bytes[] = {
        // size = 7
        0x55,            // 55       push ebp    ; hook here
        0x8b, 0xec,      // 8bec     mov ebp, esp
        0x53,            // 53       push ebx
        0x8b, 0x5d, 0x1c // 8b5d 1c  mov ebx, dword ptr ss:[ebp+1c]
    };
    // enum { addr_offset = 0 }; // current instruction is the first one
    ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
    if (!addr)
    {
      ConsoleOutput("QLIE2: pattern not found");
      // ConsoleOutput("Not QLIE2");
      return false;
    }

    HookParam hp;
    hp.type = DATA_INDIRECT | NO_CONTEXT; // 0x408
    hp.offset = stackoffset(5);
    hp.address = addr;

    ConsoleOutput("INSERT QLIE2");
    return NewHook(hp, "QLiE2");
  }

  // jichi: 8/18/2013: Change return type to bool
  bool InsertQLIE1Hook()
  {
    for (DWORD i = processStartAddress + 0x1000; i < processStopAddress - 4; i++)
      if (*(DWORD *)i == 0x7ffe8347)
      { // inc edi, cmp esi,7f
        DWORD t = 0;
        for (DWORD j = i; j < i + 0x10; j++)
        {
          if (*(DWORD *)j == 0xa0)
          { // cmp esi,a0
            t = 1;
            break;
          }
        }
        if (t)
          for (DWORD j = i; j > i - 0x100; j--)
            if (*(DWORD *)j == 0x83ec8b55)
            { // push ebp, mov ebp,esp, sub esp,*
              HookParam hp;
              hp.address = j;
              hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
              {
                auto addr = context->stack[6];
                if (IsBadReadPtr((void *)addr, 2))
                {
                  // https://vndb.org/v571
                  // きみはぐ
                  addr = context->stack[7];
                }
                else
                {
                  *split = context->esp;
                }
                buffer->from_t<WORD>(*(WORD *)addr);
              };
              return NewHook(hp, "QLiE");
            }
      }

    return false;
  }

} // unnamed QLIE
namespace
{
  bool _4()
  {
    // シスターシスター
    // https://vndb.org/v653
    const BYTE bytes[] = {
        0x81, 0xFB, 0x80, 0x00, 0x00, 0x00,
        XX2,
        0x81, 0xFB, 0xa0, 0x00, 0x00, 0x00,
        XX2,
        0x81, 0xFB, 0xdf, 0x00, 0x00, 0x00,
        XX2,
        0x81, 0xFB, 0xff, 0x00, 0x00, 0x00,
        XX2};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);

    if (!addr)
      return false;
    const BYTE funcstart[] = {
        0x90, 0x55, 0x8b, 0xec};
    addr = reverseFindBytes(funcstart, sizeof(funcstart), addr - 0x100, addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr + 1;
    hp.offset = stackoffset(6);
    hp.type = USING_STRING;
    return NewHook(hp, "QLIE4");
  }
  bool _5()
  {
    // おしかけおさなづま3(3乗）
    // School Festa－スクールフェスタ－
    const BYTE bytes[] = {
        0x83, 0xFF, 0x7F,
        XX2,
        0x81, 0xFf, 0xa0, 0x00, 0x00, 0x00,
        XX2,
        0x81, 0xFf, 0xdf, 0x00, 0x00, 0x00,
        XX2,
        0x81, 0xFf, 0xff, 0x00, 0x00, 0x00,
        XX2};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);

    if (!addr)
      return false;
    addr = findfuncstart(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(ecx);
    hp.type = USING_STRING;
    return NewHook(hp, "QLIE5");
  }
}
namespace
{
  //(18禁ゲーム) [240426] [ωstar] 美少女万華鏡異聞 雪おんな
  bool qlie4()
  {
    BYTE bytes[] = {
        0x55, 0x8b, 0xec,
        0x83, 0xc4, 0xe8,
        0x53, 0x56, 0x57,
        0x33, 0xdb,
        0x89, 0x5d, 0xe8,
        0x89, 0x5d, 0xf8,
        0x89, 0x4d, 0xf0,
        0x89, 0x55, 0xfc,
        0x8b, 0x45, 0xfc,
        0xe8, XX4,
        0x33, 0xc0,
        0x55,
        0x68, XX4,
        0x64, 0xff, 0x30,
        0x64, 0x89, 0x20,
        0x33, 0xf6,
        0x8d, 0x45, 0xf8,
        0x33, 0xd2,
        0xe8, XX4,
        0x8b, 0x45, 0xfc,
        0x85, 0xc0,
        0x74, XX,
        0x8b, 0xd0,
        0x83, 0xea, 0x0a,
        0x66, 0x83, 0x3a, 0x02,
        0x74, XX,
        0x8d, 0x45, 0xfc,
        0x8b, 0x55, 0xfc};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | CODEC_UTF16;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      auto __s = std::wstring_view((wchar_t *)context->esi);
      if (startWith(__s, L"[f,3"))
      {
        *split = 2; // history
      }
      else if (startWith(__s, L"[f,0"))
      {
        *split = 1; // text
      }
      else if (startWith(__s, L"[f,1"))
      {
        *split = 0; // name
      }
      else if (startWith(__s, L"[s,"))
      {
        *split = 3; //[s,36,36]「ああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああ」
      }
      else if (startWith(__s, L"[pi,") || startWith(__s, L"[rp,") || startWith(__s, L"[rs,") || startWith(__s, L"[rpi,"))
      {
        return;
      }
      buffer->from(__s);
    };
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      //[f,1][rf,1][s,34,34][c,$FFFFFFFF][rc,$FFFFFFFF]雪之進
      //[f,0][rf,0][s,36,36][c,$FFFFFFFF][rc,$FFFFFFFF]一瞬が勝負だ。私は模造刀に手をかけ、立て膝の状態（いわゆる『[rb,座業,すわりわざ]』）で待機していた。

      auto s = buffer->strW();
      s = re::sub(s, L"\\[rb,(.*?),(.*?)\\]", L"$1");
      s = re::sub(s, L"\\[(.*?)\\]");
      buffer->from(s);
    };
    return NewHook(hp, "qlie4");
  }
}
bool InsertQLIEHook()
{
  bool _ = _4() || _5();
  return InsertQLIE1Hook() || InsertQLIE2Hook() || qlie4() || InsertQLIE3Hook() || _;
}

namespace
{ // unnamed

  namespace ScenarioHook
  {
    namespace Private
    {

      template <typename strT>
      strT trim(strT text, int *size)
      {
        // int length = ::strlen(text);
        int length = *size;
        if (text[0] == '[')
        {
          if (all_ascii(text))
            return nullptr;
          if (text[length - 1] == ']' && ::CharPrevA(text, text + length) == text + length - 1)
          {
            length--;
            if (text[length - 1] == 'n' && text[length - 2] == '[')
              length -= 2;
          }
          for (int i = 1; i < length; i++)
            if ((signed char)text[i] <= 0)
            {
              text += i;
              length -= i - 1;
              break;
            }
          length--; // skip the leading '['
        }
        *size = length;
        return text;
      }

      /**
       *  Sample game: 月に寄りそう乙女の作法２
       *
       *
       *  Name:
       *
       *  019D7688  5B 66 2C 31 5D 5B 72 66 2C 31 5D 5B 73 2C 32 30  [f,1][rf,1][s,20
       *  019D7698  2C 32 30 5D 5B 63 2C 24 46 46 46 46 46 46 46 46  ,20][c,$FFFFFFFF
       *  019D76A8  5D 5B 72 63 2C 24 46 46 46 46 46 46 46 46 5D 81  ][rc,$FFFFFFFF]・
       *  019D76B8  79 8D F7 8F AC 98 48 83 41 83 67 83 8C 81 7A 00  y桜小路アトレ】.
       *
       *  0012FBCC   0055553D  RETURN to .0055553D from .00513234
       *  0012FBD0   0012FDB8  Pointer to next SEH record
       *  0012FBD4   005555A5  SE handler
       *  0012FBD8   0012FD90
       *  0012FBDC   0E9F72D0
       *  0012FBE0   0E9F72D0
       *  0012FBE4   0A24AA90
       *  0012FBE8   00000000
       *  0012FBEC   00000000
       *  0012FBF0   0C7AE0C8  ASCII "st+cc+tt"
       *  0012FBF4   00000000
       *  0012FBF8   00000000
       *  0012FBFC   00000000
       *  0012FC00   00000000
       *  0012FC04   00000000
       *  0012FC08   00000000
       *
       *  EAX 0E3885A0
       *  ECX 00000002
       *  EDX 019D7688
       *  EBX 0041D17C .0041D17C
       *  ESP 0012FBCC
       *  EBP 0012FD90
       *  ESI 0A24AA90
       *  EDI 0E9F72D0
       *  EIP 00513234 .00513234
       *
       *
       *  Dialog's arg4:
       *
       *  04A9BAD0  48 DB 51 00 B8 BA A9 04 F8 BA A9 04 07 02 00 00  HﾛQ.ｸｺｩｩ..
       *  04A9BAE0  B8 67 66 00 D0 AF A6 04 00 00 00 00 90 AC A9 04  ｸgf.ﾐｯｦ....成ｩ
       *  04A9BAF0  01 00 00 00 11 00 00 00 30 5F 64 69 61 6C 6F 67  ......0_dialog
       *  04A9BB00  6D 65 73 73 61 67 65 2C 30 00 00 00 90 AC A9 04  message,0...成ｩ
       *
       *  Scenario:
       *
       *  058DC708  5B 66 2C 30 5D 5B 72 66 2C 30 5D 5B 73 2C 32 34  [f,0][rf,0][s,24
       *  058DC718  2C 32 34 5D 5B 63 2C 24 46 46 46 46 46 46 46 46  ,24][c,$FFFFFFFF
       *  058DC728  5D 5B 72 63 2C 24 46 46 46 46 46 46 46 46 5D 81  ][rc,$FFFFFFFF]・
       *  058DC738  75 82 CD 82 A2 81 41 82 B1 82 B1 82 CD 93 FA 96  uはい、ここは日・
       *  058DC748  7B 82 C5 82 B7 81 42 8B F3 8D 60 82 CC 90 45 88  {です。空港の職・
       *  058DC758  F5 82 E0 81 41 83 56 83 87 83 62 83 76 82 CC 93  焉Aショップの・
       *  058DC768  58 88 F5 82 E0 81 41 83 8D 83 72 81 5B 82 C9 8D  X員も、ロビーに・
       *  058DC778  C0 82 E9 90 6C 82 E0 81 41 93 FA 96 7B 90 6C 82  ﾀる人も、日本人・
       *  058DC788  E7 82 B5 82 AB 90 6C 82 CE 82 A9 82 E8 82 C5 82  轤ｵき人ばかりで・
       *  058DC798  B7 81 76 00 00 8E 8D 05 01 00 00 00 8C 00 00 00  ｷ」..詩...・..
       *  058DC7A8  81 75 8D A1 93 FA 82 CD 90 E2 8D 44 82 CC 93 DC  「今日は絶好の曇
       *  058DC7B8  82 E8 8B F3 82 BE 82 E6 81 41 82 C8 82 F1 82 C4  り空だよ、なんて
       *  058DC7C8  91 66 93 47 82 C8 96 E9 8B F3 82 BE 82 EB 82 A4  素敵な夜空だろう
       *  058DC7D8  81 49 81 40 96 6C 82 CC 8B 41 8D 91 82 C9 8D 87  ！　僕の帰国に合
       *  058DC7E8  82 ED 82 B9 82 C4 91 BE 97 7A 82 F0 89 42 82 B5  わせて太陽を隠し
       *
       *  0012FBCC   0055553D  RETURN to .0055553D from .00513234
       *  0012FBD0   0012FDB8  Pointer to next SEH record
       *  0012FBD4   005555A5  SE handler
       *  0012FBD8   0012FD90
       *  0012FBDC   0E9F7110
       *  0012FBE0   0E9F7110
       *  0012FBE4   0A24AA90
       *  0012FBE8   00000000
       *  0012FBEC   00000000
       *  0012FBF0   0EA33460  ASCII "st+cc+tt"
       *  0012FBF4   00000000
       *  0012FBF8   00000000
       *  0012FBFC   00000000
       *  0012FC00   00000000
       *
       *  EAX 0E9AD230
       *  ECX 00000002
       *  EDX 058DC708
       *  EBX 0041D17C .0041D17C
       *  ESP 0012FBCC
       *  EBP 0012FD90
       *  ESI 0A24AA90
       *  EDI 0E9F7110
       *  EIP 00513234 .00513234
       *
       *  Backlog:
       *  FIXME: I don't have a way to distinguish Backlog out.
       *
       *  0A9775D8  5B 66 2C 32 5D 5B 63 2C 24 46 46 65 64 64 31 66  [f,2][c,$FFedd1f
       *  0A9775E8  66 5D 5B 72 63 2C 24 46 46 65 64 64 31 66 66 5D  f][rc,$FFedd1ff]
       *  0A9775F8  81 75 82 CD 82 A2 81 41 82 B1 82 B1 82 CD 93 FA  「はい、ここは日
       *  0A977608  96 7B 82 C5 82 B7 81 42 8B F3 8D 60 82 CC 90 45  本です。空港の職
       *  0A977618  88 F5 82 E0 81 41 83 56 83 87 83 62 83 76 82 CC  員も、ショップの
       *  0A977628  93 58 88 F5 82 E0 81 41 83 8D 83 72 81 5B 82 C9  店員も、ロビーに
       *
       *  EAX 0FF32FE0
       *  ECX 00000002
       *  EDX 0A9775D8
       *  EBX 0041D17C .0041D17C
       *  ESP 0012FBCC
       *  EBP 0012FD90
       *  ESI 0A909350
       *  EDI 0B843690
       *  EIP 00513234 .00513234
       *
       *  0012FBCC   0055553D  RETURN to .0055553D from .00513234
       *  0012FBD0   0012FDB8  Pointer to next SEH record
       *  0012FBD4   005555A5  SE handler
       *  0012FBD8   0012FD90
       *  0012FBDC   0B843690
       *  0012FBE0   0B843690
       *  0012FBE4   0A909350
       *  0012FBE8   00000000
       *  0012FBEC   00000000
       *  0012FBF0   0FF25558  ASCII ""[f,2][c,$FFedd1ff][rc,$FFedd1ff]"+text"
       *  0012FBF4   00000000
       *  0012FBF8   00000000
       *  0012FBFC   00000000
       *
       *  Sample game ワルキューレロマンツェ more&more (QLiE2):
       *  Name:
       *  0012FB84   00546877  RETURN to .00546877 from .00504AD0
       *  0012FB88   0012FDBC  Pointer to next SEH record
       *  0012FB8C   00546B1B  SE handler
       *  0012FB90   0012FD94
       *  0012FB94   11832DC0
       *  0012FB98   11832DC0
       *  0012FB9C   09278EA0
       *  0012FBA0   00000000
       *  0012FBA4   00000000
       *  0012FBA8   00000000
       *  0012FBAC   00000000
       *  0012FBB0   00000000
       *  0012FBB4   00000000
       *
       *  0A702400  5B 70 63 2C 94 FC 8D F7 5D 00 00 00 70 B6 6F 0A  [pc,美桜]...pｶo.
       *
       *  EAX 0C2763E0 ASCII "HHP"
       *  ECX 00000003
       *  EDX 0A702400
       *  EBX 0041D168 .0041D168
       *  ESP 0012FB84 ASCII "whT"
       *  EBP 0012FD94
       *  ESI 09278EA0
       *  EDI 11832DC0
       *  EIP 00504AD0 .00504AD0
       *
       *  Scenario:
       *  09E0D7C8  5B 63 2C 24 46 46 46 46 46 46 44 44 5D 5B 72 63  [c,$FFFFFFDD][rc
       *  09E0D7D8  2C 24 46 46 46 46 46 46 44 44 5D 81 75 82 A4 82  ,$FFFFFFDD]「う・
       *
       *  0012FB84   00546877  RETURN to .00546877 from .00504AD0
       *  0012FB88   0012FDBC  Pointer to next SEH record
       *  0012FB8C   00546B1B  SE handler
       *  0012FB90   0012FD94
       *  0012FB94   118314E0
       *  0012FB98   118314E0
       *  0012FB9C   09278EA0
       *  0012FBA0   00000000
       *
       *  EAX 0A72D820 ASCII "HHP"
       *  ECX 00000002
       *  EDX 09E0D7C8
       *  EBX 0041D168 .0041D168
       *  ESP 0012FB84 ASCII "whT"
       *  EBP 0012FD94
       *  ESI 09278EA0
       *  EDI 118314E0
       *  EIP 00504AD0 .00504AD0
       *
       *  Sample game ワルキューレロマンツェ (QLiE1):
       *  Garbage:
       *  0A5115D0  83 56 83 69 83 8A 83 49 5C 8B A4 92 CA 5C 6B 79  シナリオ\共通\ky
       *  0A5115E0  6F 5F 30 30 31 5F 30 30 2E 73 00 00 50 FF 50 0A  o_001_00.s..PP.
       *
       *  Name:
       *  0012FB84   00544913  RETURN to .00544913 from .004FFB04
       *  0012FB88   0012FDBC  Pointer to next SEH record
       *  0012FB8C   00544BB1  SE handler
       *  0012FB90   0012FD94
       *  0012FB94   01A139A8
       *  0012FB98   01A139A8
       *  0012FB9C   07D35D00
       *  0012FBA0   00000000
       *
       *  EAX 0C303340
       *  ECX 00000003
       *  EDX 0ED8A620
       *  EBX 0041D6A8 .0041D6A8
       *  ESP 0012FB84
       *  EBP 0012FD94
       *  ESI 07D35D00
       *  EDI 01A139A8
       *  EIP 004FFB04 .004FFB04
       *
       *  01A139A8  60 27 52 00 00 00 00 00 00 00 00 00 00 00 80 3F  `'R...........?
       *  01A139B8  00 00 80 3F 00 00 00 00 00 00 00 00 00 00 80 3F  ..?..........?
       *  01A139C8  00 00 00 00 48 D9 14 0A 68 D9 14 0A 07 02 00 00  ....Hﾙ.hﾙ...
       *  01A139D8  3C F1 07 00 93 9A 5C 00 1C 01 00 00 F4 01 00 00  <・.答\...・..
       *  01A139E8  40 33 30 0C A0 D9 A0 01 C0 29 52 00 00 00 00 00  @30.ﾙﾀ)R.....
       *  01A139F8  00 00 00 00 00 00 80 3F 00 00 80 3F 00 00 00 00  ......?..?....
       *
       *  Scenario:
       *  0012FB84   00544913  RETURN to .00544913 from .004FFB04
       *  0012FB88   0012FDBC  Pointer to next SEH record
       *  0012FB8C   00544BB1  SE handler
       *  0012FB90   0012FD94
       *  0012FB94   01A13960 ; jichi: type string is saved here in edi and arg4/arg5
       *  0012FB98   01A13960
       *  0012FB9C   07D35D00
       *  0012FBA0   00000000
       *
       *  0A14D7C8  30 5F 4D 65 73 73 61 67 65 54 65 78 74 2C 30 00  0_MessageText,0.
       *
       *  EAX 0C308500
       *  ECX 00000006
       *  EDX 0B100590
       *  EBX 0041D6A8 .0041D6A8
       *  ESP 0012FB84
       *  EBP 0012FD94
       *  ESI 07D35D00
       *  EDI 01A13960
       *  EIP 004FFB04 .004FFB04
       *
       *
       *  01A13960  60 27 52 00 00 00 00 00 00 00 00 00 00 00 80 3F  `'R...........?
       *  01A13970  00 00 80 3F 00 00 00 00 00 00 00 00 00 00 80 3F  ..?..........?
       *  01A13980  00 00 00 00 C8 D7 14 0A A8 D8 14 0A 07 02 00 00  ....ﾈﾗ.ｨﾘ...
       *  01A13990  34 90 3F 00 BE 0A 5B 00 D3 02 00 00 EC 01 00 00  4・.ｾ.[.ﾓ..・..
       *  01A139A0  00 85 30 0C A0 D9 A0 01 60 27 52 00 00 00 00 00  .・.ﾙ`'R.....
       *  01A139B0  00 00 00 00 00 00 80 3F 00 00 80 3F 00 00 00 00  ......?..?....
       *
       *  0A14D948  30 5F 4E 61 6D 65 54 65 78 74 2C 30 00 00 00 00  0_NameText,0....
       */

      /**
       *  Known Type strings
       *  These strings seems to be different for different games
       *
       *  ワルキューレロマンツェ(QLiE1)
       *  七つのふしぎの終わるとき (QLiE1)
       *
       *  0_NameText,0
       *  0_MessageText,0
       *  0_Message,0
       *
       *  ワルキューレロマンツェ More&More (QLiE2)
       *  0_nametext,0
       *  0_imo_message,0
       *
       *  月に寄りそう乙女の作法２ (QLiE2):
       *  0_dialogmessage,0
       *  $windowapril
       *  fontsize:30:30
       *
       */

      struct TextArgument // root at [edx - 4]
      {
        DWORD size;   // in [edx-4]
        char text[1]; // in edx

        bool isValid() const
        {
          return text && size && Engine::isAddressReadable(text, size) && ::strlen(text) == size;
        }
      };

      struct TypeArgument
      {
        DWORD unknown[8]; // 0x20

        DWORD textFlag;     // +0x20, 0 for QLiE1, 1 for QLie2
        LPCSTR textAddress; // for QLiE1
        char textData[1];   // for QLiE2

        LPCSTR text() const
        {
          if (textFlag == 0) // QLiE1
            return Engine::isAddressReadable(textAddress) ? textAddress : nullptr;
          else // QLiE2
            return textData;
        }

        // Return UnknownRole(0) if not sure
        Engine::TextRole role() const
        {
          if (textFlag > 0xff)
            return Engine::OtherRole;
          LPCSTR t = text();
          if (!t || !*t)
            return Engine::UnknownRole;
          for (int i = 0; t[i]; i++)
          {
            if (i > 0x40) // text too large
              return Engine::OtherRole;
            BYTE ch = t[0];
            if (ch <= 32 || ch > 127) // non-printable or not ascii
              return Engine::OtherRole;
          }

          // Convert to lower case
          std::string s = stolower(std::string(t));
          t = s.c_str();

          if (::strchr(t, '_'))
          {
            // QLiE2
            if (::strstr(t, "_imo_message,"))
              return Engine::ScenarioRole;
            if (::strstr(t, "_dialogmessage,"))
              return Engine::OtherRole;

            // QLiE1
            if (::strstr(t, "_messagetext,"))
              return Engine::ScenarioRole;

            if (::strstr(t, "_nametext,"))
              return Engine::NameRole;
            if (::strstr(t, "_message,") || // this is ambiguous and will overwrite imo_message
                ::strstr(t, "_statetext,") ||
                //::strstr(t, "_databutton,") ||
                //::strstr(t, "_selectbutton,") ||
                ::strstr(t, "button,"))
              return Engine::OtherRole;
          }

          if (s.find_first_of(".[!@*\\") != std::string::npos)
            return Engine::OtherRole;

          // DOUT("unknown text type:" << t);
          return Engine::UnknownRole;
        }
      };
      int trimmedSize;
      char *trimmedText;
      int endtype;
      void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
      {

        auto arg = (TextArgument *)(s->edx - 4);
        if (!arg->isValid())
          return;
        trimmedSize = arg->size;
        trimmedText = trim(arg->text, &trimmedSize);
        if (trimmedSize <= 0 || !trimmedText || !*trimmedText)
          return;

        if (::strstr(arg->text, "\x82\xa0\x82\xa0\x82\xa0\x82\xa0\x82\xa0")) /* Skip text containing あああああ */
          return;

        if (all_ascii(trimmedText)) // This is optional, but I don't want to translate English
          return;
        // role = Engine::OtherRole;

        enum
        {
          sig = 0
        };
        *role = Engine::ScenarioRole;

        enum : uint16_t
        {
          w_name_open = 0x7981, /* 【 */
          w_name_close = 0x7a81 /* 】 */
        };

        // if (trimmedText[trimmedSize]) // text ending withb ']' is other text
        //   *role = Engine::OtherRole;
        {
          std::string oldData(trimmedText, trimmedSize);
          endtype = 0;
          if (oldData.size() > 3 && oldData.substr(oldData.size() - 3) == "[n]")
          {
            endtype = 1;
            trimmedSize -= 3;
          }
          else if (oldData.size() > 3 && oldData.substr(oldData.size() - 3) == "[c]")
          {
            endtype = 2;
            trimmedSize -= 3;
          }
        }

        if (trimmedSize > 4 && w_name_open == *(uint16_t *)trimmedText && w_name_close == *(uint16_t *)(trimmedText + trimmedSize - 2))
        {
          trimmedText += 2;
          trimmedSize -= 4;
          if (*role == Engine::ScenarioRole)
            *role = Engine::NameRole; // FIXME: This name recognition logic does not work for ワルキューレロマンツェ
        }

        // Skip sjis 名前 = 96bc914f
        if (0 == ::strncmp(trimmedText, "\x96\xbc\x91\x4f", trimmedSize))
          return;
        /*
            if (s->stack[4] == s->stack[5]) { // && s->edi == s->stack[4]
              auto t = (TypeArgument *)s->stack[4];
              if (Engine::isAddressReadable(t)) {
                //if (!t->isValid())
                //  return true;
                if (auto r = t->role())
                  *role = r;
              }
            }
        */
        // auto split = s->stack[0]; // retaddr is always the same anyway

        buffer->from(trimmedText, trimmedSize);
      }
      void hookafter(hook_context *s, TextBuffer buffer, HookParam *)
      {
        std::string newData = buffer.strA();

        auto arg = (TextArgument *)(s->edx - 4);
        int prefixSize = trimmedText - arg->text,
            suffixSize = arg->size - prefixSize - trimmedSize;
        if (prefixSize)
          newData.insert(0, std::string(arg->text, prefixSize));
        if (suffixSize)
          newData.append(trimmedText + trimmedSize, suffixSize);
        if (endtype == 1)
          newData = newData + "[n]";
        else if (endtype == 2)
          newData = newData + "[c]";
        s->edx = (ULONG)allocateString(newData); // reset arg1
        *(DWORD *)(s->edx - 4) = newData.size();
        // arg->size = data_.size(); // no idea why this will crash ...

        //*(DWORD *)(s->edx - 4) = newData.size() + trimmedText - text;
        //::strcpy(trimmedText, newData.constData());
      }
    } // namespace Private

    /**
     *  Sample game: 月に寄りそう乙女の作法２
     *  See: http://capita.tistory.com/m/post/236
     *
     *  This function is not aligned.
     *  Text in edx. Length in [edx - 4]
     *
     *  00513234   55               PUSH EBP
     *  00513235   8BEC             MOV EBP,ESP
     *  00513237   6A 00            PUSH 0x0
     *  00513239   53               PUSH EBX
     *  0051323A   56               PUSH ESI
     *  0051323B   8BF2             MOV ESI,EDX
     *  0051323D   8BD8             MOV EBX,EAX
     *  0051323F   33C0             XOR EAX,EAX
     *  00513241   55               PUSH EBP
     *  00513242   68 AD325100      PUSH .005132AD
     *  00513247   64:FF30          PUSH DWORD PTR FS:[EAX]
     *  0051324A   64:8920          MOV DWORD PTR FS:[EAX],ESP
     *  0051324D   80BB 0A160000 00 CMP BYTE PTR DS:[EBX+0x160A],0x0 ; jichi: can be used as pattern to distinguish QLiE1/2
     *  00513254   74 07            JE SHORT .0051325D
     *  00513256   8BC3             MOV EAX,EBX
     *  00513258   8B10             MOV EDX,DWORD PTR DS:[EAX]
     *  0051325A   FF52 24          CALL DWORD PTR DS:[EDX+0x24]
     *  0051325D   8BC3             MOV EAX,EBX
     *  0051325F   E8 98C1FFFF      CALL .0050F3FC
     *  00513264   84C0             TEST AL,AL
     *  00513266   74 07            JE SHORT .0051326F
     *  00513268   8BC3             MOV EAX,EBX
     *  0051326A   8B10             MOV EDX,DWORD PTR DS:[EAX]
     *  0051326C   FF52 24          CALL DWORD PTR DS:[EDX+0x24]
     *  0051326F   8D4D FC          LEA ECX,DWORD PTR SS:[EBP-0x4]
     *  00513272   8BD6             MOV EDX,ESI
     *  00513274   8BC3             MOV EAX,EBX
     *  00513276   E8 5D310000      CALL .005163D8
     *  0051327B   8B55 FC          MOV EDX,DWORD PTR SS:[EBP-0x4]
     *  0051327E   8BC3             MOV EAX,EBX
     *  00513280   E8 1B100000      CALL .005142A0
     *  00513285   8BC3             MOV EAX,EBX
     *  00513287   E8 5C300000      CALL .005162E8
     *  0051328C   85C0             TEST EAX,EAX
     *  0051328E   75 07            JNZ SHORT .00513297
     *  00513290   8BC3             MOV EAX,EBX
     *  00513292   E8 B1070000      CALL .00513A48
     *  00513297   33C0             XOR EAX,EAX
     *  00513299   5A               POP EDX
     *  0051329A   59               POP ECX
     *  0051329B   59               POP ECX
     *  0051329C   64:8910          MOV DWORD PTR FS:[EAX],EDX
     *  0051329F   68 B4325100      PUSH .005132B4
     *  005132A4   8D45 FC          LEA EAX,DWORD PTR SS:[EBP-0x4]
     *  005132A7   E8 F421EFFF      CALL .004054A0
     *  005132AC   C3               RETN
     *  005132AD  ^E9 A21AEFFF      JMP .00404D54
     *  005132B2  ^EB F0            JMP SHORT .005132A4
     *  005132B4   5E               POP ESI
     *  005132B5   5B               POP EBX
     *  005132B6   59               POP ECX
     *  005132B7   5D               POP EBP
     *  005132B8   C3               RETN
     *  005132B9   8D40 00          LEA EAX,DWORD PTR DS:[EAX]
     *  005132BC   55               PUSH EBP
     *  005132BD   8BEC             MOV EBP,ESP
     *  005132BF   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
     *  005132C2   8B40 FC          MOV EAX,DWORD PTR DS:[EAX-0x4]
     *  005132C5   80B8 6F180000 00 CMP BYTE PTR DS:[EAX+0x186F],0x0
     *  005132CC   74 23            JE SHORT .005132F1
     *  005132CE   A1 C8EA5700      MOV EAX,DWORD PTR DS:[0x57EAC8]
     *  005132D3   8B80 FC020000    MOV EAX,DWORD PTR DS:[EAX+0x2FC]
     *  005132D9   8B15 C8EA5700    MOV EDX,DWORD PTR DS:[0x57EAC8]          ; .00586178
     *  005132DF   8B92 E8020000    MOV EDX,DWORD PTR DS:[EDX+0x2E8]
     *  005132E5   3BD0             CMP EDX,EAX
     *  005132E7   7C 02            JL SHORT .005132EB
     *  005132E9   8BC2             MOV EAX,EDX
     *  005132EB   0105 B8E45700    ADD DWORD PTR DS:[0x57E4B8],EAX
     *  005132F1   5D               POP EBP
     *  005132F2   C3               RETN
     *  005132F3   90               NOP
     *  005132F4   55               PUSH EBP
     *  005132F5   8BEC             MOV EBP,ESP
     *  005132F7   53               PUSH EBX
     *  005132F8   8B5D 08          MOV EBX,DWORD PTR SS:[EBP+0x8]
     *  ...
     *
     *  {00528988(E9 73 FC 04 00 90),00578600(8D 45 FC 8B 4D FC 66 81 39 81 79 74 05 90 90 90 90 90 E9 77 03 FB FF)}
     *  {00528988(E9 73 FC 04 00 90),005785FE(EB 27 8D 45 FC 8B 4D FC 66 81 39 81 79 74 0A 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 68 8E 89 52 00 C3)}
     *
     *  FORCEFONT(5),FONT(Gulim,-13),ENCODEKOR,HOOK(0x00513234,TRANS(EDX,LEN(-4),PTRCHEAT),RETNPOS(COPY)),HOOK(0x0057860D,TRANS(ECX,LEN(-4),PTRCHEAT),RETNPOS(SOURCE))
     *
     *  Character handled here, which is not used:
     *  00528969   74 28            JE SHORT .00528993
     *  0052896B   3C 09            CMP AL,0x9
     *  0052896D   74 24            JE SHORT .00528993
     *  0052896F   3C 2F            CMP AL,0x2F
     *  00528971   74 20            JE SHORT .00528993
     *  00528973   3C 40            CMP AL,0x40
     *  00528975   74 1C            JE SHORT .00528993
     *  00528977   8D45 E8          LEA EAX,DWORD PTR SS:[EBP-0x18]
     *  0052897A   8D93 49010000    LEA EDX,DWORD PTR DS:[EBX+0x149]
     *  00528980   E8 7FCDEDFF      CALL .00405704
     *  00528985   8B55 E8          MOV EDX,DWORD PTR SS:[EBP-0x18]
     *  00528988   8D45 FC          LEA EAX,DWORD PTR SS:[EBP-0x4]  ; jichi: 2-byte character in ecx
     *  0052898B   8B4D FC          MOV ECX,DWORD PTR SS:[EBP-0x4]
     *  0052898E   E8 25CEEDFF      CALL .004057B8
     *  00528993   8D83 4C020000    LEA EAX,DWORD PTR DS:[EBX+0x24C]
     *  00528999   8B55 FC          MOV EDX,DWORD PTR SS:[EBP-0x4]
     *  0052899C   E8 53CBEDFF      CALL .004054F4
     *  005289A1   8B83 4C020000    MOV EAX,DWORD PTR DS:[EBX+0x24C]
     *  005289A7   85C0             TEST EAX,EAX
     *  005289A9   74 05            JE SHORT .005289B0
     *  005289AB   83E8 04          SUB EAX,0x4
     *  005289AE   8B00             MOV EAX,DWORD PTR DS:[EAX]
     *  005289B0   8983 50020000    MOV DWORD PTR DS:[EBX+0x250],EAX
     *  005289B6   C645 F7 01       MOV BYTE PTR SS:[EBP-0x9],0x1
     *  005289BA   33C0             XOR EAX,EAX
     *  005289BC   5A               POP EDX
     *  005289BD   59               POP ECX
     *  005289BE   59               POP ECX
     *  005289BF   64:8910          MOV DWORD PTR FS:[EAX],EDX
     *  005289C2   68 E4895200      PUSH .005289E4
     *  005289C7   8D45 E8          LEA EAX,DWORD PTR SS:[EBP-0x18]
     *  005289CA   BA 03000000      MOV EDX,0x3
     *  005289CF   E8 F0CAEDFF      CALL .004054C4
     *  005289D4   8D45 FC          LEA EAX,DWORD PTR SS:[EBP-0x4]
     *  005289D7   E8 C4CAEDFF      CALL .004054A0
     *  005289DC   C3               RETN
     *  005289DD  ^E9 72C3EDFF      JMP .00404D54
     *  005289E2  ^EB E3            JMP SHORT .005289C7
     *  005289E4   0FB645 F7        MOVZX EAX,BYTE PTR SS:[EBP-0x9]
     *  005289E8   5F               POP EDI
     *  005289E9   5E               POP ESI
     *  005289EA   5B               POP EBX
     *  005289EB   8BE5             MOV ESP,EBP
     *  005289ED   5D               POP EBP
     *  005289EE   C3               RETN
     *  005289EF   90               NOP
     *  005289F0   55               PUSH EBP
     *  005289F1   8BEC             MOV EBP,ESP
     *  005289F3   83C4 F8          ADD ESP,-0x8
     *  005289F6   53               PUSH EBX
     *
     *  Sample game: ワルキューレロマンツェ (QLiE1)
     *
     *  This function is found by looking all all matches of the following pattern
     *  And then lookup up for push ebp
     *  005132E5   3BD0             CMP EDX,EAX
     *  005132E7   7C 02            JL SHORT .005132EB
     *  005132E9   8BC2             MOV EAX,EDX
     *
     *  004FFB04   55               PUSH EBP
     *  004FFB05   8BEC             MOV EBP,ESP
     *  004FFB07   6A 00            PUSH 0x0
     *  004FFB09   53               PUSH EBX
     *  004FFB0A   56               PUSH ESI
     *  004FFB0B   8BF2             MOV ESI,EDX
     *  004FFB0D   8BD8             MOV EBX,EAX
     *  004FFB0F   33C0             XOR EAX,EAX
     *  004FFB11   55               PUSH EBP
     *  004FFB12   68 7DFB4F00      PUSH .004FFB7D
     *  004FFB17   64:FF30          PUSH DWORD PTR FS:[EAX]
     *  004FFB1A   64:8920          MOV DWORD PTR FS:[EAX],ESP
     *  004FFB1D   80BB FA150000 00 CMP BYTE PTR DS:[EBX+0x15FA],0x0
     *  004FFB24   74 07            JE SHORT .004FFB2D
     *  004FFB26   8BC3             MOV EAX,EBX
     *  004FFB28   8B10             MOV EDX,DWORD PTR DS:[EAX]
     *  004FFB2A   FF52 1C          CALL DWORD PTR DS:[EDX+0x1C]
     *  004FFB2D   8BC3             MOV EAX,EBX
     *  004FFB2F   E8 04CFFFFF      CALL .004FCA38
     *  004FFB34   84C0             TEST AL,AL
     *  004FFB36   74 07            JE SHORT .004FFB3F
     *  004FFB38   8BC3             MOV EAX,EBX
     *  004FFB3A   8B10             MOV EDX,DWORD PTR DS:[EAX]
     *  004FFB3C   FF52 1C          CALL DWORD PTR DS:[EDX+0x1C]
     *  004FFB3F   8D4D FC          LEA ECX,DWORD PTR SS:[EBP-0x4]
     *  004FFB42   8BD6             MOV EDX,ESI
     *  004FFB44   8BC3             MOV EAX,EBX
     *  004FFB46   E8 69320000      CALL .00502DB4
     *  004FFB4B   8B55 FC          MOV EDX,DWORD PTR SS:[EBP-0x4]
     *  004FFB4E   8BC3             MOV EAX,EBX
     *  004FFB50   E8 23120000      CALL .00500D78
     *  004FFB55   8BC3             MOV EAX,EBX
     *  004FFB57   E8 58310000      CALL .00502CB4
     *  004FFB5C   85C0             TEST EAX,EAX
     *  004FFB5E   75 07            JNZ SHORT .004FFB67
     *  004FFB60   8BC3             MOV EAX,EBX
     *  004FFB62   E8 5D070000      CALL .005002C4
     *  004FFB67   33C0             XOR EAX,EAX
     *  004FFB69   5A               POP EDX
     *  004FFB6A   59               POP ECX
     *  004FFB6B   59               POP ECX
     *  004FFB6C   64:8910          MOV DWORD PTR FS:[EAX],EDX
     *  004FFB6F   68 84FB4F00      PUSH .004FFB84
     *  004FFB74   8D45 FC          LEA EAX,DWORD PTR SS:[EBP-0x4]
     *  004FFB77   E8 5859F0FF      CALL .004054D4
     *  004FFB7C   C3               RETN
     *  004FFB7D  ^E9 0652F0FF      JMP .00404D88
     *  004FFB82  ^EB F0            JMP SHORT .004FFB74
     *  004FFB84   5E               POP ESI
     *  004FFB85   5B               POP EBX
     *  004FFB86   59               POP ECX
     *  004FFB87   5D               POP EBP
     *  004FFB88   C3               RETN
     *  004FFB89   8D40 00          LEA EAX,DWORD PTR DS:[EAX]
     *  004FFB8C   55               PUSH EBP
     *  004FFB8D   8BEC             MOV EBP,ESP
     *  004FFB8F   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
     *  004FFB92   8B40 FC          MOV EAX,DWORD PTR DS:[EAX-0x4]
     *  004FFB95   80B8 4F180000 00 CMP BYTE PTR DS:[EAX+0x184F],0x0
     *  004FFB9C   74 23            JE SHORT .004FFBC1
     *  004FFB9E   A1 E4CA5600      MOV EAX,DWORD PTR DS:[0x56CAE4]
     *  004FFBA3   8B80 CC020000    MOV EAX,DWORD PTR DS:[EAX+0x2CC]
     *  004FFBA9   8B15 E4CA5600    MOV EDX,DWORD PTR DS:[0x56CAE4]          ; .005740E8
     *  004FFBAF   8B92 B8020000    MOV EDX,DWORD PTR DS:[EDX+0x2B8]
     *  004FFBB5   3BD0             CMP EDX,EAX
     *  004FFBB7   7C 02            JL SHORT .004FFBBB
     *  004FFBB9   8BC2             MOV EAX,EDX
     *  004FFBBB   0105 64C45600    ADD DWORD PTR DS:[0x56C464],EAX
     *  004FFBC1   5D               POP EBP
     *  004FFBC2   C3               RETN
     *  004FFBC3   90               NOP
     */
    bool attach(ULONG startAddress, ULONG stopAddress)
    {
      // QLiE1
      // 004FFB1D   80BB FA150000 00 CMP BYTE PTR DS:[EBX+0x15FA],0x0
      // QLiE2
      // 0051324D   80BB 0A160000 00 CMP BYTE PTR DS:[EBX+0x160A],0x0 ; jichi: instruction used as pattern

      const uint8_t bytes[] = {
          // i.e. 3BD0 7C 02 8BC2 0105
          0x3B, 0xD0, // 004FFBB5   3BD0             CMP EDX,EAX
          0x7C, 0x02, // 004FFBB7   7C 02            JL SHORT .004FFBBB
          0x8B, 0xC2, // 004FFBB9   8BC2             MOV EAX,EDX
          0x01, 0x05  // 64C45600    // 004FFBBB   0105 64C45600    ADD DWORD PTR DS:[0x56C464],EAX
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return false;
      // 00513234   55               PUSH EBP   ; jichi: hook here
      // 00513235   8BEC             MOV EBP,ESP
      // 00513237   6A 00            PUSH 0x0
      // 00513239   53               PUSH EBX
      // 0051323A   56               PUSH ESI
      enum : DWORD
      {
        sig = 0x6aec8b55
      };
      enum
      {
        AlignedStep = 1
      }; // function not aligned
      addr = MemDbg::findEnclosingFunctionBeforeDword(sig, addr, MemDbg::MaximumFunctionSize, AlignedStep);
      if (!addr)
        return false;
      HookParam hp;
      hp.address = addr;
      hp.text_fun = Private::hookBefore;
      hp.embed_fun = Private::hookafter;
      hp.lineSeparator = L"[n]";
      hp.type = EMBED_ABLE | EMBED_DYNA_SJIS | USING_STRING | NO_CONTEXT;
      hp.embed_hook_font = F_ExtTextOutA | F_GetTextExtentPoint32A;
      hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
      {
        buffer->from(re::sub(buffer->strA(), "\\[rb,(.*?),.+\\]", "$1"));
      };
      return NewHook(hp, "EmbedQLIE");
    }

  } // namespace ScenarioHook

} // unnamed namespace

bool QLIE::attach_function()
{
  auto embed = ScenarioHook::attach(processStartAddress, processStopAddress);
  return InsertQLIEHook() || embed;
}