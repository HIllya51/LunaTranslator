#include "KiriKiri.h"

namespace kirikiri
{
#pragma pack(push, 4)
#define TJS_VS_SHORT_LEN 21
  typedef int tjs_int; /* at least 32bits */
  typedef wchar_t tjs_char;
  typedef uint32_t tjs_uint32;

  struct tTJSVariantString_S
  {
    tjs_int RefCount; // reference count - 1
    tjs_char *LongString;
    tjs_char ShortString[TJS_VS_SHORT_LEN + 1];
    tjs_int Length; // string length
    tjs_uint32 HeapFlag;
    tjs_uint32 Hint;
  };
#pragma pack(pop)
  class tTJSVariantString : public tTJSVariantString_S
  {
  };
  struct tTJSString_S
  {
    tTJSVariantString *Ptr;
  };
  class tTJSString : public tTJSString_S
  {
  };
  typedef tTJSString ttstr;
#pragma pack(push, 4)
  struct tTVPPoint
  {
    tjs_int x;
    tjs_int y;
  };
#pragma pack(pop)
  struct tTVPRect
  {
    union
    {
      struct
      {
        tjs_int left;
        tjs_int top;
        tjs_int right;
        tjs_int bottom;
      };

      struct
      {
        // capital style
        tjs_int Left;
        tjs_int Top;
        tjs_int Right;
        tjs_int Bottom;
      };

      struct
      {
        tTVPPoint upper_left;
        tTVPPoint bottom_right;
      };
    };
  };
}

bool FindKiriKiriHook(DWORD fun, DWORD size, DWORD pt, DWORD flag) // jichi 10/20/2014: change return value to bool
{
  enum : DWORD
  {
    // jichi 10/20/2014: mov ebp,esp, sub esp,*
    kirikiri1_sig = 0xec8b55,

    // jichi 10/20/2014:
    // 00e01542   53               push ebx
    // 00e01543   56               push esi
    // 00e01544   57               push edi
    kirikiri2_sig = 0x575653
  };
  enum : DWORD
  {
    StartAddress = 0x1000
  };
  enum : DWORD
  {
    StartRange = 0x6000,
    StopRange = 0x8000
  }; // jichi 10/20/2014: ITH original pattern range

  // jichi 10/20/2014: The KiriKiri patterns exist in multiple places of the game.
  // enum : DWORD { StartRange = 0x8000, StopRange = 0x9000 }; // jichi 10/20/2014: change to a different range

  // WCHAR str[0x40];
  DWORD sig = flag ? kirikiri2_sig : kirikiri1_sig;
  DWORD t = 0;
  for (DWORD i = StartAddress; i < size - 4; i++)
    if (*(WORD *)(pt + i) == 0x15ff)
    { // jichi 10/20/2014: call dword ptr ds
      DWORD addr = *(DWORD *)(pt + i + 2);

      // jichi 10/20/2014: There are multiple function calls. The flag+1 one is selected.
      // i.e. KiriKiri1: The first call to GetGlyphOutlineW is selected
      //      KiriKiri2: The second call to GetTextExtentPoint32W is selected
      if (addr >= pt && addr <= pt + size - 4 && *(DWORD *)addr == fun)
        t++;
      if (t == flag + 1) // We find call to GetGlyphOutlineW or GetTextExtentPoint32W.
        // swprintf(str, L"CALL addr:0x%.8X",i+pt);
        // ConsoleOutput(str);
        for (DWORD j = i; j > i - StartAddress; j--)
          if (((*(DWORD *)(pt + j)) & 0xffffff) == sig)
          {
            if (flag)
            {                                                        // We find the function entry. flag indicate 2 hooks.
              t = 0;                                                 // KiriKiri2, we need to find call to this function.
              for (DWORD k = j + StartRange; k < j + StopRange; k++) // Empirical range.
                if (*(BYTE *)(pt + k) == 0xe8)
                {
                  if (k + 5 + *(DWORD *)(pt + k + 1) == j)
                    t++;
                  if (t == 2)
                  {
                    // for (k+=pt+0x14; *(WORD*)(k)!=0xC483;k++);
                    // swprintf(str, L"Hook addr: 0x%.8X",pt+k);
                    // ConsoleOutput(str);
                    HookParam hp;
                    hp.address = pt + k + 0x14;
                    hp.offset = regoffset(ebx);
                    hp.index = -0x2;
                    hp.split = regoffset(ecx);
                    hp.type = CODEC_UTF16 | NO_CONTEXT | USING_SPLIT | DATA_INDIRECT;
                    if (!NewHook(hp, "KiriKiri2"))
                      return false;

                    // https://vndb.org/v5127
                    // 蝶の毒 華の鎖
                    // KiriKiri2被注音的汉字数量若>=2，则会少字。
                    auto addr = pt + k + 0x14 - 5;
                    BYTE check[] = {0x66, 0x85, 0xC0, 0x75}; // mov ax,[ebx]; test ax,ax; jnz
                    if (memcmp(check, (void *)addr, sizeof(check)) == 0)
                    {
                      HookParam hp_1;
                      hp_1.address = addr;
                      hp_1.type = CODEC_UTF16 | NO_CONTEXT | USING_CHAR;
                      hp_1.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
                      {
                        *split = context->ecx;
                        if (*split != 0x16)
                          return;
                        buffer->from_t(*(WORD *)(context->ebx - 2));
                      };
                      NewHook(hp_1, "KiriKiri2X");
                    }

                    return true;
                  }
                }
            }
            else
            {
              // swprintf(str, L"Hook addr: 0x%.8X",pt+j);
              // ConsoleOutput(str);
              HookParam hp;
              hp.address = (DWORD)pt + j;
              hp.offset = regoffset(eax);
              hp.index = 0x14;
              hp.split = regoffset(eax);
              hp.type = CODEC_UTF16 | DATA_INDIRECT | USING_SPLIT | SPLIT_INDIRECT;
              if (!NewHook(hp, "KiriKiri1"))
                return false;
              // 该函数为InternalDrawText
              // 有4个xref， DrawTextMultiple*2，DrawTextSingle*2
              // DrawTextMultiple和DrawTextSingle均只有一个xref->DrawText
              auto xrefs = findxref_reverse_checkcallop(pt + j, processStartAddress, processStopAddress, 0xe8);
              if (xrefs.size() == 4)
                for (auto addr : xrefs)
                {
                  // ConsoleOutput("%p",addr);
                  addr = findfuncstart(addr, 0x300); // DrawTextMultiple or 2，DrawTextSingle
                  // ConsoleOutput("%p",addr);
                  if (addr)
                  {
                    xrefs = findxref_reverse_checkcallop(addr, processStartAddress, processStopAddress, 0xe8);
                    if (xrefs.size() == 1)
                    {
                      addr = xrefs[0];
                      // ConsoleOutput("%p",addr);
                      addr = findfuncstart(addr, 0x300); // DrawText
                      // ConsoleOutput("%p",addr);
                      if (addr)
                      {
                        /*
                        void DrawText(const tTVPRect &destrect, tjs_int x, tjs_int y, const ttstr &text,
                          tjs_uint32 color, tTVPBBBltMethod bltmode, tjs_int opa = 255,
                            bool holdalpha = true, bool aa = true, tjs_int shlevel = 0,
                            tjs_uint32 shadowcolor = 0,
                            tjs_int shwidth = 0, tjs_int shofsx = 0, tjs_int shofsy = 0,
                            tTVPComplexRect *updaterects = NULL)
                            */

                        HookParam hp;
                        hp.address = addr;
                        hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
                        hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
                        {
                          // fastcall, a4
                          auto text = (kirikiri::ttstr *)context->stack[9];
                          auto destrect = (kirikiri::tTVPRect *)context->eax;
                          //*split=destrect->Bottom-destrect->Top;//split by font size;不知道为什么destrect里面的值是乱七八糟的
                          *split = context->ecx; // y. 值似乎不是y，多行不会被分开。
                          buffer->from(text->Ptr->LongString ? text->Ptr->LongString : text->Ptr->ShortString, text->Ptr->Length * 2);
                        };
                        NewHook(hp, "tTVPNativeBaseBitmap::DrawText");
                        return true;
                      }
                    }
                  }
                }
              return true;
            }
            return false;
          }
      // ConsoleOutput("KiriKiri: FAILED to find function entry");
    }
  return false;
}

bool InsertKiriKiriHook() // 9/20/2014 jichi: change return type to bool
{
  bool k1 = FindKiriKiriHook((DWORD)GetGlyphOutlineW, processStopAddress - processStartAddress, processStartAddress, 0),     // KiriKiri1
      k2 = FindKiriKiriHook((DWORD)GetTextExtentPoint32W, processStopAddress - processStartAddress, processStartAddress, 1); // KiriKiri2
  // RegisterEngineType(ENGINE_KIRIKIRI);
  return k1 || k2;
}

/** 10/20/2014 jichi: KAGParser
 *  Sample game: [141128] Venus Blood -HYPNO- ヴィーナスブラッ�・ヒュプノ 体験版
 *
 *  drawText and drawGlyph seem to be the right function to look at.
 *  However, the latest source code does not match VenusBlood.
 *
 *  Debug method:
 *  Pre-compute: hexstr 視界のきかな�utf16, got: 96894c756e304d304b306a304430
 *  Use ollydbg to insert hardware break point before the scene is entered.
 *  It found several places either in game or KAGParser, and the last one is as follows.
 *  It tries to find "[" (0x5b) in the memory.
 *
 *  1. It cannot find character name.
 *  2. It will extract [r].
 *
 *  6e562270   75 0a            jnz short kagparse.6e56227c
 *  6e562272   c705 00000000 00>mov dword ptr ds:[0],0x0
 *  6e56227c   ffb424 24010000  push dword ptr ss:[esp+0x124]
 *  6e562283   ff9424 24010000  call dword ptr ss:[esp+0x124]
 *  6e56228a   8b8c24 20010000  mov ecx,dword ptr ss:[esp+0x120]
 *  6e562291   890d 14ed576e    mov dword ptr ds:[0x6e57ed14],ecx
 *  6e562297   68 3090576e      push kagparse.6e579030                   ; unicode "[r]"
 *  6e56229c   8d46 74          lea eax,dword ptr ds:[esi+0x74]
 *  6e56229f   50               push eax
 *  6e5622a0   ffd1             call ecx
 *  6e5622a2   8b4e 50          mov ecx,dword ptr ds:[esi+0x50]
 *  6e5622a5   8b46 54          mov eax,dword ptr ds:[esi+0x54]
 *  6e5622a8   66:833c48 5b     cmp word ptr ds:[eax+ecx*2],0x5b ; jichi: hook here
 *  6e5622ad   75 06            jnz short kagparse.6e5622b5
 *  6e5622af   8d41 01          lea eax,dword ptr ds:[ecx+0x1]
 *  6e5622b2   8946 50          mov dword ptr ds:[esi+0x50],eax
 *  6e5622b5   ff46 50          inc dword ptr ds:[esi+0x50]
 *  6e5622b8  ^e9 aebcffff      jmp kagparse.6e55df6b
 *  6e5622bd   8d8c24 88030000  lea ecx,dword ptr ss:[esp+0x388]
 *  6e5622c4   e8 b707ffff      call kagparse.6e552a80
 *  6e5622c9   84c0             test al,al
 *  6e5622cb   75 0f            jnz short kagparse.6e5622dc
 *  6e5622cd   8d8424 88030000  lea eax,dword ptr ss:[esp+0x388]
 *  6e5622d4   50               push eax
 *  6e5622d5   8bce             mov ecx,esi
 *  6e5622d7   e8 149bffff      call kagparse.6e55bdf0
 *  6e5622dc   8d8c24 80030000  lea ecx,dword ptr ss:[esp+0x380]
 *  6e5622e3   e8 9807ffff      call kagparse.6e552a80
 *  6e5622e8   84c0             test al,al
 *  6e5622ea   75 0f            jnz short kagparse.6e5622fb
 *  6e5622ec   8d8424 80030000  lea eax,dword ptr ss:[esp+0x380]
 *  6e5622f3   50               push eax
 *  6e5622f4   8bce             mov ecx,esi
 *  6e5622f6   e8 35a0ffff      call kagparse.6e55c330
 *  6e5622fb   8d8c24 c0030000  lea ecx,dword ptr ss:[esp+0x3c0]
 *  6e562302   c68424 c0040000 >mov byte ptr ss:[esp+0x4c0],0x3c
 *  6e56230a   e8 81edfeff      call kagparse.6e551090
 *  6e56230f   8d8c24 80030000  lea ecx,dword ptr ss:[esp+0x380]
 *  6e562316   c68424 c0040000 >mov byte ptr ss:[esp+0x4c0],0x3b
 *  6e56231e   e8 8deefeff      call kagparse.6e5511b0
 *  6e562323   8d8c24 88030000  lea ecx,dword ptr ss:[esp+0x388]
 *  6e56232a   e9 d7000000      jmp kagparse.6e562406
 *  6e56232f   66:837c24 20 00  cmp word ptr ss:[esp+0x20],0x0
 *  6e562335   75 10            jnz short kagparse.6e562347
 *  6e562337   ff46 4c          inc dword ptr ds:[esi+0x4c]
 *  6e56233a   c746 50 00000000 mov dword ptr ds:[esi+0x50],0x0
 *  6e562341   c646 5c 00       mov byte ptr ds:[esi+0x5c],0x0
 *
 *  Runtime regisers:
 *  EAX 09C1A626    text address
 *  ECX 00000000    0 or other offset
 *  EDX 025F1368    this value seems does not change. it is always pointed to 0
 *  EBX 0000300C
 *  ESP 0029EB7C
 *  EBP 0029F044
 *  ESI 04EE4150
 *  EDI 0029F020
 *
 *  とな�KAGParserEx.dll
 *  10013948   68 14830210      push _3.10028314                         ; UNICODE "[r]"
 *  1001394d   83c2 7c          add edx,0x7c
 *  10013950   52               push edx
 *  10013951   ffd0             call eax
 *  10013953   8b75 08          mov esi,dword ptr ss:[ebp+0x8]
 *  10013956   eb 02            jmp short _3.1001395a
 *  10013958   8bf2             mov esi,edx
 *  1001395a   8b46 58          mov eax,dword ptr ds:[esi+0x58]
 *  1001395d   8b4e 5c          mov ecx,dword ptr ds:[esi+0x5c]
 *  10013960   66:833c41 5b     cmp word ptr ds:[ecx+eax*2],0x5b    ; jichi: hook here
 *  10013965   75 06            jnz short _3.1001396d
 *  10013967   83c0 01          add eax,0x1
 *  1001396a   8946 58          mov dword ptr ds:[esi+0x58],eax
 *  1001396d   8346 58 01       add dword ptr ds:[esi+0x58],0x1
 *  10013971   807e 7a 00       cmp byte ptr ds:[esi+0x7a],0x0
 *  10013975  ^0f85 b5a7ffff    jnz _3.1000e130
 *  1001397b   8b45 08          mov eax,dword ptr ss:[ebp+0x8]
 *  1001397e   83b8 90000000 ff cmp dword ptr ds:[eax+0x90],-0x1
 *  10013985   0f84 68040000    je _3.10013df3
 *  1001398b   8bd8             mov ebx,eax
 *  1001398d  ^e9 a1a7ffff      jmp _3.1000e133
 *  10013992   8d7c24 78        lea edi,dword ptr ss:[esp+0x78]
 *  10013996   8d7424 54        lea esi,dword ptr ss:[esp+0x54]
 *  1001399a   e8 e16fffff      call _3.1000a980
 */

#if 0  // not used, as KiriKiriZ is sufficient, and most KiriKiriZ games use KAGParserEx instead of KAGParser.
namespace { // unnamed

bool KAGParserFilter(LPVOID data, size_t *size, HookParam *)
{
  StringFilter(reinterpret_cast<LPWSTR>(data), reinterpret_cast<size_t *>(size), L"[r]", 3);
  return true;
}

void SpecialHookKAGParser(hook_context *context,  HookParam *, uintptr_t *data, uintptr_t *split, size_t*len)
{
  // 6e5622a8   66:833c48 5b     cmp word ptr ds:[eax+ecx*2],0x5b
  DWORD eax = regof(eax, esp_base),
        ecx = regof(ecx, esp_base);
  if (eax && !ecx) { // skip string when ecx is not zero
    *data = eax;
    *len = ::wcslen((LPCWSTR)eax) * 2; // 2 == sizeof(wchar_t)
    *split = FIXED_SPLIT_VALUE; // merge all threads
  }
}

void SpecialHookKAGParserEx(hook_context *context,  HookParam *, uintptr_t *data, uintptr_t *split, size_t*len)
{
  // 10013960   66:833c41 5b     cmp word ptr ds:[ecx+eax*2],0x5b
  DWORD eax = regof(eax, esp_base),
        ecx = regof(ecx, esp_base);
  if (ecx && !eax) { // skip string when ecx is not zero
    *data = ecx;
    *len = ::wcslen((LPCWSTR)ecx) * 2; // 2 == sizeof(wchar_t)
    *split = FIXED_SPLIT_VALUE; // merge all threads
  }
}
} // unnamed namespace
bool InsertKAGParserHook()
{
  ULONG processStartAddress, processStopAddress;
  if (!NtInspect::getModuleMemoryRange(L"KAGParser.dll", &startAddress, &stopAddress)) {
    ConsoleOutput("KAGParser: failed to get memory range");
    return false;
  }
  const wchar_t *patternString = L"[r]";
  const size_t patternStringSize = ::wcslen(patternString) * 2;
  ULONG addr = MemDbg::findBytes(patternString, patternStringSize, processStartAddress, processStopAddress);
  if (!addr) {
    ConsoleOutput("KAGParser: [r] global string not found");
    return false;
  }
  // Find where it is used as function parameter
  addr = MemDbg::findPushAddress(addr, processStartAddress, processStopAddress);
  if (!addr) {
    ConsoleOutput("KAGParser: push address not found");
    return false;
  }

  const BYTE ins[] = {
    0x66,0x83,0x3c,0x48, 0x5b // 6e5622a8   66:833c48 5b   cmp word ptr ds:[eax+ecx*2],0x5b ; jichi: hook here
  };
  enum { range = 0x20 }; // 0x6e5622a8 - 0x6e562297 = 17
  addr = MemDbg::findBytes(ins, sizeof(ins), addr, addr + range);
  if (!addr) {
    ConsoleOutput("KAGParser: instruction pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.text_fun = SpecialHookKAGParser;
  hp.filter_fun = KAGParserFilter;
  hp.type = CODEC_UTF16|FIXING_SPLIT|NO_CONTEXT; // Fix the split value to merge all threads
  ConsoleOutput("INSERT KAGParser");
  
  return NewHook(hp, "KAGParser");
}
bool InsertKAGParserExHook()
{
  ULONG processStartAddress, processStopAddress;
  if (!NtInspect::getModuleMemoryRange(L"KAGParserEx.dll", &startAddress, &stopAddress)) {
    ConsoleOutput("KAGParserEx: failed to get memory range");
    return false;
  }
  const wchar_t *patternString = L"[r]";
  const size_t patternStringSize = ::wcslen(patternString) * 2;
  ULONG addr = MemDbg::findBytes(patternString, patternStringSize, processStartAddress, processStopAddress);
  if (!addr) {
    ConsoleOutput("KAGParserEx: [r] global string not found");
    return false;
  }
  // Find where it is used as function parameter
  addr = MemDbg::findPushAddress(addr, processStartAddress, processStopAddress);
  if (!addr) {
    ConsoleOutput("KAGParserEx: push address not found");
    return false;
  }

  const BYTE ins[] = {
    0x66,0x83,0x3c,0x41, 0x5b // 10013960   66:833c41 5b     cmp word ptr ds:[ecx+eax*2],0x5b    ; jichi: hook here
  };
  enum { range = 0x20 }; // 0x10013960 - 0x10013948 = 24
  addr = MemDbg::findBytes(ins, sizeof(ins), addr, addr + range);
  if (!addr) {
    ConsoleOutput("KAGParserEx: instruction pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.text_fun = SpecialHookKAGParserEx;
  hp.filter_fun = KAGParserFilter;
  hp.type = CODEC_UTF16|FIXING_SPLIT|NO_CONTEXT; // Fix the split value to merge all threads
  ConsoleOutput("INSERT KAGParserEx");
  
  return NewHook(hp, "KAGParserEx");
}
#endif // 0

/** 10/24/2014 jichi: New KiriKiri hook
 *  Sample game: [141128] Venus Blood -HYPNO- ヴィーナスブラッ�・ヒュプノ 体験版
 *
 *  This engine will hook to the caller of caller of the first GetGlyphOutlineW (totally three).
 *  The logic is quite similar to KiriKiri1 except it backtrack twice to get the function call.
 *
 *  1/31/2015: If the game no longer invoke GDI functions by default, one way to find the hook
 *  is to click the フォン�in the menu to force triggering GetGlyphOutlineW function.
 *
 *  KiriKiriZ:
 *  https://github.com/krkrz/krkrz
 *  http://krkrz.github.io
 *
 *  KiriKiri API: http://devdoc.kikyou.info/tvp/docs/kr2doc/contents/f_Layer.html
 *
 *  See: krkrz/src/core/visual/LayerIntf.cpp
 *  API: http://devdoc.kikyou.info/tvp/docs/kr2doc/contents/f_Layer_drawText.html
 *
 *  Debug method:
 *  Backtrack from GetGlyphOutlineW, and find the first function that is invoked more
 *  times than (cached) GetGlyphOutlineW.
 *
 *  - Find function calls to GetGlyphOutlineW (totally three)
 *
 *  - Find the caller of the first GetGlyphOutlineW
 *    Using MemDbg::findCallerAddressAfterInt3()
 *
 *  - Find the caller of the above caller
 *    Since the function address is dynamic, the function is found using KiriKiriZHook
 *
 *    00377c44   8b01             mov eax,dword ptr ds:[ecx]
 *    00377c46   ff75 10          push dword ptr ss:[ebp+0x10]
 *    00377c49   ff75 0c          push dword ptr ss:[ebp+0xc]
 *    00377c4c   53               push ebx
 *    00377c4d   ff50 1c          call dword ptr ds:[eax+0x1c] ; jichi: called here
 *    00377c50   8bf0             mov esi,eax
 *    00377c52   8975 e4          mov dword ptr ss:[ebp-0x1c],esi
 *    00377c55   ff46 04          inc dword ptr ds:[esi+0x4]
 *    00377c58   c745 fc 04000000 mov dword ptr ss:[ebp-0x4],0x4
 *
 *  Then, the UTF8 two-byte character is at [ecx]+0x14
 *    0017E950  16 00 00 00 00 02 00 00 00 00 00 00 98 D2 76 02
 *    0017E960  E0 8E 90 D9 42 7D 00 00 00 02 00 00 01 00 00 00
 *                          up: text here
 *    0017E970  01 00 01 FF 00 00 00 00 00 00 00 00 C8
 *
 *  1/30/2015:
 *  The hooked function in Venus Blood -HYPNO- is as follows.
 *  Since サノバウィッ� (150226), KiriKiriZ no longer invokes GetGlyphOutlineW.
 *  Try to extract instruction patterns from the following function instead.
 *
 *  011a7a3c   cc               int3
 *  011a7a3d   cc               int3
 *  011a7a3e   cc               int3
 *  011a7a3f   cc               int3
 *  011a7a40   55               push ebp
 *  011a7a41   8bec             mov ebp,esp
 *  011a7a43   6a ff            push -0x1
 *  011a7a45   68 dbaa3101      push .0131aadb
 *  011a7a4a   64:a1 00000000   mov eax,dword ptr fs:[0]
 *  011a7a50   50               push eax
 *  011a7a51   83ec 14          sub esp,0x14
 *  011a7a54   53               push ebx
 *  011a7a55   56               push esi
 *  011a7a56   57               push edi
 *  011a7a57   a1 00593d01      mov eax,dword ptr ds:[0x13d5900]
 *  011a7a5c   33c5             xor eax,ebp
 *  011a7a5e   50               push eax
 *  011a7a5f   8d45 f4          lea eax,dword ptr ss:[ebp-0xc]
 *  011a7a62   64:a3 00000000   mov dword ptr fs:[0],eax
 *  011a7a68   8965 f0          mov dword ptr ss:[ebp-0x10],esp
 *  011a7a6b   8bd9             mov ebx,ecx
 *  011a7a6d   803d 00113e01 00 cmp byte ptr ds:[0x13e1100],0x0
 *  011a7a74   75 17            jnz short .011a7a8d
 *  011a7a76   c745 e8 1cb83d01 mov dword ptr ss:[ebp-0x18],.013db81c
 *  011a7a7d   8d45 e8          lea eax,dword ptr ss:[ebp-0x18]
 *  011a7a80   50               push eax
 *  011a7a81   e8 4ae2f0ff      call .010b5cd0
 *  011a7a86   c605 00113e01 01 mov byte ptr ds:[0x13e1100],0x1
 *  011a7a8d   33c9             xor ecx,ecx
 *  011a7a8f   384b 21          cmp byte ptr ds:[ebx+0x21],cl
 *  011a7a92   0f95c1           setne cl
 *  011a7a95   33c0             xor eax,eax
 *  011a7a97   3843 20          cmp byte ptr ds:[ebx+0x20],al
 *  011a7a9a   0f95c0           setne al
 *  011a7a9d   33c8             xor ecx,eax
 *  011a7a9f   334b 10          xor ecx,dword ptr ds:[ebx+0x10]
 *  011a7aa2   0fb743 14        movzx eax,word ptr ds:[ebx+0x14]
 *  011a7aa6   33c8             xor ecx,eax
 *  011a7aa8   8b7b 1c          mov edi,dword ptr ds:[ebx+0x1c]
 *  011a7aab   33f9             xor edi,ecx
 *  011a7aad   337b 18          xor edi,dword ptr ds:[ebx+0x18]
 *  011a7ab0   897d e4          mov dword ptr ss:[ebp-0x1c],edi
 *  011a7ab3   57               push edi
 *  011a7ab4   53               push ebx
 *  011a7ab5   e8 06330000      call .011aadc0
 *  011a7aba   8bf0             mov esi,eax
 *  011a7abc   85f6             test esi,esi
 *  011a7abe   74 26            je short .011a7ae6
 *  011a7ac0   56               push esi
 *  011a7ac1   e8 ba330000      call .011aae80
 *  011a7ac6   8d46 2c          lea eax,dword ptr ds:[esi+0x2c]
 *  011a7ac9   85c0             test eax,eax
 *  011a7acb   74 19            je short .011a7ae6
 *  011a7acd   8b08             mov ecx,dword ptr ds:[eax]
 *  011a7acf   ff41 04          inc dword ptr ds:[ecx+0x4]
 *  011a7ad2   8b00             mov eax,dword ptr ds:[eax]
 *  011a7ad4   8b4d f4          mov ecx,dword ptr ss:[ebp-0xc]
 *  011a7ad7   64:890d 00000000 mov dword ptr fs:[0],ecx
 *  011a7ade   59               pop ecx
 *  011a7adf   5f               pop edi
 *  011a7ae0   5e               pop esi
 *  011a7ae1   5b               pop ebx
 *  011a7ae2   8be5             mov esp,ebp
 *  011a7ae4   5d               pop ebp
 *  011a7ae5   c3               retn
 *  011a7ae6   8b4d 08          mov ecx,dword ptr ss:[ebp+0x8]
 *  011a7ae9   85c9             test ecx,ecx
 *  011a7aeb   0f84 47010000    je .011a7c38
 *  011a7af1   0fb743 14        movzx eax,word ptr ds:[ebx+0x14]
 *  011a7af5   50               push eax
 *  011a7af6   e8 b5090300      call .011d84b0
 *  011a7afb   8bf0             mov esi,eax
 *  011a7afd   8975 ec          mov dword ptr ss:[ebp-0x14],esi
 *  011a7b00   85f6             test esi,esi
 *  011a7b02   0f84 30010000    je .011a7c38
 *  011a7b08   6a 34            push 0x34
 *  011a7b0a   e8 29621300      call .012ddd38
 *  011a7b0f   83c4 04          add esp,0x4
 *  011a7b12   8bf8             mov edi,eax
 *  011a7b14   897d e0          mov dword ptr ss:[ebp-0x20],edi
 *  011a7b17   c745 fc 00000000 mov dword ptr ss:[ebp-0x4],0x0
 *  011a7b1e   85ff             test edi,edi
 *  011a7b20   74 1d            je short .011a7b3f
 *  011a7b22   c747 2c 41000000 mov dword ptr ds:[edi+0x2c],0x41
 *  011a7b29   c647 32 00       mov byte ptr ds:[edi+0x32],0x0
 *  011a7b2d   c747 04 01000000 mov dword ptr ds:[edi+0x4],0x1
 *  011a7b34   c707 00000000    mov dword ptr ds:[edi],0x0
 *  011a7b3a   8945 e8          mov dword ptr ss:[ebp-0x18],eax
 *  011a7b3d   eb 05            jmp short .011a7b44
 *  011a7b3f   33ff             xor edi,edi
 *  011a7b41   897d e8          mov dword ptr ss:[ebp-0x18],edi
 *  011a7b44   c745 fc ffffffff mov dword ptr ss:[ebp-0x4],-0x1
 *  011a7b4b   0fb746 04        movzx eax,word ptr ds:[esi+0x4]
 *  011a7b4f   8947 1c          mov dword ptr ds:[edi+0x1c],eax
 *  011a7b52   0fb746 06        movzx eax,word ptr ds:[esi+0x6]
 *  011a7b56   8947 20          mov dword ptr ds:[edi+0x20],eax
 *  011a7b59   0fbf46 0c        movsx eax,word ptr ds:[esi+0xc]
 *  011a7b5d   8947 10          mov dword ptr ds:[edi+0x10],eax
 *  011a7b60   0fbf46 0e        movsx eax,word ptr ds:[esi+0xe]
 *  011a7b64   8947 14          mov dword ptr ds:[edi+0x14],eax
 *  011a7b67   0fbf46 08        movsx eax,word ptr ds:[esi+0x8]
 *  011a7b6b   0345 0c          add eax,dword ptr ss:[ebp+0xc]
 *  011a7b6e   8947 08          mov dword ptr ds:[edi+0x8],eax
 *  011a7b71   0fbf46 0a        movsx eax,word ptr ds:[esi+0xa]
 *  011a7b75   8b4d 10          mov ecx,dword ptr ss:[ebp+0x10]
 *  011a7b78   2bc8             sub ecx,eax
 *  011a7b7a   894f 0c          mov dword ptr ds:[edi+0xc],ecx
 *  011a7b7d   0fb643 20        movzx eax,byte ptr ds:[ebx+0x20]
 *  011a7b81   8847 30          mov byte ptr ds:[edi+0x30],al
 *  011a7b84   c647 32 00       mov byte ptr ds:[edi+0x32],0x0
 *  011a7b88   0fb643 21        movzx eax,byte ptr ds:[ebx+0x21]
 *  011a7b8c   8847 31          mov byte ptr ds:[edi+0x31],al
 *  011a7b8f   8b43 1c          mov eax,dword ptr ds:[ebx+0x1c]
 *  011a7b92   8947 28          mov dword ptr ds:[edi+0x28],eax
 *  011a7b95   8b43 18          mov eax,dword ptr ds:[ebx+0x18]
 *  011a7b98   8947 24          mov dword ptr ds:[edi+0x24],eax
 *  011a7b9b   c745 fc 01000000 mov dword ptr ss:[ebp-0x4],0x1
 *  011a7ba2   837f 1c 00       cmp dword ptr ds:[edi+0x1c],0x0
 *  011a7ba6   74 64            je short .011a7c0c
 *  011a7ba8   8b47 20          mov eax,dword ptr ds:[edi+0x20]
 *  011a7bab   85c0             test eax,eax
 *  011a7bad   74 5d            je short .011a7c0c
 *  011a7baf   0fb776 04        movzx esi,word ptr ds:[esi+0x4]
 *  011a7bb3   4e               dec esi
 *  011a7bb4   83e6 fc          and esi,0xfffffffc
 *  011a7bb7   83c6 04          add esi,0x4
 *  011a7bba   8977 18          mov dword ptr ds:[edi+0x18],esi
 *  011a7bbd   0fafc6           imul eax,esi
 *  011a7bc0   50               push eax
 *  011a7bc1   8bcf             mov ecx,edi
 *  011a7bc3   e8 b8f6ffff      call .011a7280
 *  011a7bc8   56               push esi
 *  011a7bc9   ff37             push dword ptr ds:[edi]
 *  011a7bcb   ff75 ec          push dword ptr ss:[ebp-0x14]
 *  011a7bce   8b4d 08          mov ecx,dword ptr ss:[ebp+0x8]
 *  011a7bd1   e8 3a090300      call .011d8510
 *  011a7bd6   807b 21 00       cmp byte ptr ds:[ebx+0x21],0x0
 *  011a7bda   74 0d            je short .011a7be9
 *  011a7bdc   ff77 28          push dword ptr ds:[edi+0x28]
 *  011a7bdf   ff77 24          push dword ptr ds:[edi+0x24]
 *  011a7be2   8bcf             mov ecx,edi
 *  011a7be4   e8 d70affff      call .011986c0
 *  011a7be9   897d ec          mov dword ptr ss:[ebp-0x14],edi
 *  011a7bec   ff47 04          inc dword ptr ds:[edi+0x4]
 *  011a7bef   c645 fc 02       mov byte ptr ss:[ebp-0x4],0x2
 *  011a7bf3   8d45 ec          lea eax,dword ptr ss:[ebp-0x14]
 *  011a7bf6   50               push eax
 *  011a7bf7   ff75 e4          push dword ptr ss:[ebp-0x1c]
 *  011a7bfa   53               push ebx
 *  011a7bfb   e8 50280000      call .011aa450
 *  011a7c00   c645 fc 01       mov byte ptr ss:[ebp-0x4],0x1
 *  011a7c04   8d4d ec          lea ecx,dword ptr ss:[ebp-0x14]
 *  011a7c07   e8 84280000      call .011aa490
 *  011a7c0c   c745 fc ffffffff mov dword ptr ss:[ebp-0x4],-0x1
 *  011a7c13   8bc7             mov eax,edi
 *  011a7c15   8b4d f4          mov ecx,dword ptr ss:[ebp-0xc]
 *  011a7c18   64:890d 00000000 mov dword ptr fs:[0],ecx
 *  011a7c1f   59               pop ecx
 *  011a7c20   5f               pop edi
 *  011a7c21   5e               pop esi
 *  011a7c22   5b               pop ebx
 *  011a7c23   8be5             mov esp,ebp
 *  011a7c25   5d               pop ebp
 *  011a7c26   c3               retn
 *  011a7c27   8b4d e8          mov ecx,dword ptr ss:[ebp-0x18]
 *  011a7c2a   e8 81f6ffff      call .011a72b0
 *  011a7c2f   6a 00            push 0x0
 *  011a7c31   6a 00            push 0x0
 *  011a7c33   e8 93cb1300      call .012e47cb
 *  011a7c38   a1 dc8a3d01      mov eax,dword ptr ds:[0x13d8adc]
 *  011a7c3d   8b0c85 88b93f01  mov ecx,dword ptr ds:[eax*4+0x13fb988]
 *  011a7c44   8b01             mov eax,dword ptr ds:[ecx]
 *  011a7c46   ff75 10          push dword ptr ss:[ebp+0x10]
 *  011a7c49   ff75 0c          push dword ptr ss:[ebp+0xc]
 *  011a7c4c   53               push ebx
 *  011a7c4d   ff50 1c          call dword ptr ds:[eax+0x1c]
 *  011a7c50   8bf0             mov esi,eax
 *  011a7c52   8975 e4          mov dword ptr ss:[ebp-0x1c],esi
 *  011a7c55   ff46 04          inc dword ptr ds:[esi+0x4]
 *  011a7c58   c745 fc 04000000 mov dword ptr ss:[ebp-0x4],0x4
 *  011a7c5f   8d45 e4          lea eax,dword ptr ss:[ebp-0x1c]
 *  011a7c62   50               push eax
 *  011a7c63   57               push edi
 *  011a7c64   53               push ebx
 *  011a7c65   e8 a62c0000      call .011aa910
 *  011a7c6a   a1 388b3f01      mov eax,dword ptr ds:[0x13f8b38]
 *  011a7c6f   8b0d 448b3f01    mov ecx,dword ptr ds:[0x13f8b44]
 *  011a7c75   3bc1             cmp eax,ecx
 *  011a7c77   76 08            jbe short .011a7c81
 *  011a7c79   2bc1             sub eax,ecx
 *  011a7c7b   50               push eax
 *  011a7c7c   e8 1f2e0000      call .011aaaa0
 *  011a7c81   c745 fc ffffffff mov dword ptr ss:[ebp-0x4],-0x1
 *  011a7c88   8b46 04          mov eax,dword ptr ds:[esi+0x4]
 *  011a7c8b   83f8 01          cmp eax,0x1
 *  011a7c8e   75 2c            jnz short .011a7cbc
 *  011a7c90   8b06             mov eax,dword ptr ds:[esi]
 *  011a7c92   85c0             test eax,eax
 *  011a7c94   74 09            je short .011a7c9f
 *  011a7c96   50               push eax
 *  011a7c97   e8 3b621300      call .012dded7
 *  011a7c9c   83c4 04          add esp,0x4
 *  011a7c9f   56               push esi
 *  011a7ca0   e8 335e1300      call .012ddad8
 *  011a7ca5   83c4 04          add esp,0x4
 *  011a7ca8   8bc6             mov eax,esi
 *  011a7caa   8b4d f4          mov ecx,dword ptr ss:[ebp-0xc]
 *  011a7cad   64:890d 00000000 mov dword ptr fs:[0],ecx
 *  011a7cb4   59               pop ecx
 *  011a7cb5   5f               pop edi
 *  011a7cb6   5e               pop esi
 *  011a7cb7   5b               pop ebx
 *  011a7cb8   8be5             mov esp,ebp
 *  011a7cba   5d               pop ebp
 *  011a7cbb   c3               retn
 *  011a7cbc   48               dec eax
 *  011a7cbd   8946 04          mov dword ptr ds:[esi+0x4],eax
 *  011a7cc0   8bc6             mov eax,esi
 *  011a7cc2   8b4d f4          mov ecx,dword ptr ss:[ebp-0xc]
 *  011a7cc5   64:890d 00000000 mov dword ptr fs:[0],ecx
 *  011a7ccc   59               pop ecx
 *  011a7ccd   5f               pop edi
 *  011a7cce   5e               pop esi
 *  011a7ccf   5b               pop ebx
 *  011a7cd0   8be5             mov esp,ebp
 *  011a7cd2   5d               pop ebp
 *  011a7cd3   c3               retn
 *  011a7cd4   cc               int3
 *  011a7cd5   cc               int3
 *  011a7cd6   cc               int3
 *  011a7cd7   cc               int3
 *  011a7cd8   cc               int3
 *
 *  Here's the hooked function in サノバウィッ� (150226).
 *  I randomly picked a pattern from VBH:
 *
 *    011a7a95   33c0             xor eax,eax
 *    011a7a97   3843 20          cmp byte ptr ds:[ebx+0x20],al
 *    011a7a9a   0f95c0           setne al
 *    011a7a9d   33c8             xor ecx,eax
 *    011a7a9f   334b 10          xor ecx,dword ptr ds:[ebx+0x10]
 *    011a7aa2   0fb743 14        movzx eax,word ptr ds:[ebx+0x14]
 *
 *  i.e: 33c03843200f95c033c8334b100fb74314
 *
 *  The new hooked function in サノバウィッ� is as follows.
 *
 *  012280dc   cc               int3
 *  012280dd   cc               int3
 *  012280de   cc               int3
 *  012280df   cc               int3
 *  012280e0   55               push ebp
 *  012280e1   8bec             mov ebp,esp
 *  012280e3   6a ff            push -0x1
 *  012280e5   68 3b813d01      push .013d813b
 *  012280ea   64:a1 00000000   mov eax,dword ptr fs:[0]
 *  012280f0   50               push eax
 *  012280f1   83ec 14          sub esp,0x14
 *  012280f4   53               push ebx
 *  012280f5   56               push esi
 *  012280f6   57               push edi
 *  012280f7   a1 00694901      mov eax,dword ptr ds:[0x1496900]
 *  012280fc   33c5             xor eax,ebp
 *  012280fe   50               push eax
 *  012280ff   8d45 f4          lea eax,dword ptr ss:[ebp-0xc]
 *  01228102   64:a3 00000000   mov dword ptr fs:[0],eax
 *  01228108   8965 f0          mov dword ptr ss:[ebp-0x10],esp
 *  0122810b   8bd9             mov ebx,ecx
 *  0122810d   803d e82d4a01 00 cmp byte ptr ds:[0x14a2de8],0x0
 *  01228114   75 17            jnz short .0122812d
 *  01228116   c745 e8 d8d44901 mov dword ptr ss:[ebp-0x18],.0149d4d8
 *  0122811d   8d45 e8          lea eax,dword ptr ss:[ebp-0x18]
 *  01228120   50               push eax
 *  01228121   e8 aadbf0ff      call .01135cd0
 *  01228126   c605 e82d4a01 01 mov byte ptr ds:[0x14a2de8],0x1
 *  0122812d   33c9             xor ecx,ecx
 *  0122812f   384b 21          cmp byte ptr ds:[ebx+0x21],cl
 *  01228132   0f95c1           setne cl
 *  01228135   33c0             xor eax,eax
 *  01228137   3843 20          cmp byte ptr ds:[ebx+0x20],al
 *  0122813a   0f95c0           setne al
 *  0122813d   33c8             xor ecx,eax
 *  0122813f   334b 10          xor ecx,dword ptr ds:[ebx+0x10]
 *  01228142   0fb743 14        movzx eax,word ptr ds:[ebx+0x14]
 *  01228146   33c8             xor ecx,eax
 *  01228148   8b7b 1c          mov edi,dword ptr ds:[ebx+0x1c]
 *  0122814b   33f9             xor edi,ecx
 *  0122814d   337b 18          xor edi,dword ptr ds:[ebx+0x18]
 *  01228150   897d e4          mov dword ptr ss:[ebp-0x1c],edi
 *  01228153   57               push edi
 *  01228154   53               push ebx
 *  01228155   e8 06330000      call .0122b460
 *  0122815a   8bf0             mov esi,eax
 *  0122815c   85f6             test esi,esi
 *  0122815e   74 26            je short .01228186
 *  01228160   56               push esi
 *  01228161   e8 ba330000      call .0122b520
 *  01228166   8d46 2c          lea eax,dword ptr ds:[esi+0x2c]
 *  01228169   85c0             test eax,eax
 *  0122816b   74 19            je short .01228186
 *  0122816d   8b08             mov ecx,dword ptr ds:[eax]
 *  0122816f   ff41 04          inc dword ptr ds:[ecx+0x4]
 *  01228172   8b00             mov eax,dword ptr ds:[eax]
 *  01228174   8b4d f4          mov ecx,dword ptr ss:[ebp-0xc]
 *  01228177   64:890d 00000000 mov dword ptr fs:[0],ecx
 *  0122817e   59               pop ecx
 *  0122817f   5f               pop edi
 *  01228180   5e               pop esi
 *  01228181   5b               pop ebx
 *  01228182   8be5             mov esp,ebp
 *  01228184   5d               pop ebp
 *  01228185   c3               retn
 *  01228186   8b4d 08          mov ecx,dword ptr ss:[ebp+0x8]
 *  01228189   85c9             test ecx,ecx
 *  0122818b   0f84 47010000    je .012282d8
 *  01228191   0fb743 14        movzx eax,word ptr ds:[ebx+0x14]
 *  01228195   50               push eax
 *  01228196   e8 950f0300      call .01259130
 *  0122819b   8bf0             mov esi,eax
 *  0122819d   8975 ec          mov dword ptr ss:[ebp-0x14],esi
 *  012281a0   85f6             test esi,esi
 *  012281a2   0f84 30010000    je .012282d8
 *  012281a8   6a 34            push 0x34
 *  012281aa   e8 297c1300      call .0135fdd8
 *  012281af   83c4 04          add esp,0x4
 *  012281b2   8bf8             mov edi,eax
 *  012281b4   897d e0          mov dword ptr ss:[ebp-0x20],edi
 *  012281b7   c745 fc 00000000 mov dword ptr ss:[ebp-0x4],0x0
 *  012281be   85ff             test edi,edi
 *  012281c0   74 1d            je short .012281df
 *  012281c2   c747 2c 41000000 mov dword ptr ds:[edi+0x2c],0x41
 *  012281c9   c647 32 00       mov byte ptr ds:[edi+0x32],0x0
 *  012281cd   c747 04 01000000 mov dword ptr ds:[edi+0x4],0x1
 *  012281d4   c707 00000000    mov dword ptr ds:[edi],0x0
 *  012281da   8945 e8          mov dword ptr ss:[ebp-0x18],eax
 *  012281dd   eb 05            jmp short .012281e4
 *  012281df   33ff             xor edi,edi
 *  012281e1   897d e8          mov dword ptr ss:[ebp-0x18],edi
 *  012281e4   c745 fc ffffffff mov dword ptr ss:[ebp-0x4],-0x1
 *  012281eb   0fb746 04        movzx eax,word ptr ds:[esi+0x4]
 *  012281ef   8947 1c          mov dword ptr ds:[edi+0x1c],eax
 *  012281f2   0fb746 06        movzx eax,word ptr ds:[esi+0x6]
 *  012281f6   8947 20          mov dword ptr ds:[edi+0x20],eax
 *  012281f9   0fbf46 0c        movsx eax,word ptr ds:[esi+0xc]
 *  012281fd   8947 10          mov dword ptr ds:[edi+0x10],eax
 *  01228200   0fbf46 0e        movsx eax,word ptr ds:[esi+0xe]
 *  01228204   8947 14          mov dword ptr ds:[edi+0x14],eax
 *  01228207   0fbf46 08        movsx eax,word ptr ds:[esi+0x8]
 *  0122820b   0345 0c          add eax,dword ptr ss:[ebp+0xc]
 *  0122820e   8947 08          mov dword ptr ds:[edi+0x8],eax
 *  01228211   0fbf46 0a        movsx eax,word ptr ds:[esi+0xa]
 *  01228215   8b4d 10          mov ecx,dword ptr ss:[ebp+0x10]
 *  01228218   2bc8             sub ecx,eax
 *  0122821a   894f 0c          mov dword ptr ds:[edi+0xc],ecx
 *  0122821d   0fb643 20        movzx eax,byte ptr ds:[ebx+0x20]
 *  01228221   8847 30          mov byte ptr ds:[edi+0x30],al
 *  01228224   c647 32 00       mov byte ptr ds:[edi+0x32],0x0
 *  01228228   0fb643 21        movzx eax,byte ptr ds:[ebx+0x21]
 *  0122822c   8847 31          mov byte ptr ds:[edi+0x31],al
 *  0122822f   8b43 1c          mov eax,dword ptr ds:[ebx+0x1c]
 *  01228232   8947 28          mov dword ptr ds:[edi+0x28],eax
 *  01228235   8b43 18          mov eax,dword ptr ds:[ebx+0x18]
 *  01228238   8947 24          mov dword ptr ds:[edi+0x24],eax
 *  0122823b   c745 fc 01000000 mov dword ptr ss:[ebp-0x4],0x1
 *  01228242   837f 1c 00       cmp dword ptr ds:[edi+0x1c],0x0
 *  01228246   74 64            je short .012282ac
 *  01228248   8b47 20          mov eax,dword ptr ds:[edi+0x20]
 *  0122824b   85c0             test eax,eax
 *  0122824d   74 5d            je short .012282ac
 *  0122824f   0fb776 04        movzx esi,word ptr ds:[esi+0x4]
 *  01228253   4e               dec esi
 *  01228254   83e6 fc          and esi,0xfffffffc
 *  01228257   83c6 04          add esi,0x4
 *  0122825a   8977 18          mov dword ptr ds:[edi+0x18],esi
 *  0122825d   0fafc6           imul eax,esi
 *  01228260   50               push eax
 *  01228261   8bcf             mov ecx,edi
 *  01228263   e8 a8f6ffff      call .01227910
 *  01228268   56               push esi
 *  01228269   ff37             push dword ptr ds:[edi]
 *  0122826b   ff75 ec          push dword ptr ss:[ebp-0x14]
 *  0122826e   8b4d 08          mov ecx,dword ptr ss:[ebp+0x8]
 *  01228271   e8 1a0f0300      call .01259190
 *  01228276   807b 21 00       cmp byte ptr ds:[ebx+0x21],0x0
 *  0122827a   74 0d            je short .01228289
 *  0122827c   ff77 28          push dword ptr ds:[edi+0x28]
 *  0122827f   ff77 24          push dword ptr ds:[edi+0x24]
 *  01228282   8bcf             mov ecx,edi
 *  01228284   e8 870affff      call .01218d10
 *  01228289   897d ec          mov dword ptr ss:[ebp-0x14],edi
 *  0122828c   ff47 04          inc dword ptr ds:[edi+0x4]
 *  0122828f   c645 fc 02       mov byte ptr ss:[ebp-0x4],0x2
 *  01228293   8d45 ec          lea eax,dword ptr ss:[ebp-0x14]
 *  01228296   50               push eax
 *  01228297   ff75 e4          push dword ptr ss:[ebp-0x1c]
 *  0122829a   53               push ebx
 *  0122829b   e8 50280000      call .0122aaf0
 *  012282a0   c645 fc 01       mov byte ptr ss:[ebp-0x4],0x1
 *  012282a4   8d4d ec          lea ecx,dword ptr ss:[ebp-0x14]
 *  012282a7   e8 84280000      call .0122ab30
 *  012282ac   c745 fc ffffffff mov dword ptr ss:[ebp-0x4],-0x1
 *  012282b3   8bc7             mov eax,edi
 *  012282b5   8b4d f4          mov ecx,dword ptr ss:[ebp-0xc]
 *  012282b8   64:890d 00000000 mov dword ptr fs:[0],ecx
 *  012282bf   59               pop ecx
 *  012282c0   5f               pop edi
 *  012282c1   5e               pop esi
 *  012282c2   5b               pop ebx
 *  012282c3   8be5             mov esp,ebp
 *  012282c5   5d               pop ebp
 *  012282c6   c3               retn
 *  012282c7   8b4d e8          mov ecx,dword ptr ss:[ebp-0x18]
 *  012282ca   e8 71f6ffff      call .01227940
 *  012282cf   6a 00            push 0x0
 *  012282d1   6a 00            push 0x0
 *  012282d3   e8 83eb1300      call .01366e5b
 *  012282d8   a1 e89a4901      mov eax,dword ptr ds:[0x1499ae8]
 *  012282dd   8b0c85 f0d64b01  mov ecx,dword ptr ds:[eax*4+0x14bd6f0]
 *  012282e4   8b01             mov eax,dword ptr ds:[ecx]
 *  012282e6   ff75 10          push dword ptr ss:[ebp+0x10]
 *  012282e9   ff75 0c          push dword ptr ss:[ebp+0xc]
 *  012282ec   53               push ebx
 *  012282ed   ff50 1c          call dword ptr ds:[eax+0x1c]
 *  012282f0   8bf0             mov esi,eax
 *  012282f2   8975 e4          mov dword ptr ss:[ebp-0x1c],esi
 *  012282f5   ff46 04          inc dword ptr ds:[esi+0x4]
 *  012282f8   c745 fc 04000000 mov dword ptr ss:[ebp-0x4],0x4
 *  012282ff   8d45 e4          lea eax,dword ptr ss:[ebp-0x1c]
 *  01228302   50               push eax
 *  01228303   57               push edi
 *  01228304   53               push ebx
 *  01228305   e8 a62c0000      call .0122afb0
 *  0122830a   a1 a0a84b01      mov eax,dword ptr ds:[0x14ba8a0]
 *  0122830f   8b0d aca84b01    mov ecx,dword ptr ds:[0x14ba8ac]
 *  01228315   3bc1             cmp eax,ecx
 *  01228317   76 08            jbe short .01228321
 *  01228319   2bc1             sub eax,ecx
 *  0122831b   50               push eax
 *  0122831c   e8 1f2e0000      call .0122b140
 *  01228321   c745 fc ffffffff mov dword ptr ss:[ebp-0x4],-0x1
 *  01228328   8b46 04          mov eax,dword ptr ds:[esi+0x4]
 *  0122832b   83f8 01          cmp eax,0x1
 *  0122832e   75 2c            jnz short .0122835c
 *  01228330   8b06             mov eax,dword ptr ds:[esi]
 *  01228332   85c0             test eax,eax
 *  01228334   74 09            je short .0122833f
 *  01228336   50               push eax
 *  01228337   e8 3b7c1300      call .0135ff77
 *  0122833c   83c4 04          add esp,0x4
 *  0122833f   56               push esi
 *  01228340   e8 33781300      call .0135fb78
 *  01228345   83c4 04          add esp,0x4
 *  01228348   8bc6             mov eax,esi
 *  0122834a   8b4d f4          mov ecx,dword ptr ss:[ebp-0xc]
 *  0122834d   64:890d 00000000 mov dword ptr fs:[0],ecx
 *  01228354   59               pop ecx
 *  01228355   5f               pop edi
 *  01228356   5e               pop esi
 *  01228357   5b               pop ebx
 *  01228358   8be5             mov esp,ebp
 *  0122835a   5d               pop ebp
 *  0122835b   c3               retn
 *  0122835c   48               dec eax
 *  0122835d   8946 04          mov dword ptr ds:[esi+0x4],eax
 *  01228360   8bc6             mov eax,esi
 *  01228362   8b4d f4          mov ecx,dword ptr ss:[ebp-0xc]
 *  01228365   64:890d 00000000 mov dword ptr fs:[0],ecx
 *  0122836c   59               pop ecx
 *  0122836d   5f               pop edi
 *  0122836e   5e               pop esi
 *  0122836f   5b               pop ebx
 *  01228370   8be5             mov esp,ebp
 *  01228372   5d               pop ebp
 *  01228373   c3               retn
 *  01228374   cc               int3
 *  01228375   cc               int3
 *  01228376   cc               int3
 *  01228377   cc               int3
 *  01228378   cc               int3
 */

namespace
{ // unnamed

  // Skip individual L'\n' which might cause repetition.
  // bool NewLineWideCharSkipper(LPVOID data, DWORD *size, HookParam *)
  //{
  //  LPCWSTR text = (LPCWSTR)data;
  //  if (*size == 2 && *text == L'\n')
  //    return false;
  //  return true;
  //}
  //

  bool NewKiriKiriZHook(DWORD addr)
  {
    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(ecx);
    hp.split = hp.offset; // the same logic but diff value as KiriKiri1, use [ecx] as split
    hp.index = 0x14;      // the same as KiriKiri1
    hp.type = CODEC_UTF16 | DATA_INDIRECT | USING_SPLIT | SPLIT_INDIRECT;
    // https://vndb.org/r67025
    // drm保护导致inlinehook失效
    return NewHookRetry(hp, "KiriKiriZ");
  }

  bool InsertKiriKiriZHook1()
  {
    ULONG addr = MemDbg::findCallerAddressAfterInt3((DWORD)::GetGlyphOutlineW, processStartAddress, processStopAddress);
    if (!addr)
      return false;

    HookParam hp;
    hp.address = addr;
    hp.text_fun =
        [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      hp->text_fun = nullptr;
      hp->type = HOOK_EMPTY;
      DWORD addr = context->stack[0];                           // retaddr
      addr = MemDbg::findEnclosingAlignedFunction(addr, 0x400); // range is around 0x377c50 - 0x377a40 = 0x210
      if (!addr)
        return;
      NewKiriKiriZHook(addr);
    };

    return NewHook(hp, "KiriKiriZ Hook");
  }

  // jichi 1/30/2015: Add KiriKiriZ2 for サノバウィッ�
  // It inserts to the same location as the old KiriKiriZ, but use a different way to find it.
  bool InsertKiriKiriZHook2()
  {
    const BYTE bytes[] = {
        0x38, 0x4b, 0x21,      // 0122812f   384b 21          cmp byte ptr ds:[ebx+0x21],cl
        0x0f, 0x95, 0xc1,      // 01228132   0f95c1           setne cl
        0x33, 0xc0,            // 01228135   33c0             xor eax,eax
        0x38, 0x43, 0x20,      // 01228137   3843 20          cmp byte ptr ds:[ebx+0x20],al
        0x0f, 0x95, 0xc0,      // 0122813a   0f95c0           setne al
        0x33, 0xc8,            // 0122813d   33c8             xor ecx,eax
        0x33, 0x4b, 0x10,      // 0122813f   334b 10          xor ecx,dword ptr ds:[ebx+0x10]
        0x0f, 0xb7, 0x43, 0x14 // 01228142   0fb743 14        movzx eax,word ptr ds:[ebx+0x14]
    };
    ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
    // GROWL_DWORD(addr);
    if (!addr)
      return false;

    // 012280e0   55               push ebp
    // 012280e1   8bec             mov ebp,esp
    addr = MemDbg::findEnclosingAlignedFunction(addr, 0x100); // 0x0122812f-0x012280e0 = 0x4F
    enum : BYTE
    {
      push_ebp = 0x55
    }; // 011d4c80  /$ 55             push ebp
    if (!addr || *(BYTE *)addr != push_ebp)
      return false;

    NewKiriKiriZHook(addr);
    return true;
  }

} // unnamed namespace

namespace
{
  void KrkrtextrenderFilter(TextBuffer *buffer, HookParam *)
  {
    // 会连续调用两次，只需修改第一次就可以了。
    static std::wstring last;
    auto ws = buffer->strW();
    if (ws == last)
      return buffer->clear();
    last = ws;
    ws = re::sub(ws, L"%p.*?;%f.*?;");
    ws = re::sub(ws, LR"(\[.*?\])");
    buffer->from(ws);
  };
  DWORD findtextrender(DWORD minAddress, DWORD maxAddress)
  {
    BYTE bytes[] = {
        0x8b, XX, XX, XX,
        0x8b, XX, XX, XX,
        XX,
        XX, XX,
        0xFF, XX,
        0x88, XX, XX, XX,
        XX, XX, XX, XX,
        XX, XX,
        0x74, XX,
        XX, XX, XX, XX,
        XX,
        XX,
        0xE8, XX, XX, XX, XX,
        0xB0, 0x01,
        0xC3};
    return MemDbg::findBytes(bytes, sizeof(bytes), minAddress, maxAddress);
  }
  DWORD findtextrender3(DWORD minAddress, DWORD maxAddress, DWORD rominAddress, DWORD romaxAddress)
  {
    char tjsGetString[] = "const tjs_char * tTJSVariant::GetString() const";
    auto addr = MemDbg::findBytes(tjsGetString, sizeof(tjsGetString), rominAddress, romaxAddress);
    if (!addr)
      return 0;
    auto pushs = MemDbg::find_leaorpush_addr_all(addr, minAddress, maxAddress);
    if (pushs.size() != 3)
      return 0;
    for (auto target : pushs)
    {
      addr = MemDbg::findEnclosingAlignedFunction(target);
      if (!addr)
        continue;
      if (findxref_reverse_checkcallop(addr, minAddress, maxAddress, 0xe8).size() != 1)
        continue;
      BYTE sig[] = {
          0x68, XX4,
          0xe8, XX4,
          0x83, 0xc4, 0x04,
          XX, XX4,
          XX,
          0xff, XX};
      if (!MatchPattern(target, sig, sizeof(sig)))
        continue;
      return target + sizeof(sig);
    }
    return 0;
  }
  DWORD findtextrender2(DWORD minAddress, DWORD maxAddress)
  {
    // 该函数很像TextRenderBase::render，但也可能并不是
    // https://github.com/3c1u/TextRender/blob/master/textrender.cc#L486
    // bool TextRenderBase::render(tTJSString text, int autoIndent, int diff, int all, bool same)
    BYTE bytes[] = {
        0x83, XX, 0x52,
        0x0f, 0x87, XX4,
        0x0f, 0xb6, XX, XX4,
        0xff, 0x24, XX, XX4};
    auto addr = MemDbg::findBytes(bytes, sizeof(bytes), minAddress, maxAddress);
    if (!addr)
      return 0;
    bytes[2] = 0x0f;
    if (!MemDbg::findBytes(bytes, sizeof(bytes), addr + sizeof(bytes), addr + sizeof(bytes) + 0x100))
      return 0;
    return findfuncstart(addr, 0x400, true);
  }
}
bool Krkrtextrenderdll()
{
  /*
  char __cdecl sub_1000BE60(
        char a1,
        int a2,
        int a3,
        int a4,
        int a5,
        int (__thiscall **a6)(int, int, int, int, int, int, int),
        int a7)
{
  int v7; // eax
  int v9; // [esp-Ch] [ebp-14h]
  int v10; // [esp-8h] [ebp-10h]
  int v11; // [esp-4h] [ebp-Ch]
  int v12; // [esp+0h] [ebp-8h]
  int v13; // [esp+4h] [ebp-4h]

  v13 = (unsigned __int8)sub_1000C800(&a1);
  v12 = (unsigned __int8)sub_1000C720(&a1);
  v11 = sub_1000C640(&a1);
  v10 = sub_1000C560(&a1);
  v9 = sub_1000C480(&a1);
  v7 = sub_1000C390(&a1); ===> sub_1000C390内部GetString，findtextrender3立即获取GetString的返回值。
                              返回值v7，findtextrender获取该返回值。
                              v7压栈然后调用*a6，a6为findtextrender2
  LOBYTE(a6) = (*a6)(a7, v7, v9, v10, v11, v12, v13);
  if ( a4 )
    sub_1000A420(a4, &a6);
  return 1;
}
  */
  HMODULE module = GetModuleHandleW(L"textrender.dll");
  if (module == 0)
    return false;
  if (GetProcAddress(module, "V2Link") == 0)
    return false;

  auto [rominAddress, romaxAddress] = Util::QueryModuleLimits(module, 0, PAGE_READONLY);
  auto [minAddress, maxAddress] = Util::QueryModuleLimits(module);
  HookParam hp;
  hp.offset = regoffset(eax);
  auto addr = findtextrender(minAddress, maxAddress);
  if (!addr)
    addr = findtextrender3(minAddress, maxAddress, rominAddress, romaxAddress);
  if (!addr)
  {
    hp.offset = stackoffset(1);
    addr = findtextrender2(minAddress, maxAddress);
  }
  if (!addr)
    return false;
  hp.address = addr;
  hp.type = EMBED_ABLE | EMBED_AFTER_NEW | CODEC_UTF16 | NO_CONTEXT | USING_STRING;
  hp.lineSeparator = L"\\n";
  hp.embed_hook_font = F_GetTextExtentPoint32W | F_GetGlyphOutlineW;
  hp.filter_fun = KrkrtextrenderFilter;
  return NewHook(hp, "TextRender");
}
namespace
{

  void KiriKiri4Filter(TextBuffer *buffer, HookParam *)
  {
    auto vw = buffer->viewW();
    // ExtKagparser
    //[>>]对话[<<][c]
    //[地]旁白[c]
    if ((!startWith(vw, L"[text]")) && (!(endWith(vw, L"[c]") && (startWith(vw, L"[>>]") || startWith(vw, L"[地]")))) && (vw[0] == L'[' && vw[vw.size() - 1] == ']'))
      return buffer->clear();
    if (vw[0] == L' ' && vw.size() <= 2)
      return buffer->clear();
    if (vw[0] == L'@' || vw[0] == L']')
      return buffer->clear();
    if (startWith(vw, L" : ") && endWith(vw, L" : "))
      return buffer->clear();
    if (vw == L" line offset ")
      return buffer->clear();
    StringReplacer(buffer, TEXTANDLEN(L"[>>]"), TEXTANDLEN(L"「"));
    StringReplacer(buffer, TEXTANDLEN(L"[<<]"), TEXTANDLEN(L"」"));
    StringFilterBetween(buffer, TEXTANDLEN(L"["), TEXTANDLEN(L"]"));
    vw = buffer->viewW();
    if (vw.size() <= 1)
      return buffer->clear();
  }

  bool kagparser()
  {
    bool succ = false;
    for (auto dllname : {L"KAGParser.dll", L"ExtKAGParser.dll"})
    {
      auto hm = GetModuleHandle(dllname);
      if (!hm)
        continue;
      auto [s, e] = Util::QueryModuleLimits(hm, 0, PAGE_READONLY);
      char tjs[] = "tTJSString tTJSString::operator +(const tjs_char *) const";
      ULONG addr = MemDbg::findBytes(tjs, sizeof(tjs), s, e);
      if (!addr)
        continue;
      addr = MemDbg::findBytes(&addr, sizeof(addr), s, e);
      if (!addr)
        continue;
      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        continue;
      HookParam hp;
      hp.address = addr;
      hp.offset = stackoffset(2);
      hp.type = CODEC_UTF16 | USING_STRING;
      hp.filter_fun = KiriKiri4Filter;
      succ |= NewHook(hp, wcasta(dllname).c_str());
    }
    return succ;
  }
  auto filterkrkrz(std::wstring &ws)
  {
    strReplace(ws, L"／");
    strReplace(ws, L"　");
    ws = re::sub(ws, LR"(\$r:(.*?),(.*?);)", L"$1");
    ws = re::sub(ws, LR"(\$(.*?);)");
    return ws;
  }
  bool krkrzx()
  {
    BYTE bytes[] = {
        0x8b, 0x4d, 0x10,
        0x66, 0x90,
        0x8b, 0x47, XX,
        0x48,
        0x83, 0xf8, 0x04,
        0x0f, 0x87, 0xaa, 0x00, 0x00, 0x00,
        0xff, 0x24, 0x85, XX4};
    auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(2);
    hp.type = CODEC_UTF16 | USING_STRING;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
      static std::wstring last;
      auto ws = buffer->strW();
      if (ws == last)
        return buffer->clear();
      last = ws;
      buffer->from(filterkrkrz(ws));
    };
    return NewHook(hp, "KiriKiriZX");
  }
}
bool InsertKiriKiriZHook()
{
  auto ok = Krkrtextrenderdll();
  ok = kagparser() || ok;
  return krkrzx() | (InsertKiriKiriZHook2() || InsertKiriKiriZHook1()) || ok;
}
namespace
{
  int type = 0;
  std::wstring saveend = L"";
  void hookafter(hook_context *s, TextBuffer buffer)
  {

    auto newText = buffer.strW(); // EngineController::instance()->dispatchTextWSTD(innner, Engine::ScenarioRole, 0);
    newText = newText + L"[plc]";
    if (type == 2)
    {
      newText = L"[x]" + newText;
    }
    else if (type == 1)
    {
      newText = re::sub(newText, L"\u300c", L"\\[\u300c\\]");
      newText = re::sub(newText, L"\u300d", L"\\[\u300d\\]");
    }
    newText += saveend;
    auto text = (LPWSTR)s->esi;
    wcscpy(text, newText.c_str());
  }
  void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
  {
    // シロガネオトメ
    auto text = (LPWSTR)s->esi;
    if (!text || !*text)
      return;

    std::wstring wstext = text;
    if (all_ascii(wstext))
      return;
    //[「]ぱ、ぱんつなんてどうしてそんなに気になるの。ゆきちゃんだってはいてるでしょ[」][plc]     ->对话
    //[x]彼女は言葉通りに、お風呂上がりにパンツを穿き忘れてそのまま一日過ごしかけたりすることがあった。ボクはそれをまじめに心配していたのだ（開き直り）。[plc]    ->旁白
    /*
    //算了，改人名容易出问题
    //[name name="？／翼"]    ->人名
    //[name name="翼"]
    auto checkisname=re::sub(wstext, std::wregex(L"\\[name name=\"(.*?)\"\\]"), L"");
    if(wstext!=L"" && checkisname==L""){
      auto name=re::sub(wstext, std::wregex(L"\\[name name=\"(.*?)\"\\]"), L"$1");

      auto _idx=name.find(L'\uff0f');
      std::wstring end=L"";
      if(_idx!=name.npos){
        name=name.substr(0,_idx);
        end=name.substr(_idx);
      }
      name = EngineController::instance()->dispatchTextWSTD(name, Engine::NameRole, 0);
      name+=end;
      name=L"[name name=\""+name+L"\"]";
      wcscpy(text,name.c_str());
      return true;
    }
    */
    if (wstext.size() < 5 || (wstext.substr(wstext.size() - 5) != L"[plc]"))
      return;

    type = 0;
    if (wstext.substr(0, 3) == L"[x]")
    {
      type = 1;
      wstext = wstext.substr(3);
    }
    else if (wstext.substr(0, 3) == L"[\u300c]")
    { // 「 」
      type = 2;
      wstext = re::sub(wstext, L"\\[\u300c\\]", L"\u300c");
      wstext = re::sub(wstext, L"\\[\u300d\\]", L"\u300d");
    }
    if (type == 0)
      return; // 未知类型
    saveend = L"";
    auto innner = wstext.substr(0, wstext.size() - 5);
    innner = re::sub(innner, L"\\[eruby text=(.*?) str=(.*?)\\]", L"$2");
    if (innner[innner.size() - 1] == L']')
    {
      // 「ボクの身体をあれだけ好き勝手しておいて、いまさらカマトトぶっても遅いよ。ほら、正直になりなよ」[waitsd layer=&CHAR6]
      for (int i = innner.size(); i > 0; i--)
      {
        if (innner[i] == '[')
        {
          saveend = innner.substr(i);
          innner = innner.substr(0, i);
          break;
        }
      }
    }
    buffer->from(innner);
  }

  bool attachkr2(ULONG startAddress, ULONG stopAddress)
  {
    // シロガネオトメ
    //    .text:005D288D 66 8B 06                      mov     ax, [esi]
    // .text:005D2890 66 83 F8 3B                   cmp     ax, 3Bh ; ';'
    // .text:005D2894 0F 84 AA 06 00 00             jz      loc_5D2F44
    // .text:005D2894
    // .text:005D289A 66 83 F8 2A                   cmp     ax, 2Ah ; '*'
    // .text:005D289E 0F 85 DF 02 00 00             jnz     loc_5D2B83

    // 修改v3的值
    //  v3 = *(const wchar_t **)(*(_DWORD *)(a1 + 100) + 8 * *(_DWORD *)(a1 + 116));
    //      if ( *v3 != 59 )
    //      {
    //        if ( *v3 == 42 )
    const uint8_t bytes[] = {
        0x66, 0x8B, 0x06, 0x66, 0x83, 0xF8, 0x3B, 0x0F, XX, XX4, 0x66, 0x83, 0xF8, 0x2A, 0x0F};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = EMBED_ABLE | CODEC_UTF16 | NO_CONTEXT;
    hp.text_fun = hookBefore;
    hp.embed_fun = hookafter;
    return NewHook(hp, "EmbedKrkr2");
  }

} // namespace Private

namespace Private
{

  bool attach(ULONG startAddress, ULONG stopAddress)
  {
    // findbytes搜索1长度BYTE[]时有问题。
    // mashiro_fhd
    //   BYTE sig0[]={0x8B,XX};//mov esi,ecx
    // ecx->XXX->esi->al/bl/cl/dl
    /*
    eax   c1
    ebx   d9
    ebp e9
    edx d1
    edi f9
    esi f1
    */

    //    BYTE sig01[]={0x8A,XX};//mov     al, [esi]
/*
al 06
bl 1e
cl 0e
dl 16
*/
#define sigs(n, N)            \
  BYTE sig1##n[] = {0x3C, N}; \
  BYTE sig2##n[] = {0x80, XX, N};
#define addsig(n) {sig1##n, sig2##n},
    sigs(1, 0x80) sigs(2, 0xc2) sigs(3, 0xE0) sigs(4, 0xF0) sigs(5, 0xF8) sigs(6, 0xFC) sigs(7, 0xFE)
        // BYTE sig1[]={0x3C,0x80,XX};//0x73//0x0f
        // BYTE sig2[]={0x3C,0xC2,XX};
        // BYTE sig3[]={0x3C,0xE0,XX};
        // BYTE sig4[]={0x3C,0xF0,XX};
        // BYTE sig5[]={0x3C,0xF8,XX};
        // BYTE sig6[]={0x3C,0xFC,XX};
        // BYTE sig7[]={0x3C,0xFE,XX};

        ULONG addr = startAddress;
    bool succ = false;
    while (addr)
    {
      // MessageBox(0,xx,L"",0);

      addr = [](DWORD addr, DWORD stopAddress)
      {
        for (; addr < stopAddress; addr++)
          if ((*(BYTE *)addr) == 0x8b)
            switch (*(BYTE *)(addr + 1))
            {
            case 0xc1:
            case 0xd9:
            case 0xe9:
            case 0xd1:
            case 0xf9:
            case 0xf1:
              return addr;
            default:
              continue;
            }
        return (DWORD)0;
      }(addr + 1, stopAddress);
      // ConsoleOutput("%p",0x400000+addr-startAddress);
      if (!addr)
        continue;
      auto check = [](DWORD addr, DWORD stopAddress)
      {
        for (; addr < stopAddress; addr++)
          if ((*(BYTE *)addr) == 0x8a)
            switch (*(BYTE *)(addr + 1))
            {
            case 0x06:
            case 0x1e:
            case 0x0e:
            case 0x16:
              return addr;
            default:
              continue;
            }
        return (DWORD)0;
      }(addr, addr + 0x10);
      if (check == 0)
        continue;
      switch (*(BYTE *)(check + 1))
      {
      case 0x06:
      case 0x1e:
      case 0x0e:
      case 0x16:
        break;
      default:
        continue;
      }
      bool ok = true;
      for (auto p : std::vector<std::pair<BYTE *, BYTE *>>{
               addsig(1) addsig(2) addsig(3) addsig(4) addsig(5) addsig(6) addsig(7)

           })
      {
        auto check1 = MemDbg::findBytes(p.first, 2, check, check + 0x1000);
        auto check2 = MemDbg::findBytes(p.second, 3, check, check + 0x1000);
        check = min(check1, check2);
        if (check == 0)
          check = max(check1, check2);
        if (check == 0)
        {
          ok = false;
          break;
        }
      }
      if (ok)
      {
        HookParam hp;
        hp.address = addr;
        hp.offset = regoffset(ecx);
        hp.type = EMBED_ABLE | EMBED_AFTER_NEW | CODEC_UTF8 | NO_CONTEXT | USING_STRING;
        hp.filter_fun = [](TextBuffer *buffer, HookParam *)
        {
          auto s = buffer->strA();
          if (s.size() > 2000)
            return buffer->clear();
          if (all_ascii(s))
            return buffer->clear();
          auto chatflags = {u8"（", u8"）", u8"。", u8"「", u8"」", u8"『", u8"』", u8"？", u8"！", u8"、", u8"―"};
          bool ok = false;
          for (auto f : chatflags)
          {
            if (strstr(s.c_str(), f))
              ok = true;
          }
          if (ok == false)
            return buffer->clear();
          s = re::sub(s, "%\\d+?;");
          s = re::sub(s, "#[0-9a-fA-F]*?;");
          s = re::sub(s, "%p.*?;%f.*?;");
          s = re::sub(s, R"(\[.*?\])");
          buffer->from(s);
        };
        hp.lineSeparator = L"\\n";
        hp.embed_hook_font = F_GetTextExtentPoint32W | F_GetGlyphOutlineW;
        succ |= NewHook(hp, "EmbedKrkrZ");
      }
    }

    return succ;
  }

} // namespace ScenarioHook
namespace
{
  bool wcslen_wcscpy()
  {
    // LOVELY×CATION
    const uint8_t bytes2[] = {
        // wcscpy 唯一
        0x55, 0x8b, 0xec,
        0x53, 0x56, 0x8b, 0x75, 0x0c, 0x56, 0xe8, XX, 0xFF, 0xFF, 0xFF, // call wcslen，距离很近，故均为ff
        0x59, 0x8b, 0xd8, 0x33, XX, 0x8b, 0x45, 0x08};
    const uint8_t bytes[] = {
        // wcslen 有多个，可以修改任意一个，但是会造成困扰
        0x55, 0x8b, 0xec,
        0x33, XX,
        0x8b, 0x45, 0x08,
        0xeb, 0x04,
        XX,
        0x83, 0xc0, 0x02,
        0x66, 0x83, 0x38, 0x00,
        0x75, 0xf6,
        0x8b, XX,
        0x5d, 0xc3};
    ULONG addr = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
    static int off;
    off = 8;
    if (!addr)
    {
      addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
      off = 4;
    }
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    if (off == 8)
      hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT | EMBED_ABLE;
    else
      hp.type = CODEC_UTF16 | USING_STRING | EMBED_ABLE;
    hp.offset = off;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
      auto t = buffer->strW();
      if (all_ascii(t))
        return buffer->clear();
      if (t.find(L".ks") != t.npos || t.find(L".tjs") != t.npos || t.find(L".xp3") != t.npos || t.find(L"/") != t.npos || t.find(L"\\") != t.npos || t[0] == L'@')
        return buffer->clear(); // 脚本路径或文件路径
      // if(t.find(L"[\u540d\u524d]")!=t.npos)return false; //[名前]，翻译后破坏结构
      if (t.find(L"\u8aad\u307f\u8fbc\u307f") != t.npos)
        return buffer->clear(); // 読み込み
      if (t.size() > 4 && t.substr(t.size() - 4) == L"[np]")
        t = t.substr(0, t.size() - 4);
      if (t.size() > 4 && t.substr(t.size() - 3) == L"[r]")
        t = t.substr(0, t.size() - 3); // 揺り籠より天使まで
      t = re::sub(t, L"\\[\ruby text=\"(.*?)\"\\]");
      t = re::sub(t, L"\\[ruby text=\"(.*?)\"\\]");
      t = re::sub(t, L"\\[ch text=\"(.*?)\"\\]", L"$1");
      if (std::any_of(t.begin(), t.end(), [](wchar_t c)
                      { return (c <= 127) && ((c != L'[') || c != L']'); }))
        return buffer->clear();
      buffer->from(t);
    };
    hp.embed_fun = [](hook_context *s, TextBuffer buffer)
    {
      auto t = std::wstring((wchar_t *)s->stack[off / 4]);
      auto newText = buffer.strW();
      if (t.size() > 4 && t.substr(t.size() - 4) == L"[np]")
        newText = newText + L"[np]";
      if (t.size() > 3 && t.substr(t.size() - 3) == L"[r]")
        newText = newText + L"[r]"; // 揺り籠より天使まで
      wcscpy((wchar_t *)s->stack[off / 4], newText.c_str());
    };
    hp.embed_hook_font = F_GetTextExtentPoint32W | F_GetGlyphOutlineW;
    return NewHook(hp, "Krkr2wcs");
  }
}
bool InsertKiriKiri4Hook()
{
  /*
      v31 = 164;
      sub_4016D4(a1 + 112, &word_6E6DD8 + 425);
      ++v32;
      sub_4016D4(&v34, *(wchar_t **)(a1 + 124));
  */
  const BYTE bytes[] = {
      0x66, 0xc7, 0x45, XX, 0xa4, 0x00,
      XX, XX, XX,
      XX, XX, XX4,
      XX, XX, XX,
      0xe8, XX4,
      XX, XX, XX,
      XX, XX, XX,
      XX, XX, XX,
      0x8B, 0x53, XX,
      0xe8, XX4};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr + sizeof(bytes) - 5;
  hp.offset = regoffset(edx);
  hp.type = NO_CONTEXT | CODEC_UTF16 | USING_STRING;
  hp.filter_fun = KiriKiri4Filter;
  return NewHook(hp, "KiriKiri4");
}
namespace
{
  bool krkrz2()
  {
    // すれ違う兄妹の壊れる倫理観
    const BYTE bytes[] = {
        0x3b, 0xd7,
        0x73, 0x18,
        0x0f, 0x1f, 0x80, 0x00, 0x00, 0x00, 0x00,
        0x8b, 0x43, 0x38,
        0x56,
        0x8b, 0x00,
        0xff, 0xd0,
        0x03, 0xf0,
        0x83, 0xc4, 0x04,
        0x3b, 0xf7,
        0x72, XX,
        0x8b, 0x43, 0x4c,
        0x8b, 0xce,
        0x48,
        0x83, 0xf8, 0x04,
        0x0f, 0x87, XX4,
        0xff, 0x24, 0x85, XX4};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(edx);
    hp.type = CODEC_UTF16 | USING_STRING;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
      static int idx;
      if (idx++ % 2 == 0)
        return buffer->clear();
      buffer->from(filterkrkrz(buffer->strW()));
    };
    return NewHook(hp, "krkrz2");
  }
}
bool KiriKiri::attach_function()
{
  if (Util::SearchResourceString(L"TVP(KIRIKIRI) Z "))
  { // TVP(KIRIKIRI) Z CORE
    // jichi 11/24/2014: Disabled that might crash VBH
    // if (Util::CheckFile(L"plugin\\KAGParser.dll"))
    //  InsertKAGParserHook();
    // else if (Util::CheckFile(L"plugin\\KAGParserEx.dll"))
    //  InsertKAGParserExHook();
    bool krz = Private::attach(processStartAddress, processStopAddress);
    if (InsertKiriKiriZHook() || krkrz2() || krz)
      return true;
  }
  bool b1 = attachkr2(processStartAddress, processStopAddress);
  bool _3 = wcslen_wcscpy();
  auto _ = InsertKiriKiriHook() || InsertKiriKiriZHook() || b1 || _3;
  return InsertKiriKiri4Hook() || _;
}
