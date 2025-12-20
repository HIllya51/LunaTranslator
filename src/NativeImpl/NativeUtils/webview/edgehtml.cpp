
#ifndef WINXP
#include "edgehtml.hpp"

double EdgeHtml::get_ZoomFactor() { return m_webview.Scale(); }
void EdgeHtml::put_ZoomFactor(double zoomFactor)
{
    m_webview.Scale(zoomFactor);
}

void EdgeHtml::resize(int w, int h)
{
    Rect bounds(0, 0, w, h);
    m_webview.Bounds(bounds);
}
void EdgeHtml::evaljs(const wchar_t *js, evaljs_callback_t cb)
{
    m_webview.InvokeScriptAsync(L"eval", winrt::single_threaded_vector<winrt::hstring>({winrt::to_hstring(js)}));
}
void EdgeHtml::navigate(const wchar_t *u)
{
    m_webview.Navigate(Uri(u));
}
void EdgeHtml::sethtml(const wchar_t *u)
{
    m_webview.NavigateToString(u);
}
void EdgeHtml::bind(const wchar_t *f, void *)
{
    std::wstring js = std::wstring{} + L"window.LUNAJSObject." + f + LR"( = function(){
    window.external.notify(JSON.stringify({    method: ')" +
                      f + L"',    args: Array.prototype.slice.call(arguments)}));};";

    InitializeScript += js;
    m_webview.AddInitializeScript(InitializeScript);
}
EdgeHtml::~EdgeHtml()
{
}
void EdgeHtml::add_menu(int index, contextmenu_gettext gettext, contextmenu_callback_t_ex callback, contextmenu_getchecked getchecked, contextmenu_getuse getuse)
{
    NativeMenuHelper::add_menu(index, gettext, callback, getchecked, getuse);
}
EdgeHtml::EdgeHtml(HWND parent, bool backgroundtransparent)
{
    init_apartment(winrt::apartment_type::single_threaded);
    auto process = WebViewControlProcess();
    auto op = process.CreateWebViewControlAsync(reinterpret_cast<int64_t>(parent), Rect());
    if (op.Status() != AsyncStatus::Completed)
    {
        CoAsyncTaskWaiter waiter;
        op.Completed([&waiter](auto, auto)
                     { waiter.Set(); });
        waiter.Wait();
    }
    m_webview = op.GetResults();
    m_webview.Settings().IsScriptNotifyAllowed(true);
    m_webview.Settings().IsJavaScriptEnabled(true);
    if (backgroundtransparent)
    {
        // 实际上不管用，不知道为什么。
        m_webview.DefaultBackgroundColor(winrt::Windows::UI::Colors::Transparent());
    }
    m_webview.IsVisible(true);
    m_webview.ScriptNotify(
        [&, parent](auto const &sender, auto const &args)
        {
            std::wstring value = args.Value().c_str();
            static std::wstring __contextmenu__helper = L"__contextmenu__helper";
            if (value._Starts_with(__contextmenu__helper))
            {
                CreateMenu(parent, value.substr(__contextmenu__helper.size()));
            }
            else if (callback)
            {
                callback(value.c_str());
            }
        });
    m_webview.NavigationStarting(
        [=](auto const &sender, auto const &args)
        { m_webview.AddInitializeScript(InitializeScript); });
}

DECLARE_API AbstractWebView *edgehtml_new(HWND parent, bool backgroundtransparent)
{
    return new EdgeHtml(parent, backgroundtransparent);
}

DECLARE_API void edgehtml_set_notify_callback(EdgeHtml *ret, web_notify_callback_t callback)
{
    if (!ret)
        return;
    ret->callback = callback;
}
#else

DECLARE_API AbstractWebView *edgehtml_new(HWND parent, bool backgroundtransparent)
{
    return nullptr;
}

DECLARE_API void edgehtml_set_notify_callback(EdgeHtml *ret, web_notify_callback_t callback)
{
}
#endif