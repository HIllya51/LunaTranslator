#ifndef WINXP

#include <wrl.h>
#include <wil/com.h>
#include <wil/result.h>
#include <wil/com.h>
#include <wrl/implements.h>
using namespace Microsoft::WRL;
#include <WebView2.h>
#define CHECK_FAILURE(x) \
    if (FAILED((x)))     \
        return x;

#endif
DECLARE_API void set_transparent_background(void *m_host)
{
#ifndef WINXP
    COREWEBVIEW2_COLOR color;
    ZeroMemory(&color, sizeof(color));
    wil::com_ptr<ICoreWebView2Controller> m_controller(reinterpret_cast<ICoreWebView2Controller *>(m_host));
    wil::com_ptr<ICoreWebView2Controller2> coreWebView2 =
        m_controller.try_query<ICoreWebView2Controller2>();
    if (coreWebView2)
    {
        coreWebView2->put_DefaultBackgroundColor(color);
    }
#endif
}

#ifndef WINXP
DECLARE_API void put_PreferredColorScheme(void *m_host, COREWEBVIEW2_PREFERRED_COLOR_SCHEME scheme)
{
    wil::com_ptr<ICoreWebView2Controller> m_controller(reinterpret_cast<ICoreWebView2Controller *>(m_host));
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
}
#else
DECLARE_API void put_PreferredColorScheme(void *m_host, int scheme)
{
}
#endif
DECLARE_API void *add_ZoomFactorChanged(void *m_host, void (*signal)(double))
{
#ifndef WINXP
    EventRegistrationToken *m_zoomFactorChangedToken = new EventRegistrationToken;
    // Register a handler for the ZoomFactorChanged event.
    // This handler just announces the new level of zoom on the window's title bar.
    reinterpret_cast<ICoreWebView2Controller *>(m_host)->add_ZoomFactorChanged(
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
DECLARE_API void remove_ZoomFactorChanged(void *m_host, void *m_zoomFactorChangedToken)
{
#ifndef WINXP
    auto token = reinterpret_cast<EventRegistrationToken *>(m_zoomFactorChangedToken);
    reinterpret_cast<ICoreWebView2Controller *>(m_host)->remove_ZoomFactorChanged(*token);
    delete token;
#endif
}
DECLARE_API double get_ZoomFactor(void *m_host)
{
#ifndef WINXP
    double zoomFactor;
    reinterpret_cast<ICoreWebView2Controller *>(m_host)->get_ZoomFactor(&zoomFactor);
    return zoomFactor;
#else
    return 1;
#endif
}
DECLARE_API void put_ZoomFactor(void *m_host, double zoomFactor)
{
#ifndef WINXP
    reinterpret_cast<ICoreWebView2Controller *>(m_host)->put_ZoomFactor(zoomFactor);
#endif
}
// https://github.com/MicrosoftEdge/WebView2Feedback/blob/main/specs/WebMessageObjects.md
DECLARE_API void remove_WebMessageReceived(void *m_host, void *m_webMessageReceivedToken)
{
#ifndef WINXP
    auto token = reinterpret_cast<EventRegistrationToken *>(m_webMessageReceivedToken);
    wil::com_ptr<ICoreWebView2Controller> m_controller(reinterpret_cast<ICoreWebView2Controller *>(m_host));
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

DECLARE_API void *add_WebMessageReceived(void *m_host, void (*callback)(const wchar_t *))
{
#ifndef WINXP
    wil::com_ptr<ICoreWebView2Controller> m_controller(reinterpret_cast<ICoreWebView2Controller *>(m_host));
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
                    if (std::wstring(L"FilesDropped") == message.get())
                    {
                        wil::com_ptr<ICoreWebView2WebMessageReceivedEventArgs2> args2 =
                            wil::com_ptr<ICoreWebView2WebMessageReceivedEventArgs>(args)
                                .query<ICoreWebView2WebMessageReceivedEventArgs2>();
                        if (args2)
                        {
                            wil::com_ptr<ICoreWebView2ObjectCollectionView>
                                objectsCollection;
                            CHECK_FAILURE(args2->get_AdditionalObjects(&objectsCollection));
                            unsigned int length;
                            CHECK_FAILURE(objectsCollection->get_Count(&length));
                            std::vector<std::wstring> paths;

                            for (unsigned int i = 0; i < length; i++)
                            {
                                wil::com_ptr<IUnknown> object;
                                CHECK_FAILURE(objectsCollection->GetValueAtIndex(i, &object));
                                // Note that objects can be null.
                                if (object)
                                {
                                    wil::com_ptr<ICoreWebView2File> file =
                                        object.query<ICoreWebView2File>();
                                    if (file)
                                    {
                                        // Add the file to message to be sent back to webview
                                        wil::unique_cotaskmem_string path;
                                        CHECK_FAILURE(file->get_Path(&path));
                                        paths.push_back(path.get());
                                    }
                                }
                            }
                            // ProcessPaths(paths);
                            if (paths.size())
                            {
                                callback(paths[0].c_str());
                            }
                        }
                    }
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
