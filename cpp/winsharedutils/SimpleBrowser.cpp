// SimpleBrowser.cpp --- simple Win32 browser
// Copyright (C) 2019 Katayama Hirofumi MZ <katayama.hirofumi.mz@gmail.com>
// This file is public domain software.

#define _CRT_SECURE_NO_WARNINGS
// SimpleBrowser.cpp --- simple Win32 browser
// Copyright (C) 2019 Katayama Hirofumi MZ <katayama.hirofumi.mz@gmail.com>
// This file is public domain software.

#define _CRT_SECURE_NO_WARNINGS
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
class MWebBrowserEx : public MWebBrowser
{
    HWND hwndParent;

public:
    std::vector<std::tuple<std::optional<std::wstring>, int>> menuitems;
    static MWebBrowserEx *Create(HWND _hwndParent);
    // IDocHostUIHandler interface
    STDMETHODIMP ShowContextMenu(
        DWORD dwID,
        POINT *ppt,
        IUnknown *pcmdtReserved,
        IDispatch *pdispReserved);

protected:
    MWebBrowserEx(HWND _hwndParent);
};
MWebBrowserEx::MWebBrowserEx(HWND _hwndParent) : MWebBrowser(_hwndParent), hwndParent(_hwndParent)
{
}
MWebBrowserEx *MWebBrowserEx::Create(HWND _hwndParent)
{
    MWebBrowserEx *pBrowser = new MWebBrowserEx(_hwndParent);
    if (!pBrowser->IsCreated())
    {
        pBrowser->Release();
        pBrowser = NULL;
    }
    return pBrowser;
}
STDMETHODIMP MWebBrowserEx::ShowContextMenu(
    DWORD dwID,
    POINT *ppt,
    IUnknown *pcmdtReserved,
    IDispatch *pdispReserved)
{
    HMENU hMenu = NULL;
    switch (dwID)
    {
    case CONTEXT_MENU_TEXTSELECT:
    {
        if (!menuitems.size())
            return S_FALSE;
        HMENU hMenu = CreatePopupMenu();
        int idx = 0;
        for (auto &item : menuitems)
        {
            if (std::get<0>(item))
            {
                AppendMenu(hMenu, MF_STRING, std::get<1>(item), std::get<0>(item).value().c_str());
            }
            else
                AppendMenu(hMenu, MF_SEPARATOR, 0, nullptr);
            idx += 1;
        }
        TrackPopupMenu(hMenu, TPM_LEFTALIGN | TPM_LEFTBUTTON, ppt->x, ppt->y, 0, hwndParent, nullptr);
        DestroyMenu(hMenu);
        return S_OK;
    }
    default:
        return S_FALSE;
    }
}
DECLARE_API DWORD html_version()
{
    return getemulation();
}
DECLARE_API void *html_new(HWND parent)
{
    DoSetBrowserEmulation(getemulation());
    auto s_pWebBrowser = MWebBrowserEx::Create(parent);
    if (!s_pWebBrowser)
        return NULL;

    s_pWebBrowser->put_Silent(VARIANT_TRUE);

    s_pWebBrowser->AllowInsecure(TRUE);

    return s_pWebBrowser;
}

DECLARE_API void html_navigate(void *web, wchar_t *path)
{
    if (!web)
        return;
    auto ww = static_cast<MWebBrowserEx *>(web);
    ww->Navigate2(path);
}
DECLARE_API void html_resize(void *web, int x, int y, int w, int h)
{
    if (!web)
        return;
    auto ww = static_cast<MWebBrowserEx *>(web);
    RECT r;
    r.left = x;
    r.top = y;
    r.right = x + w;
    r.bottom = y + h;
    ww->MoveWindow(r);
}
DECLARE_API void html_release(void *web)
{
    if (!web)
        return;
    auto ww = static_cast<MWebBrowserEx *>(web);
    ww->Destroy();
    // ww->Release(); Destroy减少引用计数，自动del
}

DECLARE_API const wchar_t *html_get_current_url(void *web)
{
    if (!web)
        return L"";
    auto ww = static_cast<MWebBrowserEx *>(web);
    wchar_t *_u;
    ww->get_LocationURL(&_u);
    return _u;
}

DECLARE_API void html_set_html(void *web, wchar_t *html)
{
    if (!web)
        return;
    auto ww = static_cast<MWebBrowserEx *>(web);
    ww->SetHtml(html);
}
DECLARE_API void html_add_menu(void *web, int index, int command, const wchar_t *label)
{
    if (!web)
        return;
    auto ww = static_cast<MWebBrowserEx *>(web);
    std::optional<std::wstring> _label;
    if (label)
        _label = label;
    auto ptr = ww->menuitems.begin() + index;
    ww->menuitems.insert(ptr, {_label, command});
}
BSTR GetSelectedText(IHTMLDocument2 *pHTMLDoc2)
{
    CComPtr<IHTMLSelectionObject> pSelectionObj = nullptr;
    HRESULT hr = pHTMLDoc2->get_selection(&pSelectionObj);
    if (FAILED(hr) || pSelectionObj == nullptr)
    {
        return nullptr;
    }

    CComPtr<IHTMLTxtRange> pTxtRange = nullptr;
    hr = pSelectionObj->createRange((IDispatch **)&pTxtRange);
    if (FAILED(hr) || pTxtRange == nullptr)
    {
        return nullptr;
    }

    BSTR selectedText = nullptr;
    hr = pTxtRange->get_text(&selectedText);

    return selectedText;
}
DECLARE_API const wchar_t *html_get_select_text(void *web)
{
    if (!web)
        return L"";
    auto ww = static_cast<MWebBrowserEx *>(web);

    if (CComPtr<IHTMLDocument2> pDocument = ww->GetIHTMLDocument2())
    {
        auto text = GetSelectedText(pDocument);
        // 不需要free，free会崩溃
        return text;
    }
    return L"";
}

DECLARE_API void html_bind_function(void *web, const wchar_t *name, void (*function)(wchar_t **, int))
{
    if (!web)
        return;
    auto ww = static_cast<MWebBrowserEx *>(web);
    ww->jsobj->bindfunction(name, function);
}

DECLARE_API HWND html_get_ie(void *web)
{
    if (!web)
        return nullptr;
    auto ww = static_cast<MWebBrowserEx *>(web);
    return ww->GetIEServerWindow();
}

DECLARE_API void html_eval(void *web, const wchar_t *js)
{
    if (!web)
        return;
    auto ww = static_cast<MWebBrowserEx *>(web);
    CComPtr<IHTMLDocument2> pDocument = ww->GetIHTMLDocument2();
    if (!pDocument)
        return;
    CComPtr<IDispatch> scriptDispatch;
    if (FAILED(pDocument->get_Script(&scriptDispatch)))
        return;
    DISPID dispid;
    CComBSTR evalStr = L"eval";
    if (scriptDispatch->GetIDsOfNames(IID_NULL, &evalStr, 1,
                                      LOCALE_SYSTEM_DEFAULT, &dispid) != S_OK)

        return;

    DISPPARAMS params;
    VARIANT arg;
    VARIANT result;
    EXCEPINFO excepInfo;
    UINT nArgErr = (UINT)-1;
    params.cArgs = 1;
    params.cNamedArgs = 0;
    params.rgvarg = &arg;
    arg.vt = VT_BSTR;
    static const wchar_t *prologue = L"(function(){";
    static const wchar_t *epilogue = L";})();";
    int n = wcslen(prologue) + wcslen(epilogue) + wcslen(js) + 1;
    auto eval = std::make_unique<wchar_t[]>(n);
    _snwprintf(eval.get(), n, L"%s%s%s", prologue, js, epilogue);
    CComBSTR bstrVal = eval.get();
    arg.bstrVal = bstrVal;
    scriptDispatch->Invoke(
        dispid, IID_NULL, 0, DISPATCH_METHOD,
        &params, &result, &excepInfo, &nArgErr);
}
