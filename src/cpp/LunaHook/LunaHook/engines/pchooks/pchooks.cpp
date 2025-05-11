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

constexpr short arg_sz = (short)sizeof(void *);
std::set<void *> hookonce;

#ifndef WINXP
std::mutex hookoncelock;
#else
class SimpleMutex
{
public:
  SimpleMutex()
  {
    mutex = CreateMutex(NULL, FALSE, NULL);
  }
  ~SimpleMutex()
  {
    CloseHandle(mutex);
  }
  void lock()
  {
    WaitForSingleObject(mutex, INFINITE);
  }
  void unlock()
  {
    ReleaseMutex(mutex);
  }

private:
  HANDLE mutex;
};
SimpleMutex hookoncelock; // xp上这个谜之导致dll free时崩溃。虽然这个锁其实没啥必要，但还是保留一下吧。
#endif
#define NEW_HOOK(ptr, _dll, _fun, _data, _data_ind, _split_off, _split_ind, _type, _len_off)                       \
  {                                                                                                                \
    HookParam hp;                                                                                                  \
    wcsncpy_s(hp.module, _dll, MAX_MODULE_SIZE - 1);                                                               \
    strncpy_s(hp.function, #_fun, MAX_MODULE_SIZE - 1);                                                            \
    hp.offset = GETARG(_data);                                                                                     \
    hp.index = GETARG(_data_ind);                                                                                  \
    hp.split = GETARG(_split_off);                                                                                 \
    hp.split_index = GETARG(_split_ind);                                                                           \
    hp.type = _type | MODULE_OFFSET | FUNCTION_OFFSET;                                                             \
    hp.length_offset = GETARG(_len_off) / arg_sz;                                                                  \
    auto currptr = GetModuleHandle(hp.module) ? GetProcAddress(GetModuleHandle(hp.module), hp.function) : nullptr; \
    if (currptr)                                                                                                   \
    {                                                                                                              \
      bool dohook = false;                                                                                         \
      std::lock_guard _(hookoncelock);                                                                             \
      if (ptr)                                                                                                     \
        dohook = currptr == ptr;                                                                                   \
      else                                                                                                         \
        dohook = !hookonce.count(currptr);                                                                         \
      if (dohook)                                                                                                  \
      {                                                                                                            \
        NewHook(hp, #_fun);                                                                                        \
        hookonce.insert(currptr);                                                                                  \
      }                                                                                                            \
    }                                                                                                              \
  }

#define NEW_MODULE_HOOK(ptr, _module, _fun, _data, _data_ind, _split_off, _split_ind, _type, _len_off) \
  {                                                                                                    \
    HookParam hp;                                                                                      \
    wchar_t path[MAX_PATH];                                                                            \
    if (GetModuleFileNameW(_module, path, MAX_PATH))                                                   \
      wcsncpy_s(hp.module, wcsrchr(path, L'\\') + 1, MAX_MODULE_SIZE - 1);                             \
    strncpy_s(hp.function, #_fun, MAX_MODULE_SIZE - 1);                                                \
    hp.offset = GETARG(_data);                                                                         \
    hp.index = GETARG(_data_ind);                                                                      \
    hp.split = GETARG(_split_off);                                                                     \
    hp.split_index = GETARG(_split_ind);                                                               \
    hp.type = _type | MODULE_OFFSET | FUNCTION_OFFSET;                                                 \
    hp.length_offset = GETARG(_len_off) / arg_sz;                                                      \
    auto currptr = GetProcAddress(_module, hp.function);                                               \
    if (currptr)                                                                                       \
    {                                                                                                  \
      bool dohook = false;                                                                             \
      std::lock_guard _(hookoncelock);                                                                 \
      if (ptr)                                                                                         \
        dohook = currptr == ptr;                                                                       \
      else                                                                                             \
        dohook = !hookonce.count(currptr);                                             \
      if (dohook)                                                                                      \
      {                                                                                                \
        NewHook(hp, #_fun);                                                                            \
        hookonce.insert(currptr);                                                                      \
      }                                                                                                \
    }                                                                                                  \
  }

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
  // gdi32.dll
  NEW_HOOK(ptr, L"gdi32.dll", GetTextExtentPoint32A, 2, 0, 1, 0, USING_STRING, 3)
  NEW_HOOK(ptr, L"gdi32.dll", GetTextExtentExPointA, 2, 0, 1, 0, USING_STRING, 3)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharacterPlacementA, 2, 0, 1, 0, USING_STRING, 3)
  NEW_HOOK(ptr, L"gdi32.dll", GetGlyphIndicesA, 2, 0, 1, 0, USING_STRING, 3)
  NEW_HOOK(ptr, L"gdi32.dll", GetGlyphOutlineA, 2, 0, 1, 0, CODEC_ANSI_BE, 0)
  NEW_HOOK(ptr, L"gdi32.dll", ExtTextOutA, 6, 0, 1, 0, USING_STRING, 7)
  NEW_HOOK(ptr, L"gdi32.dll", TextOutA, 4, 0, 1, 0, USING_STRING, 5)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharABCWidthsA, 2, 0, 1, 0, CODEC_ANSI_BE, 0)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharABCWidthsFloatA, 2, 0, 1, 0, CODEC_ANSI_BE, 0)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharWidth32A, 2, 0, 1, 0, CODEC_ANSI_BE, 0)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharWidthFloatA, 2, 0, 1, 0, CODEC_ANSI_BE, 0)

  NEW_HOOK(ptr, L"gdi32.dll", GetTextExtentPoint32W, 2, 0, 1, 0, CODEC_UTF16 | USING_STRING, 3)
  NEW_HOOK(ptr, L"gdi32.dll", GetTextExtentExPointW, 2, 0, 1, 0, CODEC_UTF16 | USING_STRING, 3)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharacterPlacementW, 2, 0, 1, 0, CODEC_UTF16 | USING_STRING, 3)
  NEW_HOOK(ptr, L"gdi32.dll", GetGlyphIndicesW, 2, 0, 1, 0, CODEC_UTF16 | USING_STRING, 3)
  NEW_HOOK(ptr, L"gdi32.dll", GetGlyphOutlineW, 2, 0, 1, 0, CODEC_UTF16, 0)
  // ExtTextOutW全是乱码，没卵用
  // NEW_HOOK(ptr, L"gdi32.dll", ExtTextOutW,            6, 0,1,0, CODEC_UTF16|USING_STRING, 7 )
  NEW_HOOK(ptr, L"gdi32.dll", TextOutW, 4, 0, 1, 0, CODEC_UTF16 | USING_STRING, 5)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharABCWidthsW, 2, 0, 1, 0, CODEC_UTF16, 0)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharABCWidthsFloatW, 2, 0, 1, 0, CODEC_UTF16, 0)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharWidth32W, 2, 0, 1, 0, CODEC_UTF16, 0)
  NEW_HOOK(ptr, L"gdi32.dll", GetCharWidthFloatW, 2, 0, 1, 0, CODEC_UTF16, 0)

  // user32.dll
  NEW_HOOK(ptr, L"user32.dll", DrawTextA, 2, 0, 1, 0, USING_STRING, 3)
  NEW_HOOK(ptr, L"user32.dll", DrawTextExA, 2, 0, 1, 0, USING_STRING, 3)
  NEW_HOOK(ptr, L"user32.dll", TabbedTextOutA, 4, 0, 1, 0, USING_STRING, 5)
  NEW_HOOK(ptr, L"user32.dll", GetTabbedTextExtentA, 2, 0, 1, 0, USING_STRING, 3)
  NEW_HOOK(ptr, L"user32.dll", DrawTextW, 2, 0, 1, 0, CODEC_UTF16 | USING_STRING, 3)
  NEW_HOOK(ptr, L"user32.dll", DrawTextExW, 2, 0, 1, 0, CODEC_UTF16 | USING_STRING, 3)
  NEW_HOOK(ptr, L"user32.dll", TabbedTextOutW, 4, 0, 1, 0, CODEC_UTF16 | USING_STRING, 5)
  NEW_HOOK(ptr, L"user32.dll", GetTabbedTextExtentW, 2, 0, 1, 0, CODEC_UTF16 | USING_STRING, 3)
}

// jichi 6/18/2015: GDI+ functions
void PcHooks::hookGDIPlusFunctions(void *ptr)
{
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
  NEW_MODULE_HOOK(ptr, hModule, GdipAddPathString, 2, 0, 5, 0, CODEC_UTF16 | USING_STRING, 3)
  NEW_MODULE_HOOK(ptr, hModule, GdipAddPathStringI, 2, 0, 5, 0, CODEC_UTF16 | USING_STRING, 3)
  NEW_MODULE_HOOK(ptr, hModule, GdipMeasureCharacterRanges, 2, 0, 1, 0, CODEC_UTF16 | USING_STRING, 3)
  NEW_MODULE_HOOK(ptr, hModule, GdipDrawString, 2, 0, 1, 0, CODEC_UTF16 | USING_STRING, 3)
  NEW_MODULE_HOOK(ptr, hModule, GdipMeasureString, 2, 0, 1, 0, CODEC_UTF16 | USING_STRING, 3)
  NEW_MODULE_HOOK(ptr, hModule, GdipDrawDriverString, 1, 0, 3, 0, CODEC_UTF16 | USING_STRING, 2)
  NEW_MODULE_HOOK(ptr, hModule, GdipMeasureDriverString, 1, 0, 3, 0, CODEC_UTF16 | USING_STRING, 2)
}

void PcHooks::hookD3DXFunctions(HMODULE d3dxModule, void *ptr)
{
  if (GetProcAddress(d3dxModule, "D3DXCreateTextA"))
  {
    NEW_MODULE_HOOK(ptr, d3dxModule, D3DXCreateTextA, 3, 0, 0, 0, USING_STRING, 0)
    NEW_MODULE_HOOK(ptr, d3dxModule, D3DXCreateTextW, 3, 0, 0, 0, USING_STRING | CODEC_UTF16, 0)
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
      hp.offset = 3;
      hp.length_offset = 4;
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
  // int TextHook::InitHook(LPVOID addr, DWORD data, DWORD data_ind, DWORD split_off, DWORD split_ind, WORD type, DWORD len_off)

  // http://msdn.microsoft.com/en-us/library/78zh94ax.aspx
  // int WINAPI lstrlen(LPCTSTR lpString);
  // Lstr functions usually extracts rubbish, and might crash certain games like 「Magical Marriage Lunatics!!」
  // Needed by Gift
  // Use arg1 address for both split and data
  NEW_HOOK(ptr, L"kernel32.dll", lstrlenA, 1, 0, 1, 0, USING_STRING, 0)
  NEW_HOOK(ptr, L"kernel32.dll", lstrcpyA, 2, 0, 0, 0, USING_STRING, 0)
  NEW_HOOK(ptr, L"kernel32.dll", lstrcpynA, 2, 0, 0, 0, USING_STRING, 0)

  NEW_HOOK(ptr, L"kernel32.dll", lstrlenW, 1, 0, 1, 0, CODEC_UTF16 | USING_STRING, 0)
  NEW_HOOK(ptr, L"kernel32.dll", lstrcpyW, 2, 0, 0, 0, CODEC_UTF16 | USING_STRING, 0)
  NEW_HOOK(ptr, L"kernel32.dll", lstrcpynW, 2, 0, 0, 0, CODEC_UTF16 | USING_STRING, 0)

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
  NEW_HOOK(ptr, L"kernel32.dll", MultiByteToWideChar, 3, 0, 4, 0, USING_STRING, 4)
  NEW_HOOK(ptr, L"kernel32.dll", WideCharToMultiByte, 3, 0, 4, 0, CODEC_UTF16 | USING_STRING, 4)

  NEW_HOOK(ptr, L"kernel32.dll", GetStringTypeA, 3, 0, 0, 0, USING_STRING, 4)
  NEW_HOOK(ptr, L"kernel32.dll", GetStringTypeExA, 3, 0, 0, 0, USING_STRING, 4)
  NEW_HOOK(ptr, L"kernel32.dll", FoldStringA, 2, 0, 0, 0, USING_STRING, 3)
  NEW_HOOK(ptr, L"kernel32.dll", GetStringTypeW, 2, 0, 0, 0, CODEC_UTF16 | USING_STRING, 3)
  NEW_HOOK(ptr, L"kernel32.dll", GetStringTypeExW, 3, 0, 0, 0, CODEC_UTF16 | USING_STRING, 4)
  NEW_HOOK(ptr, L"kernel32.dll", FoldStringW, 2, 0, 0, 0, CODEC_UTF16 | USING_STRING, 3)

  NEW_HOOK(ptr, L"user32.dll", CharNextA, 1, 0, 0, 0, DATA_INDIRECT, 0)
  NEW_HOOK(ptr, L"user32.dll", CharNextW, 1, 0, 0, 0, CODEC_UTF16 | DATA_INDIRECT, 0)
  NEW_HOOK(ptr, L"user32.dll", CharPrevA, 1, 0, 0, 0, DATA_INDIRECT, 0)
  NEW_HOOK(ptr, L"user32.dll", CharPrevW, 1, 0, 0, 0, CODEC_UTF16 | DATA_INDIRECT, 0)
  NEW_HOOK(ptr, L"user32.dll", CharNextExA, 2, 0, 0, 0, DATA_INDIRECT, 0)
  NEW_HOOK(ptr, L"user32.dll", CharPrevExA, 2, 0, 0, 0, CODEC_UTF16 | DATA_INDIRECT, 0)

  // トキノ戦華
  NEW_HOOK(ptr, L"user32.dll", wvsprintfA, 2, 0, 0, 0, USING_STRING, 0)
  NEW_HOOK(ptr, L"user32.dll", wvsprintfW, 2, 0, 0, 0, CODEC_UTF16 | USING_STRING, 0)

  if (HMODULE module = GetModuleHandleW(L"OLEAUT32.dll"))
  {
    NEW_MODULE_HOOK(ptr, module, SysAllocString, 1, 0, 0, 0, CODEC_UTF16 | USING_STRING, 0)
    NEW_MODULE_HOOK(ptr, module, SysAllocStringLen, 1, 0, 0, 0, CODEC_UTF16 | USING_STRING | KNOWN_UNSTABLE, 2)
  }
}

// EOF
