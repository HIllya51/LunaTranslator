
#include <WebView2.h>
typedef void (*evaljs_callback_t)(LPCWSTR);
typedef void (*navigating_callback_t)(LPCWSTR, bool);
typedef void (*titlechange_callback_t)(LPCWSTR);
typedef void (*contextmenu_callback_t)(LPCWSTR);
typedef LPWSTR (*contextmenu_gettext)();
typedef bool (*contextmenu_getchecked)();
typedef bool (*contextmenu_getuse)();
typedef void (*contextmenu_notext_callback_t)();
typedef void (*zoomchange_callback_t)(double);
typedef void (*webmessage_callback_t)(LPCWSTR);
typedef void (*FilesDropped_callback_t)(LPCWSTR);
typedef void (*List_Ext_callback_t)(LPCWSTR, LPCWSTR, BOOL);
typedef void (*IconChanged_callback_t)(const byte *, size_t);

class WebView2;
class WebView2ComHandler2 : public ComImpl<ICoreWebView2FaviconChangedEventHandler, ICoreWebView2GetFaviconCompletedHandler>
{
    WebView2 *ref;

public:
    WebView2ComHandler2(WebView2 *ref) : ref(ref) {}
    // ICoreWebView2FaviconChangedEventHandler
    HRESULT STDMETHODCALLTYPE Invoke(ICoreWebView2 *sender, IUnknown *args);
    // ICoreWebView2GetFaviconCompletedHandler
    HRESULT STDMETHODCALLTYPE Invoke(HRESULT errorCode, IStream *faviconStream);
};
class WebView2ComHandler : public ComImpl<ICoreWebView2NavigationStartingEventHandler, ICoreWebView2ZoomFactorChangedEventHandler, ICoreWebView2ContextMenuRequestedEventHandler, ICoreWebView2WebMessageReceivedEventHandler, ICoreWebView2PermissionRequestedEventHandler, ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler, ICoreWebView2CreateCoreWebView2ControllerCompletedHandler, ICoreWebView2NewWindowRequestedEventHandler,  ICoreWebView2DocumentTitleChangedEventHandler>
{
    WebView2 *ref;
    COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND targetKind;
    std::once_flag navigatingfirst;
    bool isextensionsettignwindow;
    CComPtr<WebView2ComHandler2> otherhandler;

public:
    WebView2ComHandler(WebView2 *ref) : ref(ref) {}
    // ICoreWebView2DocumentTitleChangedEventHandler
    HRESULT STDMETHODCALLTYPE Invoke(ICoreWebView2 *sender, IUnknown *args);
    // ICoreWebView2NavigationStartingEventHandler
    HRESULT STDMETHODCALLTYPE Invoke(ICoreWebView2 *sender, ICoreWebView2NavigationStartingEventArgs *args);
    // ICoreWebView2CreateCoreWebView2ControllerCompletedHandler
    HRESULT STDMETHODCALLTYPE Invoke(HRESULT result, ICoreWebView2Controller *controller);
    // ICoreWebView2NewWindowRequestedEventHandler
    HRESULT STDMETHODCALLTYPE Invoke(ICoreWebView2 *sender, ICoreWebView2NewWindowRequestedEventArgs *args);
    // ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler
    HRESULT STDMETHODCALLTYPE Invoke(HRESULT result, ICoreWebView2Environment *env);
    // ICoreWebView2PermissionRequestedEventHandler
    HRESULT STDMETHODCALLTYPE Invoke(ICoreWebView2 *, ICoreWebView2PermissionRequestedEventArgs *args);
    // ICoreWebView2WebMessageReceivedEventHandler
    HRESULT STDMETHODCALLTYPE Invoke(ICoreWebView2 *sender, ICoreWebView2WebMessageReceivedEventArgs *args);
    // ICoreWebView2ZoomFactorChangedEventHandler
    HRESULT STDMETHODCALLTYPE Invoke(ICoreWebView2Controller *sender, IUnknown *args);
    // ICoreWebView2ContextMenuRequestedEventHandler
    HRESULT STDMETHODCALLTYPE Invoke(ICoreWebView2 *sender, ICoreWebView2ContextMenuRequestedEventArgs *args);
};
typedef std::variant<contextmenu_callback_t, contextmenu_notext_callback_t> contextmenu_callback_t_ex;
struct MenuContexts
{
    contextmenu_gettext gettext;
    contextmenu_callback_t_ex callback;
    bool checkable;
    contextmenu_getchecked getchecked;
    contextmenu_getuse getuse;
};
class WebView2
{
    friend class WebView2ComHandler;
    HWND parent;
    bool backgroundtransparent;
    std::atomic_flag waitforloadflag = ATOMIC_FLAG_INIT;
    CComPtr<ICoreWebView2Controller> m_webViewController;
    CComPtr<ICoreWebView2> m_webView;
    CComPtr<ICoreWebView2Environment> m_env;
    CComPtr<WebView2ComHandler> handler;
    std::vector<MenuContexts> menus;
    std::vector<MenuContexts> menus_noselect;
    std::optional<std::wstring> UserDir(bool);
    HRESULT CreateCoreWebView2EnvironmentError = S_OK, CreateCoreWebView2ControllerError = S_OK;
    LONG chromeextensionpage = 0;
    bool loadextension;

public:
    zoomchange_callback_t zoomchange_callback = nullptr;
    navigating_callback_t navigating_callback = nullptr;
    webmessage_callback_t webmessage_callback = nullptr;
    FilesDropped_callback_t FilesDropped_callback = nullptr;
    titlechange_callback_t titlechange_callback = nullptr;
    IconChanged_callback_t IconChanged_callback = nullptr;
    void WaitForLoad();
    void AddMenu(int index, contextmenu_gettext gettext, contextmenu_callback_t_ex callback, bool checkable = false, contextmenu_getchecked getchecked = nullptr, contextmenu_getuse getuse = nullptr);
    WebView2(HWND parent, bool);
    HRESULT init(bool);
    void put_PreferredColorScheme(COREWEBVIEW2_PREFERRED_COLOR_SCHEME);
    void set_transparent(bool);
    void Resize(int, int);
    double get_ZoomFactor();
    void put_ZoomFactor(double);
    void EvalJS(const wchar_t *js, evaljs_callback_t cb = nullptr);
    void Navigate(LPCWSTR);
    void SetHTML(LPCWSTR);
    void Bind(LPCWSTR funcname);
    std::wstring GetUserDataFolder();

    HRESULT AddExtension(LPCWSTR);
    HRESULT ListExtensionDoSomething(List_Ext_callback_t, LPCWSTR, BOOL, BOOL);
    void Reload();

private:
    HRESULT ExtensionGetProfile7(ICoreWebView2Profile7 **profile7);
};