#ifndef DYNSJIS_H
#define DYNSJIS_H

// dynsjis.h
// 6/11/2015 jichi

namespace dynsjis {

inline bool isleadbyte(unsigned char ch)
{ return ch > 127 && (ch < 0xa1 || ch > 0xdf); }

inline bool isleadchar(unsigned int ch)
{ return isleadbyte((ch >> 8) & 0xff); }

const char *nextchar(const char *s);
inline char *nextchar(char *s)
{ return const_cast<char *>(nextchar(static_cast<const char *>(s))); }

inline bool isleadstr(const char *s) // return true if the first character of the string is widechar
{ return nextchar(s) - s == 2; }

const char *prevchar(const char *s, const char *begin = nullptr);
inline char *prevchar(char *s, const char *begin = nullptr)
{ return const_cast<char *>(prevchar(static_cast<const char *>(s), begin)); }

} // namespace dynsjis

#endif // DYNSJIS_H
