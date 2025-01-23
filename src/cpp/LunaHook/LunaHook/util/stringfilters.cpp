
inline char *str_chr(char *s, char c, size_t n) { return (char *)::memchr(s, c, n); }
inline wchar_t *str_chr(wchar_t *s, wchar_t c, size_t n) { return cpp_wcsnchr(s, c, n); }

inline char *str_npbrk(char *dest, const char *breakset, size_t n) { return cpp_strnpbrk(dest, breakset, n); }
inline wchar_t *str_npbrk(wchar_t *dest, const wchar_t *breakset, size_t n) { return cpp_wcsnpbrk(dest, breakset, n); }

inline char *str_nstr(char *s, const char *r, size_t n) { return cpp_strnstr(s, r, n); }
inline wchar_t *str_nstr(wchar_t *s, const wchar_t *r, size_t n) { return cpp_wcsnstr(s, r, n); }

template <class CharT>
inline void CharReplacer_impl(CharT *str, size_t *size, CharT fr, CharT to)
{
  size_t len = *size;
  for (size_t i = 0; i < len; i++)
    if (str[i] == fr)
      str[i] = to;
}

template <class CharT>
inline void CharFilter_impl(CharT *str, size_t *size, CharT ch)
{
  size_t len = *size / sizeof(CharT),
         curlen;
  for (CharT *cur = str_chr(str, ch, len);
       (cur && --len && (curlen = len - (cur - str)));
       cur = str_chr(cur, ch, curlen))
    ::memmove(cur, cur + 1, curlen * sizeof(CharT));
  *size = len * sizeof(CharT);
}

template <class CharT>
inline void CharsFilter_impl(CharT *str, size_t *size, const CharT *chars)
{
  size_t len = *size / sizeof(CharT),
         curlen;
  for (CharT *cur = str_npbrk(str, chars, len);
       (cur && --len && (curlen = len - (cur - str)));
       cur = str_npbrk(cur, chars, curlen))
    ::memmove(cur, cur + 1, curlen * sizeof(CharT));
  *size = len * sizeof(CharT);
}

template <class CharT>
inline void StringFilter_impl(CharT *str, size_t *size, const CharT *remove, size_t removelen)
{
  size_t len = *size / sizeof(CharT),
         curlen;
  for (CharT *cur = str_nstr(str, remove, len);
       (cur && (len -= removelen) && (curlen = len - (cur - str)));
       cur = str_nstr(cur, remove, curlen))
    ::memmove(cur, cur + removelen, curlen * sizeof(CharT));
  *size = len * sizeof(CharT);
}

template <class CharT>
inline void StringFilterBetween_impl(CharT *str, size_t *size, const CharT *fr, size_t frlen, const CharT *to, size_t tolen)
{
  size_t len = *size / sizeof(CharT),
         curlen;
  for (CharT *cur = str_nstr(str, fr, len);
       cur;
       cur = str_nstr(cur, fr, curlen))
  {
    curlen = (len - frlen) - (cur - str);
    auto end = str_nstr(cur + frlen, to, curlen);
    if (!end)
      break;
    curlen = len - (end - str) - tolen;
    ::memmove(cur, end + tolen, curlen * sizeof(CharT));
    len -= tolen + (end - cur);
  }
  *size = len * sizeof(CharT);
}

template <class CharT>
inline void StringCharReplacer_impl(CharT *str, size_t *size, const CharT *src, size_t srclen, CharT ch)
{
  size_t len = *size / sizeof(CharT),
         curlen;
  for (CharT *cur = str_nstr(str, src, len);
       cur && len;
       cur = str_nstr(cur, src, curlen))
  {
    *cur++ = ch;
    len -= srclen - 1;
    curlen = len - (cur - str);
    if (curlen == 0)
      break;
    ::memmove(cur, cur + srclen - 1, sizeof(CharT) * curlen);
  }
  *size = len * sizeof(CharT);
}

template <class CharT>
inline void StringReplacer_impl(CharT *str, size_t *size, const CharT *src, size_t srclen, const CharT *dst, size_t dstlen)
{
  size_t len = *size / sizeof(CharT),
         curlen;
  for (CharT *cur = str_nstr(str, src, len);
       cur && len;
       cur = str_nstr(cur, src, curlen))
  {
    ::memcpy(cur, dst, sizeof(CharT) * dstlen);
    cur += dstlen;
    len -= srclen - dstlen;
    curlen = len - (cur - str);
    if (curlen == 0)
      break;
    if (srclen > dstlen)
      ::memmove(cur, cur + srclen - dstlen, sizeof(CharT) * curlen);
  }
  *size = len * sizeof(CharT);
}

void NewLineCharToSpaceFilterA(TextBuffer *buffer, HookParam *)
{
  CharReplacer(buffer, '\n', ' ');
}
void all_ascii_Filter(TextBuffer *buffer, HookParam *)
{
  if (all_ascii((char *)buffer->buff, buffer->size))
    buffer->clear();
}

void CharReplacer(TextBuffer *buffer, char fr, char to) { CharReplacer_impl<char>((char *)buffer->buff, &buffer->size, fr, to); }
void CharReplacer(TextBuffer *buffer, wchar_t fr, wchar_t to) { CharReplacer_impl<wchar_t>((wchar_t *)buffer->buff, &buffer->size, fr, to); }

void CharFilter(TextBuffer *buffer, char ch) { CharFilter_impl<char>((char *)buffer->buff, &buffer->size, ch); }
void CharFilter(TextBuffer *buffer, wchar_t ch) { CharFilter_impl<wchar_t>((wchar_t *)buffer->buff, &buffer->size, ch); }

void CharsFilter(TextBuffer *buffer, const char *chars) { CharsFilter_impl<char>((char *)buffer->buff, &buffer->size, chars); }
void CharsFilter(TextBuffer *buffer, const wchar_t *chars) { CharsFilter_impl<wchar_t>((wchar_t *)buffer->buff, &buffer->size, chars); }

void StringFilter(TextBuffer *buffer, const char *remove, size_t removelen) { StringFilter_impl<char>((char *)buffer->buff, &buffer->size, remove, removelen); }
void StringFilter(TextBuffer *buffer, const wchar_t *remove, size_t removelen) { StringFilter_impl<wchar_t>((wchar_t *)buffer->buff, &buffer->size, remove, removelen); }

void StringFilterBetween(TextBuffer *buffer, const char *fr, size_t frlen, const char *to, size_t tolen) { StringFilterBetween_impl<char>((char *)buffer->buff, &buffer->size, fr, frlen, to, tolen); }
void StringFilterBetween(TextBuffer *buffer, const wchar_t *fr, size_t frlen, const wchar_t *to, size_t tolen)
{
  StringFilterBetween_impl<wchar_t>((wchar_t *)buffer->buff, &buffer->size, fr, frlen, to, tolen);
}

void StringCharReplacer(TextBuffer *buffer, const char *src, size_t srclen, char ch) { StringCharReplacer_impl<char>((char *)buffer->buff, &buffer->size, src, srclen, ch); }
void StringCharReplacer(TextBuffer *buffer, const wchar_t *src, size_t srclen, wchar_t ch) { StringCharReplacer_impl<wchar_t>((wchar_t *)buffer->buff, &buffer->size, src, srclen, ch); }

void StringReplacer(TextBuffer *buffer, const char *src, size_t srclen, const char *dst, size_t dstlen) { StringReplacer_impl<char>((char *)buffer->buff, &buffer->size, src, srclen, dst, dstlen); }
void StringReplacer(TextBuffer *buffer, const wchar_t *src, size_t srclen, const wchar_t *dst, size_t dstlen) { StringReplacer_impl<wchar_t>((wchar_t *)buffer->buff, &buffer->size, src, srclen, dst, dstlen); }