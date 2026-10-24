#include "edgehtml.hpp"
#include "../winrt/await.hpp"

namespace
{
    struct EdgeHtmlStringIterator
        : ComImpl<ABI::Windows::Foundation::Collections::IIterator<HSTRING>>
    {
        HSTRING hstr = nullptr;
        bool done = false;
        ~EdgeHtmlStringIterator()
        {
            if (hstr)
                WindowsDeleteString(hstr);
        }
        HRESULT STDMETHODCALLTYPE GetIids(ULONG *iidCount, IID **iids) override
        {
            *iidCount = 0;
            *iids = nullptr;
            return S_OK;
        }
        HRESULT STDMETHODCALLTYPE GetRuntimeClassName(HSTRING *className) override
        {
            *className = nullptr;
            return E_NOTIMPL;
        }
        HRESULT STDMETHODCALLTYPE GetTrustLevel(TrustLevel *trustLevel) override
        {
            *trustLevel = BaseTrust;
            return S_OK;
        }
        HRESULT STDMETHODCALLTYPE get_Current(HSTRING *current) override
        {
            if (done || !hstr)
                return E_BOUNDS;
            return WindowsDuplicateString(hstr, current);
        }
        HRESULT STDMETHODCALLTYPE get_HasCurrent(boolean *hasCurrent) override
        {
            *hasCurrent = (!done && hstr) ? TRUE : FALSE;
            return S_OK;
        }
        HRESULT STDMETHODCALLTYPE MoveNext(boolean *hasCurrent) override
        {
            done = true;
            return get_HasCurrent(hasCurrent);
        }
        HRESULT STDMETHODCALLTYPE GetMany(
            UINT32 capacity, HSTRING *value, UINT32 *actual) override
        {
            *actual = 0;
            if (capacity && !done && hstr)
            {
                auto hr = WindowsDuplicateString(hstr, value);
                if (FAILED(hr))
                    return hr;
                *actual = 1;
                done = true;
            }
            return S_OK;
        }
    };
    struct EdgeHtmlStringIterable
        : ComImpl<ABI::Windows::Foundation::Collections::IIterable<HSTRING>>
    {
        HSTRING hstr = nullptr;
        ~EdgeHtmlStringIterable()
        {
            if (hstr)
                WindowsDeleteString(hstr);
        }
        HRESULT STDMETHODCALLTYPE GetIids(ULONG *iidCount, IID **iids) override
        {
            *iidCount = 0;
            *iids = nullptr;
            return S_OK;
        }
        HRESULT STDMETHODCALLTYPE GetRuntimeClassName(HSTRING *className) override
        {
            *className = nullptr;
            return E_NOTIMPL;
        }
        HRESULT STDMETHODCALLTYPE GetTrustLevel(TrustLevel *trustLevel) override
        {
            *trustLevel = BaseTrust;
            return S_OK;
        }
        HRESULT STDMETHODCALLTYPE First(
            ABI::Windows::Foundation::Collections::IIterator<HSTRING> **first) override
        {
            auto it = new EdgeHtmlStringIterator();
            if (hstr)
                WindowsDuplicateString(hstr, &it->hstr);
            *first = it;
            return S_OK;
        }
    };
}

double EdgeHtml::get_ZoomFactor()
{
    DOUBLE scale;
    if (FAILED(controlsite->get_Scale(&scale)))
        return 1.0;
    return scale;
}
void EdgeHtml::put_ZoomFactor(double zoomFactor)
{
    controlsite->put_Scale(zoomFactor);
}
void EdgeHtml::setfocus()
{
    controlsite->MoveFocus(WebViewControlMoveFocusReason::WebViewControlMoveFocusReason_Programmatic);
}

void EdgeHtml::resize(int w, int h)
{
    Rect bounds{0, 0, static_cast<float>(w), static_cast<float>(h)};
    controlsite->put_Bounds(bounds);
}
void EdgeHtml::evaljs(const wchar_t *js, evaljs_callback_t cb)
{
    CComPtr<EdgeHtmlStringIterable> iterable = new EdgeHtmlStringIterable();
    CHECK_FAILURE_NORET(WindowsCreateString(js, lstrlenW(js), &iterable->hstr));
    CComPtr<ABI::Windows::Foundation::IAsyncOperation<HSTRING>> asyncOp;
    CHECK_FAILURE_NORET(control->InvokeScriptAsync(AutoHString(L"eval"), iterable, &asyncOp));
    if (cb)
    {
        AutoHString result;
        CHECK_FAILURE_NORET(await(asyncOp.p, &result));
        cb(result);
    }
}
void EdgeHtml::navigate(const wchar_t *u)
{
    CComPtr<IUriRuntimeClassFactory> uriRuntimeClassFactory;
    CHECK_FAILURE_NORET(GetActivationFactory(AutoHString(RuntimeClass_Windows_Foundation_Uri), &uriRuntimeClassFactory));
    CComPtr<IUriRuntimeClass> uriRuntimeClass;
    CHECK_FAILURE_NORET(uriRuntimeClassFactory->CreateUri(AutoHString(u), &uriRuntimeClass));
    control->Navigate(uriRuntimeClass);
}
void EdgeHtml::sethtml(const wchar_t *u)
{
    control->NavigateToString(AutoHString(u));
}
void EdgeHtml::bind(const wchar_t *f, void *)
{
    std::wstring js = std::wstring{} + L"window.LUNAJSObject." + f + LR"( = function(){
    window.external.notify(JSON.stringify({    method: ')" +
                      f + L"',    args: Array.prototype.slice.call(arguments)}));};";

    InitializeScript += js;
    control2->AddInitializeScript(AutoHString(InitializeScript));
}
EdgeHtml::~EdgeHtml()
{
}

HRESULT EdgeHtmlComHandler::Invoke(IWebViewControl *sender, IWebViewControlScriptNotifyEventArgs *args)
{
    AutoHString hvalue;
    CHECK_FAILURE(args->get_Value(&hvalue));
    std::wstring value = hvalue;
    static std::wstring __contextmenu__helper = L"__contextmenu__helper";
    if (value._Starts_with(__contextmenu__helper))
    {
        ref->CreateMenu(ref->parent, value.substr(__contextmenu__helper.size()), nullptr, ref->menu_handler);
    }
    else if (ref->callback)
    {
        ref->callback(value.c_str());
    }
    return S_OK;
}
HRESULT EdgeHtmlComHandler::Invoke(IWebViewControl *sender, IWebViewControlNavigationStartingEventArgs *args)
{
    return ref->control2->AddInitializeScript(AutoHString(ref->InitializeScript));
}
EdgeHtml::EdgeHtml(HWND parent) : parent(parent)
{
}
HRESULT EdgeHtml::init(bool backgroundtransparent)
{
    CO_INIT co;
    CComPtr<IWebViewControlProcess> process;
    CHECK_FAILURE(ActivateInstance(AutoHString(RuntimeClass_Windows_Web_UI_Interop_WebViewControlProcess), &process));
    CComPtr<ABI::Windows::Foundation::IAsyncOperation<WebViewControl *>> createWebViewAsyncOperation;
    CHECK_FAILURE(process->CreateWebViewControlAsync(reinterpret_cast<INT64>(parent), Rect{}, &createWebViewAsyncOperation));
    CHECK_FAILURE(await(createWebViewAsyncOperation.p, &control));
    CHECK_FAILURE(control.QueryInterface(&control2));
    CHECK_FAILURE(control.QueryInterface(&controlsite));
    CComPtr<IWebViewControlSettings> settings;
    CHECK_FAILURE(control->get_Settings(&settings));
    CHECK_FAILURE(settings->put_IsJavaScriptEnabled(true));
    CHECK_FAILURE(settings->put_IsScriptNotifyAllowed(true));
    if (backgroundtransparent)
    {
        // 实际上不管用，不知道为什么。
        [&]()
        {
            CComPtr<IColorsStatics> colors;
            CHECK_FAILURE_NORET(GetActivationFactory(AutoHString(RuntimeClass_Windows_UI_Colors), &colors));
            Color ts;
            CHECK_FAILURE_NORET(colors->get_Transparent(&ts));
            control->put_DefaultBackgroundColor(ts);
        }();
    }
    handler = new EdgeHtmlComHandler{this};
    CHECK_FAILURE(controlsite->put_IsVisible(true));
    EventRegistrationToken token;
    CHECK_FAILURE(control->add_ScriptNotify(handler, &token));
    CHECK_FAILURE(control->add_NavigationStarting(handler, &token));
    return S_OK;
}
DECLARE_API HRESULT edgehtml_new(EdgeHtml **web, HWND parent, bool backgroundtransparent)
{
    *web = nullptr;
    auto _ = new EdgeHtml(parent);
    if (!_)
        return E_POINTER;
    auto hr = _->init(backgroundtransparent);
    if (FAILED(hr))
    {
        delete _;
        _ = nullptr;
    }
    *web = _;
    return hr;
}

DECLARE_API void edgehtml_set_notify_callback(EdgeHtml *ret, web_notify_callback_t callback)
{
    if (!ret)
        return;
    ret->callback = callback;
}