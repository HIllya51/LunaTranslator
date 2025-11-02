#include "CodeX.h"

void CodeXFilter(TextBuffer *buffer, HookParam *)
{
  std::string result = buffer->strA();
  strReplace(result, "^n", "\n");
  if (startWith(result, "\n"))
    result = result.substr(1);

  //|晒[さら]
  result = re::sub(result, "\\|(.+?)\\[(.+?)\\]", "$1");
  buffer->from(result);
}

bool InsertCodeXHook()
{

  /*
   * Sample games:
   * https://vndb.org/v41664
   * https://vndb.org/v36122
   */
  const BYTE bytes[] = {
      0x83, 0xC4, 0x08, // add esp,08                  << hook here
      0x8D, 0x85, XX4,  // lea eax,[ebp-00000218]
      0x50,             // push eax
      0x68, XX4,        // push ???????????!.exe+10A76C
      0x85, 0xF6,       // test esi,esi
      0x74, 0x4F,       // je ???????????!.exe+2A95B
      0xFF, 0x15, XX4,  // call dword ptr [???????????!.exe+C8140]
      0x8B, 0x85, XX4   // mov eax,[ebp-00000220]      << alternative hook here
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("CodeX: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(eax);
  hp.index = 0;
  hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_OVERWRITE | NO_CONTEXT; // 无法解决中文乱码
  hp.embed_hook_font = F_GetGlyphOutlineA;
  hp.filter_fun = CodeXFilter;
  ConsoleOutput("INSERT CodeX");

  return NewHook(hp, "CodeX");
}
namespace
{
  bool hook()
  {
    // 霞外籠逗留記
    BYTE _[] = {0x90, 0x90, 0x68, 0x64, 0x7B, 0x4C, 0x00}; // aHdL db 'hd{L',0
    ULONG addr = MemDbg::findBytes(_, sizeof(_), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr += 2;
    BYTE bytes[] = {0x68, XX4};
    memcpy(bytes + 1, &addr, 4);
    auto addrs = Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress);
    bool succ = false;
    for (auto adr : addrs)
    {
      adr = MemDbg::findEnclosingAlignedFunction(adr);
      if (adr == 0)
        continue;
      HookParam hp;
      hp.address = adr;
      hp.offset = stackoffset(1);
      hp.type = CODEC_ANSI_BE;
      succ |= NewHook(hp, "CodeX");
    }
    return succ;
  }
}
namespace
{
  // https://vndb.org/v598
  // ANGEL BULLET
  bool hook2()
  {
    BYTE _[] = {
        0x8b, 0x44, 0x24, 0x04,
        0x81, 0xec, XX4,
        0x25, 0xff, 0xff, 0, 0,
        0x8d, 0x54, 0x24, 0,
        0x56,
        0x8b, 0xf1,
        0x50,
        0x8d, 0x4e, XX,
        0x51,
        0x68, XX4, //%s%03d
        0x52,
        0xff, 0x15, XX4, // wprintfA
    };
    ULONG addr = MemDbg::findBytes(_, sizeof(_), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(edx);
    hp.type = USING_STRING;
    hp.filter_fun = CodeXFilter;
    return NewHook(hp, "CodeX");
  }
}
namespace
{
  bool hook3()
  {
    BYTE _[] = {
        // if ( *(_WORD *)v38 == 8511 || (_WORD)v5 == 16161 || (_WORD)v5 == 8481 )
        0xB9, 0x3F, 0x21, 0x00, 0x00, // mov     ecx, 213Fh
        0x0F, 0xB7, 0x02,             // movzx   eax, word ptr [edx]
        0x66, 0x3B, 0xC1,             // cmp     ax, cx
        0x0F, 0x84, XX4,              // jz      loc_458294
        0xb9, 0x21, 0x3f, 0x00, 0x00, // mov     ecx, 3F21h
        0x66, 0x3B, 0xC1,
        0x0F, 0x84, XX4,
        0xb9, 0x21, 0x21, 0x00, 0x00, // mov     ecx, 2121h
        0x66, 0x3B, 0xC1,
        0x0F, 0x84, XX4};
    ULONG addr = MemDbg::findBytes(_, sizeof(_), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.split = stackoffset(2);
    hp.type = USING_STRING | NO_CONTEXT | USING_SPLIT | EMBED_ABLE | EMBED_AFTER_OVERWRITE;
    hp.embed_hook_font = F_GetGlyphOutlineA;
    hp.filter_fun = CodeXFilter;
    return NewHook(hp, "CodeX2");
  }
}
namespace
{
  //[160930] [ライアーソフト] 大迷宮＆大迷惑 -GREAT EDGES IN THE ABYSS-
  /*

char __thiscall sub_459EC0(int this, unsigned __int8 *a2)
{
  int v3; // ebx
  __int16 v4; // cx
  int v5; // eax
  int v6; // edx
  int v7; // ecx
  int v8; // edx
  __int16 v9; // cx
  unsigned __int8 *v10; // eax
  CHAR *v11; // edi
  unsigned __int8 v12; // cl
  unsigned __int8 *v13; // edi
  unsigned __int8 *v14; // eax
  unsigned __int16 v15; // ax
  char v16; // cl
  int v17; // ebp
  int v18; // eax
  unsigned int v19; // ebp
  int v20; // ecx
  __int16 v21; // dx
  char v22; // cl
  int v23; // ecx
  unsigned __int16 v24; // cx
  bool v25; // cf
  int v26; // eax
  unsigned __int16 v27; // cx
  unsigned __int16 v28; // cx
  char v29; // dl
  int v30; // ecx
  int v31; // eax
  int v33; // [esp-4h] [ebp-F0h]
  int v34; // [esp+0h] [ebp-ECh]
  int v35; // [esp+10h] [ebp-DCh]
  int v36; // [esp+14h] [ebp-D8h]
  int v37; // [esp+18h] [ebp-D4h]
  unsigned __int16 v38; // [esp+1Ch] [ebp-D0h]
  CHAR String[4]; // [esp+24h] [ebp-C8h] BYREF

  LOWORD(v35) = *(_WORD *)(this + 416);
  v3 = *(_DWORD *)(this + 412);
  v36 = *(_DWORD *)(this + 420);
  v4 = *(_WORD *)(this + 436);
  v37 = *(_DWORD *)(this + 424);
  *(_WORD *)(this + 438) = *(_WORD *)(this + 428);
  *(_WORD *)(this + 430) = v4;
  v38 = 1;
  sub_442E60(0);
LABEL_2:
  v5 = (int)a2;
LABEL_3:
  while ( 1 )
  {
    LOBYTE(v5) = *(_BYTE *)v5;
    if ( !(_BYTE)v5 )
      return v5;
    if ( _ismbblead((char)v5) )
    {
      v5 = _ismbbtrail((char)a2[1]);
      if ( v5 )
      {
        if ( *(_WORD *)(this + 96) >= *(_WORD *)(this + 98) )
          return v5;
        HIWORD(v8) = HIWORD(a2);
        LOWORD(v5) = *a2;
        LOWORD(v8) = a2[1];
        *(_WORD *)(*(_DWORD *)(this + 408) + 6 * *(unsigned __int16 *)(this + 96) + 4) = v35;
        sub_45AB40(this, v8 + (v5 << 8), v38, v3, v36, v37);
        goto LABEL_8;
      }
    }
    v5 = (int)a2;
    v9 = *(_WORD *)a2;
    if ( *(_WORD *)a2 == 8511 || v9 == 16161 || v9 == 8481 )
  */
  bool h4()
  {
    BYTE _[] = {
        0x8b, 0x84, 0x24, XX4,
        0x66, 0x8b, 0x08,
        0x66, 0x81, 0xf9, 0x3f, 0x21,
        0x0f, 0x84, XX4,
        0x66, 0x81, 0xf9, 0x21, 0x3f,
        0x0f, 0x84, XX4,
        0x66, 0x81, 0xf9, 0x21, 0x21,
        0x0f, 0x84, XX4,
        0x80, 0xf9, 0x7c};
    ULONG addr = MemDbg::findBytes(_, sizeof(_), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    auto faddr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!faddr)
      return false;
    BYTE bytes2[] = {
        0x8a, 0x00,
        0x84, 0xc0,
        0x0f, 0x84, XX4,
        0x0f, 0xbe, 0xc8,
        0x51,
        0xe8, XX4, // call    __ismbblead
        0x83, 0xc4, 0x04,
        0x85, 0xc0,
        0x0f, 0x84, XX4,
        0x8b, 0x94, 0x24, XX4,
        0x0f, 0xbe, 0x42, 0x01,
        0x50,
        0xe8, XX4, // call    __ismbbtrail
    };
    auto addrX = MemDbg::findBytes(bytes2, sizeof(bytes2), faddr, addr);
    if (!addrX)
      return false;
    auto __ismbblead = *(int *)(addrX + 2 + 2 + 6 + 3 + 1 + 1) + addrX + 2 + 2 + 6 + 3 + 1 + 5;
    auto __ismbbtrail = *(int *)(addrX + sizeof(bytes2) - 4) + addrX + sizeof(bytes2);
    ConsoleOutput("%p", __ismbblead);
    ConsoleOutput("%p", __ismbbtrail);
    HookParam hp;
    hp.address = faddr;
    hp.offset = stackoffset(1);
    hp.split = stackoffset(1);
    hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS | USING_SPLIT;
    hp.embed_hook_font = F_GetGlyphOutlineA | F_GetTextExtentPoint32A;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      // 这个东西^开头的都是各种奇葩控制符。懒得管了。
      auto result = buffer->strAW();
      result = re::sub(result, LR"(\|(.*?)\[(.*?)\])", L"$1");
      result = re::sub(result, LR"(\^d\d)");
      // 内嵌会导致^\w解析错误
      //^n ^m ...
      result = re::sub(result, LR"(\^\w)");
      buffer->fromWA(result);
    };
    patch_fun_ptrs = {{(void *)__ismbblead, +[](BYTE b)
                                            { return b != '^'; }},
                      {(void *)__ismbbtrail, +[](BYTE b)
                                             { return true; }}};
    return NewHook(hp, "CodeX");
  }
}
bool CodeX::attach_function()
{
  PcHooks::hookGDIFunctions(GetGlyphOutlineA); // 对于部分游戏，文本分两段显示，会吞掉后半段。故此用这个兜底
  return (hook3() | InsertCodeXHook()) || h4() || hook() || hook2();
}