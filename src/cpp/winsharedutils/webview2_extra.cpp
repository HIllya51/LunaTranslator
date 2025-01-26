
#ifndef WINXP
#include <wrl.h>
#include <wrl/implements.h>
#include <WebView2.h>
using namespace Microsoft::WRL;
DECLARE_API void set_transparent_background(ICoreWebView2Controller *m_host)
{
    COREWEBVIEW2_COLOR color;
    ZeroMemory(&color, sizeof(color));
    CComPtr<ICoreWebView2Controller> m_controller(m_host);
    CComPtr<ICoreWebView2Controller2> coreWebView2;
    CHECK_FAILURE_NORET(m_controller.QueryInterface(&coreWebView2));
    coreWebView2->put_DefaultBackgroundColor(color);
}

DECLARE_API void put_PreferredColorScheme(ICoreWebView2Controller *m_host, COREWEBVIEW2_PREFERRED_COLOR_SCHEME scheme)
{
    CComPtr<ICoreWebView2Controller> m_controller(m_host);
    CComPtr<ICoreWebView2> coreWebView2;
    CHECK_FAILURE_NORET(m_controller->get_CoreWebView2(&coreWebView2));
    CComPtr<ICoreWebView2_13> webView2_13;
    CHECK_FAILURE_NORET(coreWebView2.QueryInterface(&webView2_13));
    CComPtr<ICoreWebView2Profile> profile;
    CHECK_FAILURE_NORET(webView2_13->get_Profile(&profile));
    CHECK_FAILURE_NORET(profile->put_PreferredColorScheme(scheme));
}
DECLARE_API void *add_ZoomFactorChanged(ICoreWebView2Controller *m_host, void (*signal)(double))
{
    EventRegistrationToken *m_zoomFactorChangedToken = new EventRegistrationToken;
    // Register a handler for the ZoomFactorChanged event.
    // This handler just announces the new level of zoom on the window's title bar.
    m_host->add_ZoomFactorChanged(
        Callback<ICoreWebView2ZoomFactorChangedEventHandler>(
            [signal](ICoreWebView2Controller *sender, IUnknown *args) -> HRESULT
            {
                double zoomFactor;
                sender->get_ZoomFactor(&zoomFactor);
                signal(zoomFactor);
                // std::wstring message = L"WebView2APISample (Zoom: " +
                //                        std::to_wstring(int(zoomFactor * 100)) + L"%)";
                // SetWindowText(m_appWindow->GetMainWindow(), message.c_str());
                return S_OK;
            })
            .Get(),
        m_zoomFactorChangedToken);
    return m_zoomFactorChangedToken;
}
DECLARE_API void remove_ZoomFactorChanged(ICoreWebView2Controller *m_host, EventRegistrationToken *token)
{
    m_host->remove_ZoomFactorChanged(*token);
    delete token;
}
DECLARE_API double get_ZoomFactor(ICoreWebView2Controller *m_host)
{
    double zoomFactor;
    m_host->get_ZoomFactor(&zoomFactor);
    return zoomFactor;
}
DECLARE_API void put_ZoomFactor(ICoreWebView2Controller *m_host, double zoomFactor)
{
    m_host->put_ZoomFactor(zoomFactor);
}
// https://github.com/MicrosoftEdge/WebView2Feedback/blob/main/specs/WebMessageObjects.md
DECLARE_API void remove_WebMessageReceived(ICoreWebView2Controller *m_host, EventRegistrationToken *token)
{
    CComPtr<ICoreWebView2Controller> m_controller(m_host);
    CComPtr<ICoreWebView2> m_webView;
    std::unique_ptr<EventRegistrationToken> _{token};
    CHECK_FAILURE_NORET(m_controller->get_CoreWebView2(&m_webView));
    CHECK_FAILURE_NORET(m_webView->remove_WebMessageReceived(*token));
}

DECLARE_API void *add_WebMessageReceived(ICoreWebView2Controller *m_host, void (*callback)(const wchar_t *))
{
    CComPtr<ICoreWebView2Controller> m_controller(m_host);
    [&]()
    {
        CComPtr<ICoreWebView2Controller4> coreWebView4;
        CHECK_FAILURE_NORET(m_controller.QueryInterface(&coreWebView4));
        coreWebView4->put_AllowExternalDrop(true);
    }();
    CComPtr<ICoreWebView2> m_webView;
    EventRegistrationToken *m_webMessageReceivedToken = new EventRegistrationToken;
    [&]()
    {
        CHECK_FAILURE_NORET(m_controller->get_CoreWebView2(&m_webView));
        CHECK_FAILURE_NORET(m_webView->add_WebMessageReceived(
            Callback<ICoreWebView2WebMessageReceivedEventHandler>(
                [=](ICoreWebView2 *sender, ICoreWebView2WebMessageReceivedEventArgs *args) noexcept
                {
                    CComHeapPtr<WCHAR> message;
                    CHECK_FAILURE(args->TryGetWebMessageAsString(&message));
                    if (wcscmp(L"FilesDropped", message) != 0)
                        return S_OK;
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
                        callback(path);
                        break;
                    }
                    return S_OK;
                })
                .Get(),
            m_webMessageReceivedToken));
    }();
    return m_webMessageReceivedToken;
}

struct contextcallbackdatas
{
    EventRegistrationToken contextMenuRequestedToken;
    std::vector<std::pair<std::wstring, void (*)(const wchar_t *)>> menus;
    std::vector<std::pair<std::wstring, void (*)()>> menus_noselect;
};
// https://learn.microsoft.com/zh-cn/microsoft-edge/webview2/how-to/context-menus?tabs=cpp
// https://learn.microsoft.com/en-us/microsoft-edge/webview2/reference/win32/icorewebview2_11?view=webview2-1.0.2849.39
DECLARE_API void add_menu_list(contextcallbackdatas *ptr, int index, const wchar_t *label, void (*callback)(const wchar_t *))
{
    if (!ptr)
        return;
    ptr->menus.insert(ptr->menus.begin() + index, std::make_pair(label, callback));
}
DECLARE_API void add_menu_list_noselect(contextcallbackdatas *ptr, int index, const wchar_t *label, void (*callback)())
{
    if (!ptr)
        return;
    ptr->menus_noselect.insert(ptr->menus_noselect.begin() + index, std::make_pair(label, callback));
}
DECLARE_API void *add_ContextMenuRequested(ICoreWebView2Controller *m_host)
{
    contextcallbackdatas *data = new contextcallbackdatas;
    [=]()
    {
        CComPtr<ICoreWebView2Controller> m_controller(m_host);
        CComPtr<ICoreWebView2> m_webView;
        CHECK_FAILURE(m_controller->get_CoreWebView2(&m_webView));
        CComPtr<ICoreWebView2_11> m_webView2_11;
        CHECK_FAILURE(m_webView.QueryInterface(&m_webView2_11));
        m_webView2_11->add_ContextMenuRequested(
            Callback<ICoreWebView2ContextMenuRequestedEventHandler>(
                [=](
                    ICoreWebView2 *sender,
                    ICoreWebView2ContextMenuRequestedEventArgs *args)
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
                        for (auto &&[label, callback] : data->menus)
                        {
                            CComPtr<ICoreWebView2ContextMenuItem> newMenuItem;
                            if (label.size())
                            {
                                CHECK_FAILURE(webviewEnvironment_5->CreateContextMenuItem(label.c_str(), nullptr, COREWEBVIEW2_CONTEXT_MENU_ITEM_KIND_COMMAND, &newMenuItem));
                                newMenuItem->add_CustomItemSelected(
                                    Callback<ICoreWebView2CustomItemSelectedEventHandler>(
                                        [=, &callback](ICoreWebView2ContextMenuItem *sender, IUnknown *args)
                                        {
                                            CComHeapPtr<WCHAR> selecttext;
                                            CHECK_FAILURE(target->get_SelectionText(&selecttext));
                                            callback(selecttext);
                                            return S_OK;
                                        })
                                        .Get(),
                                    nullptr);
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
                        for (auto &&[label, callback] : data->menus_noselect)
                        {
                            CComPtr<ICoreWebView2ContextMenuItem> newMenuItem;
                            if (label.size())
                            {
                                CHECK_FAILURE(webviewEnvironment_5->CreateContextMenuItem(label.c_str(), nullptr, COREWEBVIEW2_CONTEXT_MENU_ITEM_KIND_COMMAND, &newMenuItem));
                                newMenuItem->add_CustomItemSelected(
                                    Callback<ICoreWebView2CustomItemSelectedEventHandler>(
                                        [=, &callback](ICoreWebView2ContextMenuItem *sender, IUnknown *args)
                                        {
                                            callback();
                                            return S_OK;
                                        })
                                        .Get(),
                                    nullptr);
                            }
                            else
                            {
                                CHECK_FAILURE(webviewEnvironment_5->CreateContextMenuItem(L"", nullptr, COREWEBVIEW2_CONTEXT_MENU_ITEM_KIND_SEPARATOR, &newMenuItem));
                            }
                            CHECK_FAILURE(items->InsertValueAtIndex(idx++, newMenuItem));
                        }
                    }
                    return S_OK;
                })
                .Get(),
            &data->contextMenuRequestedToken);
        return S_OK;
    }();
    return data;
}
DECLARE_API void remove_ContextMenuRequested(ICoreWebView2Controller *m_host, contextcallbackdatas *data)
{
    CComPtr<ICoreWebView2Controller> m_controller(m_host);
    CComPtr<ICoreWebView2> m_webView;
    std::unique_ptr<contextcallbackdatas> _{data};
    CHECK_FAILURE_NORET(m_controller->get_CoreWebView2(&m_webView));
    CComPtr<ICoreWebView2_11> m_webView2_11;
    CHECK_FAILURE_NORET(m_webView.QueryInterface(&m_webView2_11));
    CHECK_FAILURE_NORET(m_webView2_11->remove_ContextMenuRequested(data->contextMenuRequestedToken));
}
DECLARE_API void get_webview_html(ICoreWebView2Controller *m_host, void (*cb)(LPCWSTR), LPCWSTR elementid)
{
    CComPtr<ICoreWebView2Controller> m_controller(m_host);
    CComPtr<ICoreWebView2> m_webView;
    HANDLE asyncMethodCompleteEvent = CreateEvent(nullptr, false, false, nullptr);

    CHECK_FAILURE_NORET(m_controller->get_CoreWebView2(&m_webView));
    CHECK_FAILURE_NORET(
        m_webView->ExecuteScript(
            elementid ? ((std::wstring(L"document.getElementById('") + std::wstring(elementid) + std::wstring(L"').innerHTML")).c_str()) : L"document.documentElement.outerHTML",
            Callback<ICoreWebView2ExecuteScriptCompletedHandler>(
                [=](HRESULT errorCode, LPCWSTR resultObjectAsJson)
                {
                    SetEvent(asyncMethodCompleteEvent);
                    cb(resultObjectAsJson);
                    return S_OK;
                })
                .Get()));
    DWORD handleIndex = 0;
    CoWaitForMultipleHandles(COWAIT_DISPATCH_WINDOW_MESSAGES | COWAIT_DISPATCH_CALLS | COWAIT_INPUTAVAILABLE,
                             INFINITE, 1, &asyncMethodCompleteEvent, &handleIndex);
    CloseHandle(asyncMethodCompleteEvent);
}

DECLARE_API void detect_webview2_version(LPCWSTR dir, void (*cb)(LPCWSTR))
{
    CComHeapPtr<WCHAR> version;
    CHECK_FAILURE_NORET(GetAvailableCoreWebView2BrowserVersionString(dir, &version));
    cb(version);
}
#else
struct EventRegistrationToken;
struct contextcallbackdatas;
struct ICoreWebView2Controller;
enum COREWEBVIEW2_PREFERRED_COLOR_SCHEME
{
};
DECLARE_API void set_transparent_background(ICoreWebView2Controller *m_host) {}
DECLARE_API void put_PreferredColorScheme(ICoreWebView2Controller *m_host, COREWEBVIEW2_PREFERRED_COLOR_SCHEME scheme) {}
DECLARE_API void *add_ZoomFactorChanged(ICoreWebView2Controller *m_host, void (*signal)(double)) { return nullptr; }
DECLARE_API void remove_ZoomFactorChanged(ICoreWebView2Controller *m_host, EventRegistrationToken *token) {}
DECLARE_API double get_ZoomFactor(ICoreWebView2Controller *m_host) { return 1.0f; };
DECLARE_API void put_ZoomFactor(ICoreWebView2Controller *m_host, double zoomFactor){};
DECLARE_API void *add_WebMessageReceived(ICoreWebView2Controller *m_host, void (*callback)(const wchar_t *)){return nullptr;};
DECLARE_API void remove_WebMessageReceived(ICoreWebView2Controller *m_host, EventRegistrationToken *token){};
DECLARE_API void add_menu_list(contextcallbackdatas *ptr, int index, const wchar_t *label, void (*callback)(const wchar_t *)) {};
DECLARE_API void add_menu_list_noselect(contextcallbackdatas *ptr, int index, const wchar_t *label, void (*callback)()) {};
DECLARE_API void *add_ContextMenuRequested(ICoreWebView2Controller *m_host) { return nullptr; };
DECLARE_API void remove_ContextMenuRequested(ICoreWebView2Controller *m_host, contextcallbackdatas *data) {};
DECLARE_API void get_webview_html(ICoreWebView2Controller *m_host, void (*cb)(LPCWSTR), LPCWSTR elementid) {};
DECLARE_API void detect_webview2_version(LPCWSTR dir, void (*cb)(LPCWSTR)) {};
#endif