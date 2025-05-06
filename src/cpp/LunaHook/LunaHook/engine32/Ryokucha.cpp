#include "Ryokucha.h"
static void SpecialHookRyokucha(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  for (DWORD i = 1; i < 5; i++)
  {
    DWORD j = context->stack[i];
    if ((j >> 16) == 0 && (j >> 8))
    {
      hp->offset = i << 2;
      buffer->from_t<WORD>(j);
      // hp->type &= ~EXTERN_HOOK;
      hp->text_fun = nullptr;
      return;
    }
  }
}
bool InsertRyokuchaDynamicHook(LPVOID addr, hook_context *)
{
  if (addr != ::GetGlyphOutlineA)
    return false;

  auto tib = (NT_TIB *)__readfsdword(0);
  auto exception = tib->ExceptionList;
  for (int i = 0; i < 1; i++)
  {
    exception = exception->Next;
  }
  auto handler = (DWORD)exception->Handler;
  auto ptr = *(DWORD *)((DWORD)exception + 0xC);
  auto insert_addr = ptr + *(DWORD *)(ptr - 4);
  auto flag = (*(DWORD *)(insert_addr + 3) == handler);

  if (flag)
  {
    HookParam hp;
    hp.address = insert_addr;
    hp.text_fun = SpecialHookRyokucha;
    hp.type = CODEC_ANSI_BE | USING_CHAR;
    ConsoleOutput("INSERT StudioRyokucha");
    return NewHook(hp, "StudioRyokucha");
  }
  // else ConsoleOutput("Unknown Ryokucha engine.");
  ConsoleOutput("StudioRyokucha: failed");
  return true;
}
void InsertRyokuchaHook()
{
  PcHooks::hookGDIFunctions();
  // ConsoleOutput("Probably Ryokucha. Wait for text.");
  trigger_fun = InsertRyokuchaDynamicHook;
  ConsoleOutput("TRIGGER Ryokucha");
}

/**
 *  jichi 1/10/2014: Rai7 puk
 *  See: http://www.hongfire.com/forum/showthread.php/421909-%E3%80%90Space-Warfare-Sim%E3%80%91Rai-7-PUK/page10
 *  See: www.hongfire.com/forum/showthread.php/421909-%E3%80%90Space-Warfare-Sim%E3%80%91Rai-7-PUK/page19
 *
 *  Version: R7P3-13v2(131220).rar, pass: sstm http://pan.baidu.com/share/home?uk=3727185265#category/type=0
 *  /HS0@409524
 */
// bool InsertRai7Hook()
//{
// }

/**
 *  jichi 10/1/2013: sol-fa-soft
 *  See (tryguy): http://www.hongfire.com/forum/printthread.php?t=36807&pp=10&page=639
 *
 *  @tryguy
 *  [sol-fa-soft]
 *  17 スク水不要� /HA4@4AD140
 *  18 ななちも�とぁ�しょ: /HA4@5104A0
 *  19 発惁�んこぁ�� /HA4@51D720
 *  20 わたし�たまごさ� /HA4@4968E0
 *  21 修学旡�夜更かし� /HA4@49DC00
 *  22 おぼえたてキヂ�: /HA4@49DDB0
 *  23 ちっさい巫女さんSOS: /HA4@4B4AA0
 *  24 はじめてのお�ろやさん: /HA4@4B5600
 *  25 はきわすれ愛好� /HA4@57E360
 *  26 朝っぱらから発惮�� /HA4@57E360
 *  27 となり�ヴァンパイア: /HA4@5593B0
 *  28 麦わら帽子と水辺の妖精: /HA4@5593B0
 *  29 海と温泉と夏休み: /HA4@6DE8E0
 *  30 駏�子屋さん繁盛� /HA4@6DEC90
 *  31 浴衣の下�… �神社で発見�ノ�パン少女 /HA4@6DEC90
 *  32 プ�ルのじか�スク水不要�: /HA4@62AE10
 *  33 妹のお泊まり� /HA4@6087A0
 *  34 薝�少女: /HA4@6087A0
 *  35 あや�Princess Intermezzo: /HA4@609BF0
 *
 *  SG01 男湯�: /HA4@6087A0
 *
 *  c71 真�の大晦日CD: /HA4@516b50
 *  c78 sol-fa-soft真夏�お気楽CD: /HA4@6DEC90
 *
 *  Example: 35 あや�Princess Intermezzo: /HA4@609BF0
 *  - addr: 6331376 = 0x609bf0
 *  - length_offset: 1
 *  - off: 4
 *  - type: 4
 *
 *  ASCII: あや� addr_offset = -50
 *  Function starts
 *  00609bef  /> cc             int3
 *  00609bf0  /> 55             push ebp
 *  00609bf1  |. 8bec           mov ebp,esp
 *  00609bf3  |. 64:a1 00000000 mov eax,dword ptr fs:[0]
 *  00609bf9  |. 6a ff          push -0x1
 *  00609bfb  |. 68 e1266300    push あや�006326e1
 *  00609c00  |. 50             push eax
 *  00609c01  |. 64:8925 000000>mov dword ptr fs:[0],esp
 *  00609c08  |. 81ec 80000000  sub esp,0x80
 *  00609c0e  |. 53             push ebx
 *  00609c0f  |. 8b5d 08        mov ebx,dword ptr ss:[ebp+0x8]
 *  00609c12  |. 57             push edi
 *  00609c13  |. 8bf9           mov edi,ecx
 *  00609c15  |. 8b07           mov eax,dword ptr ds:[edi]
 *  00609c17  |. 83f8 02        cmp eax,0x2
 *  00609c1a  |. 75 1f          jnz short あや�00609c3b
 *  00609c1c  |. 3b5f 40        cmp ebx,dword ptr ds:[edi+0x40]
 *  00609c1f  |. 75 1a          jnz short あや�00609c3b
 *  00609c21  |. 837f 44 00     cmp dword ptr ds:[edi+0x44],0x0
 *  00609c25  |. 74 14          je short あや�00609c3b
 *  00609c27  |. 5f             pop edi
 *  00609c28  |. b0 01          mov al,0x1
 *  00609c2a  |. 5b             pop ebx
 *  00609c2b  |. 8b4d f4        mov ecx,dword ptr ss:[ebp-0xc]
 *  00609c2e  |. 64:890d 000000>mov dword ptr fs:[0],ecx
 *  00609c35  |. 8be5           mov esp,ebp
 *  00609c37  |. 5d             pop ebp
 *  00609c38  |. c2 0400        retn 0x4
 *  Function stops
 *
 *  WideChar: こいな�小田舎で初恋x中出しセクシャルライ�, addr_offset = -53
 *  0040653a     cc             int3
 *  0040653b     cc             int3
 *  0040653c     cc             int3
 *  0040653d     cc             int3
 *  0040653e     cc             int3
 *  0040653f     cc             int3
 *  00406540   > 55             push ebp
 *  00406541   . 8bec           mov ebp,esp
 *  00406543   . 64:a1 00000000 mov eax,dword ptr fs:[0]
 *  00406549   . 6a ff          push -0x1
 *  0040654b   . 68 f1584300    push erondo01.004358f1
 *  00406550   . 50             push eax
 *  00406551   . 64:8925 000000>mov dword ptr fs:[0],esp
 *  00406558   . 83ec 6c        sub esp,0x6c
 *  0040655b   . 53             push ebx
 *  0040655c   . 8bd9           mov ebx,ecx
 *  0040655e   . 57             push edi
 *  0040655f   . 8b03           mov eax,dword ptr ds:[ebx]
 *  00406561   . 8b7d 08        mov edi,dword ptr ss:[ebp+0x8]
 *  00406564   . 83f8 02        cmp eax,0x2
 *  00406567   . 75 1f          jnz short erondo01.00406588
 *  00406569   . 3b7b 3c        cmp edi,dword ptr ds:[ebx+0x3c]
 *  0040656c   . 75 1a          jnz short erondo01.00406588
 *  0040656e   . 837b 40 00     cmp dword ptr ds:[ebx+0x40],0x0
 *  00406572   . 74 14          je short erondo01.00406588
 *  00406574   . 5f             pop edi
 *  00406575   . b0 01          mov al,0x1
 *  00406577   . 5b             pop ebx
 *  00406578   . 8b4d f4        mov ecx,dword ptr ss:[ebp-0xc]
 *  0040657b   . 64:890d 000000>mov dword ptr fs:[0],ecx
 *  00406582   . 8be5           mov esp,ebp
 *  00406584   . 5d             pop ebp
 *  00406585   . c2 0400        retn 0x4
 *
 *  WideChar: 祝福�鐘�音は、桜色の風と共に, addr_offset = -50,
 *  FIXME: how to know if it is UTF16? This game has /H code, though:
 *
 *      /HA-4@94D62:shukufuku_main.exe
 *
 *  011d619e   cc               int3
 *  011d619f   cc               int3
 *  011d61a0   55               push ebp
 *  011d61a1   8bec             mov ebp,esp
 *  011d61a3   64:a1 00000000   mov eax,dword ptr fs:[0]
 *  011d61a9   6a ff            push -0x1
 *  011d61ab   68 d1811f01      push .011f81d1
 *  011d61b0   50               push eax
 *  011d61b1   64:8925 00000000 mov dword ptr fs:[0],esp
 *  011d61b8   81ec 80000000    sub esp,0x80
 *  011d61be   53               push ebx
 *  011d61bf   8b5d 08          mov ebx,dword ptr ss:[ebp+0x8]
 *  011d61c2   57               push edi
 *  011d61c3   8bf9             mov edi,ecx
 *  011d61c5   8b07             mov eax,dword ptr ds:[edi]
 *  011d61c7   83f8 02          cmp eax,0x2
 *  011d61ca   75 1f            jnz short .011d61eb
 *  011d61cc   3b5f 40          cmp ebx,dword ptr ds:[edi+0x40]
 *  011d61cf   75 1a            jnz short .011d61eb
 *  011d61d1   837f 44 00       cmp dword ptr ds:[edi+0x44],0x0
 *  011d61d5   74 14            je short .011d61eb
 *  011d61d7   5f               pop edi
 *  011d61d8   b0 01            mov al,0x1
 *  011d61da   5b               pop ebx
 *  011d61db   8b4d f4          mov ecx,dword ptr ss:[ebp-0xc]
 *  011d61de   64:890d 00000000 mov dword ptr fs:[0],ecx
 *  011d61e5   8be5             mov esp,ebp
 *  011d61e7   5d               pop ebp
 *  011d61e8   c2 0400          retn 0x4
 */
bool InsertScenarioPlayerHook()
{
  PcHooks::hookOtherPcFunctions();
  // const BYTE bytes[] = {
  //   0x53,                    // 00609c0e  |. 53             push ebx
  //   0x8b,0x5d,0x08,          // 00609c0f  |. 8b5d 08        mov ebx,dword ptr ss:[ebp+0x8]
  //   0x57,                    // 00609c12  |. 57             push edi
  //   0x8b,0xf9,               // 00609c13  |. 8bf9           mov edi,ecx
  //   0x8b,0x07,               // 00609c15  |. 8b07           mov eax,dword ptr ds:[edi]
  //   0x83,0xf8, 0x02,         // 00609c17  |. 83f8 02        cmp eax,0x2
  //   0x75, 0x1f,              // 00609c1a  |. 75 1f          jnz short あや�00609c3b
  //   0x3b,0x5f, 0x40,         // 00609c1c  |. 3b5f 40        cmp ebx,dword ptr ds:[edi+0x40]
  //   0x75, 0x1a,              // 00609c1f  |. 75 1a          jnz short あや�00609c3b
  //   0x83,0x7f, 0x44, 0x00,   // 00609c21  |. 837f 44 00     cmp dword ptr ds:[edi+0x44],0x0
  //   0x74, 0x14,              // 00609c25  |. 74 14          je short あや�00609c3b
  // };
  // enum { addr_offset = 0x00609bf0 - 0x00609c0e }; // distance to the beginning of the function

  const BYTE bytes[] = {
      0x74, 0x14,      // 00609c25  |. 74 14          je short あや�00609c3b
      0x5f,            // 00609c27  |. 5f             pop edi
      0xb0, 0x01,      // 00609c28  |. b0 01          mov al,0x1
      0x5b,            // 00609c2a  |. 5b             pop ebx
      0x8b, 0x4d, 0xf4 // 00609c2b  |. 8b4d f4        mov ecx,dword ptr ss:[ebp-0xc]
  };
  enum
  {                                         // distance to the beginning of the function
    addr_offset_A = 0x00609bf0 - 0x00609c25 // -53
    ,
    addr_offset_W = 0x00406540 - 0x00406572 // -50
  };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG start = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!start)
  {
    ConsoleOutput("ScenarioPlayer: pattern not found");
    return false;
  }

  DWORD addr = MemDbg::findEnclosingAlignedFunction(start, 80); // range is around 50, use 80

  enum : BYTE
  {
    push_ebp = 0x55
  }; // 011d4c80  /$ 55             push ebp
  if (!addr || *(BYTE *)addr != push_ebp)
  {
    ConsoleOutput("ScenarioPlayer: pattern found but the function offset is invalid");
    return false;
  }
  auto succ = false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  if (
      (addr - start == addr_offset_W) ||
      ((Util::FindImportEntry(processStartAddress, (DWORD)GetGlyphOutlineA) == 0) &&
       (Util::FindImportEntry(processStartAddress, (DWORD)TextOutA) == 0) &&
       (Util::FindImportEntry(processStartAddress, (DWORD)ExtTextOutA) == 0) &&
       (Util::FindImportEntry(processStartAddress, (DWORD)GetTextExtentPoint32A) == 0)
       // 祝福の鐘の音は、桜色の風と共に
       ))
  {
    // Artikash 8/18/2018: can't figure out how to tell apart which hook is needed, so alert user
    // (The method used to tell the hooks apart previously fails on https://vndb.org/v19713)

    hp.type = CODEC_UTF16;
    ConsoleOutput("INSERT ScenarioPlayerW");
    succ = NewHook(hp, "ScenarioPlayerW");
  }
  else
  {
    hp.type = CODEC_ANSI_BE; // 4
    ConsoleOutput("INSERT ScenarioPlayerA");
    succ = NewHook(hp, "ScenarioPlayerA");
  }
  ConsoleOutput("Text encoding might be wrong: try changing it if this hook finds garbage!");
  return succ;
}

bool InsertScenarioPlayerHookx()
{
  // 夏彩恋呗
  // 为避免和engine中的冲突，进行一次xref
  const BYTE bytes[] = {
      0xC1, 0xE8, 0x02, 0x25, 0x01, 0xFF, 0xFF, 0xFF, 0x89, 0x45, XX};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  ConsoleOutput("%p", addr);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  ConsoleOutput("%p", addr);
  if (!addr)
    return false;
  auto addrs = findxref_reverse_checkcallop(addr, addr - 0x1000, addr, 0xe9);
  if (addrs.size() != 1)
    return false;
  addr = addrs[0];
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = CODEC_UTF16;
  return NewHook(hp, "sutajioryokutyaW");
}
namespace
{
  bool Iyashikei()
  {
    // 癒し系ソープ嬢ヒロさん
    const BYTE bytes[] = {
        0x6A, 0xFF,
        0x68, XX4,
        0x64, 0xA1, 0x00, 0x00, 0x00, 0x00,
        0x50,
        0x83, 0xEC, 0x08,
        0x56,
        0xA1, 0x08, 0x6E, 0x6B, 0x00,
        0x33, 0xC4,
        0x50,
        0x8D, 0x44, 0x24, XX,
        0x64, 0xA3, 0x00, 0x00, 0x00, 0x00,
        0x8B, 0xF1,
        0x8B, 0x44, 0x24, XX,
        0x50,
        0x8D, 0x4C, 0x24, XX,
        0x51,
        0x8B, 0xCE,
        0xE8, XX4};
    auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = CODEC_ANSI_BE;
    return NewHook(hp, "Iyashikei");
  }
}
bool InsertScenarioPlayerHook_all()
{
  bool b1 = InsertScenarioPlayerHook();
  bool b2 = InsertScenarioPlayerHookx();
  return b1 || b2 || Iyashikei();
}
bool Ryokucha::attach_function()
{
  InsertRyokuchaHook();

  if (Util::CheckFile(L"*.iar") && Util::CheckFile(L"*.sec5")) // jichi 9/27/2014: For new Ryokucha games
    InsertScenarioPlayerHook_all();

  return true;
}

bool ScenarioPlayer_last::attach_function()
{

  return InsertScenarioPlayerHook_all();
}
bool Ryokucha2::attach_function()
{
  // 夏日
  const BYTE bytes[] = {
      0x8b, XX2, 0x2b, 0xd1, 0xc1, 0xfa, 0x02, 0x3b, 0xd0, 0x76};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  ConsoleOutput("%p", addr);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  ConsoleOutput("%p", addr);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(6);
  hp.type = USING_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    auto s = buffer->viewA();
    if (s[0] == '#')
      buffer->clear();
  };
  return NewHook(hp, "sutajioryokutya");
}