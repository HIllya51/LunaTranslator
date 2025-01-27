#include "webview2.hpp"

DECLARE_API WebView2 *webview2_create(HWND parent, bool backgroundtransparent)
{
    try
    {
        auto _ = new WebView2(parent, backgroundtransparent);
        return _;
    }
    catch (...)
    {
        return nullptr;
    }
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
    RECT rect{0, 0, w, h};
    web->m_webViewController->put_Bounds(rect);
}
DECLARE_API void webview2_add_menu(WebView2 *web, int index, const wchar_t *label, contextmenu_callback_t callback)
{
    if (!web)
        return;
    web->menus.insert(web->menus.begin() + index, std::make_pair(label, callback));
}
DECLARE_API void webview2_add_menu_noselect(WebView2 *web, int index, const wchar_t *label, contextmenu_notext_callback_t callback)
{
    if (!web)
        return;
    web->menus_noselect.insert(web->menus_noselect.begin() + index, std::make_pair(label, callback));
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
    double zoomFactor;
    web->m_webViewController->get_ZoomFactor(&zoomFactor);
    return zoomFactor;
}
DECLARE_API void webview2_put_ZoomFactor(WebView2 *web, double zoomFactor)
{
    if (!web)
        return;
    web->m_webViewController->put_ZoomFactor(zoomFactor);
}
DECLARE_API void webview2_put_PreferredColorScheme(WebView2 *web, COREWEBVIEW2_PREFERRED_COLOR_SCHEME scheme)
{
    if (!web)
        return;
    CComPtr<ICoreWebView2_13> webView2_13;
    CHECK_FAILURE_NORET(web->m_webView.QueryInterface(&webView2_13));
    CComPtr<ICoreWebView2Profile> profile;
    CHECK_FAILURE_NORET(webView2_13->get_Profile(&profile));
    CHECK_FAILURE_NORET(profile->put_PreferredColorScheme(scheme));
}

DECLARE_API void webview2_evaljs(WebView2 *web, const wchar_t *js, evaljs_callback_t cb = nullptr)
{
    if (!web)
        return;
    if (cb)
    {
        CComPtr<JSEvalCallback> callback = new JSEvalCallback{cb};
        CHECK_FAILURE_NORET(web->m_webView->ExecuteScript(js, callback));
        callback->waitforexec.Wait();
    }
    else
        web->m_webView->ExecuteScript(js, nullptr);
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
    web->m_webView->Navigate(uri);
}

DECLARE_API void webview2_sethtml(WebView2 *web, LPCWSTR html)
{
    if (!web)
        return;
    web->m_webView->NavigateToString(html);
}

DECLARE_API void webview2_bind(WebView2 *web, LPCWSTR funcname)
{
    if (!web)
        return;
    std::wstring js = std::wstring{} + L"window.LUNAJSObject." + funcname + L" = function(){window.chrome.webview.postMessage({    method: '" + funcname + L"',    args: Array.prototype.slice.call(arguments)});};";
    CHECK_FAILURE_NORET(web->m_webView->AddScriptToExecuteOnDocumentCreated(js.c_str(), nullptr));
}