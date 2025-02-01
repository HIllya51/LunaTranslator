#pragma once
struct AutoHString
{
    HSTRING hstr = nullptr;
    AutoHString()
    {
    }
    AutoHString(LPCWSTR wstr)
    {
        WindowsCreateString(wstr, lstrlenW(wstr), &hstr);
    }
    ~AutoHString()
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