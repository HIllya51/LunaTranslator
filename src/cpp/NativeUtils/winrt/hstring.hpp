#pragma once
struct AutoHString
{
    HSTRING hstr = nullptr;
    HSTRING_HEADER hh;
    AutoHString()
    {
    }
    explicit AutoHString(LPCWSTR wstr)
    {
        WindowsCreateStringReference(wstr, lstrlenW(wstr), &hh, &hstr);
    }
    template <unsigned int sizeDest>
    explicit AutoHString(wchar_t const (&str)[sizeDest])
    {
        WindowsCreateStringReference(str, sizeDest - 1, &hh, &hstr);
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