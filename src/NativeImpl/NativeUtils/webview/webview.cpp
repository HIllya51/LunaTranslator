#include "webview.hpp"
#include "webview2.hpp"

DECLARE_API void webview_destroy(AbstractWebView *web)
{
    if (!web)
        return;
    delete web;
}
DECLARE_API void webview_resize(AbstractWebView *web, int w, int h)
{
    if (!web)
        return;
    web->resize(w, h);
}
DECLARE_API void webview_add_menu(AbstractWebView *web, int index, contextmenu_gettext gettext, void *callback, contextmenu_getchecked getchecked, contextmenu_getuse getuse, bool hasSelectText)
{
    if (!web)
        return;
    web->add_menu(index, gettext, hasSelectText ? contextmenu_callback_t_ex{(contextmenu_callback_t)callback} : contextmenu_callback_t_ex{(contextmenu_notext_callback_t)callback}, getchecked, getuse);
}
DECLARE_API double webview_get_ZoomFactor(AbstractWebView *web)
{
    if (!web)
        return 1;
    return web->get_ZoomFactor();
}

DECLARE_API void webview_put_ZoomFactor(AbstractWebView *web, double zoomFactor)
{
    if (!web)
        return;
    web->put_ZoomFactor(zoomFactor);
}
DECLARE_API void webview_put_PreferredColorScheme(AbstractWebView *web, PREFERRED_COLOR_SCHEME scheme)
{
    if (!web)
        return;
    web->put_PreferredColorScheme(scheme);
}
DECLARE_API void webview_evaljs(AbstractWebView *web, const wchar_t *js, evaljs_callback_t cb = nullptr)
{
    if (!web)
        return;
    web->evaljs(js, cb);
}
DECLARE_API void webview_navigate(AbstractWebView *web, LPCWSTR uri)
{
    if (!web)
        return;
    web->navigate(uri);
}
DECLARE_API void webview_sethtml(AbstractWebView *web, LPCWSTR html)
{
    if (!web)
        return;
    web->sethtml(html);
}
DECLARE_API void webview_bind(AbstractWebView *web, LPCWSTR funcname, void *f)
{
    if (!web)
        return;
    web->bind(funcname, f);
}
double AbstractWebView::get_ZoomFactor() { return 1.0; }
void AbstractWebView::put_ZoomFactor(double) {}
void AbstractWebView::put_PreferredColorScheme(PREFERRED_COLOR_SCHEME) {}

void NativeMenuHelper::add_menu(int index, contextmenu_gettext gettext, contextmenu_callback_t_ex callback, contextmenu_getchecked getchecked, contextmenu_getuse getuse)
{
    if (auto c = std::get_if<contextmenu_callback_t>(&callback))
    {
        auto ptr = menuitems.begin() + index;
        auto command = CommandBase++;
        menuitems.insert(ptr, {gettext, command, getuse, getchecked});
        menucallbacks[command] = *c;
    }
    else if (auto c = std::get_if<contextmenu_notext_callback_t>(&callback))
    {
        auto ptr = menuitems_noselect.begin() + index;
        auto command = CommandBase++;
        menuitems_noselect.insert(ptr, {gettext, command, getuse, getchecked});
        menucallbacks_noselect[command] = *c;
    }
}

static std::optional<std::wstring> getstring(contextmenu_gettext gettext)
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

void NativeMenuHelper::CreateMenu(HWND hwndParent, const std::wstring &s, POINT *ppt)
{
    auto usemenu = s.empty() ? menuitems_noselect : menuitems;
    if (!usemenu.size())
        return;
    HMENU hMenu = CreatePopupMenu();
    int idx = 0;
    for (auto &item : usemenu)
    {
        if (std::get<2>(item) && !std::get<2>(item)())
            continue;
        if (auto text = getstring(std::get<0>(item)))
        {
            auto flag = MF_STRING;
            if (auto check = std::get<3>(item))
            {
                if (check())
                    flag |= MF_CHECKED;
                else
                    flag |= MF_UNCHECKED;
            }
            AppendMenu(hMenu, flag, std::get<1>(item), text.value().c_str());
        }
        else if (idx)
            AppendMenu(hMenu, MF_SEPARATOR, 0, nullptr);
        idx += 1;
    }
    POINT p;
    GetCursorPos(&p);
    if (!ppt)
        ppt = &p;
    auto wp = TrackPopupMenu(hMenu, TPM_RETURNCMD | TPM_LEFTALIGN | TPM_LEFTBUTTON, ppt->x, ppt->y, 0, hwndParent, nullptr);
    auto found = menucallbacks.find((int)wp);
    if (found != menucallbacks.end())
    {
        [&]()
        {
            found->second(s.c_str());
        }();
    }
    else
    {
        auto found2 = menucallbacks_noselect.find((int)wp);
        if (found2 != menucallbacks_noselect.end())
            found2->second();
    }
    DestroyMenu(hMenu);
}