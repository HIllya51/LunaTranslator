#pragma once

namespace Hijack
{
  inline bool Disable_Font_Switch = false;

#define DEF_FUN(_fun, _return, ...)                   \
  typedef _return(WINAPI *_fun##_fun_t)(__VA_ARGS__); \
  extern _fun##_fun_t old##_fun;                      \
  _return WINAPI new##_fun(__VA_ARGS__);

  DEF_FUN(MultiByteToWideChar, int, UINT CodePage, DWORD dwFlags, LPCSTR lpMultiByteStr, int cbMultiByte, LPWSTR lpWideCharStr, int cchWideChar)
  DEF_FUN(WideCharToMultiByte, int, UINT CodePage, DWORD dwFlags, LPCWSTR lpWideCharStr, int cchWideChar, LPSTR lpMultiByteStr, int cbMultiByte, LPCSTR lpDefaultChar, LPBOOL lpUsedDefaultChar)

  DEF_FUN(CreateFontIndirectA, HFONT, const LOGFONTA *lplf)
  DEF_FUN(CreateFontIndirectW, HFONT, const LOGFONTW *lplf)

  DEF_FUN(CreateFontA, HFONT, int nHeight, int nWidth, int nEscapement, int nOrientation, int fnWeight, DWORD fdwItalic, DWORD fdwUnderline, DWORD fdwStrikeOut, DWORD fdwCharSet, DWORD fdwOutputPrecision, DWORD fdwClipPrecision, DWORD fdwQuality, DWORD fdwPitchAndFamily, LPCSTR lpszFace)
  DEF_FUN(CreateFontW, HFONT, int nHeight, int nWidth, int nEscapement, int nOrientation, int fnWeight, DWORD fdwItalic, DWORD fdwUnderline, DWORD fdwStrikeOut, DWORD fdwCharSet, DWORD fdwOutputPrecision, DWORD fdwClipPrecision, DWORD fdwQuality, DWORD fdwPitchAndFamily, LPCWSTR lpszFace)

  DEF_FUN(GetGlyphOutlineA, DWORD, HDC hdc, UINT uChar, UINT uFormat, LPGLYPHMETRICS lpgm, DWORD cbBuffer, LPVOID lpvBuffer, const MAT2 *lpmat2)
  DEF_FUN(GetGlyphOutlineW, DWORD, HDC hdc, UINT uChar, UINT uFormat, LPGLYPHMETRICS lpgm, DWORD cbBuffer, LPVOID lpvBuffer, const MAT2 *lpmat2)

  DEF_FUN(GetTextExtentPoint32A, BOOL, HDC hdc, LPCSTR lpString, int cchString, LPSIZE lpSize)
  DEF_FUN(GetTextExtentPoint32W, BOOL, HDC hdc, LPCWSTR lpString, int cchString, LPSIZE lpSize)

  DEF_FUN(GetTextExtentExPointA, BOOL, HDC hdc, LPCSTR lpszStr, int cchString, int nMaxExtent, LPINT lpnFit, LPINT alpDx, LPSIZE lpSize)
  DEF_FUN(GetTextExtentExPointW, BOOL, HDC hdc, LPCWSTR lpszStr, int cchString, int nMaxExtent, LPINT lpnFit, LPINT alpDx, LPSIZE lpSize)

  DEF_FUN(GetCharABCWidthsA, BOOL, HDC hdc, UINT uFirstChar, UINT uLastChar, LPABC lpabc)
  DEF_FUN(GetCharABCWidthsW, BOOL, HDC hdc, UINT uFirstChar, UINT uLastChar, LPABC lpabc)

  DEF_FUN(TextOutA, BOOL, HDC hdc, int nXStart, int nYStart, LPCSTR lpString, int cchString)
  DEF_FUN(TextOutW, BOOL, HDC hdc, int nXStart, int nYStart, LPCWSTR lpString, int cchString)

  DEF_FUN(ExtTextOutA, BOOL, HDC hdc, int X, int Y, UINT fuOptions, const RECT *lprc, LPCSTR lpString, UINT cbCount, const INT *lpDx)
  DEF_FUN(ExtTextOutW, BOOL, HDC hdc, int X, int Y, UINT fuOptions, const RECT *lprc, LPCWSTR lpString, UINT cbCount, const INT *lpDx)

  DEF_FUN(DrawTextA, int, HDC hdc, LPCSTR lpString, int nCount, LPRECT lpRect, UINT uFormat)
  DEF_FUN(DrawTextW, int, HDC hdc, LPCWSTR lpString, int nCount, LPRECT lpRect, UINT uFormat)

  DEF_FUN(DrawTextExA, int, HDC hdc, LPSTR lpString, int nCount, LPRECT lpRect, UINT dwDTFormat, LPDRAWTEXTPARAMS lpDTParams)
  DEF_FUN(DrawTextExW, int, HDC hdc, LPWSTR lpString, int nCount, LPRECT lpRect, UINT dwDTFormat, LPDRAWTEXTPARAMS lpDTParams)

  DEF_FUN(CharNextA, LPSTR, LPCSTR lpString)
  // DEF_FUN(CharNextW, LPWSTR, LPCWSTR lpString)
  // DEF_FUN(CharNextExA, LPSTR, WORD COdePage, LPCSTR lpString, DWORD dwFlags)
  // DEF_FUN(CharNextExW, LPWSTR, WORD COdePage, LPCWSTR lpString, DWORD dwFlags)
  DEF_FUN(CharPrevA, LPSTR, LPCSTR lpStart, LPCSTR lpCurrent)
  // DEF_FUN(CharNextW, LPWSTR, LPCWSTR lpStart, LPCWSTR lpCurrent)
#undef DEF_FUN

  // Global variables

} // namespace Hijack

// EOF
