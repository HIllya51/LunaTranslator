// pchooks.cc
// 8/1/2014 jichi

#include "pchooks.h"
// #include <gdiplus.h>

// 8/1/2014 jichi: Split is not used.
// Although split is specified, USING_SPLIT is not assigned.

// Use LPASTE to convert to wchar_t
// http://bytes.com/topic/c/answers/135834-defining-wide-character-strings-macros
// #define LPASTE(s) L##s
// #define L(s) LPASTE(s)
#define NEW_HOOK(ptr, _dll, _fun, _data, _data_ind, _split_off, _split_ind, _type, _len_off) \
  {                                                                                          \
    HookParam hp;                                                                            \
    wcsncpy_s(hp.module, _dll, MAX_MODULE_SIZE - 1);                                         \
    strncpy_s(hp.function, #_fun, MAX_MODULE_SIZE - 1);                                      \
    hp.offset = _data;                                                                       \
    hp.index = _data_ind;                                                                    \
    hp.split = _split_off;                                                                   \
    hp.split_index = _split_ind;                                                             \
    hp.type = _type | MODULE_OFFSET | FUNCTION_OFFSET;                                       \
    hp.length_offset = _len_off;                                                             \
    if ((!ptr) ||                                                                            \
        (GetModuleHandle(hp.module) &&                                                       \
         GetProcAddress(GetModuleHandle(hp.module), hp.function) &&                          \
         GetProcAddress(GetModuleHandle(hp.module), hp.function) == ptr))                    \
      NewHook(hp, #_fun);                                                                    \
  }

#define NEW_MODULE_HOOK(_module, _fun, _data, _data_ind, _split_off, _split_ind, _type, _len_off) \
  {                                                                                               \
    HookParam hp;                                                                                 \
    wchar_t path[MAX_PATH];                                                                       \
    if (GetModuleFileNameW(_module, path, MAX_PATH))                                              \
      wcsncpy_s(hp.module, wcsrchr(path, L'\\') + 1, MAX_MODULE_SIZE - 1);                        \
    strncpy_s(hp.function, #_fun, MAX_MODULE_SIZE - 1);                                           \
    hp.offset = _data;                                                                            \
    hp.index = _data_ind;                                                                         \
    hp.split = _split_off;                                                                        \
    hp.split_index = _split_ind;                                                                  \
    hp.type = _type | MODULE_OFFSET | FUNCTION_OFFSET;                                            \
    hp.length_offset = _len_off;                                                                  \
    NewHook(hp, #_fun);                                                                           \
  }

#ifndef _WIN64
enum args
{
  s_retaddr = 0,
  s_arg1 = 4 * 1, // 0x4
  s_arg2 = 4 * 2, // 0x8
  s_arg3 = 4 * 3, // 0xc
  s_arg4 = 4 * 4, // 0x10
  s_arg5 = 4 * 5, // 0x14
  s_arg6 = 4 * 6, // 0x18
  s_arg7 = 4 * 7
};
#else  // _WIN32
enum args
{
  s_retaddr = 0x0,
  s_arg1 = -0x20,
  s_arg2 = -0x28,
  s_arg3 = -0x50,
  s_arg4 = -0x58,
  s_arg5 = 0x8,
  s_arg6 = 0x10,
  s_arg7 = 0x18
};
#endif // _WIN64

bool once_hookGDIFunctions = false;
bool once_hookGDIPlusFunctions = false;
bool once_hookD3DXFunctions = false;
bool once_hookOtherPcFunctions = false;
#define once_run_pchooks(x) \
  {                         \
    if (once_##x)           \
      return;               \
    once_##x = true;        \
  }
constexpr short arg_sz = (short)sizeof(void *);
void PcHooks::hookGdiGdiplusD3dxFunctions()
{
  for (std::wstring DXVersion : {L"d3dx9", L"d3dx10"})
    if (HMODULE module = GetModuleHandleW(DXVersion.c_str()))
      PcHooks::hookD3DXFunctions(module);
    else
      for (int i = 0; i < 50; ++i)
        if (HMODULE module = GetModuleHandleW((DXVersion + L"_" + std::to_wstring(i)).c_str()))
          PcHooks::hookD3DXFunctions(module);

  PcHooks::hookGDIFunctions();
  PcHooks::hookGDIPlusFunctions();
}
// jichi 7/17/2014: Renamed from InitDefaultHook
void PcHooks::hookGDIFunctions(void *ptr)
{
  once_run_pchooks(hookGDIFunctions);
  // gdi32.dll
  NEW_HOOK(ptr, L"gdi32.dll", GetTextExtentPoint32A, s_arg2, 0, s_arg1, 0, USING_STRING, s_arg3 / arg_sz)
  NEW_HOOK(ptr, L"gdi32.dll", GetTextExtentExPointA, s_arg2, 0, s_arg1, 0, USING_STRING, s_arg3 / arg_sz)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharacterPlacementA, s_arg2, 0, s_arg1, 0, USING_STRING, s_arg3 / arg_sz)
  NEW_HOOK(ptr, L"gdi32.dll", GetGlyphIndicesA, s_arg2, 0, s_arg1, 0, USING_STRING, s_arg3 / arg_sz)
  NEW_HOOK(ptr, L"gdi32.dll", GetGlyphOutlineA, s_arg2, 0, s_arg1, 0, CODEC_ANSI_BE, 0)
  NEW_HOOK(ptr, L"gdi32.dll", ExtTextOutA, s_arg6, 0, s_arg1, 0, USING_STRING, s_arg7 / arg_sz)
  NEW_HOOK(ptr, L"gdi32.dll", TextOutA, s_arg4, 0, s_arg1, 0, USING_STRING, s_arg5 / arg_sz)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharABCWidthsA, s_arg2, 0, s_arg1, 0, CODEC_ANSI_BE, 0)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharABCWidthsFloatA, s_arg2, 0, s_arg1, 0, CODEC_ANSI_BE, 0)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharWidth32A, s_arg2, 0, s_arg1, 0, CODEC_ANSI_BE, 0)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharWidthFloatA, s_arg2, 0, s_arg1, 0, CODEC_ANSI_BE, 0)

  NEW_HOOK(ptr, L"gdi32.dll", GetTextExtentPoint32W, s_arg2, 0, s_arg1, 0, CODEC_UTF16 | USING_STRING, s_arg3 / arg_sz)
  NEW_HOOK(ptr, L"gdi32.dll", GetTextExtentExPointW, s_arg2, 0, s_arg1, 0, CODEC_UTF16 | USING_STRING, s_arg3 / arg_sz)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharacterPlacementW, s_arg2, 0, s_arg1, 0, CODEC_UTF16 | USING_STRING, s_arg3 / arg_sz)
  NEW_HOOK(ptr, L"gdi32.dll", GetGlyphIndicesW, s_arg2, 0, s_arg1, 0, CODEC_UTF16 | USING_STRING, s_arg3 / arg_sz)
  NEW_HOOK(ptr, L"gdi32.dll", GetGlyphOutlineW, s_arg2, 0, s_arg1, 0, CODEC_UTF16, 0)
  // ExtTextOutW全是乱码，没卵用
  // NEW_HOOK(ptr, L"gdi32.dll", ExtTextOutW,            s_arg6, 0,s_arg1,0, CODEC_UTF16|USING_STRING, s_arg7 / arg_sz)
  NEW_HOOK(ptr, L"gdi32.dll", TextOutW, s_arg4, 0, s_arg1, 0, CODEC_UTF16 | USING_STRING, s_arg5 / arg_sz)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharABCWidthsW, s_arg2, 0, s_arg1, 0, CODEC_UTF16, 0)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharABCWidthsFloatW, s_arg2, 0, s_arg1, 0, CODEC_UTF16, 0)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharWidth32W, s_arg2, 0, s_arg1, 0, CODEC_UTF16, 0)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharWidthFloatW, s_arg2, 0, s_arg1, 0, CODEC_UTF16, 0)

  // user32.dll
  NEW_HOOK(ptr, L"user32.dll", DrawTextA, s_arg2, 0, s_arg1, 0, USING_STRING, s_arg3 / arg_sz)
  NEW_HOOK(ptr, L"user32.dll", DrawTextExA, s_arg2, 0, s_arg1, 0, USING_STRING, s_arg3 / arg_sz)
  NEW_HOOK(ptr, L"user32.dll", TabbedTextOutA, s_arg4, 0, s_arg1, 0, USING_STRING, s_arg5 / arg_sz)
  NEW_HOOK(ptr, L"user32.dll", GetTabbedTextExtentA, s_arg2, 0, s_arg1, 0, USING_STRING, s_arg3 / arg_sz)
  NEW_HOOK(ptr, L"user32.dll", DrawTextW, s_arg2, 0, s_arg1, 0, CODEC_UTF16 | USING_STRING, s_arg3 / arg_sz)
  NEW_HOOK(ptr, L"user32.dll", DrawTextExW, s_arg2, 0, s_arg1, 0, CODEC_UTF16 | USING_STRING, s_arg3 / arg_sz)
  NEW_HOOK(ptr, L"user32.dll", TabbedTextOutW, s_arg4, 0, s_arg1, 0, CODEC_UTF16 | USING_STRING, s_arg5 / arg_sz)
  NEW_HOOK(ptr, L"user32.dll", GetTabbedTextExtentW, s_arg2, 0, s_arg1, 0, CODEC_UTF16 | USING_STRING, s_arg3 / arg_sz)
}

// jichi 6/18/2015: GDI+ functions
void PcHooks::hookGDIPlusFunctions()
{
  once_run_pchooks(hookGDIPlusFunctions);
  HMODULE hModule = ::GetModuleHandleA("gdiplus.dll");
  if (!hModule)
    return;

  // gdiplus.dll
  // https://msdn.microsoft.com/en-us/library/windows/desktop/ms534053%28v=vs.85%29.aspx
  // https://msdn.microsoft.com/en-us/library/windows/desktop/ms534052%28v=vs.85%29.aspx
  // https://msdn.microsoft.com/en-us/library/windows/desktop/ms534039%28v=vs.85%29.aspx
  // Use arg1 pionter to GpGraphics as split
  // using namespace Gdiplus::DllExports;
  // Use arg5 style as split
  NEW_MODULE_HOOK(hModule, GdipAddPathString, s_arg2, 0, s_arg5, 0, CODEC_UTF16 | USING_STRING, s_arg3 / arg_sz)
  NEW_MODULE_HOOK(hModule, GdipAddPathStringI, s_arg2, 0, s_arg5, 0, CODEC_UTF16 | USING_STRING, s_arg3 / arg_sz)
  NEW_MODULE_HOOK(hModule, GdipMeasureCharacterRanges, s_arg2, 0, s_arg1, 0, CODEC_UTF16 | USING_STRING, s_arg3 / arg_sz)
  NEW_MODULE_HOOK(hModule, GdipDrawString, s_arg2, 0, s_arg1, 0, CODEC_UTF16 | USING_STRING, s_arg3 / arg_sz)
  NEW_MODULE_HOOK(hModule, GdipMeasureString, s_arg2, 0, s_arg1, 0, CODEC_UTF16 | USING_STRING, s_arg3 / arg_sz)
  NEW_MODULE_HOOK(hModule, GdipDrawDriverString, s_arg1, 0, s_arg3, 0, CODEC_UTF16 | USING_STRING, s_arg2 / arg_sz)
  NEW_MODULE_HOOK(hModule, GdipMeasureDriverString, s_arg1, 0, s_arg3, 0, CODEC_UTF16 | USING_STRING, s_arg2 / arg_sz)
}

void PcHooks::hookD3DXFunctions(HMODULE d3dxModule)
{
  once_run_pchooks(hookD3DXFunctions);
  if (GetProcAddress(d3dxModule, "D3DXCreateTextA"))
  {
    NEW_MODULE_HOOK(d3dxModule, D3DXCreateTextA, s_arg3, 0, 0, 0, USING_STRING, 0)
    NEW_MODULE_HOOK(d3dxModule, D3DXCreateTextW, s_arg3, 0, 0, 0, USING_STRING | CODEC_UTF16, 0)
  }

  // Second call in D3DX(10)CreateFontIndirect is D3DXFont constructor, which sets up the vtable
  // Call it to set up the vtable then extract the function addresses from that vtable
  uintptr_t createFont = (uintptr_t)GetProcAddress(d3dxModule, "D3DXCreateFontIndirectA");
  if (!createFont)
    createFont = (uintptr_t)GetProcAddress(d3dxModule, "D3DX10CreateFontIndirectA");
  if (!createFont)
  {
    ConsoleOutput("D3DX failed: couldn't find entry function");
    return;
  }

  struct D3DXFont
  {
    uintptr_t (*vtable)[20];
    DWORD data[2000];
  } font;
  for (int i = 0, calls = 0; i < 100; ++i)
  {
    if (*(BYTE *)(createFont + i) == 0xe8)
      ++calls;
    if (calls == 2)
    {
      union
      {
        void (D3DXFont::*ctor)();
        uintptr_t addr;
      } fuckTheTypeSystem;
      fuckTheTypeSystem.addr = *(DWORD *)(createFont + i + 1) + createFont + i + 5;
      (font.*(fuckTheTypeSystem.ctor))();

      HookParam hp;
      hp.address = (*font.vtable)[14];
      hp.offset = s_arg3;
      hp.length_offset = s_arg4 / arg_sz;
      hp.type = USING_STRING;
      auto suc = NewHook(hp, "ID3DXFont::DrawTextA");
      hp.address = (*font.vtable)[15];
      hp.type = USING_STRING | CODEC_UTF16;
      suc |= NewHook(hp, "ID3DXFont::DrawTextW");
      return;
    }
  }
  ConsoleOutput("D3DX failed: couldn't find vtable");
  return;
}

// jichi 10/2/2013
// Note: All functions does not have NO_CONTEXT attribute and will be filtered.
void PcHooks::hookOtherPcFunctions(void *ptr)
{
  once_run_pchooks(hookOtherPcFunctions);
  // int TextHook::InitHook(LPVOID addr, DWORD data, DWORD data_ind, DWORD split_off, DWORD split_ind, WORD type, DWORD len_off)

  // http://msdn.microsoft.com/en-us/library/78zh94ax.aspx
  // int WINAPI lstrlen(LPCTSTR lpString);
  // Lstr functions usually extracts rubbish, and might crash certain games like 「Magical Marriage Lunatics!!」
  // Needed by Gift
  // Use arg1 address for both split and data
  NEW_HOOK(ptr, L"kernel32.dll", lstrlenA, s_arg1, 0, s_arg1, 0, USING_STRING, 0)
  NEW_HOOK(ptr, L"kernel32.dll", lstrcpyA, s_arg2, 0, 0, 0, USING_STRING, 0)
  NEW_HOOK(ptr, L"kernel32.dll", lstrcpynA, s_arg2, 0, 0, 0, USING_STRING, 0)

  NEW_HOOK(ptr, L"kernel32.dll", lstrlenW, s_arg1, 0, s_arg1, 0, CODEC_UTF16 | USING_STRING, 0)
  NEW_HOOK(ptr, L"kernel32.dll", lstrcpyW, s_arg2, 0, 0, 0, CODEC_UTF16 | USING_STRING, 0)
  NEW_HOOK(ptr, L"kernel32.dll", lstrcpynW, s_arg2, 0, 0, 0, CODEC_UTF16 | USING_STRING, 0)

  // size_t strlen(const char *str);
  // size_t strlen_l(const char *str, _locale_t locale);
  // size_t wcslen(const wchar_t *str);
  // size_t wcslen_l(const wchar_t *str, _locale_t locale);
  // size_t _mbslen(const unsigned char *str);
  // size_t _mbslen_l(const unsigned char *str, _locale_t locale);
  // size_t _mbstrlen(const char *str);
  // size_t _mbstrlen_l(const char *str, _locale_t locale);

  // http://msdn.microsoft.com/en-us/library/ex0hs2ad.aspx
  // Needed by 娘姉妹
  //
  // <tchar.h>
  // char *_strinc(const char *current, _locale_t locale);
  // wchar_t *_wcsinc(const wchar_t *current, _locale_t locale);
  // <mbstring.h>
  // unsigned char *_mbsinc(const unsigned char *current);
  // unsigned char *_mbsinc_l(const unsigned char *current, _locale_t locale);
  //_(L"_strinc", _strinc, 4,  0,4,0, USING_STRING, 0) // 12/13/2013 jichi
  //_(L"_wcsinc", _wcsinc, 4,  0,4,0, CODEC_UTF16|USING_STRING, 0)

  // 12/1/2013 jichi:
  // AlterEgo
  // http://tieba.baidu.com/p/2736475133
  // http://www.hongfire.com/forum/showthread.php/36807-AGTH-text-extraction-tool-for-games-translation/page355
  //
  // MultiByteToWideChar
  // http://blgames.proboards.com/thread/265
  //
  // WideCharToMultiByte
  // http://www.hongfire.com/forum/showthread.php/36807-AGTH-text-extraction-tool-for-games-translation/page156
  //
  // int MultiByteToWideChar(
  //   _In_       UINT CodePage,
  //   _In_       DWORD dwFlags,
  //   _In_       LPCSTR lpMultiByteStr, // hook here
  //   _In_       int cbMultiByte,
  //   _Out_opt_  LPWSTR lpWideCharStr,
  //   _In_       int cchWideChar
  // );
  // int WideCharToMultiByte(
  //   _In_       UINT CodePage,
  //   _In_       DWORD dwFlags,
  //   _In_       LPCWSTR lpWideCharStr,
  //   _In_       int cchWideChar,
  //   _Out_opt_  LPSTR lpMultiByteStr,
  //   _In_       int cbMultiByte,
  //   _In_opt_   LPCSTR lpDefaultChar,
  //   _Out_opt_  LPBOOL lpUsedDefaultChar
  // );

  // 2/29/2020 Artikash: TODO: Sort out what to do for string comparison functions
  // http://sakuradite.com/topic/159
  NEW_HOOK(ptr, L"kernel32.dll", MultiByteToWideChar, s_arg3, 0, 4, 0, USING_STRING, s_arg4 / arg_sz)
  NEW_HOOK(ptr, L"kernel32.dll", WideCharToMultiByte, s_arg3, 0, 4, 0, CODEC_UTF16 | USING_STRING, s_arg4 / arg_sz)

  NEW_HOOK(ptr, L"kernel32.dll", GetStringTypeA, s_arg3, 0, 0, 0, USING_STRING, s_arg4 / arg_sz)
  NEW_HOOK(ptr, L"kernel32.dll", GetStringTypeExA, s_arg3, 0, 0, 0, USING_STRING, s_arg4 / arg_sz)
  NEW_HOOK(ptr, L"kernel32.dll", FoldStringA, s_arg2, 0, 0, 0, USING_STRING, s_arg3 / arg_sz)
  NEW_HOOK(ptr, L"kernel32.dll", GetStringTypeW, s_arg2, 0, 0, 0, CODEC_UTF16 | USING_STRING, s_arg3 / arg_sz)
  NEW_HOOK(ptr, L"kernel32.dll", GetStringTypeExW, s_arg3, 0, 0, 0, CODEC_UTF16 | USING_STRING, s_arg4 / arg_sz)
  NEW_HOOK(ptr, L"kernel32.dll", FoldStringW, s_arg2, 0, 0, 0, CODEC_UTF16 | USING_STRING, s_arg3 / arg_sz)

  NEW_HOOK(ptr, L"user32.dll", CharNextA, s_arg1, 0, 0, 0, DATA_INDIRECT, 0)
  NEW_HOOK(ptr, L"user32.dll", CharNextW, s_arg1, 0, 0, 0, CODEC_UTF16 | DATA_INDIRECT, 0)
  NEW_HOOK(ptr, L"user32.dll", CharPrevA, s_arg1, 0, 0, 0, DATA_INDIRECT, 0)
  NEW_HOOK(ptr, L"user32.dll", CharPrevW, s_arg1, 0, 0, 0, CODEC_UTF16 | DATA_INDIRECT, 0)
  NEW_HOOK(ptr, L"user32.dll", CharNextExA, s_arg2, 0, 0, 0, DATA_INDIRECT, 0)
  NEW_HOOK(ptr, L"user32.dll", CharPrevExA, s_arg2, 0, 0, 0, CODEC_UTF16 | DATA_INDIRECT, 0)

  // トキノ戦華
  NEW_HOOK(ptr, L"user32.dll", wvsprintfA, s_arg2, 0, 0, 0, USING_STRING, 0)
  NEW_HOOK(ptr, L"user32.dll", wvsprintfW, s_arg2, 0, 0, 0, CODEC_UTF16 | USING_STRING, 0)

  if (HMODULE module = GetModuleHandleW(L"OLEAUT32.dll"))
  {
    NEW_MODULE_HOOK(module, SysAllocString, s_arg1, 0, 0, 0, CODEC_UTF16 | USING_STRING, 0)
    NEW_MODULE_HOOK(module, SysAllocStringLen, s_arg1, 0, 0, 0, CODEC_UTF16 | USING_STRING | KNOWN_UNSTABLE, s_arg2 / arg_sz)
  }
}

// EOF
