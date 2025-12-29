

template <class CharT>
inline bool all_ascii_impl(const CharT *s, int maxsize)
{
  if (s)
    for (int i = 0; i < maxsize && *s; i++, s++)
      if ((unsigned)*s > 127)
        return false;
  return true;
}

template <class StringT>
inline bool all_ascii_impl(const StringT &s)
{
  for (auto c : s)
  {
    if ((unsigned)c > 127)
      return false;
  }
  return true;
}
template <class StringT>
inline StringT &strReplace_impl(StringT &str, const StringT &oldStr, const StringT &newStr)
{
  size_t pos = 0;
  while ((pos = str.find(oldStr, pos)) != StringT::npos)
  {
    str.replace(pos, oldStr.length(), newStr);
    pos += newStr.length();
  }
  return str;
}

template <class StringT>
inline std::vector<StringT> strSplit_impl(const StringT &s, const StringT &delim)
{
  StringT item;
  std::vector<StringT> tokens;

  StringT str = s;

  size_t pos = 0;
  while ((pos = str.find(delim)) != StringT::npos)
  {
    item = str.substr(0, pos);
    tokens.push_back(item);
    str.erase(0, pos + delim.length());
  }
  tokens.push_back(str);
  return tokens;
}

template <class StringT>
inline bool endWith_impl(const StringT &s, const StringT &s2)
{
  return (s.size() >= s2.size()) && (s.substr(s.size() - s2.size()) == s2);
}

template <class StringT>
inline bool startWith_impl(const StringT &s, const StringT &s2)
{
  return (s.size() >= s2.size()) && (s.substr(0, s2.size()) == s2);
}

bool all_ascii(const char *s, int maxsize) { return all_ascii_impl<char>(s, maxsize); }
bool all_ascii(const wchar_t *s, int maxsize) { return all_ascii_impl<wchar_t>(s, maxsize); }

bool all_ascii(const std::wstring &s) { return all_ascii_impl(s); }
bool all_ascii(const std::wstring_view &s) { return all_ascii_impl(s); }
bool all_ascii(const std::string &s) { return all_ascii_impl(s); }
bool all_ascii(const std::string_view &s) { return all_ascii_impl(s); }

std::string &strReplace(std::string &str, const std::string &oldStr, const std::string &newStr) { return strReplace_impl<std::string>(str, oldStr, newStr); }
std::wstring &strReplace(std::wstring &str, const std::wstring &oldStr, const std::wstring &newStr) { return strReplace_impl<std::wstring>(str, oldStr, newStr); }
std::u32string &strReplace(std::u32string &str, const std::u32string &oldStr, const std::u32string &newStr) { return strReplace_impl<std::u32string>(str, oldStr, newStr); }
std::vector<std::string> strSplit(const std::string &s, const std::string &delim) { return strSplit_impl<std::string>(s, delim); }
std::vector<std::wstring> strSplit(const std::wstring &s, const std::wstring &delim) { return strSplit_impl<std::wstring>(s, delim); }
bool startWith(const std::string_view &s, const std::string_view &s2) { return startWith_impl<std::string_view>(s, s2); }
bool startWith(const std::wstring_view &s, const std::wstring_view &s2) { return startWith_impl<std::wstring_view>(s, s2); }
bool endWith(const std::string_view &s, const std::string_view &s2) { return endWith_impl<std::string_view>(s, s2); }
bool endWith(const std::wstring_view &s, const std::wstring_view &s2) { return endWith_impl<std::wstring_view>(s, s2); }

typedef HRESULT(WINAPI *CONVERTINETMULTIBYTETOUNICODE)(
    LPDWORD lpdwMode,
    DWORD dwSrcEncoding,
    LPCSTR lpSrcStr,
    LPINT lpnMultiCharCount,
    LPWSTR lpDstStr,
    LPINT lpnWideCharCount);
typedef HRESULT(WINAPI *CONVERTINETUNICODETOMULTIBYTE)(
    LPDWORD lpdwMode,
    DWORD dwEncoding,
    LPCWSTR lpSrcStr,
    LPINT lpnWideCharCount,
    LPSTR lpDstStr,
    LPINT lpnMultiCharCount);
std::optional<std::wstring> StringToWideString(const std::string &text, UINT encoding)
{
  return StringToWideString(std::string_view(text), encoding);
}

std::optional<std::wstring> StringToWideString(std::string_view text, UINT encoding)
{
  std::vector<wchar_t> buffer(text.size());
  if (disable_mbwc)
  {
    int _s = text.size();
    int _s2 = buffer.size();
    auto h = LoadLibrary(TEXT("mlang.dll"));
    if (h == 0)
      return {};
    auto ConvertINetMultiByteToUnicode = (CONVERTINETMULTIBYTETOUNICODE)GetProcAddress(h, "ConvertINetMultiByteToUnicode");
    if (ConvertINetMultiByteToUnicode == 0)
      return {};
    auto hr = ConvertINetMultiByteToUnicode(0, encoding, text.data(), &_s, buffer.data(), &_s2);
    if (SUCCEEDED(hr))
    {
      return std::wstring(buffer.data(), _s2);
    }
    else
      return {};
  }
  else
  {
    if (int length = MultiByteToWideChar(encoding, 0, text.data(), text.size(), buffer.data(), buffer.size()))
      return std::wstring(buffer.data(), length);
    return {};
  }
}

std::wstring StringToWideString(const std::string &text)
{
  if (!text.size())
    return L"";
  return StringToWideString(text, CP_UTF8).value_or(L"");
}
std::wstring StringToWideString(std::string_view text)
{
  if (!text.size())
    return L"";
  return StringToWideString(text, CP_UTF8).value_or(L"");
}

std::optional<std::wstring> StringToWideString(const char *text, UINT encoding)
{
  return StringToWideString(std::string_view(text), encoding);
}

std::wstring StringToWideString(const char *text)
{
  return StringToWideString(std::string_view(text));
}
std::string WideStringToString(const std::wstring &text, UINT cp)
{
  return WideStringToString(std::wstring_view(text), cp);
}

std::string WideStringToString(const wchar_t *text, UINT cp)
{
  return WideStringToString(std::wstring_view(text), cp);
}
std::string WideStringToString(std::wstring_view text, UINT cp)
{
  if (!text.size())
    return "";
  std::vector<char> buffer((text.size()) * 4);
  if (disable_wcmb)
  {
    int _s = text.size();
    int _s2 = buffer.size();
    auto h = LoadLibrary(TEXT("mlang.dll"));
    if (h == 0)
      return {};
    auto ConvertINetUnicodeToMultiByte = (CONVERTINETUNICODETOMULTIBYTE)GetProcAddress(h, "ConvertINetUnicodeToMultiByte");
    if (ConvertINetUnicodeToMultiByte == 0)
      return {};
    auto hr = ConvertINetUnicodeToMultiByte(0, cp, text.data(), &_s, buffer.data(), &_s2);
    if (SUCCEEDED(hr))
    {
      return std::string(buffer.data(), _s2);
    }
    else
      return {};
  }
  else
  {
    WideCharToMultiByte(cp, 0, text.data(), text.size(), buffer.data(), buffer.size(), nullptr, nullptr);
    return buffer.data();
  }
}
inline unsigned int convertUTF32ToUTF16(unsigned int cUTF32, unsigned int &h, unsigned int &l)
{
  if (cUTF32 < 0x10000)
  {
    h = 0;
    l = cUTF32;
    return cUTF32;
  }
  unsigned int t = cUTF32 - 0x10000;
  h = (((t << 12) >> 22) + 0xD800);
  l = (((t << 22) >> 22) + 0xDC00);
  unsigned int ret = ((h << 16) | (l & 0x0000FFFF));
  return ret;
}

std::u32string utf16_to_utf32(std::wstring_view wsv)
{
  std::u32string utf32String;
  for (size_t i = 0; i < wsv.size(); i++)
  {
    auto u16c = wsv[i];
    if (u16c - 0xd800u < 2048u)
      if (((u16c & 0xfffffc00) == 0xd800) && (i < wsv.size() - 1) && ((wsv[i + 1] & 0xfffffc00) == 0xdc00))
      {
        utf32String += (u16c << 10) + wsv[i + 1] - 0x35fdc00;
        i += 1;
      }
      else
      {
        // error invalid u16 char
      }
    else
      utf32String += wsv[i];
  }
  return utf32String;
}

std::wstring utf32_to_utf16(std::u32string_view sv)
{
  std::wstring u16str;
  for (auto i = 0; i < sv.size(); i++)
  {
    unsigned h, l;
    convertUTF32ToUTF16(sv[i], h, l);
    if (h)
      u16str.push_back((wchar_t)h);
    u16str.push_back((wchar_t)l);
  }
  return u16str;
}

char32_t *u32strcpy(char32_t *s, const char32_t *r)
{
  while (*r)
  {
    *s = *r;
    s += 1;
    r += 1;
  }
  *s = 0;
  return s;
}
// 检查一个字节是否是有效的 UTF-8 后续字节
int is_valid_following_byte(unsigned char byte)
{
  return (byte & 0xC0) == 0x80; // 10xxxxxx
}
int utf8charlen(const char *str)
{
  if ((!str) || (!*str))
    return 0;
  unsigned char first_byte = (unsigned char)*str;

  if ((first_byte & 0x80) == 0)
  {
    // 0xxxxxxx - 1 byte character
    return 1;
  }
  else if ((first_byte & 0xE0) == 0xC0)
  {
    // 110xxxxx - 2 byte character
    if (is_valid_following_byte((unsigned char)str[1]))
    {
      return 2;
    }
  }
  else if ((first_byte & 0xF0) == 0xE0)
  {
    // 1110xxxx - 3 byte character
    if (is_valid_following_byte((unsigned char)str[1]) &&
        is_valid_following_byte((unsigned char)str[2]))
    {
      return 3;
    }
  }
  else if ((first_byte & 0xF8) == 0xF0)
  {
    // 11110xxx - 4 byte character
    if (is_valid_following_byte((unsigned char)str[1]) &&
        is_valid_following_byte((unsigned char)str[2]) &&
        is_valid_following_byte((unsigned char)str[3]))
    {
      return 4;
    }
  }
  return 0; // 不是有效的UTF-8序列
}

bool isStringUtf8(const std::string_view str)
{
  size_t len = 0;
  while (len < str.size())
  {
    auto l = utf8charlen(len + str.data());
    if (!l)
      break;
    len += l;
  }
  return len == str.size();
}
std::string wcasta(const std::wstring &x)
{
  std::string xx;
  for (auto c : x)
    xx += c;
  return xx;
}

std::wstring acastw(const std::string &x)
{
  std::wstring xx;
  for (auto c : x)
    xx += c;
  return xx;
}
std::optional<std::wstring> commonparsestring(void *data, size_t length, void *php, DWORD df)
{
  auto hp = (HookParam *)php;
  if (hp->type & CODEC_UTF16)
    return std::wstring((wchar_t *)data, length / sizeof(wchar_t));
  else if (hp->type & CODEC_UTF32)
    return utf32_to_utf16(std::u32string_view((char32_t *)data, length / sizeof(char32_t)));
  else if (auto converted = StringToWideString(std::string((char *)data, length), (hp->type & CODEC_UTF8) ? CP_UTF8 : (hp->codepage ? hp->codepage : df)))
    return converted.value();
  else
    return {};
}