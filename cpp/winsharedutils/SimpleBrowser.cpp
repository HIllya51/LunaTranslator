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
    CRegKey hKey;
    if (ERROR_SUCCESS != hKey.Open(HKEY_LOCAL_MACHINE, LR"(SOFTWARE\Microsoft\Internet Explorer)", KEY_READ))
        return FALSE;
    DWORD cb = cchVersionMax * sizeof(WCHAR);
    if ((ERROR_SUCCESS == hKey.QueryStringValue(L"svcVersion", pszVersion, &cb)) ||
        (ERROR_SUCCESS == hKey.QueryStringValue(L"Version", pszVersion, &cb)))
        return TRUE;
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
        TEXT(R"(SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl)");

    TCHAR szPath[MAX_PATH], *pchFileName;
    GetModuleFileName(NULL, szPath, ARRAYSIZE(szPath));
    pchFileName = PathFindFileName(szPath);

    CRegKey hkeyControl;
    if (ERROR_SUCCESS != hkeyControl.Open(HKEY_CURRENT_USER, s_szFeatureControl, KEY_ALL_ACCESS))
        return FALSE;

    CRegKey hkeyEmulation;
    if (ERROR_SUCCESS != hkeyEmulation.Create(hkeyControl, TEXT("FEATURE_BROWSER_EMULATION"), 0, 0, KEY_ALL_ACCESS, NULL, NULL))
        return FALSE;

    if (dwValue)
    {
        return ERROR_SUCCESS == hkeyEmulation.SetValue(dwValue, pchFileName);
    }
    else
    {
        hkeyEmulation.DeleteValue(pchFileName);
        return TRUE;
    }
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

DECLARE_API void html_get_current_url(void *web, void (*cb)(LPCWSTR))
{
    if (!web)
        return;
    auto ww = static_cast<MWebBrowserEx *>(web);
    CComBSTR _u;
    CHECK_FAILURE_NORET(ww->get_LocationURL(&_u));
    cb(_u);
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
DECLARE_API void html_get_select_text(void *web, void (*cb)(LPCWSTR))
{
    if (!web)
        return;
    auto ww = static_cast<MWebBrowserEx *>(web);
    CComPtr<IHTMLDocument2> pDocument;
    CHECK_FAILURE_NORET(ww->GetIHTMLDocument2(&pDocument));
    CComPtr<IHTMLSelectionObject> pSelectionObj;
    CHECK_FAILURE_NORET(pDocument->get_selection(&pSelectionObj));
    CComPtr<IHTMLTxtRange> pTxtRange;
    CHECK_FAILURE_NORET(pSelectionObj->createRange((IDispatch **)&pTxtRange));
    CComBSTR selectedText;
    CHECK_FAILURE_NORET(pTxtRange->get_text(&selectedText));
    cb(selectedText);
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
    CComPtr<IHTMLDocument2> pDocument;
    CHECK_FAILURE_NORET(ww->GetIHTMLDocument2(&pDocument));
    CComPtr<IDispatch> scriptDispatch;
    CHECK_FAILURE_NORET(pDocument->get_Script(&scriptDispatch));
    DISPID dispid;
    CComBSTR evalStr = L"eval";
    CHECK_FAILURE_NORET(scriptDispatch->GetIDsOfNames(IID_NULL, &evalStr, 1,
                                                      LOCALE_SYSTEM_DEFAULT, &dispid) != S_OK);

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
