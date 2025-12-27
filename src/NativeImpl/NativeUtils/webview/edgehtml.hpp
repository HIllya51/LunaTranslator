#include "webview.hpp"

#ifndef WINXP
// EdgeHTML headers and libs
#include <roapi.h>
#include <windows.ui.h>
#include <windows.foundation.h>
#include <windows.foundation.collections.h>
#include <windows.web.ui.interop.h>
#include "../winrt/hstring.hpp"
using ABI::Windows::Foundation::ActivateInstance;
using ABI::Windows::Foundation::GetActivationFactory;
using ABI::Windows::Foundation::IAsyncOperation;
using ABI::Windows::Foundation::IAsyncOperationCompletedHandler;
using ABI::Windows::Foundation::IPropertyValueStatics;
using ABI::Windows::Foundation::ITypedEventHandler;
using ABI::Windows::Foundation::IUriRuntimeClass;
using ABI::Windows::Foundation::IUriRuntimeClassFactory;
using ABI::Windows::Foundation::Rect;
using ABI::Windows::Foundation::Collections::IIterable;
using ABI::Windows::Foundation::Collections::IVector;
using ABI::Windows::Foundation::Collections::IVectorView;
using ABI::Windows::UI::Color;
using ABI::Windows::UI::IColorsStatics;
using ABI::Windows::Web::UI::IWebViewControl;
using ABI::Windows::Web::UI::IWebViewControl2;
using ABI::Windows::Web::UI::IWebViewControlNavigationStartingEventArgs;
using ABI::Windows::Web::UI::IWebViewControlScriptNotifyEventArgs;
using ABI::Windows::Web::UI::IWebViewControlSettings;
using ABI::Windows::Web::UI::WebViewControlNavigationStartingEventArgs;
using ABI::Windows::Web::UI::WebViewControlScriptNotifyEventArgs;
using ABI::Windows::Web::UI::Interop::IWebViewControlProcess;
using ABI::Windows::Web::UI::Interop::IWebViewControlSite;
using ABI::Windows::Web::UI::Interop::WebViewControl;
using ABI::Windows::Web::UI::Interop::WebViewControlProcess;

typedef void (*web_notify_callback_t)(LPCWSTR);

class EdgeHtml;

class EdgeHtmlComHandler : public ComImpl<ITypedEventHandler<IWebViewControl *, WebViewControlScriptNotifyEventArgs *>, ITypedEventHandler<IWebViewControl *, WebViewControlNavigationStartingEventArgs *>>
{
  EdgeHtml *ref;

public:
  EdgeHtmlComHandler(EdgeHtml *ref) : ref(ref) {}
  //__FITypedEventHandler_2_Windows__CWeb__CUI__CIWebViewControl_Windows__CWeb__CUI__CWebViewControlNavigationStartingEventArgs
  virtual HRESULT STDMETHODCALLTYPE Invoke(IWebViewControl *sender, IWebViewControlNavigationStartingEventArgs *args) override;
  //__FITypedEventHandler_2_Windows__CWeb__CUI__CIWebViewControl_Windows__CWeb__CUI__CWebViewControlScriptNotifyEventArgs
  virtual HRESULT STDMETHODCALLTYPE Invoke(IWebViewControl *sender, IWebViewControlScriptNotifyEventArgs *args) override;
};

class EdgeHtml : public AbstractWebView, public NativeMenuHelper
{
  friend class EdgeHtmlComHandler;
  CComPtr<EdgeHtmlComHandler> handler;
  CComPtr<IWebViewControlSite> controlsite = nullptr;
  CComPtr<IWebViewControl> control = nullptr;
  CComPtr<IWebViewControl2> control2 = nullptr;
  HWND parent;
  std::wstring InitializeScript = LR"(
            window.LUNAJSObject={};
            document.addEventListener('contextmenu', function(e) {
          e.preventDefault();
          const selection = window.getSelection();
          const selectedText = selection.toString().trim();
          window.external.notify("__contextmenu__helper"+selectedText);
        }, false);)";

public:
  web_notify_callback_t callback;

  EdgeHtml(HWND);
  HRESULT init(bool backgroundtransparent);
  virtual double get_ZoomFactor() override;
  virtual void put_ZoomFactor(double zoomFactor) override;
  VIRTUAL_FUNCTIONS_IMPL;
  ~EdgeHtml();
};
#endif