#ifndef __LUNA_STRINGUILTS_H
#define __LUNA_STRINGUILTS_H

using u32string = std::basic_string<uint32_t>;
using u32string_view = std::basic_string_view<uint32_t>;
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

LPCSTR reverse_search_begin(const char *s, int maxsize = VNR_TEXT_CAPACITY);

bool all_ascii(const char *s, int maxsize = VNR_TEXT_CAPACITY);
bool all_ascii(const wchar_t *s, int maxsize = VNR_TEXT_CAPACITY);
std::string &strReplace(std::string &str, const std::string &oldStr, const std::string &newStr = "");
std::wstring &strReplace(std::wstring &str, const std::wstring &oldStr, const std::wstring &newStr = L"");
std::vector<std::string> strSplit(const std::string &s, const std::string &delim);
std::vector<std::wstring> strSplit(const std::wstring &s, const std::wstring &delim);
bool startWith(const std::string_view &s, const std::string_view &s2);
bool startWith(const std::wstring_view &s, const std::wstring_view &s2);

bool endWith(const std::string_view &s, const std::string_view &s2);
bool endWith(const std::wstring_view &s, const std::wstring_view &s2);
std::wstring utf32_to_utf16(u32string_view sv);
u32string utf16_to_utf32(std::wstring_view);

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
uint32_t *u32strcpy(uint32_t *s, const uint32_t *r);

template <class CharT>
size_t strlenEx(const CharT *s)
{
  return std::basic_string_view<CharT>(s).size();
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
  else if constexpr (std::is_same_v<CharT, uint32_t>)
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
  else if constexpr (std::is_same_v<CharT, uint32_t>)
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
  else if constexpr (std::is_same_v<CharT, uint32_t>)
    return u32strcpy(s, r);
  else
    static_assert(true);
  return nullptr;
}

int utf8charlen(char *data);
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