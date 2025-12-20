// SimpleBrowser.cpp --- simple Win32 browser
// Copyright (C) 2019 Katayama Hirofumi MZ <katayama.hirofumi.mz@gmail.com>
// This file is public domain software.

#include "mshtml.hpp"
#include "webview.hpp"
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
        return ERROR_SUCCESS == hkeyEmulation.SetDWORDValue(pchFileName, dwValue);
    }
    else
    {
        hkeyEmulation.DeleteValue(pchFileName);
        return TRUE;
    }
}
typedef bool (*contextmenu_getuse)();
typedef LPWSTR (*contextmenu_gettext)();
class MWebBrowserEx : public MWebBrowser, public AbstractWebView, public NativeMenuHelper
{
    HWND hwndParent;

    std::optional<std::wstring> getstring(contextmenu_gettext gettext)
    {
        if (!gettext)
            return {};
        auto text_ = gettext();
        if (!text_)
            return {};
        std::wstring _ = text_;
        delete text_;
        return _;
    };

public:
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
    ~MWebBrowserEx() override;
    VIRTUAL_FUNCTIONS_IMPL;
};

void MWebBrowserEx::resize(int w, int h)
{
    RECT r{};
    r.right = w;
    r.bottom = h;
    MoveWindow(r);
}
void MWebBrowserEx::add_menu(int index, contextmenu_gettext gettext, contextmenu_callback_t_ex callback, contextmenu_getchecked getchecked, contextmenu_getuse getuse)
{
    NativeMenuHelper::add_menu(index, gettext, callback, getchecked, getuse);
}
void MWebBrowserEx::evaljs(const wchar_t *js, evaljs_callback_t cb)
{
    CComPtr<IHTMLDocument2> pDocument;
    CHECK_FAILURE_NORET(GetIHTMLDocument2(&pDocument));
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
    _snwprintf_s(eval.get(), n, _TRUNCATE, L"%s%s%s", prologue, js, epilogue);
    CComBSTR bstrVal = eval.get();
    arg->bstrVal = bstrVal;
    scriptDispatch->Invoke(
        dispid, IID_NULL, 0, DISPATCH_METHOD,
        &params, &result, &excepInfo, &nArgErr);
}
void MWebBrowserEx::navigate(LPCWSTR uri)
{
    Navigate2(uri);
}
void MWebBrowserEx::sethtml(LPCWSTR html)
{
    SetHtml(html);
}
void MWebBrowserEx::bind(LPCWSTR funcname, void *f)
{

    jsobj->bindfunction(funcname, static_cast<void (*)(wchar_t **, int)>(f));
}
MWebBrowserEx::~MWebBrowserEx()
{
    // 可能double free，不过目前似乎这个东西除非退出否则永远不会析构，就这样吧先。
    printf("warning: freeing MWebBrowserEx\n");
    Destroy();
}
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
    case CONTEXT_MENU_DEFAULT:
    case CONTEXT_MENU_TEXTSELECT:
    {
        std::wstring s;
        if (dwID == CONTEXT_MENU_DEFAULT)
        {
            CComBSTR selectedText;
            if (SUCCEEDED(getselectedtext(&selectedText)))
                s = selectedText;
        }
        CreateMenu(hwndParent, s, ppt);
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
DECLARE_API void html_new(HWND parent, AbstractWebView **ret)
{
    // MWebBrowserEx是多继承虚类，所以必须要转成目标基类在返回，否则指针指向不对。
    DoSetBrowserEmulation(getemulation());
    auto s_pWebBrowser = MWebBrowserEx::Create(parent);
    if (!s_pWebBrowser)
        return;

    s_pWebBrowser->put_Silent(VARIANT_TRUE);
    s_pWebBrowser->AllowInsecure(TRUE);
    *ret = s_pWebBrowser;
}

DECLARE_API void html_get_current_url(AbstractWebView *ww, void (*cb)(LPCWSTR))
{
    if (!ww)
        return;
    auto _ = dynamic_cast<MWebBrowserEx *>(ww);
    if (!_)
        return;
    CComBSTR _u;
    CHECK_FAILURE_NORET(_->get_LocationURL(&_u));
    cb(_u);
}

DECLARE_API void html_get_select_text(AbstractWebView *ww, void (*cb)(LPCWSTR))
{
    if (!ww)
        return;
    auto _ = dynamic_cast<MWebBrowserEx *>(ww);
    if (!_)
        return;
    CComBSTR selectedText;
    CHECK_FAILURE_NORET(_->getselectedtext(&selectedText));
    cb(selectedText);
}

DECLARE_API bool html_check_ctrlc(AbstractWebView *ww)
{
    if (!ww)
        return false;
    auto _ = dynamic_cast<MWebBrowserEx *>(ww);
    if (!_)
        return false;
    return GetAsyncKeyState(VK_CONTROL) && GetAsyncKeyState(67) && (_->GetIEServerWindow() == GetFocus());
}

DECLARE_API void html_get_html(AbstractWebView *ww, void (*cb)(LPCWSTR), LPWSTR elementid)
{
    if (!ww)
        return;
    auto _ = dynamic_cast<MWebBrowserEx *>(ww);
    if (!_)
        return;
    CComPtr<IHTMLDocument2> pDocument;
    CHECK_FAILURE_NORET(_->GetIHTMLDocument2(&pDocument));
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