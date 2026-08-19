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

DECLARE_API void *webview_allocate_buffer(size_t s)
{
    return new BYTE[s];
}

DECLARE_API std::vector<MenuItem> *webview_menu_create()
{
    return new std::vector<MenuItem>;
}
DECLARE_API void webview_menu_delete(std::vector<MenuItem> *i)
{
    if (!i)
        return;
    delete i;
}
DECLARE_API void webview_menu_append(std::vector<MenuItem> *i, MenuItem *it)
{
    if (!i || !it)
        return;
    i->push_back(std::move(*it));
}
DECLARE_API MenuItem *webview_menuitem_create(LPCWSTR text, bool issep, bool checkable, bool checked, contextmenu_clicked_t clicked)
{
    auto item = new MenuItem{};
    item->text = text;
    item->issep = issep;
    item->checked = checked;
    item->clicked = clicked;
    item->checkable = checkable;
    return item;
}
DECLARE_API void webview_menuitem_append_submenu(MenuItem *parent, MenuItem *sub)
{
    if (!parent || !sub)
        return;
    if (!parent->submenu)
        parent->submenu = std::vector<MenuItem>{};
    parent->submenu->push_back(std::move(*sub));
}
DECLARE_API void webview_menuitem_delete(MenuItem *parent)
{
    if (!parent)
        return;
    delete parent;
}
typedef std::vector<MenuItem> *(*c_menu_handler_t)(LPCWSTR);

DECLARE_API void webview_set_menu_handler(AbstractWebView *web, c_menu_handler_t h)
{
    if (!web)
        return;
    web->menu_handler = [=](LPCWSTR text) -> std::vector<MenuItem>
    {
        auto _ = h(text);
        if (!_)
            return {};
        return std::move(*_);
    };
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

void NativeMenuHelper::CreateMenu(HWND hwndParent, const std::wstring &s, POINT *ppt, menu_handler_t menu_handler)
{
    if (!menu_handler)
        return;
    auto menuitems = menu_handler(s.c_str());
    if (menuitems.empty())
        return;
    HMENU hMenu = CreatePopupMenu();
    int idx = 0;
    for (auto &item : menuitems)
    {
        if (item.issep)
            AppendMenu(hMenu, MF_SEPARATOR, 0, nullptr);
        else
        {
            auto flag = MF_STRING;
            if (item.checkable)
            {
                if (item.checked)
                    flag |= MF_CHECKED;
                else
                    flag |= MF_UNCHECKED;
            }
            auto command = CommandBase++;
            AppendMenu(hMenu, flag, command, item.text.c_str());
            menucallbacks[command] = item.clicked;
        }
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
        if (found->second)
            found->second();
    }
    DestroyMenu(hMenu);
}