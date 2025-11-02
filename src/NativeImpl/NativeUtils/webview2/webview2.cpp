#include "webview2_impl.hpp"
namespace
{
    std::set<WebView2 *> save_ptrs;
}
DECLARE_API void webview2_set_transparent(WebView2 *web, bool backgroundtransparent)
{
    if (!web)
        return;
    web->set_transparent(backgroundtransparent);
}
DECLARE_API HRESULT webview2_create(WebView2 **web, HWND parent, bool backgroundtransparent, bool loadextension)
{
    *web = nullptr;
    auto _ = new WebView2(parent, backgroundtransparent);
    if (!_)
        return E_POINTER;
    auto hr = _->init(loadextension);
    if (FAILED(hr))
    {
        delete _;
        _ = nullptr;
    }
    else
    {
        if (loadextension)
            save_ptrs.insert(_);
    }
    *web = _;
    return hr;
}
DECLARE_API HRESULT webview2_ext_add(LPCWSTR extpath)
{
    auto begin = save_ptrs.begin();
    if (begin == save_ptrs.end())
        return E_ACCESSDENIED;
    CHECK_FAILURE((*begin)->AddExtension(extpath));
    for (auto web : save_ptrs)
    {
        web->Reload();
    }
    return S_OK;
}
DECLARE_API HRESULT webview2_ext_list(List_Ext_callback_t cb)
{
    auto begin = save_ptrs.begin();
    if (begin == save_ptrs.end())
        return E_ACCESSDENIED;
    return (*begin)->ListExtensionDoSomething(cb, nullptr, FALSE, FALSE);
}
DECLARE_API HRESULT webview2_ext_enable(LPCWSTR id, BOOL enable)
{
    auto begin = save_ptrs.begin();
    if (begin == save_ptrs.end())
        return E_ACCESSDENIED;
    CHECK_FAILURE((*begin)->ListExtensionDoSomething(nullptr, id, FALSE, enable));
    for (auto web : save_ptrs)
    {
        web->Reload();
    }
    return S_OK;
}
DECLARE_API HRESULT webview2_ext_rm(LPCWSTR id)
{
    auto begin = save_ptrs.begin();
    if (begin == save_ptrs.end())
        return E_ACCESSDENIED;
    CHECK_FAILURE((*begin)->ListExtensionDoSomething(nullptr, id, TRUE, FALSE));
    for (auto web : save_ptrs)
    {
        web->Reload();
    }
    return S_OK;
}
DECLARE_API void webview2_destroy(WebView2 *web)
{
    if (!web)
        return;
    delete web;
    try
    {
        save_ptrs.erase(web);
    }
    catch (...)
    {
    }
}
DECLARE_API void webview2_resize(WebView2 *web, int w, int h)
{
    if (!web)
        return;
    web->Resize(w, h);
}
DECLARE_API void webview2_add_menu(WebView2 *web, int index, contextmenu_gettext gettext, void *callback, contextmenu_getchecked getchecked, contextmenu_getuse getuse, bool hasSelectText)
{
    if (!web)
        return;
    web->AddMenu(index, gettext, hasSelectText ? contextmenu_callback_t_ex{(contextmenu_callback_t)callback} : contextmenu_callback_t_ex{(contextmenu_notext_callback_t)callback}, getchecked, getuse);
}
DECLARE_API void webview2_detect_version(LPCWSTR dir, void (*cb)(LPCWSTR))
{
    CComHeapPtr<WCHAR> version;
    CHECK_FAILURE_NORET(GetAvailableCoreWebView2BrowserVersionString(dir, &version));
    cb(version);
}
DECLARE_API double webview2_get_ZoomFactor(WebView2 *web)
{
    if (!web)
        return 1;
    return web->get_ZoomFactor();
}
DECLARE_API void webview2_put_ZoomFactor(WebView2 *web, double zoomFactor)
{
    if (!web)
        return;
    web->put_ZoomFactor(zoomFactor);
}
DECLARE_API void webview2_put_PreferredColorScheme(WebView2 *web, COREWEBVIEW2_PREFERRED_COLOR_SCHEME scheme)
{
    if (!web)
        return;
    web->put_PreferredColorScheme(scheme);
}

DECLARE_API void webview2_evaljs(WebView2 *web, const wchar_t *js, evaljs_callback_t cb = nullptr)
{
    if (!web)
        return;
    web->EvalJS(js, cb);
}

DECLARE_API void webview2_set_observe_ptrs(WebView2 *web, zoomchange_callback_t zoomchange_callback, navigating_callback_t navigating_callback, webmessage_callback_t webmessage_callback, FilesDropped_callback_t FilesDropped_callback, titlechange_callback_t titlechange_callback, IconChanged_callback_t IconChanged_callback)
{
    if (!web)
        return;
    web->zoomchange_callback = zoomchange_callback;
    web->navigating_callback = navigating_callback;
    web->webmessage_callback = webmessage_callback;
    web->FilesDropped_callback = FilesDropped_callback;
    web->titlechange_callback = titlechange_callback;
    web->IconChanged_callback = IconChanged_callback;
}

DECLARE_API void webview2_navigate(WebView2 *web, LPCWSTR uri)
{
    if (!web)
        return;
    web->Navigate(uri);
}

DECLARE_API void webview2_sethtml(WebView2 *web, LPCWSTR html)
{
    if (!web)
        return;
    web->SetHTML(html);
}

DECLARE_API void webview2_bind(WebView2 *web, LPCWSTR funcname)
{
    if (!web)
        return;
    web->Bind(funcname);
}

DECLARE_API void webview2_get_userdir(void (*cb)(LPCWSTR))
{
    auto begin = save_ptrs.begin();
    if (begin == save_ptrs.end())
        return;
    cb((*begin)->GetUserDataFolder().c_str());
}
