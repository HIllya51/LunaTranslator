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
typedef LPWSTR  (*contextmenu_gettext)();
class MWebBrowserEx : public MWebBrowser
{
    HWND hwndParent;

    std::optional<std::wstring> getstring(contextmenu_gettext gettext)
    {
        if (!gettext)
            return {};
        auto text_ = gettext();
        if (!text_)
            return {};
        return text_;
    };

public:
    std::vector<std::tuple<contextmenu_gettext, int>> menuitems;
    std::vector<std::tuple<contextmenu_gettext, int>> menuitems_noselect;
    std::map<int, void (*)(LPCWSTR)> menucallbacks;
    std::map<int, void (*)()> menucallbacks_noselect;
    UINT CommandBase = 10086;
    static MWebBrowserEx *Create(HWND _hwndParent);
    // IDocHostUIHandler interface
    STDMETHODIMP ShowContextMenu(
        DWORD dwID,
        POINT *ppt,
        IUnknown *pcmdtReserved,
        IDispatch *pdispReserved);
    HRESULT getselectedtext(LPWSTR *selectedText)
    {
        CComPtr<IHTMLDocument2> pDocument;
        CHECK_FAILURE(GetIHTMLDocument2(&pDocument));
        CComPtr<IHTMLSelectionObject> pSelectionObj;
        CHECK_FAILURE(pDocument->get_selection(&pSelectionObj));
        CComPtr<IHTMLTxtRange> pTxtRange;
        CHECK_FAILURE(pSelectionObj->createRange((IDispatch **)&pTxtRange));
        CHECK_FAILURE(pTxtRange->get_text(selectedText));
        if (!*selectedText)
            return -1;
        return S_OK;
    }

protected:
    MWebBrowserEx(HWND _hwndParent);
};
MWebBrowserEx::MWebBrowserEx(HWND _hwndParent) : MWebBrowser(_hwndParent), hwndParent(_hwndParent)
{
}
LRESULT CALLBACK Extra_Menu_Handle(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp)
{
    auto proc = (WNDPROC)GetProp(hwnd, L"GWLP_WNDPROC");
    auto thisptr = (MWebBrowserEx *)GetProp(hwnd, L"THIS_PTR");
    if (msg == WM_COMMAND)
    {
        auto found = thisptr->menucallbacks.find((int)wp);
        if (found != thisptr->menucallbacks.end())
        {
            [&]()
            {
                CComBSTR selectedText;
                CHECK_FAILURE_NORET(thisptr->getselectedtext(&selectedText));
                found->second(selectedText);
            }();
        }
        else
        {
            auto found2 = thisptr->menucallbacks_noselect.find((int)wp);
            if (found2 != thisptr->menucallbacks_noselect.end())
                found2->second();
        }
    }
    return proc(hwnd, msg, wp, lp);
}

MWebBrowserEx *MWebBrowserEx::Create(HWND _hwndParent)
{
    MWebBrowserEx *pBrowser = new MWebBrowserEx(_hwndParent);
    if (!pBrowser->IsCreated())
    {
        pBrowser->Release();
        pBrowser = NULL;
    }
    SetProp(_hwndParent, L"GWLP_WNDPROC", (HANDLE)GetWindowLongPtr(_hwndParent, GWLP_WNDPROC));
    SetProp(_hwndParent, L"THIS_PTR", (HANDLE)pBrowser);
    SetWindowLongPtr(_hwndParent, GWLP_WNDPROC, (ULONG_PTR)Extra_Menu_Handle);
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
    case CONTEXT_MENU_DEFAULT:
    {
        if (!menuitems_noselect.size())
            return S_FALSE;
        HMENU hMenu = CreatePopupMenu();
        int idx = 0;
        for (auto &item : menuitems_noselect)
        {
            if (auto text = getstring(std::get<0>(item)))
            {
                AppendMenu(hMenu, MF_STRING, std::get<1>(item), text.value().c_str());
            }
            else if (idx)
                AppendMenu(hMenu, MF_SEPARATOR, 0, nullptr);
            idx += 1;
        }
        TrackPopupMenu(hMenu, TPM_LEFTALIGN | TPM_LEFTBUTTON, ppt->x, ppt->y, 0, hwndParent, nullptr);
        DestroyMenu(hMenu);
        return S_OK;
    }
    case CONTEXT_MENU_TEXTSELECT:
    {
        if (!menuitems.size())
            return S_FALSE;
        HMENU hMenu = CreatePopupMenu();
        int idx = 0;
        for (auto &item : menuitems)
        {
            if (auto text = getstring(std::get<0>(item)))
            {
                AppendMenu(hMenu, MF_STRING, std::get<1>(item), text.value().c_str());
            }
            else if (idx)
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
DECLARE_API MWebBrowserEx *html_new(HWND parent)
{
    DoSetBrowserEmulation(getemulation());
    auto s_pWebBrowser = MWebBrowserEx::Create(parent);
    if (!s_pWebBrowser)
        return NULL;

    s_pWebBrowser->put_Silent(VARIANT_TRUE);

    s_pWebBrowser->AllowInsecure(TRUE);

    return s_pWebBrowser;
}

DECLARE_API void html_navigate(MWebBrowserEx *ww, wchar_t *path)
{
    if (!ww)
        return;
    ww->Navigate2(path);
}
DECLARE_API void html_resize(MWebBrowserEx *ww, int x, int y, int w, int h)
{
    if (!ww)
        return;
    RECT r;
    r.left = x;
    r.top = y;
    r.right = x + w;
    r.bottom = y + h;
    ww->MoveWindow(r);
}
DECLARE_API void html_release(MWebBrowserEx *ww)
{
    if (!ww)
        return;
    ww->Destroy();
    // ww->Release(); Destroy减少引用计数，自动del
}

DECLARE_API void html_get_current_url(MWebBrowserEx *ww, void (*cb)(LPCWSTR))
{
    if (!ww)
        return;
    CComBSTR _u;
    CHECK_FAILURE_NORET(ww->get_LocationURL(&_u));
    cb(_u);
}

DECLARE_API void html_set_html(MWebBrowserEx *ww, wchar_t *html)
{
    if (!ww)
        return;
    ww->SetHtml(html);
}
DECLARE_API void html_add_menu(MWebBrowserEx *ww, int index, contextmenu_gettext getlabel, void (*callback)(const wchar_t *))
{
    if (!ww)
        return;
    auto ptr = ww->menuitems.begin() + index;
    auto command = ww->CommandBase++;
    ww->menuitems.insert(ptr, {getlabel, command});
    ww->menucallbacks[command] = callback;
}
DECLARE_API void html_add_menu_noselect(MWebBrowserEx *ww, int index, contextmenu_gettext getlabel, void (*callback)())
{
    if (!ww)
        return;
    auto ptr = ww->menuitems_noselect.begin() + index;
    auto command = ww->CommandBase++;
    ww->menuitems_noselect.insert(ptr, {getlabel, command});
    ww->menucallbacks_noselect[command] = callback;
}
DECLARE_API void html_get_select_text(MWebBrowserEx *ww, void (*cb)(LPCWSTR))
{
    if (!ww)
        return;
    CComBSTR selectedText;
    CHECK_FAILURE_NORET(ww->getselectedtext(&selectedText));
    cb(selectedText);
}

DECLARE_API void html_bind_function(MWebBrowserEx *ww, const wchar_t *name, void (*function)(wchar_t **, int))
{
    if (!ww)
        return;
    ww->jsobj->bindfunction(name, function);
}

DECLARE_API bool html_check_ctrlc(MWebBrowserEx *ww)
{
    if (!ww)
        return false;
    return GetAsyncKeyState(VK_CONTROL) && GetAsyncKeyState(67) && (ww->GetIEServerWindow() == GetFocus());
}

DECLARE_API void html_eval(MWebBrowserEx *ww, const wchar_t *js)
{
    if (!ww)
        return;
    CComPtr<IHTMLDocument2> pDocument;
    CHECK_FAILURE_NORET(ww->GetIHTMLDocument2(&pDocument));
    CComPtr<IDispatch> scriptDispatch;
    CHECK_FAILURE_NORET(pDocument->get_Script(&scriptDispatch));
    DISPID dispid;
    CComBSTR evalStr = L"eval";
    CHECK_FAILURE_NORET(scriptDispatch->GetIDsOfNames(IID_NULL, &evalStr, 1,
                                                      LOCALE_SYSTEM_DEFAULT, &dispid) != S_OK);

    DISPPARAMS params;
    AutoVariant arg;
    AutoVariant result;
    EXCEPINFO excepInfo;
    UINT nArgErr = (UINT)-1;
    params.cArgs = 1;
    params.cNamedArgs = 0;
    params.rgvarg = &arg;
    arg->vt = VT_BSTR;
    static const wchar_t *prologue = L"(function(){";
    static const wchar_t *epilogue = L";})();";
    int n = wcslen(prologue) + wcslen(epilogue) + wcslen(js) + 1;
    auto eval = std::make_unique<wchar_t[]>(n);
    _snwprintf(eval.get(), n, L"%s%s%s", prologue, js, epilogue);
    CComBSTR bstrVal = eval.get();
    arg->bstrVal = bstrVal;
    scriptDispatch->Invoke(
        dispid, IID_NULL, 0, DISPATCH_METHOD,
        &params, &result, &excepInfo, &nArgErr);
}
DECLARE_API void html_get_html(MWebBrowserEx *ww, void (*cb)(LPCWSTR), LPWSTR elementid)
{
    if (!ww)
        return;
    CComPtr<IHTMLDocument2> pDocument;
    CHECK_FAILURE_NORET(ww->GetIHTMLDocument2(&pDocument));
    CComPtr<IHTMLDocument3> pDocument3;
    CHECK_FAILURE_NORET(pDocument.QueryInterface(&pDocument3));
    CComPtr<IHTMLElement> ele;
    if (!elementid)
    {
        CHECK_FAILURE_NORET(pDocument3->get_documentElement(&ele));
    }
    else
    {
        CHECK_FAILURE_NORET(pDocument3->getElementById(elementid, &ele));
    }
    if (!ele)
        return;
    CComBSTR data;
    CHECK_FAILURE_NORET(ele->get_outerHTML(&data));
    cb(data);
}