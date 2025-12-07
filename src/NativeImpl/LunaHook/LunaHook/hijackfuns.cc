
#pragma intrinsic(_ReturnAddress)

// Disable only for debugging purpose
// #define HIJACK_GDI_FONT
// #define HIJACK_GDI_TEXT

#define DEF_FUN(_f) Hijack::_f##_fun_t Hijack::old##_f = ::_f;
DEF_FUN(CreateFontA)
DEF_FUN(CreateFontW)
DEF_FUN(CreateFontIndirectA)
DEF_FUN(CreateFontIndirectW)
DEF_FUN(GetGlyphOutlineA)
DEF_FUN(GetGlyphOutlineW)
DEF_FUN(GetTextExtentPoint32A)
DEF_FUN(GetTextExtentPoint32W)
DEF_FUN(GetTextExtentExPointA)
DEF_FUN(GetTextExtentExPointW)
DEF_FUN(GetCharABCWidthsA)
DEF_FUN(GetCharABCWidthsW)
DEF_FUN(TextOutA)
DEF_FUN(TextOutW)
DEF_FUN(ExtTextOutA)
DEF_FUN(ExtTextOutW)
DEF_FUN(DrawTextA)
DEF_FUN(DrawTextW)
DEF_FUN(DrawTextExA)
DEF_FUN(DrawTextExW)
DEF_FUN(CharNextA)
// DEF_FUN(CharNextW)
// DEF_FUN(CharNextExA)
// DEF_FUN(CharNextExW)
DEF_FUN(CharPrevA)
// DEF_FUN(CharPrevW)
DEF_FUN(MultiByteToWideChar)
DEF_FUN(WideCharToMultiByte)
#undef DEF_FUN

/** Helper */
namespace
{
  inline const wchar_t *maybe_disabled_fontFamily()
  {
    return Hijack::Disable_Font_Switch ? L"" : commonsharedmem->fontFamily;
  }
}
namespace
{ // unnamed
  UINT8 systemCharSet()
  {
    enum CodePage
    {
      NullCodePage = 0,
      Utf8CodePage = 65001, // UTF-8
      Utf16CodePage = 1200, // UTF-16
      SjisCodePage = 932,   // SHIFT-JIS
      GbkCodePage = 936,    // GB2312
      KscCodePage = 949,    // EUC-KR
      Big5CodePage = 950,   // BIG5
      TisCodePage = 874,    // TIS-620
      Koi8CodePage = 866    // KOI8-R
    };
    auto systemCodePage = ::GetACP();
    switch (systemCodePage)
    {
    case TisCodePage:
      return THAI_CHARSET;
    case Koi8CodePage:
      return RUSSIAN_CHARSET;
    case SjisCodePage:
      return SHIFTJIS_CHARSET;
    case GbkCodePage:
      return GB2312_CHARSET;
    case Big5CodePage:
      return CHINESEBIG5_CHARSET;

    case KscCodePage:
      return HANGUL_CHARSET;
    case 1361:
      return JOHAB_CHARSET; // alternative Korean character set

    case 1250:
      return EASTEUROPE_CHARSET;
    case 1251:
      return RUSSIAN_CHARSET; // cyrillic
    case 1253:
      return GREEK_CHARSET;
    case 1254:
      return TURKISH_CHARSET;

    case 862:
      return HEBREW_CHARSET; // obsolete
    case 1255:
      return HEBREW_CHARSET;

    case 1256:
      return ARABIC_CHARSET;
    case 1257:
      return BALTIC_CHARSET;
    case 1258:
      return VIETNAMESE_CHARSET;

    // default: return DEFAULT_CHARSET;
    default:
      return 0;
    }
  }
  void customizeLogFontA(LOGFONTA *lplf)
  {

    if (commonsharedmem->fontCharSetEnabled)
    {
      auto charSet = commonsharedmem->fontCharSet;
      if (!charSet)
        charSet = systemCharSet();
      if (charSet)
        lplf->lfCharSet = charSet;
    }
    /*
    if (s->fontWeight)
      lplf->lfWeight = s->fontWeight;
    if (s->isFontScaled()) {
      lplf->lfWidth *= s->fontScale;
      lplf->lfHeight *= s->fontScale;
    }
    */
  }

  void customizeLogFontW(LOGFONTW *lplf)
  {
    customizeLogFontA((LOGFONTA *)lplf);

    std::wstring s = maybe_disabled_fontFamily();
    if (!s.empty())
    {
      lplf->lfFaceName[s.size()] = 0;
      memcpy(lplf->lfFaceName, s.c_str(), s.size());
    }
  }

  // LogFont manager

  class LogFontManager
  {
    typedef std::pair<HFONT, LOGFONTW> font_pair;
    std::list<font_pair> fonts_;

    static bool eq(const LOGFONTW &x, const LOGFONTW &y);

  public:
    HFONT get(const LOGFONTW &lf) const;
    void add(HFONT hf, const LOGFONTW &lf);
    void remove(HFONT hf);
    void remove(const LOGFONTW &lf);
  };

  bool LogFontManager::eq(const LOGFONTW &x, const LOGFONTW &y)
  { // I assume there is no padding
    return ::wcscmp(x.lfFaceName, y.lfFaceName) == 0 && ::memcmp(&x, &y, sizeof(x) - sizeof(x.lfFaceName)) == 0;
  }

  void LogFontManager::add(HFONT hf, const LOGFONTW &lf)
  {
    fonts_.push_back(std::make_pair(hf, lf));
  }

  void LogFontManager::remove(HFONT hf)
  {
    auto _ = std::remove_if(fonts_.begin(), fonts_.end(), [&hf](const font_pair &it)
                            { return it.first == hf; });
  }

  void LogFontManager::remove(const LOGFONTW &lf)
  {
    auto _ = std::remove_if(fonts_.begin(), fonts_.end(), [&lf](const font_pair &it)
                            { return eq(it.second, lf); });
  }

  HFONT LogFontManager::get(const LOGFONTW &lf) const
  {
    for (const font_pair &it : fonts_)
      if (eq(it.second, lf))
        return it.first;
    return nullptr;
  }

  // GDI font switcher

  class DCFontSwitcher
  {
    static LogFontManager fonts_;

    HDC hdc_;
    HFONT oldFont_,
        newFont_;
    std::wstring newfontname;

  public:
    explicit DCFontSwitcher(HDC hdc); // pass 0 to disable this class
    ~DCFontSwitcher();
  };

  LogFontManager DCFontSwitcher::fonts_;

  DCFontSwitcher::~DCFontSwitcher()
  {
    // No idea why selecting old font will crash Mogeko Castle
    // if (oldFont_ && oldFont_ != HGDI_ERROR)
    //  ::SelectObject(hdc_, oldFont_);

    // Never delete new font but cache them
    // This could result in bad font after game is reset and deleted my font
    // if (newFont_)
    //  ::DeleteObject(newFont_);
  }
  bool isFontCustomized()
  {
    return commonsharedmem->fontCharSetEnabled || wcslen(maybe_disabled_fontFamily());
  }
  DCFontSwitcher::DCFontSwitcher(HDC hdc)
      : hdc_(hdc), oldFont_(nullptr), newFont_(nullptr), newfontname(L"")
  {
    if (!hdc_)
      return;
    /*
  auto p = HijackHelper::instance();
  if (!p)
    return;
  auto s = p->settings();
  if (!s->deviceContextFontEnabled || !s->isFontCustomized())
    return;
*/
    TEXTMETRICW tm;
    if (!::GetTextMetricsW(hdc, &tm))
      return;

    LOGFONTW lf = {};
    lf.lfHeight = tm.tmHeight;
    lf.lfWeight = tm.tmWeight;
    lf.lfItalic = tm.tmItalic;
    lf.lfUnderline = tm.tmUnderlined;
    lf.lfStrikeOut = tm.tmStruckOut;
    lf.lfCharSet = tm.tmCharSet;
    lf.lfPitchAndFamily = tm.tmPitchAndFamily;

    customizeLogFontW(&lf);

    if (std::wstring(maybe_disabled_fontFamily()).empty())
      ::GetTextFaceW(hdc_, LF_FACESIZE, lf.lfFaceName);
    else
    {
      wcscpy(lf.lfFaceName, maybe_disabled_fontFamily());
    }
    newFont_ = fonts_.get(lf);
    if ((!newFont_) || (newfontname != std::wstring(maybe_disabled_fontFamily())))
    {
      newFont_ = Hijack::oldCreateFontIndirectW(&lf);
      fonts_.add(newFont_, lf);
      newfontname = std::wstring(maybe_disabled_fontFamily());
    }
    oldFont_ = (HFONT)SelectObject(hdc_, newFont_);
  }

} // unnamed namespace

/** Fonts */

// http://forums.codeguru.com/showthread.php?500522-Need-clarification-about-CreateFontIndirect
// The font creation functions will never fail
HFONT WINAPI Hijack::newCreateFontIndirectA(const LOGFONTA *lplf)
{

  // DOUT("width:" << lplf->lfWidth << ", height:" << lplf->lfHeight << ", weight:" << lplf->lfWeight);
  // if (auto p = HijackHelper::instance()) {
  // auto s = p->settings();
  std::wstring fontFamily = maybe_disabled_fontFamily();
  if (lplf && isFontCustomized())
  {
    union
    {
      LOGFONTA a;
      LOGFONTW w;
    } lf = {*lplf}; // only initialize the first member of LOGFONTA
    customizeLogFontA(&lf.a);
    if (!fontFamily.empty())
    {
      if (all_ascii(fontFamily))
        ::strcpy(lf.a.lfFaceName, WideStringToString(fontFamily, CP_ACP).c_str());
      else
      {
        lf.w.lfFaceName[fontFamily.size()] = 0;
        // s->fontFamily.toWCharArray(lf.w.lfFaceName);
        memcpy(lf.w.lfFaceName, fontFamily.c_str(), fontFamily.size());
        return oldCreateFontIndirectW(&lf.w);
      }
    }
    return oldCreateFontIndirectA(&lf.a);
  }
  //}
  return oldCreateFontIndirectA(lplf);
}

HFONT WINAPI Hijack::newCreateFontIndirectW(const LOGFONTW *lplf)
{

  // DOUT("width:" << lplf->lfWidth << ", height:" << lplf->lfHeight << ", weight:" << lplf->lfWeight);
  // if (auto p = HijackHelper::instance()) {
  // auto s = p->settings();
  if (lplf && isFontCustomized())
  {
    LOGFONTW lf(*lplf);
    customizeLogFontW(&lf);
    return oldCreateFontIndirectW(&lf);
  }
  // }
  return oldCreateFontIndirectW(lplf);
}

#define CREATE_FONT_ARGS nHeight, nWidth, nEscapement, nOrientation, fnWeight, fdwItalic, fdwUnderline, fdwStrikeOut, fdwCharSet, fdwOutputPrecision, fdwClipPrecision, fdwQuality, fdwPitchAndFamily, lpszFace
HFONT WINAPI Hijack::newCreateFontA(int nHeight, int nWidth, int nEscapement, int nOrientation, int fnWeight, DWORD fdwItalic, DWORD fdwUnderline, DWORD fdwStrikeOut, DWORD fdwCharSet, DWORD fdwOutputPrecision, DWORD fdwClipPrecision, DWORD fdwQuality, DWORD fdwPitchAndFamily, LPCSTR lpszFace)
{

  if (isFontCustomized())
  {
    if (commonsharedmem->fontCharSetEnabled)
    {
      auto charSet = commonsharedmem->fontCharSet;
      if (!charSet)
        charSet = systemCharSet();
      if (charSet)
        fdwCharSet = charSet;
    }
    /*
    if (s->fontWeight)
      fnWeight = s->fontWeight;
    if (s->isFontScaled()) {
      nWidth *= s->fontScale;
      nHeight *= s->fontScale;
    }
    */
    std::wstring fontFamily = maybe_disabled_fontFamily();
    if (!fontFamily.empty())
    {
      if (all_ascii(fontFamily))
      {
        lpszFace = WideStringToString(fontFamily, CP_ACP).c_str();
        return oldCreateFontA(CREATE_FONT_ARGS);
      }
      else
      {
        auto lpszFace = (LPCWSTR)fontFamily.c_str();
        return oldCreateFontW(CREATE_FONT_ARGS);
      }
    }
  }
  return oldCreateFontA(CREATE_FONT_ARGS);
}

HFONT WINAPI Hijack::newCreateFontW(int nHeight, int nWidth, int nEscapement, int nOrientation, int fnWeight, DWORD fdwItalic, DWORD fdwUnderline, DWORD fdwStrikeOut, DWORD fdwCharSet, DWORD fdwOutputPrecision, DWORD fdwClipPrecision, DWORD fdwQuality, DWORD fdwPitchAndFamily, LPCWSTR lpszFace)
{

  if (isFontCustomized())
  {
    if (commonsharedmem->fontCharSetEnabled)
    {
      auto charSet = commonsharedmem->fontCharSet;
      if (!charSet)
        charSet = systemCharSet();
      if (charSet)
        fdwCharSet = charSet;
    }
    /*
    if (s->fontWeight)
      fnWeight = s->fontWeight;
    if (s->isFontScaled()) {
      nWidth *= s->fontScale;
      nHeight *= s->fontScale;
    }*/
    if (!std::wstring(maybe_disabled_fontFamily()).empty())
      lpszFace = (LPCWSTR)commonsharedmem;
  }
  return oldCreateFontW(CREATE_FONT_ARGS);
}
#undef CREATE_FONT_ARGS

/** Encoding */

LPSTR WINAPI Hijack::newCharNextA(LPCSTR lpString)
{

  // if (::GetACP() == 932)
  return const_cast<char *>(dynsjis::nextchar(lpString));
  // return oldCharNextA(lpString);
}

LPSTR WINAPI Hijack::newCharPrevA(LPCSTR lpStart, LPCSTR lpCurrent)
{

  // if (::GetACP() == 932)
  return const_cast<char *>(dynsjis::prevchar(lpCurrent, lpStart));
  // return oldCharNextA(lpStart, lpCurrent);
}
extern DynamicShiftJISCodec *dynamiccodec;
int WINAPI Hijack::newMultiByteToWideChar(UINT CodePage, DWORD dwFlags, LPCSTR lpMultiByteStr, int cbMultiByte, LPWSTR lpWideCharStr, int cchWideChar)
{
  //
  /* if (auto p = HijackHelper::instance())
     if (p->settings()->localeEmulationEnabled)
       if (CodePage == CP_THREAD_ACP || CodePage == CP_OEMCP)
         CodePage = CP_ACP;
         */
  if (CodePage == CP_THREAD_ACP || CodePage == CP_OEMCP)
    CodePage = CP_ACP;
  // CP_ACP(0), CP_MACCP(1), CP_OEMCP(2), CP_THREAD_ACP(3)
  if ((CodePage <= 3 || CodePage == 932) && cchWideChar > 0 && cbMultiByte > 1)
  {
    bool dynamic;
    std::string data(lpMultiByteStr, cbMultiByte);
    auto text = dynamiccodec->decode(data, &dynamic);
    if (dynamic && !text.empty())
    {
      int size = min(text.size() + 1, cchWideChar);
      ::memcpy(lpWideCharStr, text.c_str(), size * 2);
      // lpWideCharStr[size - 1] = 0; // enforce trailing zero
      return size - 1;
    }
  }
  return oldMultiByteToWideChar(CodePage, dwFlags, lpMultiByteStr, cbMultiByte, lpWideCharStr, cchWideChar);
}

int WINAPI Hijack::newWideCharToMultiByte(UINT CodePage, DWORD dwFlags, LPCWSTR lpWideCharStr, int cchWideChar, LPSTR lpMultiByteStr, int cbMultiByte, LPCSTR lpDefaultChar, LPBOOL lpUsedDefaultChar)
{
  //
  if (CodePage == CP_THREAD_ACP || CodePage == CP_OEMCP)
    CodePage = CP_ACP;

  if ((CodePage <= 3 || CodePage == 932) && cchWideChar > 0 && cbMultiByte >= 0)
  {
    bool dynamic;
    auto text = std::wstring(lpWideCharStr, cchWideChar);
    auto data = dynamiccodec->encodeSTD(text, &dynamic);
    if (dynamic && !data.empty())
    {

      int size = data.size() + 1;
      if (cbMultiByte && cbMultiByte < size)
        size = cbMultiByte;
      ::memcpy(lpMultiByteStr, data.c_str(), size);
      // lpMultiByteStr[size - 1] = 0; // enforce trailing zero
      return size - 1;
    }
  }
  return oldWideCharToMultiByte(CodePage, dwFlags, lpWideCharStr, cchWideChar, lpMultiByteStr, cbMultiByte, lpDefaultChar, lpUsedDefaultChar);
}

/** Text */
UINT decodeChar(UINT ch, bool *dynamic)
{
  if (dynamic)
    *dynamic = false;
  if (ch > 0xff)
  {
    bool t;
    char data[3] = {(char)((BYTE)(ch >> 8) & 0xff), char((BYTE)ch & 0xff), 0};
    auto text = dynamiccodec->decode(data, &t);
    if (t && text.size() == 1)
    {
      if (dynamic)
        *dynamic = true;
      return text[0];
    }
  }
  return ch;
}
#define DECODE_CHAR(uChar, ...)                \
  {                                            \
    if (uChar > 0xff)                          \
      if (1)                                   \
      {                                        \
        bool dynamic;                          \
        UINT ch = decodeChar(uChar, &dynamic); \
        if (dynamic && ch)                     \
        {                                      \
          uChar = ch;                          \
          return (__VA_ARGS__);                \
        }                                      \
      }                                        \
  }

#define DECODE_TEXT(lpString, cchString, ...)                                                \
  {                                                                                          \
    if (cchString == -1 || cchString > 1)                                                    \
      if (1)                                                                                 \
      {                                                                                      \
        bool dynamic;                                                                        \
        auto data = std::string(lpString, cchString == -1 ? ::strlen(lpString) : cchString); \
        if (data.size() > 1)                                                                 \
        {                                                                                    \
          auto text = dynamiccodec->decode(data, &dynamic);                                  \
          if (dynamic && !text.empty())                                                      \
          {                                                                                  \
            LPCWSTR lpString = (LPCWSTR)text.c_str();                                        \
            cchString = text.size();                                                         \
            return (__VA_ARGS__);                                                            \
          }                                                                                  \
        }                                                                                    \
      }                                                                                      \
  }
#define TRANSLATE_TEXT_A(lpString, cchString, ...)                                         \
  {                                                                                        \
    if (auto q = EngineController::instance())                                             \
    {                                                                                      \
      auto data = std::string(lpString, cchString == -1 ? ::strlen(lpString) : cchString); \
      std::wstring oldText = q->decode(data);                                              \
      if (!oldText.empty())                                                                \
      {                                                                                    \
        enum                                                                               \
        {                                                                                  \
          role = Engine::OtherRole                                                         \
        };                                                                                 \
        ULONG split = (ULONG)_ReturnAddress();                                             \
        auto sig = Engine::hashThreadSignature(role, split);                               \
        auto newText = q->dispatchTextWSTD(oldText, role, sig);                            \
        if (newText != oldText)                                                            \
        {                                                                                  \
          LPCWSTR lpString = (LPCWSTR)newText.c_str();                                     \
          cchString = newText.size();                                                      \
          return (__VA_ARGS__);                                                            \
        }                                                                                  \
      }                                                                                    \
    }                                                                                      \
  }

#define TRANSLATE_TEXT_W(lpString, cchString, ...)           \
  {                                                          \
    if (auto q = EngineController::instance())               \
    {                                                        \
      auto text = std::wstring(lpString, cchString);         \
      if (!text.empty())                                     \
      {                                                      \
        enum                                                 \
        {                                                    \
          role = Engine::OtherRole                           \
        };                                                   \
        ULONG split = (ULONG)_ReturnAddress();               \
        auto sig = Engine::hashThreadSignature(role, split); \
        text = q->dispatchTextWSTD(text, role, sig);         \
        LPCWSTR lpString = (LPCWSTR)text.c_str();            \
        cchString = text.size();                             \
        return (__VA_ARGS__);                                \
      }                                                      \
    }                                                        \
  }

DWORD WINAPI Hijack::newGetGlyphOutlineA(HDC hdc, UINT uChar, UINT uFormat, LPGLYPHMETRICS lpgm, DWORD cbBuffer, LPVOID lpvBuffer, const MAT2 *lpmat2)
{
  DCFontSwitcher fs(hdc);

  DECODE_CHAR(uChar, oldGetGlyphOutlineW(hdc, ch, uFormat, lpgm, cbBuffer, lpvBuffer, lpmat2))
  return oldGetGlyphOutlineA(hdc, uChar, uFormat, lpgm, cbBuffer, lpvBuffer, lpmat2);
}

DWORD WINAPI Hijack::newGetGlyphOutlineW(HDC hdc, UINT uChar, UINT uFormat, LPGLYPHMETRICS lpgm, DWORD cbBuffer, LPVOID lpvBuffer, const MAT2 *lpmat2)
{

  DCFontSwitcher fs(hdc);
  return oldGetGlyphOutlineW(hdc, uChar, uFormat, lpgm, cbBuffer, lpvBuffer, lpmat2);
}

BOOL WINAPI Hijack::newGetTextExtentPoint32A(HDC hdc, LPCSTR lpString, int cchString, LPSIZE lpSize)
{

  DCFontSwitcher fs(hdc);
  // TRANSLATE_TEXT_A(lpString, cchString, oldGetTextExtentPoint32W(hdc, lpString, cchString, lpSize))
  DECODE_TEXT(lpString, cchString, oldGetTextExtentPoint32W(hdc, lpString, cchString, lpSize))
  return oldGetTextExtentPoint32A(hdc, lpString, cchString, lpSize);
}

BOOL WINAPI Hijack::newGetTextExtentPoint32W(HDC hdc, LPCWSTR lpString, int cchString, LPSIZE lpSize)
{

  DCFontSwitcher fs(hdc);
  // TRANSLATE_TEXT_W(lpString, cchString, oldGetTextExtentPoint32W(hdc, lpString, cchString, lpSize))
  return oldGetTextExtentPoint32W(hdc, lpString, cchString, lpSize);
}

BOOL WINAPI Hijack::newGetTextExtentExPointA(HDC hdc, LPCSTR lpString, int cchString, int nMaxExtent, LPINT lpnFit, LPINT alpDx, LPSIZE lpSize)
{

  // DCFontSwitcher fs(hdc);
  // TRANSLATE_TEXT_A(lpString, cchString, oldGetTextExtentExPointW(hdc, lpString, cchString, nMaxExtent, lpnFit, alpDx, lpSize))
  DECODE_TEXT(lpString, cchString, oldGetTextExtentExPointW(hdc, lpString, cchString, nMaxExtent, lpnFit, alpDx, lpSize))
  return oldGetTextExtentExPointA(hdc, lpString, cchString, nMaxExtent, lpnFit, alpDx, lpSize);
}

BOOL WINAPI Hijack::newGetTextExtentExPointW(HDC hdc, LPCWSTR lpString, int cchString, int nMaxExtent, LPINT lpnFit, LPINT alpDx, LPSIZE lpSize)
{

  DCFontSwitcher fs(hdc);
  // TRANSLATE_TEXT_W(lpString, cchString, oldGetTextExtentExPointW(hdc, lpString, cchString, nMaxExtent, lpnFit, alpDx, lpSize))
  return oldGetTextExtentExPointW(hdc, lpString, cchString, nMaxExtent, lpnFit, alpDx, lpSize);
}

int WINAPI Hijack::newDrawTextA(HDC hdc, LPCSTR lpString, int cchString, LPRECT lpRect, UINT uFormat)
{

  DCFontSwitcher fs(hdc);
  // if (HijackManager::instance()->isFunctionTranslated((uintptr_t)::DrawTextA))
  //   TRANSLATE_TEXT_A(lpString, cchString, oldDrawTextW(hdc, lpString, cchString, lpRect, uFormat))
  // else
  DECODE_TEXT(lpString, cchString, oldDrawTextW(hdc, lpString, cchString, lpRect, uFormat))
  return oldDrawTextA(hdc, lpString, cchString, lpRect, uFormat);
}

int WINAPI Hijack::newDrawTextW(HDC hdc, LPCWSTR lpString, int cchString, LPRECT lpRect, UINT uFormat)
{

  DCFontSwitcher fs(hdc);
  // if (HijackManager::instance()->isFunctionTranslated((ULONG)::DrawTextW))
  //   TRANSLATE_TEXT_W(lpString, cchString, oldDrawTextW(hdc, lpString, cchString, lpRect, uFormat))
  return oldDrawTextW(hdc, lpString, cchString, lpRect, uFormat);
}

int WINAPI Hijack::newDrawTextExA(HDC hdc, LPSTR lpString, int cchString, LPRECT lpRect, UINT dwDTFormat, LPDRAWTEXTPARAMS lpDTParams)
{

  DCFontSwitcher fs(hdc);
  if (!(dwDTFormat & DT_MODIFYSTRING))
  {
    // if (HijackManager::instance()->isFunctionTranslated((uintptr_t)::DrawTextExA))
    //   TRANSLATE_TEXT_A(lpString, cchString, oldDrawTextExW(hdc, const_cast<LPWSTR>(lpString), cchString, lpRect, dwDTFormat, lpDTParams))
    // else
    DECODE_TEXT(lpString, cchString, oldDrawTextExW(hdc, const_cast<LPWSTR>(lpString), cchString, lpRect, dwDTFormat, lpDTParams))
  }
  return oldDrawTextExA(hdc, lpString, cchString, lpRect, dwDTFormat, lpDTParams);
}

int WINAPI Hijack::newDrawTextExW(HDC hdc, LPWSTR lpString, int cchString, LPRECT lpRect, UINT dwDTFormat, LPDRAWTEXTPARAMS lpDTParams)
{

  DCFontSwitcher fs(hdc);
  // if (!(dwDTFormat & DT_MODIFYSTRING) && HijackManager::instance()->isFunctionTranslated((ULONG)::DrawTextExW))
  //   TRANSLATE_TEXT_W(lpString, cchString, oldDrawTextExW(hdc, const_cast<LPWSTR>(lpString), cchString, lpRect, dwDTFormat, lpDTParams))
  return oldDrawTextExW(hdc, lpString, cchString, lpRect, dwDTFormat, lpDTParams);
}

BOOL WINAPI Hijack::newTextOutA(HDC hdc, int nXStart, int nYStart, LPCSTR lpString, int cchString)
{

  DCFontSwitcher fs(hdc);
  // if (HijackManager::instance()->isFunctionTranslated((uintptr_t)::TextOutA))
  //   TRANSLATE_TEXT_A(lpString, cchString, oldTextOutW(hdc, nXStart, nYStart, lpString, cchString))
  // else
  DECODE_TEXT(lpString, cchString, oldTextOutW(hdc, nXStart, nYStart, lpString, cchString))
  return oldTextOutA(hdc, nXStart, nYStart, lpString, cchString);
}

BOOL WINAPI Hijack::newTextOutW(HDC hdc, int nXStart, int nYStart, LPCWSTR lpString, int cchString)
{

  DCFontSwitcher fs(hdc);
  // if (HijackManager::instance()->isFunctionTranslated((ULONG)::TextOutW))
  //   TRANSLATE_TEXT_W(lpString, cchString, oldTextOutW(hdc, nXStart, nYStart, lpString, cchString))
  return oldTextOutW(hdc, nXStart, nYStart, lpString, cchString);
}

BOOL WINAPI Hijack::newExtTextOutA(HDC hdc, int X, int Y, UINT fuOptions, const RECT *lprc, LPCSTR lpString, UINT cchString, const INT *lpDx)
{

  DCFontSwitcher fs(hdc);
  // if (HijackManager::instance()->isFunctionTranslated((uintptr_t)::ExtTextOutA))
  //   TRANSLATE_TEXT_A(lpString, cchString, oldExtTextOutW(hdc, X, Y, fuOptions, lprc, lpString, cchString, lpDx))
  // else
  DECODE_TEXT(lpString, cchString, oldExtTextOutW(hdc, X, Y, fuOptions, lprc, lpString, cchString, lpDx))
  return oldExtTextOutA(hdc, X, Y, fuOptions, lprc, lpString, cchString, lpDx);
}

BOOL WINAPI Hijack::newExtTextOutW(HDC hdc, int X, int Y, UINT fuOptions, const RECT *lprc, LPCWSTR lpString, UINT cchString, const INT *lpDx)
{

  DCFontSwitcher fs(hdc);
  // if (HijackManager::instance()->isFunctionTranslated((ULONG)::ExtTextOutW))
  //   TRANSLATE_TEXT_W(lpString, cchString, oldExtTextOutW(hdc, X, Y, fuOptions, lprc, lpString, cchString, lpDx))
  return oldExtTextOutW(hdc, X, Y, fuOptions, lprc, lpString, cchString, lpDx);
}

// EOF
