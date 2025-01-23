// dynsjis.cc
// 6/11/2015 jichi
// http://en.wikipedia.org/wiki/Shift_JIS
#include "dyncodec/dynsjis.h"

const char *dynsjis::nextchar(const char *s)
{
  if (!s || !s[0])
    return s;
  if (!s[1])
    return s + 1;
  if (!isleadbyte(s[0]))
    return s + 1;
  return s + 2; // unused byte treated as two-byte character
}

const char *dynsjis::prevchar(const char *s, const char *begin)
{
  if (!s || s <= begin)
    return s;
  if (!*s || s == begin + 1)
    return s - 1;
  if (isleadbyte(s[0]))
    return s - 2;
  if (!isleadbyte(s[-1]))
    return s - 1;
  // 0 is single-width
  // -1 is double-width
  if (!isleadbyte(s[-3]))
    return s - 2;
  const char *p = s - 1;
  while (p != begin && isleadbyte(*p))
    p--;
  size_t dist = s - p;
  if (!isleadbyte(*p))
    dist++;
  return s - 2 + (dist % 2);
}

// EOF
