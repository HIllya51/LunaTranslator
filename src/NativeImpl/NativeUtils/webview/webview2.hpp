
#include <WebView2.h>
#include "webview.hpp"

typedef void (*navigating_callback_t)(LPCWSTR, bool);
typedef void (*titlechange_callback_t)(LPCWSTR);
typedef void (*zoomchange_callback_t)(double);
typedef void (*webmessage_callback_t)(LPCWSTR);
typedef void (*FilesDropped_callback_t)(LPCWSTR);
typedef void (*IconChanged_callback_t)(const byte *, size_t);
typedef void (*List_Ext_callback_t)(LPCWSTR, LPCWSTR, BOOL);
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
class WebView2ComHandler : public ComImpl<ICoreWebView2NavigationStartingEventHandler, ICoreWebView2ZoomFactorChangedEventHandler, ICoreWebView2ContextMenuRequestedEventHandler, ICoreWebView2WebMessageReceivedEventHandler, ICoreWebView2PermissionRequestedEventHandler, ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler, ICoreWebView2CreateCoreWebView2ControllerCompletedHandler, ICoreWebView2NewWindowRequestedEventHandler, ICoreWebView2DocumentTitleChangedEventHandler>
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
struct MenuContexts
{
    contextmenu_gettext gettext;
    contextmenu_callback_t_ex callback;
    contextmenu_getchecked getchecked;
    contextmenu_getuse getuse;
};
class WebView2 : public AbstractWebView
{
    friend class WebView2ComHandler;
    friend class WebView2ComHandler2;
    HWND parent;
    bool __init_backgroundtransparent = false;
    std::atomic_flag waitforloadflag = ATOMIC_FLAG_INIT;
    CComPtr<ICoreWebView2Controller> m_webViewController;
    CComPtr<ICoreWebView2> m_webView;
    CComPtr<ICoreWebView2Environment> m_env;
    CComPtr<WebView2ComHandler> handler;
    std::vector<MenuContexts> menus;
    std::vector<MenuContexts> menus_noselect;
    std::optional<std::wstring> UserDir(bool);
    HRESULT CreateCoreWebView2EnvironmentError = S_OK, CreateCoreWebView2ControllerError = S_OK;
    LONG chromeextensionpageoverride;
    bool loadextension;

    zoomchange_callback_t zoomchange_callback = nullptr;
    navigating_callback_t navigating_callback = nullptr;
    webmessage_callback_t webmessage_callback = nullptr;
    FilesDropped_callback_t FilesDropped_callback = nullptr;
    titlechange_callback_t titlechange_callback = nullptr;
    IconChanged_callback_t IconChanged_callback = nullptr;

    void set_transparent(bool);
    HRESULT ExtensionGetProfile7(ICoreWebView2Profile7 **profile7);
    void WaitForLoad();
    double fastcachezoom = 1.0;

public:
    WebView2(HWND parent, bool);
    HRESULT init(bool);
    std::wstring GetUserDataFolder();

    HRESULT AddExtension(LPCWSTR);
    HRESULT ListExtensionDoSomething(List_Ext_callback_t, LPCWSTR, BOOL, BOOL);
    void Reload();
    void set_callbacks(zoomchange_callback_t zoomchange_callback, navigating_callback_t navigating_callback, webmessage_callback_t webmessage_callback, FilesDropped_callback_t FilesDropped_callback, titlechange_callback_t titlechange_callback, IconChanged_callback_t IconChanged_callback);

    double slow_get_ZoomFactor();

public:
    virtual ~WebView2();
    VIRTUAL_FUNCTIONS_IMPL;

    virtual double get_ZoomFactor() override;
    virtual void put_ZoomFactor(double zoomFactor) override;
    virtual void put_PreferredColorScheme(PREFERRED_COLOR_SCHEME scheme) override;

public:
    static HRESULT Create(WebView2 **web, HWND parent, bool backgroundtransparent, bool loadextension);
};
