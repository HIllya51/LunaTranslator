#include "define.h"

#include <wrl.h>
#include <wil/com.h>
#include <wil/result.h>
#include <wil/com.h>
#include <wrl/implements.h>
using namespace Microsoft::WRL;
#include <WebView2.h>

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