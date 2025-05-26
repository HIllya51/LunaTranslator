#include "MinHook.h"
std::atomic<bool> patch_fun_ptrs_patch_once_flag = true;
DynamicShiftJISCodec *dynamiccodec = new DynamicShiftJISCodec(932);

void cast_back(const HookParam &hp, TextBuffer *buff, const std::wstring &trans, bool normal)
{

  if ((hp.type & EMBED_CODEC_UTF16) || (hp.type & CODEC_UTF16))
  { // renpy
    buff->from(trans);
  }
  else if (hp.type & CODEC_UTF32)
  {
    buff->from(utf16_to_utf32(trans));
  }
  else
  {
    std::string astr;
    if (hp.type & EMBED_DYNA_SJIS && !normal)
    {
      astr = dynamiccodec->encodeSTD(trans, 0);
    }
    else
    {
      astr = WideStringToString(trans, hp.codepage ? hp.codepage : ((hp.type & CODEC_UTF8) ? CP_UTF8 : commonsharedmem->codepage));
    }
    buff->from(astr);
  }
}

struct FunctionInfo
{
  const char *name; // for debugging purpose
  uintptr_t *oldFunction,
      newFunction;
  bool attached;
  uintptr_t addr;
  explicit FunctionInfo(const uintptr_t _addr = 0, const char *name = "", uintptr_t *oldFunction = nullptr, uintptr_t newFunction = 0,
                        bool attached = false)
      : name(name), oldFunction(oldFunction), newFunction(newFunction), attached(attached), addr(_addr)
  {
  }
};
std::unordered_map<uintptr_t, FunctionInfo> funcs; // attached functions
std::vector<uintptr_t> replacedfuns;               // attached functions
bool _1f()
{
#define ADD_FUN(_f) funcs[F_##_f] = FunctionInfo((uintptr_t)_f, #_f, (uintptr_t *)&Hijack::old##_f, (uintptr_t)Hijack::new##_f);
  ADD_FUN(CreateFontA)
  ADD_FUN(CreateFontW)
  ADD_FUN(CreateFontIndirectA)
  ADD_FUN(CreateFontIndirectW)
  ADD_FUN(GetGlyphOutlineA)
  ADD_FUN(GetGlyphOutlineW)
  ADD_FUN(GetTextExtentPoint32A)
  ADD_FUN(GetTextExtentPoint32W)
  ADD_FUN(GetTextExtentExPointA)
  ADD_FUN(GetTextExtentExPointW)
  // ADD_FUN(GetCharABCWidthsA)
  // ADD_FUN(GetCharABCWidthsW)
  ADD_FUN(TextOutA)
  ADD_FUN(TextOutW)
  ADD_FUN(ExtTextOutA)
  ADD_FUN(ExtTextOutW)
  ADD_FUN(DrawTextA)
  ADD_FUN(DrawTextW)
  ADD_FUN(DrawTextExA)
  ADD_FUN(DrawTextExW)
  ADD_FUN(CharNextA)
  // ADD_FUN(CharNextW)
  // ADD_FUN(CharNextExA)
  // ADD_FUN(CharNextExW)
  ADD_FUN(CharPrevA)
  // ADD_FUN(CharPrevW)
  ADD_FUN(MultiByteToWideChar)
  ADD_FUN(WideCharToMultiByte)
#undef ADD_FUN
  return 0;
}
bool _1 = _1f();
bool ReplaceFunction(PVOID oldf, PVOID newf, PVOID *pOrigin)
{
  PVOID oldx;
  if (!pOrigin)
    pOrigin = &oldx;
  RemoveHook((uintptr_t)oldf);
  if (MH_OK == MH_CreateHook(oldf, newf, pOrigin))
    return MH_OK == MH_EnableHook(oldf);
  else
  {
    MH_RemoveHook(oldf);
    return false;
  }
}
void attachFunction(uintptr_t _hook_font_flag)
{
  for (auto &_func : funcs)
  {
    if (_func.first & _hook_font_flag)
    {
      if (_func.second.attached)
        continue;

      if (ReplaceFunction((PVOID)_func.second.addr, (PVOID)_func.second.newFunction, (PVOID *)_func.second.oldFunction))
      {
        _func.second.attached = true;
        replacedfuns.push_back(_func.first);
      }
    }
  }
}
void detachall()
{
  for (auto _flag : replacedfuns)
  {
    auto info = funcs.at(_flag);
    if (MH_OK == MH_DisableHook((LPVOID)info.addr))
      MH_RemoveHook((LPVOID)info.addr);
  }

  if (!patch_fun_ptrs_patch_once_flag.load())
  {
    for (auto &&[ptr1, ptr2] : patch_fun_ptrs)
    {
      if (MH_OK == MH_DisableHook(ptr1))
        MH_RemoveHook(ptr1);
    }
  }
}
void patch_fun_ptrs_patch_once()
{
  if (auto cur_patch_fun_ptrs_patch_once_flag = patch_fun_ptrs_patch_once_flag.exchange(false))
  {
    // 理论上搞个激活内嵌的行的使用计数是可以更早的detach的，但感觉好麻烦，算了。
    for (auto &&[ptr1, ptr2] : patch_fun_ptrs)
    {
      ReplaceFunction(ptr1, ptr2);
    }
  }
}
void solvefont(HookParam hp)
{
  if (hp.embed_hook_font & DISABLE_FONT_SWITCH)
  {
    Hijack::Disable_Font_Switch = true;
  }
  if (hp.embed_hook_font)
  {
    attachFunction(hp.embed_hook_font);
  }
  if (hp.embed_hook_font & F_MultiByteToWideChar)
    disable_mbwc = true;
  if (hp.embed_hook_font & F_WideCharToMultiByte)
    disable_wcmb = true;

  if (auto current_patch_fun = patch_fun.exchange(nullptr))
  {
    current_patch_fun();
    dont_detach = true;
  }
  patch_fun_ptrs_patch_once();
}
static std::wstring alwaysInsertSpacesSTD(const std::wstring &text)
{
  std::wstring ret;
  for (auto c : text)
  {
    ret.push_back(c);
    if (c >= 32)           // ignore non-printable characters
      ret.push_back(L' '); // or insert \u3000 if needed
  }
  return ret;
}
bool charEncodableSTD(const wchar_t &ch, UINT codepage)
{

  if (ch <= 127) // ignore ascii characters
    return true;
  std::wstring s;
  s.push_back(ch);
  return StringToWideString(WideStringToString(s, codepage), codepage).value() == s;
}
static std::wstring insertSpacesAfterUnencodableSTD(const std::wstring &text, HookParam hp)
{

  std::wstring ret;
  for (const wchar_t &c : text)
  {
    ret.push_back(c);
    if (!charEncodableSTD(c, hp.codepage ? hp.codepage : commonsharedmem->codepage))
      ret.push_back(L' ');
  }
  return ret;
}
std::wstring adjustSpacesSTD(const std::wstring &text, HookParam hp)
{
  if (hp.type & EMBED_INSERT_SPACE_ALWAYS)
    return alwaysInsertSpacesSTD(text);
  else if (hp.type & EMBED_INSERT_SPACE_AFTER_UNENCODABLE)
    return insertSpacesAfterUnencodableSTD(text, hp);
  return text;
}
bool isPauseKeyPressed()
{
  return WinKey::isKeyControlPressed() || WinKey::isKeyShiftPressed() && !WinKey::isKeyReturnPressed();
}
std::unordered_map<UINT64, std::wstring> translatecache;
bool check_is_thread_selected(const ThreadParam &tp)
{
  for (int i = 0; i < ARRAYSIZE(commonsharedmem->embedtps); i++)
  {
    if (commonsharedmem->embedtps[i].use && (commonsharedmem->embedtps[i].tp == tp))
      return true;
  }
  return false;
}
bool check_embed_able(const ThreadParam &tp)
{
  return host_connected && check_is_thread_selected(tp) && ((isPauseKeyPressed() == false) ? true : !commonsharedmem->fastskipignore);
}
bool waitforevent(UINT32 timems, const ThreadParam &tp, const std::wstring &origin)
{
  char eventname[1000];
  sprintf(eventname, LUNA_EMBED_notify_event, GetCurrentProcessId(), simplehash::djb2_n2((const unsigned char *)(origin.c_str()), origin.size() * 2));
  auto event = win_event(eventname);
  while (timems)
  {
    if (check_embed_able(tp) == false)
      return false;
    auto sleepstep = min(100, timems);
    if (event.wait(sleepstep))
      return true;
    timems -= sleepstep;
  }
  return false;
}

void TextHook::parsenewlineseperator(TextBuffer *buff)
{
  if (!(hp.lineSeparator))
    return;

  if (hp.type & CODEC_UTF16)
  {
    StringCharReplacer(buff, hp.lineSeparator, wcslen(hp.lineSeparator), L'\n');
  }
  else if (hp.type & CODEC_UTF32)
    return;
  else
  {
    // ansi/utf8，newlineseperator都是简单字符
    std::string newlineseperatorA = wcasta(hp.lineSeparator);
    StringCharReplacer(buff, newlineseperatorA.c_str(), newlineseperatorA.size(), '\n');
  }
}
UINT64 texthash(void *data, size_t len)
{
  UINT64 sum = 0;
  auto u8data = (UINT8 *)data;
  for (int i = 0; i < len; i++)
  {
    sum += u8data[i];
    sum = sum << 1;
  }
  return sum;
}
bool checktranslatedok(TextBuffer buff)
{
  ZeroMemory(commonsharedmem->text, sizeof(commonsharedmem->text)); // clear trans before call
  if (buff.size > 1000)
    return true;
  return translatecache.count(texthash(buff.buff, buff.size));
}
bool TextHook::waitfornotify(TextBuffer *buff, ThreadParam tp)
{
  if (commonsharedmem->clearText)
  {
    buff->from(" "); // 也可以选择对齐空格长度。到底哪个更稳定需要更多测试
    return true;
  }
  std::wstring origin;
  if (auto t = commonparsestring(buff->buff, buff->size, &hp, commonsharedmem->codepage))
    origin = t.value();
  else
    return false;
  std::wstring translate;
  auto hash = texthash(buff->buff, buff->size);
  auto found = translatecache.find(hash);
  if (found != translatecache.end())
  {
    translate = found->second;
  }
  else
  {
    if (waitforevent(commonsharedmem->waittime, tp, origin) == false)
      return false;
    translate = commonsharedmem->text;
    if ((translate.size() == 0))
      return false;
    translatecache.insert(std::make_pair(hash, translate));
  }
  if (hp.lineSeparator)
    strReplace(translate, L"\n", hp.lineSeparator);
  translate = adjustSpacesSTD(translate, hp);
  switch (commonsharedmem->displaymode)
  {
  case Displaymode::TRANS:
    break;
  case Displaymode::ORI_TRANS:
    translate = origin + L" " + translate;
    break;
  case Displaymode::TRANS_ORI:
    translate = translate + L" " + origin;
    break;
  }
  solvefont(hp);
  cast_back(hp, buff, translate, false);
  return true;
}