#include "webview.hpp"

#ifndef WINXP
// EdgeHTML headers and libs
#include <objbase.h>
#include <winrt/Windows.UI.h>
#include <winrt/Windows.Foundation.h>
#include <winrt/Windows.Foundation.Collections.h>
#include <winrt/Windows.Web.UI.Interop.h>
using namespace winrt;
using namespace Windows::Foundation;
using namespace Windows::Web::UI;
using namespace Windows::Web::UI::Interop;

typedef void (*web_notify_callback_t)(LPCWSTR);

class EdgeHtml : public AbstractWebView, public NativeMenuHelper
{
  WebViewControl m_webview = nullptr;
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

  EdgeHtml(HWND, bool backgroundtransparent);
  virtual double get_ZoomFactor() override;
  virtual void put_ZoomFactor(double zoomFactor) override;
  VIRTUAL_FUNCTIONS_IMPL;
  ~EdgeHtml();
};
#endif