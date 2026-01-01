#include "Yuris.h"
/********************************************************************************************
YU-RIS hook:
  Becomes common recently. I first encounter this game in Whirlpool games.
  Problem is name is repeated multiple times.
  Step out of function call to TextOuA, just before call to this function,
  there should be a piece of code to calculate the length of the name.
  This length is 2 for single character name and text,
  For a usual name this value is greater than 2.
********************************************************************************************/

// bool InsertWhirlpoolHook() // jichi: 12/27/2014: Renamed to YU-RIS
bool Yuris::InsertYuris1Hook()
{
  // IthBreak();
  DWORD entry = Util::FindCallAndEntryBoth((DWORD)TextOutA, processStopAddress - processStartAddress, processStartAddress, 0xec83);
  // GROWL_DWORD(entry);
  if (!entry)
  {
    ConsoleOutput("YU-RIS: function entry does not exist");
    return false;
  }
  entry = Util::FindCallAndEntryRel(entry - 4, processStopAddress - processStartAddress, processStartAddress, 0xec83);
  // GROWL_DWORD(entry);
  if (!entry)
  {
    ConsoleOutput("YU-RIS: function entry does not exist");
    return false;
  }
  entry = Util::FindCallOrJmpRel(entry - 4, processStopAddress - processStartAddress - 0x10000, processStartAddress + 0x10000, false);
  DWORD i,
      t = 0;
  // GROWL_DWORD(entry);
  __try
  { // jichi 12/27/2014
    for (i = entry - 4; i > entry - 0x100; i--)
      if (::IsBadReadPtr((LPCVOID)i, 4))
      { // jichi 12/27/2014: might raise in new YU-RIS, 4 = sizeof(DWORD)
        ConsoleOutput("YU-RIS: do not have read permission");
        return false;
      }
      else if (*(WORD *)i == 0xc085)
      {
        t = *(WORD *)(i + 2);
        if ((t & 0xff) == 0x76)
        {
          t = 4;
          break;
        }
        else if ((t & 0xffff) == 0x860f)
        {
          t = 8;
          break;
        }
      }
  }
  __except (EXCEPTION_EXECUTE_HANDLER)
  {
    ConsoleOutput("YU-RIS: illegal access exception");
    return false;
  }
  if (i == entry - 0x100)
  {
    ConsoleOutput("YU-RIS: pattern not exist");
    return false;
  }
  // GROWL_DWORD2(i,t);
  HookParam hp;
  hp.address = i + t;
  hp.offset = regoffset(edi);
  hp.split = regoffset(eax);
  hp.type = USING_STRING | USING_SPLIT;
  ConsoleOutput("INSERT YU-RIS");
  // GROWL_DWORD(hp.address);
  return NewHook(hp, "YU-RIS");
}

/** jichi 12/27/2014
 *
 *  Sample game: [Whirlpool] [150217] 鯨神�ヂ�アスヂ�ラ
 *  Call site of TextOutA.
 *  00441811   90               nop
 *  00441812   90               nop
 *  00441813   90               nop
 *  00441814   8b4424 04        mov eax,dword ptr ss:[esp+0x4]
 *  00441818   8b5424 08        mov edx,dword ptr ss:[esp+0x8]
 *  0044181c   8b4c24 0c        mov ecx,dword ptr ss:[esp+0xc]
 *  00441820   57               push edi
 *  00441821   56               push esi
 *  00441822   55               push ebp
 *  00441823   53               push ebx
 *  00441824   83ec 50          sub esp,0x50
 *  00441827   8bf9             mov edi,ecx
 *  00441829   897c24 1c        mov dword ptr ss:[esp+0x1c],edi
 *  0044182d   8bda             mov ebx,edx
 *  0044182f   8be8             mov ebp,eax
 *  00441831   8b349d 603f7b00  mov esi,dword ptr ds:[ebx*4+0x7b3f60]
 *  00441838   807c24 74 01     cmp byte ptr ss:[esp+0x74],0x1
 *  0044183d   b9 00000000      mov ecx,0x0
 *  00441842   0f94c1           sete cl
 *  00441845   8d041b           lea eax,dword ptr ds:[ebx+ebx]
 *  00441848   03c3             add eax,ebx
 *  0044184a   0fafc1           imul eax,ecx
 *  0044184d   03c3             add eax,ebx
 *  0044184f   894424 0c        mov dword ptr ss:[esp+0xc],eax
 *  00441853   897424 10        mov dword ptr ss:[esp+0x10],esi
 *  00441857   8bc3             mov eax,ebx
 *  00441859   8bd7             mov edx,edi
 *  0044185b   0fbe4c24 70      movsx ecx,byte ptr ss:[esp+0x70]
 *  00441860   e8 0c030000      call .00441b71
 *  00441865   0fbec8           movsx ecx,al
 *  00441868   83f9 ff          cmp ecx,-0x1
 *  0044186b   0f84 db020000    je .00441b4c
 *  00441871   8bce             mov ecx,esi
 *  00441873   0fafc9           imul ecx,ecx
 *  00441876   a1 64365d00      mov eax,dword ptr ds:[0x5d3664]
 *  0044187b   8bf9             mov edi,ecx
 *  0044187d   c1ff 02          sar edi,0x2
 *  00441880   c1ef 1d          shr edi,0x1d
 *  00441883   03f9             add edi,ecx
 *  00441885   c1ff 03          sar edi,0x3
 *  00441888   68 ff000000      push 0xff
 *  0044188d   57               push edi
 *  0044188e   ff3485 70b48300  push dword ptr ds:[eax*4+0x83b470]
 *  00441895   ff15 a4355d00    call dword ptr ds:[0x5d35a4]             ; .00401c88
 *  0044189b   83c4 0c          add esp,0xc
 *  0044189e   8b0d 64365d00    mov ecx,dword ptr ds:[0x5d3664]
 *  004418a4   ff348d b4b48300  push dword ptr ds:[ecx*4+0x83b4b4]
 *  004418ab   ff348d d4b48300  push dword ptr ds:[ecx*4+0x83b4d4]
 *  004418b2   ff15 54e05800    call dword ptr ds:[0x58e054]             ; gdi32.selectobject
 *  004418b8   a3 b0b48300      mov dword ptr ds:[0x83b4b0],eax
 *  004418bd   8b0d 64365d00    mov ecx,dword ptr ds:[0x5d3664]
 *  004418c3   ff348d 30b48300  push dword ptr ds:[ecx*4+0x83b430]
 *  004418ca   ff348d d4b48300  push dword ptr ds:[ecx*4+0x83b4d4]
 *  004418d1   ff15 54e05800    call dword ptr ds:[0x58e054]             ; gdi32.selectobject
 *  004418d7   a3 2cb48300      mov dword ptr ds:[0x83b42c],eax
 *  004418dc   8b3d 64365d00    mov edi,dword ptr ds:[0x5d3664]
 *  004418e2   33c9             xor ecx,ecx
 *  004418e4   880cbd f5b48300  mov byte ptr ds:[edi*4+0x83b4f5],cl
 *  004418eb   880cbd f6b48300  mov byte ptr ds:[edi*4+0x83b4f6],cl
 *  004418f2   0fb64d 00        movzx ecx,byte ptr ss:[ebp]
 *  004418f6   0fb689 a0645b00  movzx ecx,byte ptr ds:[ecx+0x5b64a0]
 *  004418fd   41               inc ecx
 *  004418fe   0fbec9           movsx ecx,cl
 *  00441901   51               push ecx
 *  00441902   55               push ebp
 *  00441903   33c9             xor ecx,ecx
 *  00441905   51               push ecx
 *  00441906   51               push ecx
 *  00441907   ff34bd d4b48300  push dword ptr ds:[edi*4+0x83b4d4]
 *  0044190e   ff15 74e05800    call dword ptr ds:[0x58e074]             ; gdi32.textouta, jichi: TextOutA here
 *  00441914   0fb67d 00        movzx edi,byte ptr ss:[ebp]
 *  00441918   0fb68f a0645b00  movzx ecx,byte ptr ds:[edi+0x5b64a0]
 *  0044191f   41               inc ecx
 *  00441920   0fbef9           movsx edi,cl
 *  00441923   8b0d 64365d00    mov ecx,dword ptr ds:[0x5d3664]
 *  00441929   03c9             add ecx,ecx
 *  0044192b   8d8c09 f4b48300  lea ecx,dword ptr ds:[ecx+ecx+0x83b4f4]
 *
 *  Runtime stack: The first dword after arguments on the stack seems to be good split value.
 */
bool Yuris::InsertYuris2Hook()
{
  ULONG addr = MemDbg::findCallAddress((ULONG)::TextOutA, processStartAddress, processStopAddress);
  if (!addr)
  {
    ConsoleOutput("YU-RIS2: failed");
    return false;
  }

  // BOOL TextOut(
  //   _In_  HDC hdc,
  //   _In_  int nXStart,
  //   _In_  int nYStart,
  //   _In_  LPCTSTR lpString,
  //   _In_  int cchString
  // );
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING | USING_SPLIT | NO_CONTEXT; // disable context that will cause thread split
  hp.offset = stackoffset(3);
  hp.split = stackoffset(5);

  ConsoleOutput("INSERT YU-RIS 2");
  return NewHook(hp, "YU-RIS2");
}

bool Yuris::InsertYuris4Hook()
{

  /*
   * Sample games:
   * https://vndb.org/v6540
   */
  bool found = false;
  const BYTE pattern[] = {
      0x52,                               // 52               push edx
      0x68, 0x00, 0x42, 0x5C, 0x00,       // 68 00425C00      push euphoria.exe+1C4200
      0xFF, 0x15, 0x90, 0x44, 0x7E, 0x00, // FF 15 90447E00   call dword ptr [euphoria.exe+3E4490]
      0x83, 0xC4, 0x0C,                   // 83 C4 0C         add esp,0C
      0xEB, 0x5F,                         // EB 5F            jmp euphoria.exe+4F4C5
      0xFF, 0x35, 0xA4, 0x19, 0x66, 0x00, // FF 35 A4196600   push [euphoria.exe+2619A4]
      0x52                                // 52               push edx
  };
  enum
  {
    addr_offset = 12
  }; // distance to the beginning of the function, which is 0x83, 0xC4, 0x0C (add esp,0C)

  for (auto addr : Util::SearchMemory(pattern, sizeof(pattern), PAGE_EXECUTE, processStartAddress, processStopAddress))
  {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.offset = regoffset(edx);
    hp.type = USING_STRING;
    ConsoleOutput("INSERT YU-RIS 4");
    found |= NewHook(hp, "YU-RIS4");
  }
  return found;
}

bool Yuris::InsertYuris5Hook()
{

  /*
   * Sample games:
   * https://vndb.org/v4037
   */
  const BYTE bytes[] = {
      0x33, 0xD2,       // xor edx,edx
      0x88, 0x14, 0x0F, // mov [edi+ecx],dl
      0xA1, XX4,        // mov eax,[exe+2DE630]
      0x8B, 0x78, 0x3C, // mov edi,[eax+3C]
      0x8B, 0x58, 0x5C, // mov ebx,[eax+5C]
      0x88, 0x14, 0x3B  // mov [ebx+edi],dl
  };

  enum
  {
    addr_offset = 0
  }; // distance to the beginning of the function, which is 0x55 (push ebp)
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr + addr_offset;
  hp.offset = regoffset(ecx);
  hp.type = USING_STRING | NO_CONTEXT;

  ConsoleOutput("INSERT YU-RIS 5");
  return NewHook(hp, "YU-RIS5");
}

static void Yuris6Filter(TextBuffer *buffer, HookParam *hp)
{
  static std::string last;
  if (last == buffer->viewA())
    return buffer->clear();
  last = buffer->viewA();

  if (hp->codepage == CP_UTF8 || hp->type & CODEC_UTF8)
  {
    buffer->from(re::sub(buffer->strA(), u8R"(≪(.*?)／(.*?)≫)", "$1"));
    buffer->from(re::sub(buffer->strA(), u8R"(＜(.*?)／(.*?)＞)", "$1"));
  }
  else
  {
    buffer->from(re::sub(buffer->strA(), R"(\x81\x83(.*?)\x81\x5E(.*?)\x81\x84)", "$1"));
    buffer->from(re::sub(buffer->strA(), R"(\x81\xE1(.*?)\x81\x5E(.*?)\x81\xE2)", "$1"));

    CharReplacer(buffer, '=', '-');
    StringFilter(buffer, TEXTANDLEN("\xEF\xF0"));
    StringFilter(buffer, TEXTANDLEN("\xEF\xF1"));
    StringFilter(buffer, TEXTANDLEN("\xEF\xF2"));
    StringFilter(buffer, TEXTANDLEN("\xEF\xF3"));
    StringFilter(buffer, TEXTANDLEN("\xEF\xF4"));
    StringFilter(buffer, TEXTANDLEN("\xEF\xF5"));
    StringFilter(buffer, TEXTANDLEN("\x81\x98"));
  }
}
bool Yuris::InsertYuris6Hook()
{

  /*
   * work with Windows 11
   * Sample games:
   * https://vndb.org/v40058
   * https://vndb.org/v42883
   * https://vndb.org/v44092
   * https://vndb.org/v21171
   * https://vndb.org/r46910
   */
  const BYTE bytes[] = {
      0xE9, XX4,  // jmp oshitona01.exe+1B629     << hook here
      0xBF, XX4,  // mov edi,oshitona01.exe+24EEA0
      0x8A, 0x17, // mov dl,[edi]
      0x47,       // inc edi
      0x88, 0x16, // mov [esi],dl
      0x46,       // inc esi
      0x84, 0xD2  // test dl,dl
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;
  BYTE checkbefore[] = {
      0x8b, 0x78, XX,
      0x8a, 0x17,
      0x47,
      0x88, 0x16,
      0x46,
      0x84, 0xd2,
      0x75, 0xf6};
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(eax);
  hp.index = 0x38;
  if (MatchPattern(addr - sizeof(checkbefore), checkbefore, sizeof(checkbefore)))
  {
    hp.index = *(BYTE *)(addr - sizeof(checkbefore) + 2);
  }
  hp.filter_fun = Yuris6Filter;
  hp.type = USING_STRING | NO_CONTEXT | DATA_INDIRECT;
  hp.codepage = codepage;
  return NewHook(hp, "YU-RIS6");
}
bool Yuris::yuris7()
{
  // 猫忍えくすはーとSPIN!
  // 夏空あすてりずむ

  // https://vndb.org/r111807
  //[210924][1139364][Liquid] 黒獣2改 ～淫欲に染まる背徳の都、再び～ 多国語版 Chinese-English DL版 (files)
  const BYTE bytes[] = {
      0x57, 0x56, 0x55, 0x53, 0x83, 0xec, 0x10,
      0x8b, 0x5c, 0x24, 0x24,
      0x8b, 0x15, XX4,
      0x8b, 0x0c, 0x9a,
      0xc6, 0x41, 0x01, 0x03,
      0x8b, 0xc3,
      0xe8};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(edx);
  hp.type = USING_STRING;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    if (context->edi > 0x100)
      return;
    // if(context->eax==1)return;
    if (context->edi < 0x60 || context->edi > 0x80)
      return;
    if (strlen((char *)context->edx) > 2)
      return;
    if (strcmp((char *)context->edx, "BG") == 0 || strcmp((char *)context->edx, "VO") == 0)
      return;

    *split = context->edi; //|(context->eax*0x100);//会把人名的引号分开
    buffer->from(context->edx, min(2, strlen((char *)context->edx)));
  };
  hp.codepage = codepage;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    auto text = buffer->viewA();
    if (std::all_of(text.begin(), text.end(), [](char c)
                    { return c == '1' || c == '2' || c == 'E' || c == 'C' || c == 'c' || c == 'R' || c == 'B' || c == 'P' || c == 'Z'; }))
      return buffer->clear();
  };
  return NewHook(hp, "yuris7");
}
bool Yuris::yuris8()
{
  // けもの道☆ガーリッシュスクエア LOVE+PLUS
  // https://vndb.org/v36773
  // codepage 950
  const BYTE bytes[] = {
      0x8b, XX,
      0x8b, 0x94, 0x24, XX, 0, 0, 0,
      0x8b, 0x8c, 0x24, XX, 0, 0, 0,
      0xe8, XX4,
      0xeb, XX,
      0x8b, XX,
      0x8b, 0x94, 0x24, XX, 0, 0, 0,
      0x8b, 0x8c, 0x24, XX, 0, 0, 0,
      0xe8, XX4};
  const BYTE bytes2[] = {
      0x8b, XX,
      0x8b, 0x94, 0x24, XX, 0, 0, 0,
      0x8b, 0x8c, 0x24, XX, 0, 0, 0,
      0xe8, XX4,
      0xeb, XX,
      0x8b, XX,
      0x8b, XX,
      0x8b, 0x8c, 0x24, XX, 0, 0, 0,
      0xe8, XX4};
  // 这两个E8调用的同一个函数，上面的那个更全一点，下面的这个有的会漏。不过无所谓了，其他钩子关于，就不改这个了。
  int offset = sizeof(bytes) - 5;
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
  {
    addr = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
    offset = sizeof(bytes2) - 5;
  }
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr + offset;
  hp.type = USING_STRING;
  hp.offset = regoffset(ecx);
  hp.codepage = codepage;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    auto text = buffer->viewA();
    if (std::all_of(text.begin(), text.end(), [](char c)
                    { return c == '1' || c == '2' || c == 'E' || c == 'C' || c == 'c' || c == 'R' || c == 'B' || c == 'P' || c == 'Z'; }))
      return buffer->clear();
  };
  auto calltarget = addr + offset + 5 + *(int *)(addr + offset + 1);
  auto yuris9 = [&]()
  {
    // 竜姫ぐーたらいふ 2 & 3 官方英文+繁中版
    // yuris8无法捕获旁白
    /*
.text:00453460 85 C9                                         test    ecx, ecx
.text:00453462 74 12                                         jz      short loc_453476
.text:00453464 8B C5                                         mov     eax, ebp
.text:00453466 8B 94 24 AC 00 00 00                          mov     edx, [esp+0CCh+var_20]
.text:0045346D 8B CE                                         mov     ecx, esi
<----- 在这里也可以
.text:0045346F E8 84 85 00 00                                call    sub_45B9F8
.text:00453474 EB 10                                         jmp     short loc_453486
.text:00453476                               ; ---------------------------------------------------------------------------
.text:00453476
.text:00453476                               loc_453476:                             ; CODE XREF: sub_453178+2EA↑j
.text:00453476 8B C3                                         mov     eax, ebx
.text:00453478 8B 94 24 B0 00 00 00                          mov     edx, [esp+0CCh+var_1C]
.text:0045347F 8B CE                                         mov     ecx, esi
.text:00453481 E8 72 85 00 00                                call    sub_45B9F8
    */
    HookParam hp;
    hp.address = calltarget;
    hp.type = USING_STRING | NO_CONTEXT | FULL_STRING;
    hp.offset = regoffset(ecx);
    hp.codepage = codepage;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      // 会把双语都提取出来。
      // 调用频率过高，不要用filter_fun，不然会疯狂拷贝
      std::string_view text = (char *)context->ecx;
      if (text.size() <= 2)
        return;
      if (text[0] != '"' && text[text.size() - 1] != '"')
        return;
      static lru_cache<std::string> cache(4);
      if (cache.touch(std::string(text)))
        return;
      buffer->from(text.substr(1, text.size() - 2));
    };
    return NewHook(hp, "yuris9");
  };
  return NewHook(hp, "yuris8") && yuris9();
}
UINT Yuris::codepagechecker()
{
  auto wcmb = Util::FindImportEntry(processStartAddress, (DWORD)WideCharToMultiByte);
  if (!wcmb)
    return false;
  // 国际版会有一个wcmb(932)的调用，日文版没有
  BYTE check[] = {
      0x68, 0xA4, 0x03, 0x00, 0x00,
      0xff, 0x15, XX4};
  *(int *)(check + 5 + 2) = wcmb;
  if (!MemDbg::findBytes(check, sizeof(check), processStartAddress, processStopAddress))
    return 0;
  return CP_UTF8;
}
bool Yuris::attach_function()
{
  codepage = codepagechecker();
  bool ok = InsertYuris1Hook();
  ok = InsertYuris2Hook() || ok;
  ok = InsertYuris4Hook() || ok;
  ok = InsertYuris5Hook() || ok;
  ok = InsertYuris6Hook() || ok;
  ok = yuris7() || ok;
  ok = yuris8() || ok;
  return ok;
}