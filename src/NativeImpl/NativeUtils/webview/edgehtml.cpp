#include "edgehtml.hpp"
#include "../winrt/await.hpp"

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

void EdgeHtml::resize(int w, int h)
{
    Rect bounds{0, 0, static_cast<float>(w), static_cast<float>(h)};
    controlsite->put_Bounds(bounds);
}
void EdgeHtml::evaljs(const wchar_t *js, evaljs_callback_t cb)
{
    CComPtr<IPropertyValueStatics> propertyValueStatics;
    CHECK_FAILURE_NORET(GetActivationFactory(AutoHString(RuntimeClass_Windows_Foundation_PropertyValue), &propertyValueStatics));
    CComPtr<IInspectable> inspectable;
    HSTRING arr[1] = {AutoHString(js)};
    CHECK_FAILURE_NORET(propertyValueStatics->CreateStringArray(1, arr, &inspectable));
    CComPtr<IVectorView<HSTRING>> args;
    CHECK_FAILURE_NORET(inspectable.QueryInterface(&args));
    CComPtr<ABI::Windows::Foundation::IAsyncOperation<HSTRING>> asyncOp;
    CComPtr<IIterable<HSTRING>> ihs;
    CHECK_FAILURE_NORET(args.QueryInterface(&ihs));
    control->InvokeScriptAsync(AutoHString(L"eval"), ihs, &asyncOp);
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
void EdgeHtml::add_menu(int index, contextmenu_gettext gettext, contextmenu_callback_t_ex callback, contextmenu_getchecked getchecked, contextmenu_getuse getuse)
{
    NativeMenuHelper::add_menu(index, gettext, callback, getchecked, getuse);
}

HRESULT EdgeHtmlComHandler::Invoke(IWebViewControl *sender, IWebViewControlScriptNotifyEventArgs *args)
{
    AutoHString hvalue;
    CHECK_FAILURE(args->get_Value(&hvalue));
    std::wstring value = hvalue;
    static std::wstring __contextmenu__helper = L"__contextmenu__helper";
    if (value._Starts_with(__contextmenu__helper))
    {
        ref->CreateMenu(ref->parent, value.substr(__contextmenu__helper.size()));
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