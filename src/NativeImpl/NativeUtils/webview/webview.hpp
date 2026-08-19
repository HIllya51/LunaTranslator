#pragma once

typedef void (*evaljs_callback_t)(LPCWSTR);
typedef void (*contextmenu_clicked_t)();
typedef LPWSTR (*contextmenu_gettext)();
typedef bool (*contextmenu_getchecked)();
typedef bool (*contextmenu_getuse)();
typedef void (*contextmenu_notext_callback_t)();

struct MenuItem
{
    std::optional<std::vector<MenuItem>> submenu;
    std::wstring text;
    bool issep;
    bool checkable;
    bool checked;
    contextmenu_clicked_t clicked;
};

typedef std::function<std::vector<MenuItem>(LPCWSTR)> menu_handler_t;

#define VIRTUAL_FUNCTIONS_PURE(__)                                              \
    virtual void resize(int w, int h)##__;                                      \
    virtual void evaljs(const wchar_t *js, evaljs_callback_t cb = nullptr)##__; \
    virtual void navigate(LPCWSTR uri)##__;                                     \
    virtual void sethtml(LPCWSTR html)##__;                                     \
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
    menu_handler_t menu_handler = nullptr;
    virtual ~AbstractWebView() = default;
    VIRTUAL_FUNCTIONS_BASE;
    virtual double get_ZoomFactor();
    virtual void put_ZoomFactor(double zoomFactor);
    virtual void put_PreferredColorScheme(PREFERRED_COLOR_SCHEME scheme);
};

class NativeMenuHelper
{
    UINT CommandBase = 10086;
    std::map<int, void (*)()> menucallbacks;

public:
    void CreateMenu(HWND hwndParent, const std::wstring &s, POINT *ppt = nullptr, menu_handler_t menu_handler = nullptr);
};