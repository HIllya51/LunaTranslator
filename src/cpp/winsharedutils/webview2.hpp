#include <variant>
#include <WebView2.h>
typedef void (*evaljs_callback_t)(LPCWSTR);
typedef void (*navigating_callback_t)(LPCWSTR);
typedef void (*contextmenu_callback_t)(LPCWSTR);
typedef void (*contextmenu_notext_callback_t)();
typedef void (*zoomchange_callback_t)(double);
typedef void (*webmessage_callback_t)(LPCWSTR);
typedef void (*FilesDropped_callback_t)(LPCWSTR);

#ifdef WINXP
#define COWAIT_INPUTAVAILABLE 4
#define COWAIT_DISPATCH_CALLS 8
#define COWAIT_DISPATCH_WINDOW_MESSAGES 0x10
#endif
struct CoAsyncTaskWaiter
{
    CEvent event;
    CoAsyncTaskWaiter()
    {
        event.Create(nullptr, false, false, nullptr);
    }
    void Set()
    {
        SetEvent(event);
    }
    void Wait()
    {
        DWORD handleIndex = 0;
        CoWaitForMultipleHandles(COWAIT_DISPATCH_WINDOW_MESSAGES | COWAIT_DISPATCH_CALLS | COWAIT_INPUTAVAILABLE, INFINITE, 1, &event.m_h, &handleIndex);
    }
};
class webview2_com_handler;

class CustomItemSelectedEventHandler_1 : public ComImpl<ICoreWebView2CustomItemSelectedEventHandler>
{
    contextmenu_callback_t callback;
    ICoreWebView2ContextMenuTarget *target;

public:
    CustomItemSelectedEventHandler_1(contextmenu_callback_t callback, ICoreWebView2ContextMenuTarget *target) : target(target), callback(callback) {}

    HRESULT STDMETHODCALLTYPE Invoke(ICoreWebView2ContextMenuItem *sender, IUnknown *args)
    {
        CComHeapPtr<WCHAR> selecttext;
        CHECK_FAILURE(target->get_SelectionText(&selecttext));
        callback(selecttext);
        return S_OK;
    }
};

class CustomItemSelectedEventHandler_2 : public ComImpl<ICoreWebView2CustomItemSelectedEventHandler>
{
    contextmenu_notext_callback_t callback;

public:
    CustomItemSelectedEventHandler_2(contextmenu_notext_callback_t callback) : callback(callback) {}

    HRESULT STDMETHODCALLTYPE Invoke(ICoreWebView2ContextMenuItem *sender, IUnknown *args)
    {
        callback();
        return S_OK;
    }
};

struct WebView2
{
    WebView2(HWND parent, bool);
    HWND parent;
    bool backgroundtransparent;
    CoAsyncTaskWaiter WaitForCreateCoreWebView2Environment, WaitForCreateCoreWebView2Controller;
    CComPtr<ICoreWebView2Controller> m_webViewController;
    CComPtr<ICoreWebView2> m_webView;
    CComPtr<webview2_com_handler> handler;
    std::vector<std::pair<std::wstring, contextmenu_callback_t>> menus;
    std::vector<std::pair<std::wstring, contextmenu_notext_callback_t>> menus_noselect;
    zoomchange_callback_t zoomchange_callback;
    navigating_callback_t navigating_callback;
    webmessage_callback_t webmessage_callback;
    FilesDropped_callback_t FilesDropped_callback;
};
class webview2_com_handler : public ComImpl<ICoreWebView2NavigationStartingEventHandler, ICoreWebView2ZoomFactorChangedEventHandler, ICoreWebView2ContextMenuRequestedEventHandler, ICoreWebView2WebMessageReceivedEventHandler, ICoreWebView2PermissionRequestedEventHandler, ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler, ICoreWebView2CreateCoreWebView2ControllerCompletedHandler>
{
    WebView2 *ref;

public:
    webview2_com_handler(WebView2 *ref) : ref(ref) {}
    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID riid, void **ppvObj)
    {
        if (riid == __uuidof(ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler))
            *ppvObj = static_cast<ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler *>(this);
        else if (riid == __uuidof(ICoreWebView2ZoomFactorChangedEventHandler))
            *ppvObj = static_cast<ICoreWebView2ZoomFactorChangedEventHandler *>(this);
        else if (riid == __uuidof(ICoreWebView2CreateCoreWebView2ControllerCompletedHandler))
            *ppvObj = static_cast<ICoreWebView2CreateCoreWebView2ControllerCompletedHandler *>(this);
        else if (riid == __uuidof(ICoreWebView2WebMessageReceivedEventHandler))
            *ppvObj = static_cast<ICoreWebView2WebMessageReceivedEventHandler *>(this);
        else if (riid == __uuidof(ICoreWebView2ContextMenuRequestedEventHandler))
            *ppvObj = static_cast<ICoreWebView2ContextMenuRequestedEventHandler *>(this);
        else if (riid == __uuidof(ICoreWebView2PermissionRequestedEventHandler))
            *ppvObj = static_cast<ICoreWebView2PermissionRequestedEventHandler *>(this);
        else
            return E_NOINTERFACE;
        AddRef();
        return S_OK;
    }
    // ICoreWebView2NavigationStartingEventHandler
    HRESULT STDMETHODCALLTYPE Invoke(ICoreWebView2 *sender, ICoreWebView2NavigationStartingEventArgs *args)
    {
        auto StartsWith = [](const wchar_t *str, const wchar_t *prefix)
        {
            if (str == nullptr || prefix == nullptr)
            {
                return false;
            }
            while (*prefix)
            {
                if (*str != *prefix)
                {
                    return false;
                }
                str++;
                prefix++;
            }
            return true;
        };
        CComHeapPtr<WCHAR> uri{};
        CHECK_FAILURE(args->get_Uri(&uri));
        if (ref->navigating_callback && (!StartsWith(uri, L"data:text/html")))
            ref->navigating_callback(uri);
        return S_OK;
    }

    // ICoreWebView2CreateCoreWebView2ControllerCompletedHandler
    HRESULT STDMETHODCALLTYPE Invoke(HRESULT result, ICoreWebView2Controller *controller)
    {
        [&]()
        {
            CHECK_FAILURE_NORET(result);
            ::EventRegistrationToken token;
            ref->m_webViewController = controller;
            ref->m_webViewController->put_IsVisible(TRUE);
            ref->m_webViewController->add_ZoomFactorChanged(this, &token);
            [&]()
            {
                if (!ref->backgroundtransparent)
                    return;
                COREWEBVIEW2_COLOR color;
                ZeroMemory(&color, sizeof(color));
                CComPtr<ICoreWebView2Controller2> coreWebView2;
                CHECK_FAILURE_NORET(ref->m_webViewController.QueryInterface(&coreWebView2));
                coreWebView2->put_DefaultBackgroundColor(color);
            }();
            CHECK_FAILURE_NORET(ref->m_webViewController->get_CoreWebView2(&ref->m_webView));
            ref->m_webView->add_WebMessageReceived(this, &token);
            ref->m_webView->add_PermissionRequested(this, &token);
            ref->m_webView->add_NavigationStarting(this, &token);
            [&]()
            {
                CComPtr<ICoreWebView2_11> m_webView2_11;
                CHECK_FAILURE_NORET(ref->m_webView.QueryInterface(&m_webView2_11));
                m_webView2_11->add_ContextMenuRequested(this, &token);
            }();
            CComPtr<ICoreWebView2Settings> settings;
            CHECK_FAILURE_NORET(ref->m_webView->get_Settings(&settings));
            settings->put_AreDevToolsEnabled(TRUE);
            settings->put_AreDefaultContextMenusEnabled(TRUE);
            settings->put_IsStatusBarEnabled(FALSE);
        }();
        ref->WaitForCreateCoreWebView2Controller.Set();
        return S_OK;
    }
    // ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler
    HRESULT STDMETHODCALLTYPE Invoke(HRESULT result, ICoreWebView2Environment *env)
    {
        auto hr = [=]()
        {
            CHECK_FAILURE(result);
            CHECK_FAILURE(env->CreateCoreWebView2Controller(ref->parent, this));
            return S_OK;
        }();
        if (FAILED(hr))
        {
            ref->WaitForCreateCoreWebView2Controller.Set();
        }
        ref->WaitForCreateCoreWebView2Environment.Set();
        return S_OK;
    }
    // ICoreWebView2PermissionRequestedEventHandler
    HRESULT STDMETHODCALLTYPE Invoke(ICoreWebView2 *, ICoreWebView2PermissionRequestedEventArgs *args)
    {
        COREWEBVIEW2_PERMISSION_KIND kind;
        args->get_PermissionKind(&kind);
        if (kind == COREWEBVIEW2_PERMISSION_KIND_CLIPBOARD_READ)
        {
            args->put_State(COREWEBVIEW2_PERMISSION_STATE_ALLOW);
        }
        return S_OK;
    }
    // ICoreWebView2WebMessageReceivedEventHandler
    HRESULT STDMETHODCALLTYPE Invoke(ICoreWebView2 *sender, ICoreWebView2WebMessageReceivedEventArgs *args)
    {
        CComHeapPtr<WCHAR> message{};
        CHECK_FAILURE(args->get_WebMessageAsJson(&message));
        if (wcscmp(L"\"FilesDropped\"", message) == 0)
        {
            CComPtr<ICoreWebView2WebMessageReceivedEventArgs2> args2;
            CHECK_FAILURE(args->QueryInterface(&args2));
            CComPtr<ICoreWebView2ObjectCollectionView> objectsCollection;
            CHECK_FAILURE(args2->get_AdditionalObjects(&objectsCollection));
            if (!objectsCollection)
                return S_OK;
            unsigned int length;
            CHECK_FAILURE(objectsCollection->get_Count(&length));

            for (unsigned int i = 0; i < length; i++)
            {
                CComPtr<IUnknown> object;
                CHECK_FAILURE(objectsCollection->GetValueAtIndex(i, &object));
                // Note that objects can be null.
                if (!object)
                    continue;
                CComPtr<ICoreWebView2File> file;
                CHECK_FAILURE(object.QueryInterface(&file));
                // Add the file to message to be sent back to webview
                CComHeapPtr<WCHAR> path;
                CHECK_FAILURE(file->get_Path(&path));
                if (ref->FilesDropped_callback)
                    ref->FilesDropped_callback(path);
                break;
            }
        }
        else
        {
            if (ref->webmessage_callback)
                ref->webmessage_callback(message);
        }
        return S_OK;
    }
    // ICoreWebView2ZoomFactorChangedEventHandler
    HRESULT STDMETHODCALLTYPE Invoke(ICoreWebView2Controller *sender, IUnknown *args)
    {
        double zoomFactor;
        CHECK_FAILURE(sender->get_ZoomFactor(&zoomFactor));
        if (ref->zoomchange_callback)
            ref->zoomchange_callback(zoomFactor);
        return S_OK;
    }
    // ICoreWebView2ContextMenuRequestedEventHandler
    HRESULT STDMETHODCALLTYPE Invoke(ICoreWebView2 *sender, ICoreWebView2ContextMenuRequestedEventArgs *args)
    {
        CComPtr<ICoreWebView2ContextMenuTarget> target;
        CHECK_FAILURE(args->get_ContextMenuTarget(&target));
        COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND targetKind;
        BOOL hasselection;
        CHECK_FAILURE(target->get_Kind(&targetKind));
        CHECK_FAILURE(target->get_HasSelection(&hasselection));
        if (!(((hasselection && (targetKind == COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND_SELECTED_TEXT))) ||
              (targetKind == COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND_PAGE)))
            return S_OK;
        CComPtr<ICoreWebView2_11> m_webView2_11;
        CHECK_FAILURE(sender->QueryInterface(&m_webView2_11));
        CComPtr<ICoreWebView2Environment> webviewEnvironment;
        CHECK_FAILURE(m_webView2_11->get_Environment(&webviewEnvironment));
        CComPtr<ICoreWebView2Environment9> webviewEnvironment_5;
        CHECK_FAILURE(webviewEnvironment.QueryInterface(&webviewEnvironment_5));
        CComPtr<ICoreWebView2ContextMenuItemCollection> items;
        CHECK_FAILURE(args->get_MenuItems(&items));
        UINT32 itemsCount;
        CHECK_FAILURE(items->get_Count(&itemsCount));
        // Adding a custom context menu item for the page that will display the page's URI.
        UINT idx = 0;
        if (targetKind == COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND_SELECTED_TEXT)
        {
            for (auto &&[label, callback] : ref->menus)
            {
                CComPtr<ICoreWebView2ContextMenuItem> newMenuItem;
                if (label.size())
                {
                    CHECK_FAILURE(webviewEnvironment_5->CreateContextMenuItem(label.c_str(), nullptr, COREWEBVIEW2_CONTEXT_MENU_ITEM_KIND_COMMAND, &newMenuItem));
                    newMenuItem->add_CustomItemSelected(new CustomItemSelectedEventHandler_1(callback, target), nullptr);
                }
                else
                {
                    CHECK_FAILURE(webviewEnvironment_5->CreateContextMenuItem(L"", nullptr, COREWEBVIEW2_CONTEXT_MENU_ITEM_KIND_SEPARATOR, &newMenuItem));
                }
                CHECK_FAILURE(items->InsertValueAtIndex(idx++, newMenuItem));
            }
        }
        else
        {
            for (auto &&[label, callback] : ref->menus_noselect)
            {
                CComPtr<ICoreWebView2ContextMenuItem> newMenuItem;
                if (label.size())
                {
                    CHECK_FAILURE(webviewEnvironment_5->CreateContextMenuItem(label.c_str(), nullptr, COREWEBVIEW2_CONTEXT_MENU_ITEM_KIND_COMMAND, &newMenuItem));
                    newMenuItem->add_CustomItemSelected(new CustomItemSelectedEventHandler_2(callback), nullptr);
                }
                else
                {
                    CHECK_FAILURE(webviewEnvironment_5->CreateContextMenuItem(L"", nullptr, COREWEBVIEW2_CONTEXT_MENU_ITEM_KIND_SEPARATOR, &newMenuItem));
                }
                CHECK_FAILURE(items->InsertValueAtIndex(idx++, newMenuItem));
            }
        }
        return S_OK;
    }
};
WebView2::WebView2(HWND parent, bool backgroundtransparent) : parent(parent), backgroundtransparent(backgroundtransparent)
{
    handler = new webview2_com_handler{this};
    HRESULT hr = CreateCoreWebView2EnvironmentWithOptions(nullptr, nullptr, nullptr, handler);
    if (SUCCEEDED(hr))
    {
        WaitForCreateCoreWebView2Environment.Wait();
        WaitForCreateCoreWebView2Controller.Wait();
    }
    if (!(SUCCEEDED(hr) && m_webView && m_webViewController))
        throw std::exception{};
}

class JSEvalCallback : public ComImpl<ICoreWebView2ExecuteScriptCompletedHandler>
{
public:
    CoAsyncTaskWaiter waitforexec;
    evaljs_callback_t cb;
    JSEvalCallback(evaljs_callback_t cb) : cb(cb) {}
    // ICoreWebView2CreateCoreWebView2ControllerCompletedHandler
    HRESULT STDMETHODCALLTYPE Invoke(HRESULT errorCode, LPCWSTR resultObjectAsJson)
    {
        cb(resultObjectAsJson);
        waitforexec.Set();
        return S_OK;
    }
};
