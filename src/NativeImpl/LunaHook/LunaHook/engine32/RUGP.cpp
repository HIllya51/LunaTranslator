#include "RUGP.h"

namespace
{ // unnamed rUGP

  /********************************************************************************************
  rUGP hook:
    Process name is rugp.exe. Used by AGE/GIGA games.

    Font caching issue. Find call to GetGlyphOutlineA and keep stepping out functions.
    After several tries we comes to address in rvmm.dll and everything is catched.
    We see CALL [E*X+0x*] while EBP contains the character data.
    It's not as simple to reverse in rugp at run time as like reallive since rugp dosen't set
    up stack frame. In other words EBP is used for other purpose. We need to find alternative
    approaches.
    The way to the entry of that function gives us clue to find it. There is one CMP EBP,0x8140
    instruction in this function and that's enough! 0x8140 is the start of SHIFT-JIS
    characters. It's determining if ebp contains a SHIFT-JIS character. This function is not likely
    to be used in other ways. We simply search for this instruction and place hook around.
  ********************************************************************************************/
  void SpecialHookRUGP1(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    // CC_UNUSED(split);
    DWORD *_stack = (DWORD *)context->base;
    DWORD i, val;
    for (i = 0; i < 4; i++)
    {
      val = *_stack++;
      if ((val >> 16) == 0)
        break;
    }
    if (i < 4)
    {
      hp->offset = i << 2;
      if (i == 2 && hp->user_value != 1)
      {
        hp->split = stackoffset(1);
        hp->type |= USING_SPLIT;
      }
      buffer->from_t<WORD>(val);
      hp->text_fun = nullptr;
      // hp->type &= ~EXTERN_HOOK;
    }
  }

  // jichi 10/1/2013: Change return type to bool
  bool InsertRUGP1Hook()
  {
    DWORD low;
    if (!Util::CheckFile(L"rvmm.dll"))
    {
      return false;
    }
    // WCHAR str[0x40];
    LPVOID ch = (LPVOID)0x8140;
    enum
    {
      range = 0x20000
    };
    low = (DWORD)GetModuleHandleW(L"rvmm.dll");
    DWORD t = SearchPattern(low + range, processStopAddress, &ch, 4) + range;
    BYTE *s = (BYTE *)(low + t);
    // if (t) {
    if (t != range)
    { // jichi 10/1/2013: Changed to compare with 0x20000
      if (*(s - 2) != 0x81)
        return false;
      if (DWORD i = SafeFindEnclosingAlignedFunction((DWORD)s, 0x200))
      {
        auto [s, e] = Util::QueryModuleLimits((HMODULE)low);
        auto refs = findxref_reverse_checkcallop(i, s, e, 0xe8);
        if (refs.size() == 1)
        {
          auto f2 = findfuncstart(refs[0], 0x100, true);
          if (f2)
          {
            HookParam hp;
            hp.address = f2;
            hp.text_fun = SpecialHookRUGP1;
            hp.user_value = 1;
            hp.type = CODEC_ANSI_BE | USING_CHAR;
            return NewHook(hp, "rUGP");
          }
        }
        BYTE check[] = {
            // 螺旋回廊 2000版
            0x75, XX,
            0x8b, 0x86};
        if (MatchPattern(i, check, sizeof(check)))
          return false;
        HookParam hp;
        hp.address = i;
        hp.text_fun = SpecialHookRUGP1;
        hp.type = CODEC_ANSI_BE | USING_CHAR;
        return NewHook(hp, "rUGP");
      }
    }
    else
    {
      t = SearchPattern(low, range, &s, 4);
      if (!t)
      {
        // ConsoleOutput("Can't find characteristic instruction.");
        return false;
      }

      s = (BYTE *)(low + t);
      for (int i = 0; i < 0x200; i++, s--)
        if (s[0] == 0x90 && *(DWORD *)(s - 3) == 0x90909090)
        {
          t = low + t - i + 1;
          // swprintf(str, L"HookAddr 0x%.8x", t);
          // ConsoleOutput(str);
          HookParam hp;
          hp.address = t;
          hp.offset = stackoffset(1);
          hp.type = CODEC_ANSI_BE;
          ConsoleOutput("INSERT rUGP#2");
          return NewHook(hp, "rUGP");
        }
    }
    ConsoleOutput("rUGP: failed");
    return false;
    // rt:
    // ConsoleOutput("Unknown rUGP engine.");
  }

  /** rUGP2 10/11/2014 jichi
   *
   *  Sample game: マブラヴ オルタネイヂ�ヴ ト�タル・イクリプス
   *  The existing rUGP#1/#2 cannot be identified.
   *  H-codes:
   *  - /HAN-4@1E51D:VM60.DLL
   *    - addr: 124189 = 0x1e51d
   *    - length_offset: 1
   *    - module: 3037492083 = 0xb50c7373
   *    - off: 4294967288 = 0xfffffff8 = -8
   *    - type: 1092 = 0x444
   *  - /HAN-4@1001E51D ( alternative)
   *    - addr: 268559645 = 0x1001e51d
   *    - length_offset: 1
   *    - type: 1028 = 0x404
   *
   *  This function is very long.
   *  1001e4b2  ^e9 c0fcffff      jmp _18.1001e177
   *  1001e4b7   8b45 14          mov eax,dword ptr ss:[ebp+0x14]
   *  1001e4ba   c745 08 08000000 mov dword ptr ss:[ebp+0x8],0x8
   *  1001e4c1   85c0             test eax,eax
   *  1001e4c3   74 3c            je short _18.1001e501
   *  1001e4c5   8378 04 00       cmp dword ptr ds:[eax+0x4],0x0
   *  1001e4c9   7f 36            jg short _18.1001e501
   *  1001e4cb   7c 05            jl short _18.1001e4d2
   *  1001e4cd   8338 00          cmp dword ptr ds:[eax],0x0
   *  1001e4d0   73 2f            jnb short _18.1001e501
   *  1001e4d2   8b4d f0          mov ecx,dword ptr ss:[ebp-0x10]
   *  1001e4d5   8b91 38a20000    mov edx,dword ptr ds:[ecx+0xa238]
   *  1001e4db   8910             mov dword ptr ds:[eax],edx
   *  1001e4dd   8b89 3ca20000    mov ecx,dword ptr ds:[ecx+0xa23c]
   *  1001e4e3   8948 04          mov dword ptr ds:[eax+0x4],ecx
   *  1001e4e6   eb 19            jmp short _18.1001e501
   *  1001e4e8   c745 08 09000000 mov dword ptr ss:[ebp+0x8],0x9
   *  1001e4ef   eb 10            jmp short _18.1001e501
   *  1001e4f1   c745 08 16000000 mov dword ptr ss:[ebp+0x8],0x16
   *  1001e4f8   eb 07            jmp short _18.1001e501
   *  1001e4fa   c745 08 1f000000 mov dword ptr ss:[ebp+0x8],0x1f
   *  1001e501   8b45 08          mov eax,dword ptr ss:[ebp+0x8]
   *  1001e504   8ad0             mov dl,al
   *  1001e506   80f2 20          xor dl,0x20
   *  1001e509   80c2 5f          add dl,0x5f
   *  1001e50c   80fa 3b          cmp dl,0x3b
   *  1001e50f   0f87 80010000    ja _18.1001e695
   *  1001e515   0fb60e           movzx ecx,byte ptr ds:[esi]
   *  1001e518   c1e0 08          shl eax,0x8
   *  1001e51b   0bc1             or eax,ecx
   *  1001e51d   b9 01000000      mov ecx,0x1     ; jichi: hook here
   *  1001e522   03f1             add esi,ecx
   *  1001e524   8945 08          mov dword ptr ss:[ebp+0x8],eax
   *  1001e527   8975 0c          mov dword ptr ss:[ebp+0xc],esi
   *  1001e52a   3d 79810000      cmp eax,0x8179
   *  1001e52f   0f85 9d000000    jnz _18.1001e5d2
   *  1001e535   8b4d f0          mov ecx,dword ptr ss:[ebp-0x10]
   *  1001e538   56               push esi
   *  1001e539   8d55 d0          lea edx,dword ptr ss:[ebp-0x30]
   *  1001e53c   52               push edx
   *  1001e53d   e8 0e0bffff      call _18.1000f050
   *  1001e542   8d4d d0          lea ecx,dword ptr ss:[ebp-0x30]
   *  1001e545   c745 fc 07000000 mov dword ptr ss:[ebp-0x4],0x7
   *  1001e54c   ff15 500a0e10    call dword ptr ds:[0x100e0a50]           ; _19.6a712fa9
   *  1001e552   84c0             test al,al
   *  1001e554   75 67            jnz short _18.1001e5bd
   *  1001e556   8b75 f0          mov esi,dword ptr ss:[ebp-0x10]
   *  1001e559   8d45 d0          lea eax,dword ptr ss:[ebp-0x30]
   *  1001e55c   50               push eax
   *  1001e55d   8bce             mov ecx,esi
   *  1001e55f   c745 e4 01000000 mov dword ptr ss:[ebp-0x1c],0x1
   *  1001e566   c745 e0 00000000 mov dword ptr ss:[ebp-0x20],0x0
   *  1001e56d   e8 5e80ffff      call _18.100165d0
   *  1001e572   0fb7f8           movzx edi,ax
   *  1001e575   57               push edi
   *  1001e576   8bce             mov ecx,esi
   *  1001e578   e8 c380ffff      call _18.10016640
   *  1001e57d   85c0             test eax,eax
   *  1001e57f   74 0d            je short _18.1001e58e
   *  1001e581   f640 38 02       test byte ptr ds:[eax+0x38],0x2
   *  1001e585   74 07            je short _18.1001e58e
   *  1001e587   c745 e0 01000000 mov dword ptr ss:[ebp-0x20],0x1
   *  1001e58e   837d bc 10       cmp dword ptr ss:[ebp-0x44],0x10
   *  1001e592   74 29            je short _18.1001e5bd
   *  1001e594   8b43 28          mov eax,dword ptr ds:[ebx+0x28]
   *  1001e597   85c0             test eax,eax
   */
  bool InsertRUGP2Hook()
  {
    auto module = GetModuleHandleW(L"vm60.dll");
    if (!module /*|| !SafeFillRange(L"vm60.dll", &low, &high)*/)
    {
      ConsoleOutput("rUGP2: vm60.dll does not exist");
      return false;
    }
    const BYTE bytes[] = {
        0x0f, 0xb6, 0x0e,             // 1001e515   0fb60e           movzx ecx,byte ptr ds:[esi]
        0xc1, 0xe0, 0x08,             // 1001e518   c1e0 08          shl eax,0x8
        0x0b, 0xc1,                   // 1001e51b   0bc1             or eax,ecx
        0xb9, 0x01, 0x00, 0x00, 0x00, // 1001e51d   b9 01000000      mov ecx,0x1     ; jichi: hook here
        0x03, 0xf1,                   // 1001e522   03f1             add esi,ecx
        0x89, 0x45, 0x08,             // 1001e524   8945 08          mov dword ptr ss:[ebp+0x8],eax
        0x89, 0x75, 0x0c              // 1001e527   8975 0c          mov dword ptr ss:[ebp+0xc],esi
    };
    enum
    {
      addr_offset = 0x1001e51d - 0x1001e515
    };
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), (DWORD)module, Util::QueryModuleLimits(module).second);
    // GROWL_DWORD(addr);
    if (!addr)
    {
      return false;
    }

    HookParam hp;
    hp.address = addr + addr_offset;
    hp.offset = regoffset(eax);
    hp.type = NO_CONTEXT | CODEC_ANSI_BE;
    return NewHook(hp, "rUGP2");
  }

} // unnamed namespace

namespace
{
  // マブラヴ オルタネイティヴ クロニクルズ04
  bool h3()
  {

    auto low = GetModuleHandleW(L"rvmm.dll");
    if (!low)
      return false;
    auto [s, e] = Util::QueryModuleLimits(low);
    auto caller = findiatcallormov((DWORD)GetGlyphOutlineA, (DWORD)low, s, e);
    ConsoleOutput("%p", caller);
    if (!caller)
      return false;
    auto func = findfuncstart(caller, 0x200, true);
    if (!func)
      return false;
    // a2 == 33088
    BYTE sig[] = {0x81, XX, 0x40, 0x81, 0x00, 0x00};
    if (!MemDbg::findBytes(sig, sizeof(sig), func, caller))
      return false;
    auto refs = findxref_reverse_checkcallop(func, s, e, 0xe8);
    if (refs.size() == 1)
    {
      auto f2 = findfuncstart(refs[0], 0x100, true);
      if (f2)
      {
        HookParam hp;
        hp.address = f2;
        hp.offset = stackoffset(2);
        hp.type = CODEC_ANSI_BE;
        return NewHook(hp, "rUGP3");
      }
    }
    HookParam hp;
    hp.address = func;
    hp.offset = stackoffset(2);
    hp.split = stackoffset(1);
    hp.type = NO_CONTEXT | CODEC_ANSI_BE | USING_SPLIT;
    return NewHook(hp, "rUGP3");
  }
}
static bool GetCachedFont()
{
  // 螺旋回廊 2000版
  auto UnivUI = GetModuleHandleW(L"UnivUI.dll");
  if (!UnivUI)
    return false;
  auto GetCachedFont = GetProcAddress(UnivUI, "?GetCachedFont@CFontAttr@@QAEPAUCS5RFontEntry@@I@Z");
  if (!GetCachedFont)
    return false;
  HookParam hp;
  hp.address = (DWORD)GetCachedFont;
  hp.offset = stackoffset(1);
  hp.type = CODEC_ANSI_BE;
  return NewHook(hp, "UnivUI::GetCachedFont");
}
bool InsertRUGPHook()
{
  return InsertRUGP1Hook() || InsertRUGP2Hook() || GetCachedFont();
}

bool RUGP::attach_function()
{

  return InsertRUGPHook() || h3();
}