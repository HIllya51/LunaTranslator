#pragma once
struct AutoHStringRef
{
    HSTRING hstr = nullptr;
    HSTRING_HEADER hh;
    AutoHStringRef()
    {
    }
    AutoHStringRef(LPCWSTR wstr)
    {
        WindowsCreateStringReference(wstr, lstrlenW(wstr), &hh, &hstr);
    }
    AutoHStringRef(LPCWSTR wstr, size_t len)
    {
        WindowsCreateStringReference(wstr, len, &hh, &hstr);
    }
    ~AutoHStringRef()
    {
        if (hstr)
            WindowsDeleteString(hstr);
    }
    operator HSTRING()
    {
        return hstr;
    }
    HSTRING *operator&() throw()
    {
        return &hstr;
    }
    operator const WCHAR *()
    {
        return WindowsGetStringRawBuffer(hstr, NULL);
    }
};

#define AutoHStringRefX(x) AutoHStringRef(x, ARRAYSIZE(x) - 1)