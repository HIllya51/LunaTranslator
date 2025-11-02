#include "Reallive.h"

/********************************************************************************************
Reallive hook:
  Process name is reallive.exe or reallive*.exe.

  Technique to find Reallive hook is quite different from 2 above.
  Usually Reallive engine has a font caching issue. This time we wait
  until the first call to GetGlyphOutlineA. Reallive engine usually set
  up stack frames so we can just refer to EBP to find function entry.

********************************************************************************************/
/** jichi 5/13/2015
 *  RealLive does not work for 水着少女と媚薬アイス from 裸足少女
 *  012da80f   cc               int3
 *  012da810   55               push ebp    ; jichi: change to hook here
 *  012da811   8bec             mov ebp,esp
 *  012da813   83ec 10          sub esp,0x10 ; jichi: hook here by default
 *  012da816   53               push ebx
 *  012da817   56               push esi
 *  012da818   57               push edi
 *  012da819   8b7d 18          mov edi,dword ptr ss:[ebp+0x18]
 *  012da81c   81ff 5c810000    cmp edi,0x815c
 *  012da822   75 0a            jnz short reallive.012da82e
 *  012da824   c745 18 9f840000 mov dword ptr ss:[ebp+0x18],0x849f
 *  012da82b   8b7d 18          mov edi,dword ptr ss:[ebp+0x18]
 *  012da82e   b8 9041e301      mov eax,reallive.01e34190
 *  012da833   b9 18a49001      mov ecx,reallive.0190a418
 *  012da838   e8 a38d0000      call reallive.012e35e0
 *  012da83d   85c0             test eax,eax
 *  012da83f   74 14            je short reallive.012da855
 *  012da841   e8 6addffff      call reallive.012d85b0
 *  012da846   ba 9041e301      mov edx,reallive.01e34190
 *  012da84b   b8 18a49001      mov eax,reallive.0190a418
 *  012da850   e8 ab7c0000      call reallive.012e2500
 *  012da855   8d45 f0          lea eax,dword ptr ss:[ebp-0x10]
 *  012da858   50               push eax
 *  012da859   8d4d f4          lea ecx,dword ptr ss:[ebp-0xc]
 *  012da85c   51               push ecx
 *  012da85d   8d55 fc          lea edx,dword ptr ss:[ebp-0x4]
 *  012da860   52               push edx
 *  012da861   8d45 f8          lea eax,dword ptr ss:[ebp-0x8]
 *  012da864   50               push eax
 *  012da865   8bc7             mov eax,edi
 *  012da867   e8 54dfffff      call reallive.012d87c0
 *  012da86c   8bf0             mov esi,eax
 *  012da86e   83c4 10          add esp,0x10
 *  012da871   85f6             test esi,esi
 *  012da873   75 4b            jnz short reallive.012da8c0
 *  012da875   8d4d f4          lea ecx,dword ptr ss:[ebp-0xc]
 *  012da878   51               push ecx
 *  012da879   57               push edi
 *  012da87a   8d4d f0          lea ecx,dword ptr ss:[ebp-0x10]
 *  012da87d   e8 cef0ffff      call reallive.012d9950
 *  012da882   8bf0             mov esi,eax
 *  012da884   83c4 08          add esp,0x8
 *  012da887   85f6             test esi,esi
 */
static bool InsertRealliveDynamicHook(LPVOID addr, hook_context *context)
{
  if (addr != ::GetGlyphOutlineA)
    return false;
  // jichi 5/13/2015: Find the enclosing caller of GetGlyphOutlineA
  if (DWORD i = context->ebp)
  {
    i = *(DWORD *)(i + 4);
    for (DWORD j = i; j > i - 0x100; j--)
      if (*(WORD *)j == 0xec83)
      { // jichi 7/26/2014: function starts
        // 012da80f   cc               int3
        // 012da810   55               push ebp    ; jichi: change to hook here
        // 012da811   8bec             mov ebp,esp
        // 012da813   83ec 10          sub esp,0x10 ; jichi: hook here by default
        if (*(DWORD *)(j - 3) == 0x83ec8b55)
          j -= 3;

        HookParam hp;
        hp.address = j;
        hp.offset = stackoffset(5);
        hp.split = regoffset(esp);
        hp.type = CODEC_ANSI_BE | USING_SPLIT;
        // GROWL_DWORD(hp.address);

        // RegisterEngineType(ENGINE_REALLIVE);
        ConsoleOutput("RealLive: disable GDI hooks");

        return NewHook(hp, "RealLive");
      }
  }
  return true; // jichi 12/25/2013: return true
}
void InsertRealliveHook()
{
  PcHooks::hookGDIFunctions();
  // ConsoleOutput("Probably Reallive. Wait for text.");
  ConsoleOutput("TRIGGER Reallive");
  trigger_fun = InsertRealliveDynamicHook;
}

void RlBabelFilter(TextBuffer *buffer, HookParam *)
{
  if (((char *)buffer->buff)[0] == '\x01')
  {
    StringFilterBetween(buffer, TEXTANDLEN("\x01"), TEXTANDLEN("\x02")); // remove names
  }

  CharReplacer(buffer, '\x08', '"');
  CharReplacer(buffer, '\x09', '\'');
  CharReplacer(buffer, '\x0A', '\'');
  CharFilter(buffer, '\x1F');                                             // remove color
  StringReplacer(buffer, TEXTANDLEN("\x89\x85"), TEXTANDLEN("\x81\x63")); // "\x89\x85"-> shift-JIS"…"
  StringReplacer(buffer, TEXTANDLEN("\x89\x97"), TEXTANDLEN("--"));
}

bool InsertRlBabelHook()
{

  /*
   * Sample games:
   * https://vndb.org/r78318
   */
  const BYTE bytes[] = {
      0xCC,                 // int 3
      0x55,                 // push ebp        <- hook here
      0x8B, 0xEC,           // mov ebp,esp
      0x83, 0xEC, 0x20,     // sub esp,20
      0xC7, 0x45, 0xFC, XX4 // mov [ebp-04],rlBabel.DLL+16804
  };

  HMODULE module = GetModuleHandleW(L"rlBabel.dll");
  if (!module)
    return false;
  auto [minAddress, maxAddress] = Util::QueryModuleLimits(module);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), minAddress, maxAddress);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr + 1;
  hp.offset = regoffset(eax);
  hp.type = USING_STRING;
  hp.filter_fun = RlBabelFilter;
  ConsoleOutput("INSERT RealLive Babel");
  return NewHook(hp, "RealLive Babel");
}
namespace
{
  bool clannad_en_steam()
  {
    // if ( v12 == 33116 || v12 == 33951 || v12 == 33962 )
    BYTE sig[] = {
        0x81, 0xFE, 0x5C, 0x81, 0x00, 0x00,
        0x74, 0x10,
        0x81, 0xFE, 0x9F, 0x84, 0x00, 0x00,
        0x74, 0x08,
        0x81, 0xFE, 0xAA, 0x84, 0x00, 0x00,
        0x75, XX};
    ULONG addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;

    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(esi);
    hp.type = USING_CHAR | CODEC_ANSI_LE;
    return NewHook(hp, "RealLiveX");
  }
}
namespace
{
  // https://vndb.org/r1944
  bool veryold()
  {
    HookParam hp;
    hp.address = (DWORD)GetProcAddress(GetModuleHandleA("gdi32.dll"), "GetGlyphOutline");
    hp.type = HOOK_RETURN;
    hp.text_fun = [](hook_context *context, HookParam *hps, TextBuffer *buffer, uintptr_t *split)
    {
      hps->type = HOOK_EMPTY;
      auto addr = findfuncstart(hps->address);
      if (!addr)
        return;
      auto addrs = findxref_reverse_checkcallop(addr, processStartAddress, processStopAddress, 0xe8);
      if (addrs.size() != 1)
        return;
      addr = addrs[0];
      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        return;
      HookParam hp;
      hp.address = addr;
      hp.offset = stackoffset(5);
      hp.type = USING_CHAR | CODEC_ANSI_BE;
      NewHook(hp, "RealLiveOld");
    };
    return NewHook(hp, "GetGlyphOutline");
  }
}
bool Reallive::attach_function()
{
  InsertRealliveHook();
  InsertRlBabelHook() || clannad_en_steam() || veryold();
  return true;
}

bool avg3216dattach_function()
{
  BYTE pattern1[] = {
      0x3c, 0x81, XX2,
      0x3c, 0x9f, XX2,
      0x3c, 0xe0, XX2,
      0x3c, 0xfc, XX2};
  BYTE pattern2[] = {
      0x8b, 0x75, 0x08,
      0x8a, 0x06,
      0x3c, 0x81,
      0x75, XX,
      0x80, 0x7e, 0x01, 0x7a};
  auto addr = MemDbg::findBytes(pattern2, sizeof(pattern2), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  auto check = MemDbg::findBytes(pattern1, sizeof(pattern1), addr, addr + 0x200);
  if (!check)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = NO_CONTEXT | DATA_INDIRECT;
  return NewHook(hp, "avg3216d");
}

bool avg3216dattach_function2()
{
  // https://vndb.org/v12860
  // effect～悪魔の仔～
  BYTE pattern2[] = {
      0x80, 0xf9, 0x81,
      0x72, 0x05,
      0x80, 0xf9, 0x9f,
      0x76, XX, // 76 17
      0x80, 0xf9, 0xe0,
      0x72, 0x05,
      0x80, 0xf9, 0xfc,
      0x76, 0x0d};
  auto addr = MemDbg::findBytes(pattern2, sizeof(pattern2), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = findfuncstart(addr, 0x200, true);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    // いいなり
    // https://vndb.org/r17019
    if (startWith(buffer->viewA(), "\x81\x7a"))
    {
      buffer->from(buffer->viewA().substr(2));
    }
  };
  return NewHook(hp, "avg3217d");
}
bool avg3216d::attach_function()
{
  return avg3216dattach_function() || avg3216dattach_function2();
}