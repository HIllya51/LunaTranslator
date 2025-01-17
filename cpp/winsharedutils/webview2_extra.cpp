#ifndef WINXP

#include <wrl.h>
#include <wil/com.h>
#include <wil/result.h>
#include <wil/com.h>
#include <wrl/implements.h>
using namespace Microsoft::WRL;
#include <WebView2.h>
#else
typedef int COREWEBVIEW2_PREFERRED_COLOR_SCHEME;
typedef int EventRegistrationToken;
typedef int ICoreWebView2Controller;
#endif
DECLARE_API void set_transparent_background(ICoreWebView2Controller *m_host)
{
#ifndef WINXP
    COREWEBVIEW2_COLOR color;
    ZeroMemory(&color, sizeof(color));
    wil::com_ptr<ICoreWebView2Controller> m_controller(m_host);
    wil::com_ptr<ICoreWebView2Controller2> coreWebView2 =
        m_controller.try_query<ICoreWebView2Controller2>();
    if (coreWebView2)
    {
        coreWebView2->put_DefaultBackgroundColor(color);
    }
#endif
}

DECLARE_API void put_PreferredColorScheme(ICoreWebView2Controller *m_host, COREWEBVIEW2_PREFERRED_COLOR_SCHEME scheme)
{
#ifndef WINXP
    wil::com_ptr<ICoreWebView2Controller> m_controller(m_host);
    wil::com_ptr<ICoreWebView2> coreWebView2;
    [&]()
    {
        CHECK_FAILURE(m_controller->get_CoreWebView2(&coreWebView2));
        auto webView2_13 = coreWebView2.try_query<ICoreWebView2_13>();
        if (webView2_13)
        {
            wil::com_ptr<ICoreWebView2Profile> profile;
            CHECK_FAILURE(webView2_13->get_Profile(&profile));
            CHECK_FAILURE(profile->put_PreferredColorScheme(scheme));
        }
        return S_OK;
    }();
#endif
}
DECLARE_API void *add_ZoomFactorChanged(ICoreWebView2Controller *m_host, void (*signal)(double))
{
#ifndef WINXP
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
#else
    return NULL;
#endif
}
DECLARE_API void remove_ZoomFactorChanged(ICoreWebView2Controller *m_host, EventRegistrationToken *token)
{
#ifndef WINXP
    m_host->remove_ZoomFactorChanged(*token);
    delete token;
#endif
}
DECLARE_API double get_ZoomFactor(ICoreWebView2Controller *m_host)
{
#ifndef WINXP
    double zoomFactor;
    m_host->get_ZoomFactor(&zoomFactor);
    return zoomFactor;
#else
    return 1;
#endif
}
DECLARE_API void put_ZoomFactor(ICoreWebView2Controller *m_host, double zoomFactor)
{
#ifndef WINXP
    m_host->put_ZoomFactor(zoomFactor);
#endif
}
// https://github.com/MicrosoftEdge/WebView2Feedback/blob/main/specs/WebMessageObjects.md
DECLARE_API void remove_WebMessageReceived(ICoreWebView2Controller *m_host, EventRegistrationToken *token)
{
#ifndef WINXP
    wil::com_ptr<ICoreWebView2Controller> m_controller(m_host);
    wil::com_ptr<ICoreWebView2> m_webView;
    [&]()
    {
        CHECK_FAILURE(m_controller->get_CoreWebView2(&m_webView));
        CHECK_FAILURE(m_webView->remove_WebMessageReceived(*token));
        return S_OK;
    }();
    delete token;
#endif
}

DECLARE_API void *add_WebMessageReceived(ICoreWebView2Controller *m_host, void (*callback)(const wchar_t *))
{
#ifndef WINXP
    wil::com_ptr<ICoreWebView2Controller> m_controller(m_host);
    wil::com_ptr<ICoreWebView2Controller4> coreWebView4 =
        m_controller.try_query<ICoreWebView2Controller4>();
    if (coreWebView4)
    {
        coreWebView4->put_AllowExternalDrop(true);
    }
    wil::com_ptr<ICoreWebView2> m_webView;
    EventRegistrationToken *m_webMessageReceivedToken = new EventRegistrationToken;
    [&]()
    {
        CHECK_FAILURE(m_controller->get_CoreWebView2(&m_webView));
        CHECK_FAILURE(m_webView->add_WebMessageReceived(
            Callback<ICoreWebView2WebMessageReceivedEventHandler>(
                [=](ICoreWebView2 *sender, ICoreWebView2WebMessageReceivedEventArgs *args) noexcept
                {
                    wil::unique_cotaskmem_string message;
                    CHECK_FAILURE(args->TryGetWebMessageAsString(&message));
                    do
                    {
                        if (std::wstring(L"FilesDropped") != message.get())
                            break;
                        wil::com_ptr<ICoreWebView2WebMessageReceivedEventArgs2> args2 =
                            wil::com_ptr<ICoreWebView2WebMessageReceivedEventArgs>(args)
                                .query<ICoreWebView2WebMessageReceivedEventArgs2>();
                        if (!args2)
                            break;
                        wil::com_ptr<ICoreWebView2ObjectCollectionView> objectsCollection;
                        CHECK_FAILURE(args2->get_AdditionalObjects(&objectsCollection));
                        if (!objectsCollection)
                            break;
                        unsigned int length;
                        CHECK_FAILURE(objectsCollection->get_Count(&length));
                        std::vector<std::wstring> paths;

                        for (unsigned int i = 0; i < length; i++)
                        {
                            wil::com_ptr<IUnknown> object;
                            CHECK_FAILURE(objectsCollection->GetValueAtIndex(i, &object));
                            // Note that objects can be null.
                            if (!object)
                                continue;
                            wil::com_ptr<ICoreWebView2File> file = object.query<ICoreWebView2File>();
                            if (!file)
                                continue;
                            // Add the file to message to be sent back to webview
                            wil::unique_cotaskmem_string path;
                            CHECK_FAILURE(file->get_Path(&path));
                            paths.push_back(path.get());
                        }
                        // ProcessPaths(paths);
                        if (!paths.size())
                            break;
                        callback(paths[0].c_str());

                    } while (0);
                    return S_OK;
                })
                .Get(),
            m_webMessageReceivedToken));
        return S_OK;
    }();
    return m_webMessageReceivedToken;
#else
    return NULL;
#endif
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
#ifndef WINXP
    contextcallbackdatas *data = new contextcallbackdatas;
    [=]()
    {
        wil::com_ptr<ICoreWebView2Controller> m_controller(m_host);
        wil::com_ptr<ICoreWebView2> m_webView;
        CHECK_FAILURE(m_controller->get_CoreWebView2(&m_webView));
        auto m_webView2_11 = m_webView.try_query<ICoreWebView2_11>();
        if (!m_webView2_11)
            return S_OK;
        m_webView2_11->add_ContextMenuRequested(
            Callback<ICoreWebView2ContextMenuRequestedEventHandler>(
                [=](
                    ICoreWebView2 *sender,
                    ICoreWebView2ContextMenuRequestedEventArgs *args)
                {
                    wil::com_ptr<ICoreWebView2ContextMenuTarget> target;
                    CHECK_FAILURE(args->get_ContextMenuTarget(&target));
                    COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND targetKind;
                    BOOL hasselection;
                    CHECK_FAILURE(target->get_Kind(&targetKind));
                    CHECK_FAILURE(target->get_HasSelection(&hasselection));
                    if (!(((hasselection && (targetKind == COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND_SELECTED_TEXT))) ||
                          (targetKind == COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND_PAGE)))
                        return S_OK;
                    wil::com_ptr<ICoreWebView2_11> m_webView2_11;
                    CHECK_FAILURE(sender->QueryInterface(IID_PPV_ARGS(&m_webView2_11)));

                    wil::com_ptr<ICoreWebView2Environment> webviewEnvironment;
                    CHECK_FAILURE(m_webView2_11->get_Environment(&webviewEnvironment));
                    auto webviewEnvironment_5 = webviewEnvironment.try_query<ICoreWebView2Environment9>();
                    if (!webviewEnvironment_5)
                        return S_OK;
                    wil::com_ptr<ICoreWebView2ContextMenuItemCollection> items;
                    CHECK_FAILURE(args->get_MenuItems(&items));
                    UINT32 itemsCount;
                    CHECK_FAILURE(items->get_Count(&itemsCount));
                    // Adding a custom context menu item for the page that will display the page's URI.
                    UINT idx = 0;
                    if (targetKind == COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND_SELECTED_TEXT)
                    {
                        for (auto &&[label, callback] : data->menus)
                        {
                            wil::com_ptr<ICoreWebView2ContextMenuItem> newMenuItem;
                            if (label.size())
                            {
                                CHECK_FAILURE(webviewEnvironment_5->CreateContextMenuItem(
                                    label.c_str(),
                                    nullptr,
                                    COREWEBVIEW2_CONTEXT_MENU_ITEM_KIND_COMMAND, &newMenuItem));
                                newMenuItem->add_CustomItemSelected(
                                    Callback<ICoreWebView2CustomItemSelectedEventHandler>(
                                        [=, &callback](
                                            ICoreWebView2ContextMenuItem *sender,
                                            IUnknown *args)
                                        {
                                            wil::unique_cotaskmem_string selecttext;
                                            CHECK_FAILURE(target->get_SelectionText(&selecttext));
                                            callback(selecttext.get());
                                            return S_OK;
                                        })
                                        .Get(),
                                    nullptr);
                            }
                            else
                            {
                                CHECK_FAILURE(webviewEnvironment_5->CreateContextMenuItem(
                                    L"",
                                    nullptr,
                                    COREWEBVIEW2_CONTEXT_MENU_ITEM_KIND_SEPARATOR, &newMenuItem));
                            }
                            CHECK_FAILURE(items->InsertValueAtIndex(idx++, newMenuItem.get()));
                        }
                    }
                    else
                    {
                        for (auto &&[label, callback] : data->menus_noselect)
                        {
                            wil::com_ptr<ICoreWebView2ContextMenuItem> newMenuItem;
                            if (label.size())
                            {
                                CHECK_FAILURE(webviewEnvironment_5->CreateContextMenuItem(
                                    label.c_str(),
                                    nullptr,
                                    COREWEBVIEW2_CONTEXT_MENU_ITEM_KIND_COMMAND, &newMenuItem));
                                newMenuItem->add_CustomItemSelected(
                                    Callback<ICoreWebView2CustomItemSelectedEventHandler>(
                                        [=, &callback](
                                            ICoreWebView2ContextMenuItem *sender,
                                            IUnknown *args)
                                        {
                                            callback();
                                            return S_OK;
                                        })
                                        .Get(),
                                    nullptr);
                            }
                            else
                            {
                                CHECK_FAILURE(webviewEnvironment_5->CreateContextMenuItem(
                                    L"",
                                    nullptr,
                                    COREWEBVIEW2_CONTEXT_MENU_ITEM_KIND_SEPARATOR, &newMenuItem));
                            }
                            CHECK_FAILURE(items->InsertValueAtIndex(idx++, newMenuItem.get()));
                        }
                    }
                    return S_OK;
                })
                .Get(),
            &data->contextMenuRequestedToken);
        return S_OK;
    }();
    return data;
#else
    return NULL;
#endif
}
DECLARE_API void remove_ContextMenuRequested(ICoreWebView2Controller *m_host, contextcallbackdatas *data)
{
#ifndef WINXP
    wil::com_ptr<ICoreWebView2Controller> m_controller(m_host);
    wil::com_ptr<ICoreWebView2> m_webView;
    [&]()
    {
        CHECK_FAILURE(m_controller->get_CoreWebView2(&m_webView));
        auto m_webView2_11 = m_webView.try_query<ICoreWebView2_11>();
        if (!m_webView2_11)
            return S_OK;
        CHECK_FAILURE(m_webView2_11->remove_ContextMenuRequested(data->contextMenuRequestedToken));
        return S_OK;
    }();
    delete data;
#endif
}
DECLARE_API void get_webview_html(ICoreWebView2Controller *m_host, void (*cb)(LPCWSTR), LPCWSTR elementid)
{
#ifndef WINXP
    wil::com_ptr<ICoreWebView2Controller> m_controller(m_host);
    wil::com_ptr<ICoreWebView2> m_webView;
    wil::unique_handle asyncMethodCompleteEvent(CreateEvent(nullptr, false, false, nullptr));

    CHECK_FAILURE_NORET(m_controller->get_CoreWebView2(&m_webView));
    CHECK_FAILURE_NORET(
        m_webView->ExecuteScript(
            elementid ? ((std::wstring(L"document.getElementById('") + std::wstring(elementid) + std::wstring(L"').innerHTML")).c_str()) : L"document.documentElement.outerHTML",
            Callback<ICoreWebView2ExecuteScriptCompletedHandler>(
                [=, asyncMethodCompleteEventHandle = asyncMethodCompleteEvent.get()](HRESULT errorCode, LPCWSTR resultObjectAsJson)
                {
                    SetEvent(asyncMethodCompleteEventHandle);
                    cb(resultObjectAsJson);
                    return S_OK;
                })
                .Get()));
    DWORD handleIndex = 0;
    CoWaitForMultipleHandles(COWAIT_DISPATCH_WINDOW_MESSAGES | COWAIT_DISPATCH_CALLS | COWAIT_INPUTAVAILABLE,
                             INFINITE, 1, asyncMethodCompleteEvent.addressof(), &handleIndex);
#endif
}
