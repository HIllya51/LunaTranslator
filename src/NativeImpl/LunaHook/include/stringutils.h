#ifndef __LUNA_STRINGUILTS_H_F321BF85_D072_4884_B284_5FEFC759E925
#define __LUNA_STRINGUILTS_H_F321BF85_D072_4884_B284_5FEFC759E925

enum
{
  VNR_TEXT_CAPACITY = 1500
}; // estimated max number of bytes allowed in VNR, slightly larger than VNR's text limit (1000)

template <class StringT>
StringT stolower(StringT s)
{
  std::transform(s.begin(), s.end(), s.begin(), tolower);
  return s;
}

template <typename StringT>
size_t strSize(const StringT &s)
{
  return s.size() * sizeof(StringT::value_type);
}

namespace re
{

  template <typename CharT>
  constexpr auto default_string()
  {
    if constexpr (std::is_same_v<CharT, char>)
    {
      return "";
    }
    else if constexpr (std::is_same_v<CharT, wchar_t>)
    {
      return L"";
    }
  }

  template <typename CharT, class StringT = std::basic_string<CharT>>
  StringT sub(const StringT &str, const CharT *pattern, const CharT *as = default_string<CharT>(), std::regex_constants::syntax_option_type _Flags = std::regex_constants::ECMAScript)
  {
    return std::regex_replace(str, std::basic_regex<CharT>(pattern, _Flags), as);
  }
  template <typename CharT>
  using MatchT = std::conditional_t<std::is_same_v<CharT, char>, std::smatch, std::conditional_t<std::is_same_v<CharT, wchar_t>, std::wsmatch, void>>;

  template <typename CharT, class StringT = std::basic_string<CharT>, class Match = MatchT<CharT>>
  std::optional<Match> match(const StringT &str, const CharT *pattern)
  {
    Match match;
    if (!std::regex_match(str, match, std::basic_regex<CharT>(pattern)))
      return {};
    return match;
  }
  template <typename CharT, class StringT = std::basic_string<CharT>, class Match = MatchT<CharT>>
  std::optional<Match> search(const StringT &str, const CharT *pattern)
  {
    Match match;
    if (!std::regex_search(str, match, std::basic_regex<CharT>(pattern)))
      return {};
    return match;
  }
  template <typename CharT, class StringT = std::basic_string<CharT>, class iteratorT = std::conditional_t<std::is_same_v<CharT, char>, std::sregex_token_iterator, std::conditional_t<std::is_same_v<CharT, wchar_t>, std::wsregex_token_iterator, void>>>
  std::vector<StringT> split(const StringT &str, const CharT *pattern)
  {
    auto r = std::basic_regex<CharT>(pattern);
    iteratorT it(str.begin(), str.end(), r, -1);
    iteratorT end;
    std::vector<StringT> parts(it, end);
    return parts;
  }
}
bool all_ascii(const std::wstring&);
bool all_ascii(const std::wstring_view&);
bool all_ascii(const std::string&);
bool all_ascii(const std::string_view&);
bool all_ascii(const char *s, int maxsize = VNR_TEXT_CAPACITY);
bool all_ascii(const wchar_t *s, int maxsize = VNR_TEXT_CAPACITY);
std::string &strReplace(const std::string &str, const std::string &oldStr, const std::string &newStr = "");
std::wstring &strReplace(const std::wstring &str, const std::wstring &oldStr, const std::wstring &newStr = L"");
std::string &strReplace(std::string &str, const std::string &oldStr, const std::string &newStr = "");
std::wstring &strReplace(std::wstring &str, const std::wstring &oldStr, const std::wstring &newStr = L"");
std::u32string &strReplace(std::u32string &str, const std::u32string &oldStr, const std::u32string &newStr = U"");
std::vector<std::string> strSplit(const std::string &s, const std::string &delim);
std::vector<std::wstring> strSplit(const std::wstring &s, const std::wstring &delim);
bool startWith(const std::string_view &s, const std::string_view &s2);
bool startWith(const std::wstring_view &s, const std::wstring_view &s2);

bool endWith(const std::string_view &s, const std::string_view &s2);
bool endWith(const std::wstring_view &s, const std::wstring_view &s2);
std::wstring utf32_to_utf16(std::u32string_view sv);
std::u32string utf16_to_utf32(std::wstring_view);

std::string WideStringToString(const std::wstring &text, UINT cp = CP_UTF8);
std::string WideStringToString(std::wstring_view text, UINT cp = CP_UTF8);
std::string WideStringToString(const wchar_t *, UINT cp = CP_UTF8);

std::wstring StringToWideString(const std::string &text);
std::wstring StringToWideString(std::string_view);
std::wstring StringToWideString(const char *);
std::optional<std::wstring> StringToWideString(const std::string &text, UINT encoding);
std::optional<std::wstring> StringToWideString(std::string_view text, UINT encoding);
std::optional<std::wstring> StringToWideString(const char *, UINT encoding);

std::string wcasta(const std::wstring &x);
std::wstring acastw(const std::string &x);
char32_t *u32strcpy(char32_t *s, const char32_t *r);

template <class CharT>
size_t strlenEx(const CharT *s)
{
  return std::char_traits<CharT>::length(s);
}
template <class CharT>
size_t strnlenEx(const CharT *s, size_t sz)
{
  size_t t = 0;
  sz /= sizeof(CharT);
  if constexpr (std::is_same_v<CharT, char>)
    t = strnlen(s, sz);
  else if constexpr (std::is_same_v<CharT, wchar_t>)
    t = wcsnlen(s, sz);
  else if constexpr (std::is_same_v<CharT, char32_t>)
    t = strlenEx(s);
  else
    static_assert(true);
  return t;
}

template <class CharT>
CharT *strcpyEx(CharT *s, const CharT *r)
{
  if constexpr (std::is_same_v<CharT, char>)
    return strcpy(s, r);
  else if constexpr (std::is_same_v<CharT, wchar_t>)
    return wcscpy(s, r);
  else if constexpr (std::is_same_v<CharT, char32_t>)
    return u32strcpy(s, r);
  else
    static_assert(true);
  return nullptr;
}
template <class CharT>
CharT *strncpyEx(CharT *s, const CharT *r, size_t sz)
{
  sz /= sizeof(CharT);
  if constexpr (std::is_same_v<CharT, char>)
    return strncpy(s, r, sz);
  else if constexpr (std::is_same_v<CharT, wchar_t>)
    return wcsncpy(s, r, sz);
  else if constexpr (std::is_same_v<CharT, char32_t>)
    return u32strcpy(s, r);
  else
    static_assert(true);
  return nullptr;
}

int utf8charlen(const char *str);
bool isStringUtf8(const std::string_view str);
inline bool disable_mbwc = false;
inline bool disable_wcmb = false;
template <class ST>
inline ST &Trim(ST &text)
{
  text.erase(text.begin(), std::find_if_not(text.begin(), text.end(), iswspace));
  text.erase(std::find_if_not(text.rbegin(), text.rend(), iswspace).base(), text.end());
  return text;
}

template <typename T>
inline auto FormatArg(T arg) { return arg; }
template <typename C>
inline auto FormatArg(const std::basic_string<C> &arg) { return arg.c_str(); }

#pragma warning(push)
#pragma warning(disable : 4996)
template <typename... Args>
inline std::string FormatString(const char *format, const Args &...args)
{
  std::string buffer(snprintf(nullptr, 0, format, FormatArg(args)...), '\0');
  sprintf(buffer.data(), format, FormatArg(args)...);
  return buffer;
}

template <typename... Args>
inline std::wstring FormatString(const wchar_t *format, const Args &...args)
{
  std::wstring buffer(_snwprintf(nullptr, 0, format, FormatArg(args)...), L'\0');
  _swprintf(buffer.data(), format, FormatArg(args)...);
  return buffer;
}

std::optional<std::wstring> commonparsestring(void *, size_t, void *, DWORD);
#pragma warning(pop)
#endif