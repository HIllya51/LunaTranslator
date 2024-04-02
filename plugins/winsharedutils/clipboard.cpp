
#include "define.h"
#include <windows.h>
bool tryopenclipboard(HWND hwnd = 0)
{
    bool success = false;
    for (int i = 0; i < 50; i++)
    {
        if (OpenClipboard(hwnd))
        {
            success = true;
            break;
        }
        else
        {
            Sleep(10);
        }
    }
    return success;
}
wchar_t *clipboard_get()
{
    wchar_t *data = 0;
    if (tryopenclipboard() == false)
        return 0;
    do
    {
        HANDLE hData = GetClipboardData(CF_UNICODETEXT);
        if (hData == 0)
            break;
        LPWSTR pszText = static_cast<LPWSTR>(GlobalLock(hData));
        if (pszText == 0)
            break;
        int sz = GlobalSize(hData);
        data = new wchar_t[sz + 1];
        wcscpy_s(data, sz, pszText);
        data[sz] = 0;
        GlobalUnlock(hData);
    } while (false);
    CloseClipboard();
    return data;
}
bool clipboard_set(HWND hwnd, wchar_t *text)
{
    bool success = false;
    // static HWND hwnd=CreateWindowExA(0,"STATIC",0,0,0,0,0,0,0,0,0,0);
    if (tryopenclipboard(hwnd) == false)
        return false;
    EmptyClipboard();
    do
    {
        HGLOBAL hClipboardData;
        size_t len = wcslen(text) + 1;
        hClipboardData = GlobalAlloc(GMEM_MOVEABLE, len * sizeof(wchar_t));
        if (hClipboardData == 0)
            break;
        auto pchData = (wchar_t *)GlobalLock(hClipboardData);
        if (pchData == 0)
            break;
        wcscpy_s(pchData, len, text);
        GlobalUnlock(hClipboardData);
        SetClipboardData(CF_UNICODETEXT, hClipboardData);
        success = true;

    } while (false);
    CloseClipboard();
    return success;
}