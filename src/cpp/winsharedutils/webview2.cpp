#include "webview2_impl.hpp"

DECLARE_API WebView2 *webview2_create(HWND parent, bool backgroundtransparent, bool loadextension)
{
    try
    {
        auto _ = new WebView2(parent, backgroundtransparent, loadextension);
        return _;
    }
    catch (...)
    {
        return nullptr;
    }
}
DECLARE_API void webview2_ext_add(WebView2 *web, LPCWSTR extpath)
{
    if (!web)
        return;
    web->AddExtension(extpath);
}
DECLARE_API void webview2_ext_list(WebView2 *web, List_Ext_callback_t cb)
{
    if (!web)
        return;
    return web->ListExtension(cb);
}
DECLARE_API void webview2_ext_enable(WebView2 *web, LPCWSTR id, BOOL enable)
{
    if (!web)
        return;
    return web->EnableExtension(id, enable);
}
DECLARE_API void webview2_ext_rm(WebView2 *web, LPCWSTR id)
{
    if (!web)
        return;
    return web->RemoveExtension(id);
}
DECLARE_API void webview2_destroy(WebView2 *web)
{
    if (!web)
        return;
    delete web;
}
DECLARE_API void webview2_resize(WebView2 *web, int w, int h)
{
    if (!web)
        return;
    web->Resize(w, h);
}
DECLARE_API void webview2_add_menu(WebView2 *web, int index, const wchar_t *label, contextmenu_callback_t callback)
{
    if (!web)
        return;
    web->AddMenu(index, label, callback);
}
DECLARE_API void webview2_add_menu_noselect(WebView2 *web, int index, const wchar_t *label, contextmenu_notext_callback_t callback)
{
    if (!web)
        return;
    web->AddMenu(index, label, callback);
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

DECLARE_API void webview2_set_observe_ptrs(WebView2 *web, zoomchange_callback_t zoomchange_callback, navigating_callback_t navigating_callback, webmessage_callback_t webmessage_callback, FilesDropped_callback_t FilesDropped_callback)
{
    if (!web)
        return;
    web->zoomchange_callback = zoomchange_callback;
    web->navigating_callback = navigating_callback;
    web->webmessage_callback = webmessage_callback;
    web->FilesDropped_callback = FilesDropped_callback;
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
