// SimpleBrowser.cpp --- simple Win32 browser
// Copyright (C) 2019 Katayama Hirofumi MZ <katayama.hirofumi.mz@gmail.com>
// This file is public domain software.

#define _CRT_SECURE_NO_WARNINGS
// SimpleBrowser.cpp --- simple Win32 browser
// Copyright (C) 2019 Katayama Hirofumi MZ <katayama.hirofumi.mz@gmail.com>
// This file is public domain software.

#define _CRT_SECURE_NO_WARNINGS
#include <windows.h>
#include <windowsx.h>
#include <commctrl.h>
#include <commdlg.h>
#include <mmsystem.h>
#include <shlobj.h>
#include <shlwapi.h>
#include <mshtml.h>
#include <string>
#include <cctype>
#include <cassert>
#include <strsafe.h>
#include <comdef.h>
#include <mshtmcid.h>
#include <process.h>
#include "MWebBrowser.hpp"

BOOL GetIEVersion(LPWSTR pszVersion, DWORD cchVersionMax)
{
    pszVersion[0] = 0;
    HKEY hKey = NULL;
    RegOpenKeyExW(HKEY_LOCAL_MACHINE, L"SOFTWARE\\Microsoft\\Internet Explorer", 0,
                  KEY_READ, &hKey);
    if (hKey)
    {
        DWORD cb = cchVersionMax * sizeof(WCHAR);
        LONG ret = RegQueryValueExW(hKey, L"svcVersion", NULL, NULL, (LPBYTE)pszVersion, &cb);
        if (ret != ERROR_SUCCESS)
        {
            ret = RegQueryValueExW(hKey, L"Version", NULL, NULL, (LPBYTE)pszVersion, &cb);
        }
        RegCloseKey(hKey);

        return ret == ERROR_SUCCESS;
    }

    return FALSE;
}
static DWORD getemulation()
{
    DWORD m_emulation = 0;
    WCHAR szVersion[32];
    if (GetIEVersion(szVersion, ARRAYSIZE(szVersion)))
    {
        if (szVersion[1] == L'.')
        {
            switch (szVersion[0])
            {
            case '7':
                m_emulation = 7000;
                break;
            case '8':
                m_emulation = 8888;
                break;
            case '9':
                m_emulation = 9999;
                break;
            }
        }
        else if (szVersion[2] == L'.')
        {
            if (szVersion[0] == L'1' && szVersion[1] == L'0')
            {
                m_emulation = 10001;
            }
            if (szVersion[0] == L'1' && szVersion[1] == L'1')
            {
                m_emulation = 11001;
            }
        }
    }
    return m_emulation;
}
BOOL DoSetBrowserEmulation(DWORD dwValue)
{
    static const TCHAR s_szFeatureControl[] =
        TEXT("SOFTWARE\\Microsoft\\Internet Explorer\\Main\\FeatureControl");

    TCHAR szPath[MAX_PATH], *pchFileName;
    GetModuleFileName(NULL, szPath, ARRAYSIZE(szPath));
    pchFileName = PathFindFileName(szPath);

    BOOL bOK = FALSE;
    HKEY hkeyControl = NULL;
    RegOpenKeyEx(HKEY_CURRENT_USER, s_szFeatureControl, 0, KEY_ALL_ACCESS, &hkeyControl);
    if (hkeyControl)
    {
        HKEY hkeyEmulation = NULL;
        RegCreateKeyEx(hkeyControl, TEXT("FEATURE_BROWSER_EMULATION"), 0, NULL, 0,
                       KEY_ALL_ACCESS, NULL, &hkeyEmulation, NULL);
        if (hkeyEmulation)
        {
            if (dwValue)
            {
                DWORD value = dwValue, size = sizeof(value);
                LONG result = RegSetValueEx(hkeyEmulation, pchFileName, 0,
                                            REG_DWORD, (LPBYTE)&value, size);
                bOK = (result == ERROR_SUCCESS);
            }
            else
            {
                RegDeleteValue(hkeyEmulation, pchFileName);
                bOK = TRUE;
            }

            RegCloseKey(hkeyEmulation);
        }

        RegCloseKey(hkeyControl);
    }

    return bOK;
}
extern "C" __declspec(dllexport) void *html_new(HWND parent)
{
    DoSetBrowserEmulation(getemulation());
    auto s_pWebBrowser = MWebBrowser::Create(parent);
    if (!s_pWebBrowser)
        return NULL;

    s_pWebBrowser->put_Silent(VARIANT_TRUE);

    s_pWebBrowser->AllowInsecure(TRUE);

    return s_pWebBrowser;
}

extern "C" __declspec(dllexport) void html_navigate(void *web, wchar_t *path)
{
    if (!web)
        return;
    auto ww = static_cast<MWebBrowser *>(web);
    ww->Navigate2(path);
}
extern "C" __declspec(dllexport) void html_resize(void *web, int x, int y, int w, int h)
{
    if (!web)
        return;
    auto ww = static_cast<MWebBrowser *>(web);
    RECT r;
    r.left = x;
    r.top = y;
    r.right = x + w;
    r.bottom = y + h;
    ww->MoveWindow(r);
}
extern "C" __declspec(dllexport) void html_release(void *web)
{
    if (!web)
        return;
    auto ww = static_cast<MWebBrowser *>(web);
    ww->Destroy();
    // ww->Release(); Destroy减少引用计数，自动del
}