#include "Artemis.h"

/**
 *  jichi 10/1/2013: Artemis Engine
 *  See: http://www.ies-net.com/
 *  See (CaoNiMaGeBi): http://tieba.baidu.com/p/2625537737
 *  Pattern:
 *     650a2f 83c4 0c   add esp,0xc ; hook here
 *     650a32 0fb6c0    movzx eax,al
 *     650a35 85c0      test eax,eax
 *     0fb6c0 75 0e     jnz short tsugokaz.0065a47
 *
 *  Wrong: 0x400000 + 0x7c574
 *
 *  //Example: [130927]妹スパイラル /HBN-8*0:14@65589F
 *  Example: ヂ�ウノイイ家�Trial /HBN-8*0:14@650A2F
 *  Note: 0x650a2f > 40000(base) + 20000(limit)
 *  - addr: 0x650a2f
 *  - text_fun: 0x0
 *  - function: 0
 *  - hook_len: 0
 *  - ind: 0
 *  - length_offset: 1
 *  - module: 0
 *  - off: 4294967284 = 0xfffffff4 = -0xc
 *  - recover_len: 0
 *  - split: 20 = 0x14
 *  - split_ind: 0
 *  - type: 1048 = 0x418
 *
 *  @CaoNiMaGeBi:
 *  RECENT GAMES:
 *    [130927]妹スパイラル /HBN-8*0:14@65589F
 *    [130927]サ�ライホルモン
 *    [131025]ヂ�ウノイイ家�/HBN-8*0:14@650A2F (for trial version)
 *    CLIENT ORGANIZAIONS:
 *    CROWD
 *    D:drive.
 *    Hands-Aid Corporation
 *    iMel株式会社
 *    SHANNON
 *    SkyFish
 *    SNACK-FACTORY
 *    team flap
 *    Zodiac
 *    くらむちめ�� *    まかろんソフト
 *    アイヂ�アファクトリー株式会社
 *    カラクリズ�
 *    合赼�社ファーストリー�
 *    有限会社ウルクスへブン
 *    有限会社ロータス
 *    株式会社CUCURI
 *    株式会社アバン
 *    株式会社インタラクヂ�ブブレインズ
 *    株式会社ウィンヂ�ール
 *    株式会社エヴァンジェ
 *    株式会社ポニーキャニオン
 *    株式会社大福エンターヂ�ンメン� */
bool InsertArtemis1Hook()
{
  const BYTE bytes[] = {
      0x83, 0xc4, 0x0c, // add esp,0xc ; hook here
      0x0f, 0xb6, 0xc0, // movzx eax,al
      0x85, 0xc0,       // test eax,eax
      0x75, 0x0e        // jnz XXOO ; it must be 0xe, or there will be duplication
  };
  // enum { addr_offset = 0 };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  // GROWL_DWORD3(reladdr, processStartAddress, range);
  if (!addr)
  {
    ConsoleOutput("Artemis1: pattern not exist");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(ecx);
  hp.split = stackoffset(5);
  hp.type = NO_CONTEXT | DATA_INDIRECT | USING_SPLIT; // 0x418

  // hp.address = 0x650a2f;
  // GROWL_DWORD(hp.address);

  ConsoleOutput("INSERT Artemis1");

  // ConsoleOutput("Artemis1");
  return NewHook(hp, "Artemis1");
}

bool InsertArtemis2Hook()
{
  const BYTE bytes[] = {
      // 0054461F | CC                       | int3                                    |
      0x55,                               // 00544620 | 55                       | push ebp                                |
      0x8B, 0xEC,                         // 00544621 | 8B EC                    | mov ebp,esp                             |
      0x83, 0xE4, 0xF8,                   // 00544623 | 83 E4 F8                 | and esp,FFFFFFF8                        |
      0x6A, 0xFF,                         // 00544626 | 6A FF                    | push FFFFFFFF                           |
      0x68, XX4,                          // 00544628 | 68 68 7C 6A 00           | push 空のつくりかた体験版_ver3.0.6A7C68           |
      0x64, 0xA1, 0x00, 0x00, 0x00, 0x00, // 0054462D | 64 A1 00 00 00 00        | mov eax,dword ptr fs:[0]                |
      0x50,                               // 00544633 | 50                       | push eax                                |
      0x83, 0xEC, XX,                     // 00544634 | 83 EC 28                 | sub esp,28                              |
      0xA1, XX4,                          // 00544637 | A1 F0 57 81 00           | mov eax,dword ptr ds:[8157F0]           |
      0x33, 0xC4,                         // 0054463C | 33 C4                    | xor eax,esp                             |
      0x89, 0x44, 0x24, XX,               // 0054463E | 89 44 24 20              | mov dword ptr ss:[esp+20],eax           |
      0x53,                               // 00544642 | 53                       | push ebx                                |
      0x56,                               // 00544643 | 56                       | push esi                                |
      0x57,                               // 00544644 | 57                       | push edi                                |
      0xA1, XX4,                          // 00544645 | A1 F0 57 81 00           | mov eax,dword ptr ds:[8157F0]           |
      0x33, 0xC4,                         // 0054464A | 33 C4                    | xor eax,esp                             |
      0x50,                               // 0054464C | 50                       | push eax                                |
      0x8D, 0x44, 0x24, XX,               // 0054464D | 8D 44 24 38              | lea eax,dword ptr ss:[esp+38]           | [esp+38]:BaseThreadInitThunk
      0x64, 0xA3, 0x00, 0x00, 0x00, 0x00, // 00544651 | 64 A3 00 00 00 00        | mov dword ptr fs:[0],eax                |
      0x8B, 0xF1,                         // 00544657 | 8B F1                    | mov esi,ecx                             |
      0x8B, 0x5D, 0x08,                   // 00544659 | 8B 5D 08                 | mov ebx,dword ptr ss:[ebp+8]            |
      0x8B, 0x4D, 0x0C                    // 0054465C | 8B 4D 0C                 | mov ecx,dword ptr ss:[ebp+C]            | ecx:DbgUiRemoteBreakin, [ebp+C]:BaseThreadInitThunk
  };
  enum
  {
    addr_offset = 0
  }; // distance to the beginning of the function, which is 0x55 (push ebp)
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("Artemis2: pattern not found");
    return false;
  }
  addr += addr_offset;
  enum
  {
    push_ebp = 0x55
  }; // beginning of the function
  if (*(BYTE *)addr != push_ebp)
  {
    ConsoleOutput("Artemis2: beginning of the function not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING | NO_CONTEXT;

  ConsoleOutput("INSERT Artemis2");
  bool succ = NewHook(hp, "Artemis2");

  // Artikash 1/1/2019: Recent games seem to use utf8 encoding instead, other than that the hook is identical.
  // Not sure how to differentiate which games are sjis/utf8 so insert both
  hp.address = addr + 6;
  hp.offset = regoffset(ebp);
  hp.index = 8; // ebp was also pushed
  hp.type = CODEC_UTF8 | USING_STRING | DATA_INDIRECT;
  succ |= NewHook(hp, "Artemis2");
  // ConsoleOutput("Artemis2");
  return succ;
}

bool InsertArtemis3Hook()
{
  const BYTE bytes[] = {
      0x55,                                           // 005FD780 | 55                       | push ebp                                |
      0x8B, 0xEC,                                     // 005FD781 | 8BEC                     | mov ebp,esp                             |
      0x83, 0xE4, 0xF8,                               // 005FD783 | 83E4 F8                  | and esp,FFFFFFF8                        |
      0x83, 0xEC, 0x3C,                               // 005FD786 | 83EC 3C                  | sub esp,3C                              |
      0xA1, XX4,                                      // 005FD789 | A1 6C908600              | mov eax,dword ptr ds:[86906C]           |
      0x33, 0xC4,                                     // 005FD78E | 33C4                     | xor eax,esp                             |
      0x89, 0x44, 0x24, 0x38,                         // 005FD790 | 894424 38                | mov dword ptr ss:[esp+38],eax           |
      0x53,                                           // 005FD794 | 53                       | push ebx                                |
      0x56,                                           // 005FD795 | 56                       | push esi                                |
      0x8B, 0xC1,                                     // 005FD796 | 8BC1                     | mov eax,ecx                             |
      0xC7, 0x44, 0x24, 0x14, 0x00, 0x00, 0x00, 0x00, // 005FD798 | C74424 14 00000000       | mov dword ptr ss:[esp+14],0             |
      0x8B, 0x4D, 0x0C,                               // 005FD7A0 | 8B4D 0C                  | mov ecx,dword ptr ss:[ebp+C]            |
      0x33, 0xF6,                                     // 005FD7A3 | 33F6                     | xor esi,esi                             |
      0x57,                                           // 005FD7A5 | 57                       | push edi                                |
      0x8B, 0x7D, 0x08,                               // 005FD7A6 | 8B7D 08                  | mov edi,dword ptr ss:[ebp+8]            |
      0x89, 0x44, 0x24, 0x14,                         // 005FD7A9 | 894424 14                | mov dword ptr ss:[esp+14],eax           |
      0x89, 0x4C, 0x24, 0x28,                         // 005FD7AD | 894C24 28                | mov dword ptr ss:[esp+28],ecx           |
      0x80, 0x3F, 0x00,                               // 005FD7B1 | 803F 00                  | cmp byte ptr ds:[edi],0                 |
      0x0F, 0x84, XX4,                                // 005FD7B4 | 0F84 88040000            | je ヘンタイ・プリズンsplit 1.5FDC42              |
      0x83, 0xB8, XX4, 0x00,                          // 005FD7BA | 83B8 74030000 00         | cmp dword ptr ds:[eax+374],0            |
      0x8B, 0xDF,                                     // 005FD7C1 | 8BDF                     | mov ebx,edi                             |
  };

  enum
  {
    addr_offset = 0
  }; // distance to the beginning of the function, which is 0x55 (push ebp)
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("Artemis3: pattern not found");
    return false;
  }
  addr += addr_offset;
  enum
  {
    push_ebp = 0x55
  }; // beginning of the function
  if (*(BYTE *)addr != push_ebp)
  {
    ConsoleOutput("Artemis3: beginning of the function not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING | EMBED_ABLE | CODEC_UTF8 | EMBED_AFTER_NEW;

  return NewHook(hp, "EmbedArtemis");
}

namespace
{
  bool a4()
  {
    // 高慢な奥さんは好きですか？～傲慢人妻教師の堕とし方～
    std::vector<uint64_t> addrs;
    for (DWORD func : {(DWORD)GetGlyphOutlineA, (DWORD)GetGlyphOutlineW})
    {
      auto addrs_ = findiatcallormov_all(func, processStartAddress, processStartAddress, processStopAddress, PAGE_EXECUTE);
      addrs.insert(addrs.end(), addrs_.begin(), addrs_.end());
    }
    bool ok = false;
    for (auto addr : addrs)
    {
      auto funcaddr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!funcaddr)
        continue;
      BYTE sig1[] = {0x81, XX, 0x00, 0x00, 0x10, 0x00};
      BYTE sig2[] = {0x68, 0x00, 0x02, 0x00, 0x00, 0x68, 0x00, 0x02, 0x00, 0x00};
      BYTE sig3[] = {XX, 0x80, 0x00, 0x00, 0x00, 0x0f, 0x95, 0xc1};
      BYTE sig4[] = {0xC1, XX, 0x18};
      int found = 0;
      for (auto sigsz : std::vector<std::pair<BYTE *, int>>{{sig1, sizeof(sig1)}, {sig2, sizeof(sig2)}, {sig3, sizeof(sig3)}, {sig4, sizeof(sig4)}})
      {
        auto fd = MemDbg::findBytes(sigsz.first, sigsz.second, funcaddr, addr);
        if (fd)
          found += 1;
      }
      if (found == 4)
      {
        {
          HookParam hp;
          hp.address = funcaddr;
          hp.type = CODEC_ANSI_BE;
          hp.offset = stackoffset(2);
          ok |= NewHook(hp, "Artemis4A");
        }
        {
          HookParam hp;
          hp.address = funcaddr + 5;
          hp.type = CODEC_UTF16;
          hp.offset = stackoffset(2);
          ok |= NewHook(hp, "Artemis4W");
        }
        return ok;
      }
    }
    return false;
  }
}
namespace
{
  bool artemis()
  {
    /*
    char __cdecl sub_417EF0(char a1, _DWORD *a2, int a3)
{
  int i; // [esp+0h] [ebp-4h]

  if ( !a3 )
  {
    if ( ((unsigned __int8)a1 ^ 0x20u) - 161 < 0x3C )
    {
      if ( a2 )
        *a2 = 1;
      return 1;
    }
    return 0;
  }
  if ( a3 == 1 )
  {
    if ( ((unsigned __int8)a1 < 0xA1u || (unsigned __int8)a1 > 0xF4u) && (unsigned __int8)a1 != 142 )
      return 0;
    if ( a2 )
      *a2 = 1;

      这个和64位的那个是一样的，但是这个函数在64位下是内联的，32位不内联，所以必须xref一下
    */
    const BYTE BYTES[] = {
        0x0f, 0xb6, 0x45, 0x08,
        0x83, 0xf0, 0x20,
        0x2d, 0xa1, 0x00, 0x00, 0x00,
        0x83, 0xf8, 0x3c,
        0x73, XX4

    };
    ULONG addr = MemDbg::findBytes(BYTES, sizeof(BYTES), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    for (auto addr_1 : findxref_reverse_checkcallop(addr, processStartAddress, processStopAddress, 0xe8))
    {
      /*
      char __cdecl sub_417EF0(char a1, _DWORD *a2, int a3)
{
  int i; // [esp+0h] [ebp-4h]

  if ( !a3 )
  {
    if ( ((unsigned __int8)a1 ^ 0x20u) - 161 < 0x3C )
    {
      if ( a2 )
        *a2 = 1;
      return 1;
    }
    return 0;
  }
  if ( a3 == 1 )
  {
    if ( ((unsigned __int8)a1 < 0xA1u || (unsigned __int8)a1 > 0xF4u) && (unsigned __int8)a1 != 142 )
      return 0;
    if ( a2 )
      *a2 = 1;
    return 1;
  }
  else
  {
    if ( a3 != 2 || (a1 & 0x80) == 0 )
      return 0;
    if ( a2 )
    {
      *a2 = -1;
      for ( i = 128; (i & a1) != 0; i >>= 1 )
        ++*a2;
    }
    return 1;
  }
}
      */
      /*
      .text:006032CC                 cmp     [ebp+var_10], 3FFh
 .text:006032D3                 jge     short loc_603315
 .text:006032D5                 mov     edx, [ebp+var_8]
 .text:006032D8                 movsx   eax, byte ptr [edx]
 .text:006032DB                 cmp     eax, 41h ; 'A'
 .text:006032DE                 jl      short loc_6032EB
 .text:006032E0                 mov     ecx, [ebp+var_8]
 .text:006032E3                 movsx   edx, byte ptr [ecx]
 .text:006032E6                 cmp     edx, 5Ah ; 'Z'
 .text:006032E9                 jle     short loc_603301
 .text:006032EB
 .text:006032EB loc_6032EB:                             ; CODE XREF: sub_603210+CE↑j
 .text:006032EB                 mov     eax, [ebp+var_8]
 .text:006032EE                 movsx   ecx, byte ptr [eax]
 .text:006032F1                 cmp     ecx, 61h ; 'a'
 .text:006032F4                 jl      short loc_603311
 .text:006032F6                 mov     edx, [ebp+var_8]
 .text:006032F9                 movsx   eax, byte ptr [edx]
 .text:006032FC                 cmp     eax, 7Ah ; 'z'
 .text:006032FF                 jg      short loc_603311
      */
      BYTE sig[] = {
          0x81, 0x7d, 0xf0, 0xff, 0x03, 0x00, 0x00};
      if (MemDbg::findBytes(sig, sizeof(sig), addr_1, addr_1 + 0x100))
      {
        addr = MemDbg::findEnclosingAlignedFunction(addr_1);
        if (!addr)
          return false;
        HookParam hp;
        hp.address = addr;
        hp.type = USING_STRING | CODEC_UTF8;
        hp.offset = stackoffset(1);
        return NewHook(hp, "Artemis");
      }
    }
    return false;
  }
}
bool Artemis::attach_function()
{

  return artemis() | (InsertArtemis1Hook() || InsertArtemis2Hook() || InsertArtemis3Hook() || a4());
}