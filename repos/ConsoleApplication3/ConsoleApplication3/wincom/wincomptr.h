#pragma once

// wincomptr.h
// 8/11/2014 jichi
// Smart pointers for COM.

#include "wincom/wincom.h"
#include <unknwn.h> // IUnknown

WINCOM_BEGIN_NAMESPACE

class ScopedUnknownPtr
{
  IUnknown *p;
public:
  ScopedUnknownPtr(IUnknown *p) : p(p) {}
  ~ScopedUnknownPtr() { if (p) p->Release(); }
  IUnknown *get() const throw() { return p; }
};

// See: http://msdn.microsoft.com/en-us/library/xda6xzx7.aspx
class ScopedBstr
{
  BSTR p;
public:
  ScopedBstr(const wchar_t *s) : p(::SysAllocString(s)) {}
  ~ScopedBstr() { if (p) ::SysFreeString(p); }
  BSTR get() const throw() { return p; }
};

WINCOM_END_NAMESPACE
