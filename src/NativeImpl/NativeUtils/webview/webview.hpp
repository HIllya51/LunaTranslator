#pragma once

typedef void (*evaljs_callback_t)(LPCWSTR);
typedef void (*contextmenu_callback_t)(LPCWSTR);
typedef LPWSTR (*contextmenu_gettext)();
typedef bool (*contextmenu_getchecked)();
typedef bool (*contextmenu_getuse)();
typedef void (*contextmenu_notext_callback_t)();
typedef std::variant<contextmenu_callback_t, contextmenu_notext_callback_t> contextmenu_callback_t_ex;

#define VIRTUAL_FUNCTIONS_PURE(__)                                                                                                                                       \
    virtual void resize(int w, int h)##__;                                                                                                                               \
    virtual void add_menu(int index, contextmenu_gettext gettext, contextmenu_callback_t_ex callback, contextmenu_getchecked getchecked, contextmenu_getuse getuse)##__; \
    virtual void evaljs(const wchar_t *js, evaljs_callback_t cb = nullptr)##__;                                                                                          \
    virtual void navigate(LPCWSTR uri)##__;                                                                                                                              \
    virtual void sethtml(LPCWSTR html)##__;                                                                                                                              \
    virtual void bind(LPCWSTR funcname, void *)##__;

#define VIRTUAL_FUNCTIONS_BASE VIRTUAL_FUNCTIONS_PURE(= 0)
#define VIRTUAL_FUNCTIONS_IMPL VIRTUAL_FUNCTIONS_PURE(override)

enum class PREFERRED_COLOR_SCHEME
{
    AUTO,
    LIGHT,
    DARK
};
class AbstractWebView
{
public:
    virtual ~AbstractWebView() = default;
    VIRTUAL_FUNCTIONS_BASE;
    virtual double get_ZoomFactor();
    virtual void put_ZoomFactor(double zoomFactor);
    virtual void put_PreferredColorScheme(PREFERRED_COLOR_SCHEME scheme);
};

class NativeMenuHelper
{
    std::vector<std::tuple<contextmenu_gettext, int, contextmenu_getuse, contextmenu_getchecked>> menuitems;
    std::vector<std::tuple<contextmenu_gettext, int, contextmenu_getuse, contextmenu_getchecked>> menuitems_noselect;
    std::map<int, void (*)(LPCWSTR)> menucallbacks;
    std::map<int, void (*)()> menucallbacks_noselect;
    UINT CommandBase = 10086;

public:
    void add_menu(int index, contextmenu_gettext gettext, contextmenu_callback_t_ex callback, contextmenu_getchecked getchecked, contextmenu_getuse getuse);
    void CreateMenu(HWND hwndParent, const std::wstring &s, POINT *ppt = nullptr);
};