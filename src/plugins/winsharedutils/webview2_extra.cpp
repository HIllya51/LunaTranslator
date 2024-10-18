#include "define.h"

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

DECLARE void set_transparent_background(void* m_host){
    COREWEBVIEW2_COLOR color;
    ZeroMemory(&color,sizeof(color));
    wil::com_ptr<ICoreWebView2Controller> m_controller(reinterpret_cast<ICoreWebView2Controller *>(m_host));
    wil::com_ptr<ICoreWebView2Controller2> coreWebView2 =
                m_controller.try_query<ICoreWebView2Controller2>();
    if(coreWebView2){
        coreWebView2->put_DefaultBackgroundColor(color);
    }
}

DECLARE HRESULT put_PreferredColorScheme(void *m_host, COREWEBVIEW2_PREFERRED_COLOR_SCHEME scheme)
{

    wil::com_ptr<ICoreWebView2Controller> m_controller(reinterpret_cast<ICoreWebView2Controller *>(m_host));
    wil::com_ptr<ICoreWebView2> coreWebView2;
    CHECK_FAILURE(m_controller->get_CoreWebView2(&coreWebView2));
    auto webView2_13 = coreWebView2.try_query<ICoreWebView2_13>();
    if (webView2_13)
    {
        wil::com_ptr<ICoreWebView2Profile> profile;
        CHECK_FAILURE(webView2_13->get_Profile(&profile));
        CHECK_FAILURE(profile->put_PreferredColorScheme(scheme));
    }
    return S_FALSE;
}
DECLARE void *add_ZoomFactorChanged(void *m_host, void (*signal)(double))
{
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
}
DECLARE void remove_ZoomFactorChanged(void *m_host, void *m_zoomFactorChangedToken)
{

    reinterpret_cast<ICoreWebView2Controller *>(m_host)->remove_ZoomFactorChanged(*reinterpret_cast<EventRegistrationToken *>(m_zoomFactorChangedToken));
    delete m_zoomFactorChangedToken;
}
DECLARE double get_ZoomFactor(void *m_host)
{
    double zoomFactor;
    reinterpret_cast<ICoreWebView2Controller *>(m_host)->get_ZoomFactor(&zoomFactor);
    return zoomFactor;
}
DECLARE void put_ZoomFactor(void *m_host, double zoomFactor)
{
    reinterpret_cast<ICoreWebView2Controller *>(m_host)->put_ZoomFactor(zoomFactor);
}