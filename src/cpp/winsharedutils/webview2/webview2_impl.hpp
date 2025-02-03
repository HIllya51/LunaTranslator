
#include <WebView2.h>
typedef void (*evaljs_callback_t)(LPCWSTR);
typedef void (*navigating_callback_t)(LPCWSTR);
typedef void (*contextmenu_callback_t)(LPCWSTR);
typedef bool (*contextmenu_getchecked)();
typedef void (*contextmenu_notext_callback_t)();
typedef void (*zoomchange_callback_t)(double);
typedef void (*webmessage_callback_t)(LPCWSTR);
typedef void (*FilesDropped_callback_t)(LPCWSTR);
typedef void (*List_Ext_callback_t)(LPCWSTR, LPCWSTR, BOOL);

class WebView2;
class WebView2ComHandler : public ComImpl<ICoreWebView2NavigationStartingEventHandler, ICoreWebView2ZoomFactorChangedEventHandler, ICoreWebView2ContextMenuRequestedEventHandler, ICoreWebView2WebMessageReceivedEventHandler, ICoreWebView2PermissionRequestedEventHandler, ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler, ICoreWebView2CreateCoreWebView2ControllerCompletedHandler, ICoreWebView2NewWindowRequestedEventHandler, ICoreWebView2CustomItemSelectedEventHandler>
{
    WebView2 *ref;
    CComHeapPtr<WCHAR> CurrSelectText;
    COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND targetKind;

public:
    WebView2ComHandler(WebView2 *ref) : ref(ref) {}
    // ICoreWebView2CustomItemSelectedEventHandler
    HRESULT STDMETHODCALLTYPE Invoke(ICoreWebView2ContextMenuItem *sender, IUnknown *args);
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
    std::vector<CComPtr<ICoreWebView2ContextMenuItem>> menus;
    std::vector<CComPtr<ICoreWebView2ContextMenuItem>> menus_noselect;
    typedef std::variant<contextmenu_callback_t, contextmenu_notext_callback_t> contextmenu_callback_t_ex;
    std::map<INT32, std::pair<contextmenu_callback_t_ex, contextmenu_getchecked>> menuscallback;
    std::optional<std::wstring> UserDir();
    HRESULT CreateCoreWebView2EnvironmentError = S_OK, CreateCoreWebView2ControllerError = S_OK;

public:
    zoomchange_callback_t zoomchange_callback;
    navigating_callback_t navigating_callback;
    webmessage_callback_t webmessage_callback;
    FilesDropped_callback_t FilesDropped_callback;
    void WaitForLoad();
    void AddMenu(int index, const wchar_t *label, contextmenu_callback_t_ex callback, bool checkable = false, contextmenu_getchecked getchecked = nullptr);
    WebView2(HWND parent, bool);
    HRESULT init(bool);
    void put_PreferredColorScheme(COREWEBVIEW2_PREFERRED_COLOR_SCHEME);
    void Resize(int, int);
    double get_ZoomFactor();
    void put_ZoomFactor(double);
    void EvalJS(const wchar_t *js, evaljs_callback_t cb = nullptr);
    void Navigate(LPCWSTR);
    void SetHTML(LPCWSTR);
    void Bind(LPCWSTR funcname);

    HRESULT AddExtension(LPCWSTR);
    HRESULT ListExtensionDoSomething(List_Ext_callback_t, LPCWSTR, BOOL, BOOL);

private:
    HRESULT ExtensionGetProfile7(ICoreWebView2Profile7 **profile7);
};