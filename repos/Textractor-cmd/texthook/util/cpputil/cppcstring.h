#ifndef CPPCSTRING_H
#define CPPCSTRING_H

// cppcstring.h
// 10/12/2014 jichi

#include <cstddef> // for size_t
#include <cstring>
//#include <algorithm> // for std::min

// strlen

template <typename charT>
inline size_t cpp_basic_strlen(const charT *s)
{
  const charT *p = s;
  while (*p) p++;
  return p - s;
}

inline size_t cpp_strlen(const char *s) { return cpp_basic_strlen<char>(s); }
inline size_t cpp_wstrlen(const wchar_t *s) { return cpp_basic_strlen<wchar_t>(s); }

template <typename charT>
inline size_t cpp_basic_strnlen(const charT *s, size_t n)
{
  const charT *p = s;
  while (*p && n) p++, n--;
  return p - s;
}

inline size_t cpp_strnlen(const char *s, size_t n) { return cpp_basic_strnlen<char>(s, n); }
inline size_t cpp_wstrnlen(const wchar_t *s, size_t n) { return cpp_basic_strnlen<wchar_t>(s, n); }

// strnchr

#define cpp_basic_strnchr_(s, c, n) \
  { \
    while (*s && n) { \
      if (*s == c) \
        return s; \
      s++, n--; \
    } \
    return nullptr; \
  }
template <typename charT>
inline charT *cpp_basic_strnchr(charT *s, charT c, size_t n) cpp_basic_strnchr_(s, c, n)
template <typename charT>
inline const charT *cpp_basic_strnchr(const charT *s, charT c, size_t n) cpp_basic_strnchr_(s, c, n)

// The same as memchr
inline char *cpp_strnchr(char *s, char c, size_t n) { return cpp_basic_strnchr<char>(s, c, n); }
inline const char *cpp_strnchr(const char *s, char c, size_t n) { return cpp_basic_strnchr<char>(s, c, n); }
inline wchar_t *cpp_wcsnchr(wchar_t *s, wchar_t c, size_t n) { return cpp_basic_strnchr<wchar_t>(s, c, n); }
inline const wchar_t *cpp_wcsnchr(const wchar_t *s, wchar_t c, size_t n) { return cpp_basic_strnchr<wchar_t>(s, c, n); }

// strnstr

#define cpp_basic_strnstr_(s, slen, r, rlen, ncmp) \
  { \
    while (*s && slen >= rlen) { \
      if (ncmp(s, r, slen < rlen ? slen : rlen) == 0) \
        return s; \
      s++, slen--; \
    } \
    return nullptr; \
  }

template <typename charT>
inline charT *cpp_basic_strnstr(charT *s, const charT *r, size_t n) cpp_basic_strnstr_(s, n, r, ::strlen(r), ::strncmp)
template <typename charT>
inline const charT *cpp_basic_strnstr(const charT *s, const charT *r, size_t n) cpp_basic_strnstr_(s, n, r, ::strlen(r), ::strncmp)

template <>
inline wchar_t *cpp_basic_strnstr<wchar_t>(wchar_t *s, const wchar_t *r, size_t n) cpp_basic_strnstr_(s, n, r, ::wcslen(r), ::wcsncmp)
template <>
inline const wchar_t *cpp_basic_strnstr<wchar_t>(const wchar_t *s, const wchar_t *r, size_t n) cpp_basic_strnstr_(s, n, r, ::wcslen(r), ::wcsncmp)

inline char *cpp_strnstr(char *s, const char *r, size_t n) { return cpp_basic_strnstr<char>(s, r, n); }
inline const char *cpp_strnstr(const char *s, const char *r, size_t n) { return cpp_basic_strnstr<char>(s, r, n); }
inline wchar_t *cpp_wcsnstr(wchar_t *s, const wchar_t *r, size_t n) { return cpp_basic_strnstr<wchar_t>(s, r, n); }
inline const wchar_t *cpp_wcsnstr(const wchar_t *s, const wchar_t *r, size_t n) { return cpp_basic_strnstr<wchar_t>(s, r, n); }

// strnpbrk

// it might be faster to use strchr functions, which is not portable though
#define cpp_basic_strnpbrk_(s, sep, n) \
  { \
    while (*s && n) { \
      for (auto p = sep; *p; p++) \
        if (*s == *p) \
          return s; \
      s++, n--; \
    } \
    return nullptr; \
  }

template <typename charT, typename char2T>
inline charT *cpp_basic_strnpbrk(charT *dest, const char2T *breakset, size_t n)
cpp_basic_strnpbrk_(dest, breakset, n)

template <typename charT, typename char2T>
inline const charT *cpp_basic_strnpbrk(const charT *dest, const char2T *breakset, size_t n)
cpp_basic_strnpbrk_(dest, breakset, n)

inline char *cpp_strnpbrk(char *dest, const char *breakset, size_t n) { return cpp_basic_strnpbrk(dest, breakset, n); }
inline const char *cpp_strnpbrk(const char *dest, const char *breakset, size_t n) { return cpp_basic_strnpbrk(dest, breakset, n); }
inline wchar_t *cpp_wcsnpbrk(wchar_t *dest, const wchar_t *breakset, size_t n) { return cpp_basic_strnpbrk(dest, breakset, n); }
inline const wchar_t *cpp_wcsnpbrk(const wchar_t *dest, const wchar_t *breakset, size_t n) { return cpp_basic_strnpbrk(dest, breakset, n); }

#endif // CPPCSTRING_H
