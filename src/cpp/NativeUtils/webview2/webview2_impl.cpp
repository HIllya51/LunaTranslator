#include "webview2_impl.hpp"

class JSEvalCallback : public ComImpl<ICoreWebView2ExecuteScriptCompletedHandler>
{
public:
    CoAsyncTaskWaiter waitforexec;
    evaljs_callback_t cb;
    JSEvalCallback(evaljs_callback_t cb) : cb(cb) {}
    HRESULT STDMETHODCALLTYPE Invoke(HRESULT errorCode, LPCWSTR resultObjectAsJson)
    {
        cb(resultObjectAsJson);
        waitforexec.Set();
        return S_OK;
    }
};
class AddExtCallback : public ComImpl<ICoreWebView2ProfileAddBrowserExtensionCompletedHandler>
{
public:
    HRESULT error;
    CoAsyncTaskWaiter waitforexec;
    // ICoreWebView2ProfileAddBrowserExtensionCompletedHandler
    HRESULT STDMETHODCALLTYPE Invoke(HRESULT errorCode, ICoreWebView2BrowserExtension *extension)
    {
        error = errorCode;
        waitforexec.Set();
        return S_OK;
    }
};
class ListExtCallback : public ComImpl<ICoreWebView2ProfileGetBrowserExtensionsCompletedHandler, ICoreWebView2BrowserExtensionEnableCompletedHandler, ICoreWebView2BrowserExtensionRemoveCompletedHandler>
{
public:
    CoAsyncTaskWaiter waitforexec;
    List_Ext_callback_t cb;
    std::wstring idfuck;
    BOOL remove, enable;
    HRESULT listerror = S_OK;
    HRESULT editerror = S_OK;
    ListExtCallback(List_Ext_callback_t cb, LPCWSTR id1 = nullptr, BOOL remove = FALSE, BOOL enable = FALSE) : idfuck(id1 ? id1 : L""), remove(remove), enable(enable), cb(cb) {}
    // ICoreWebView2BrowserExtensionEnableCompletedHandler
    HRESULT STDMETHODCALLTYPE Invoke(HRESULT errorCode)
    {
        editerror = errorCode;
        return errorCode;
    }
    HRESULT STDMETHODCALLTYPE Invoke(HRESULT errorCode, ICoreWebView2BrowserExtensionList *extensionList)
    {
        listerror = [&]()
        {
            CHECK_FAILURE(errorCode);
            UINT count;
            CHECK_FAILURE(extensionList->get_Count(&count));
            for (UINT i = 0; i < count; i++)
            {
                CComPtr<ICoreWebView2BrowserExtension> ext;
                CHECK_FAILURE_CONTINUE(extensionList->GetValueAtIndex(i, &ext));
                CComHeapPtr<WCHAR> id{};
                CHECK_FAILURE_CONTINUE(ext->get_Id(&id));
                if (cb)
                {
                    BOOL isEnabled;
                    CComHeapPtr<WCHAR> name{};
                    CHECK_FAILURE_CONTINUE(ext->get_Name(&name));
                    CHECK_FAILURE_CONTINUE(ext->get_IsEnabled(&isEnabled));
                    cb(id, name, isEnabled);
                }
                else if (idfuck.size() && (wcscmp(idfuck.c_str(), id) == 0))
                {
                    return remove ? ext->Remove(this) : ext->Enable(enable, this);
                }
            }
            return S_OK;
        }();
        waitforexec.Set();
        return listerror;
    }
};
static bool StartsWith(const wchar_t *str, const wchar_t *prefix)
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
// ICoreWebView2NavigationStartingEventHandler
HRESULT STDMETHODCALLTYPE WebView2ComHandler::Invoke(ICoreWebView2 *sender, ICoreWebView2NavigationStartingEventArgs *args)
{
    CComHeapPtr<WCHAR> uri{};
    CHECK_FAILURE(args->get_Uri(&uri));
    bool skip = false;
    [&]()
    {
        CComPtr<ICoreWebView2NavigationStartingEventArgs3> args3;
        CHECK_FAILURE_NORET(args->QueryInterface(&args3));
        COREWEBVIEW2_NAVIGATION_KIND kind;
        CHECK_FAILURE_NORET(args3->get_NavigationKind(&kind));
        skip = COREWEBVIEW2_NAVIGATION_KIND_RELOAD == kind;
    }();
    if (skip || (!ref->navigating_callback) || StartsWith(uri, L"data:text/html"))
        return S_OK;
    auto isextension = StartsWith(uri, L"chrome-extension://");
    std::call_once(navigatingfirst, [&]()
                   { isextensionsettignwindow = isextension; });
    if (isextension)
    {
        if (!isextensionsettignwindow)
        {
            args->put_Cancel(TRUE);
            ref->navigating_callback(uri, true);
        }
        else
        {
            ref->navigating_callback(uri, false);
        }
    }
    else
    {
        ref->navigating_callback(uri, false);
    }
    return S_OK;
}
// ICoreWebView2DocumentTitleChangedEventHandler
HRESULT STDMETHODCALLTYPE WebView2ComHandler::Invoke(ICoreWebView2 *sender, IUnknown *args)
{
    CComHeapPtr<WCHAR> uri;
    CHECK_FAILURE(sender->get_DocumentTitle(&uri));
    if (ref->titlechange_callback)
    {
        ref->titlechange_callback(uri);
    }
    return S_OK;
}

// ICoreWebView2GetFaviconCompletedHandler
HRESULT STDMETHODCALLTYPE WebView2ComHandler2::Invoke(HRESULT errorCode, IStream *faviconStream)
{
    if (!ref->IconChanged_callback)
        return S_OK;
    CHECK_FAILURE(errorCode);
    ULARGE_INTEGER curr;
    CHECK_FAILURE(IStream_Size(faviconStream, &curr));
    auto data = std::make_unique<byte[]>(curr.LowPart);
    CHECK_FAILURE(IStream_Read(faviconStream, data.get(), curr.LowPart));
    ref->IconChanged_callback(data.get(), curr.LowPart);
    return S_OK;
}
// ICoreWebView2FaviconChangedEventHandler
HRESULT STDMETHODCALLTYPE WebView2ComHandler2::Invoke(ICoreWebView2 *sender, IUnknown *args)
{
    CComPtr<ICoreWebView2_15> w215;
    CHECK_FAILURE(sender->QueryInterface(&w215));
    CHECK_FAILURE(w215->GetFavicon(COREWEBVIEW2_FAVICON_IMAGE_FORMAT_PNG, this));
    return S_OK;
}
// ICoreWebView2CreateCoreWebView2ControllerCompletedHandler
HRESULT STDMETHODCALLTYPE WebView2ComHandler::Invoke(HRESULT result, ICoreWebView2Controller *controller)
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
        ref->m_webView->AddScriptToExecuteOnDocumentCreated(L"window.LUNAJSObject={}", nullptr);
        ref->m_webView->add_NewWindowRequested(this, &token);
        ref->m_webView->add_DocumentTitleChanged(this, &token);
        [&]()
        {
            CComPtr<ICoreWebView2_11> m_webView2_11;
            CHECK_FAILURE_NORET(ref->m_webView.QueryInterface(&m_webView2_11));
            m_webView2_11->add_ContextMenuRequested(this, &token);
        }();
        [&]()
        {
            otherhandler = new WebView2ComHandler2{ref};
            CComPtr<ICoreWebView2_15> m_webView2_15;
            CHECK_FAILURE_NORET(ref->m_webView.QueryInterface(&m_webView2_15));
            m_webView2_15->add_FaviconChanged(otherhandler, &token);
        }();
        CComPtr<ICoreWebView2Settings> settings;
        CHECK_FAILURE_NORET(ref->m_webView->get_Settings(&settings));
        settings->put_AreDevToolsEnabled(TRUE);
        settings->put_AreDefaultContextMenusEnabled(TRUE);
        settings->put_IsStatusBarEnabled(FALSE);
    }();
    ref->CreateCoreWebView2ControllerError = result;
    ref->waitforloadflag.clear();
    return result;
}
// ICoreWebView2NewWindowRequestedEventHandler
HRESULT STDMETHODCALLTYPE WebView2ComHandler::Invoke(ICoreWebView2 *sender, ICoreWebView2NewWindowRequestedEventArgs *args)
{
    CComHeapPtr<WCHAR> uri{};
    CHECK_FAILURE(args->get_Uri(&uri));
    CHECK_FAILURE(args->put_Handled(TRUE));
    if (StartsWith(uri, L"chrome-extension://"))
    {
        if (ref->navigating_callback)
            ref->navigating_callback(uri, true);
    }
    else if (StartsWith(uri, L"chrome://"))
    {
        ref->m_webView->Navigate(uri);
    }
    else
    {
        ShellExecute(NULL, TEXT("open"), uri, NULL, NULL, SW_SHOW);
    }
    return S_OK;
}
// ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler
HRESULT STDMETHODCALLTYPE WebView2ComHandler::Invoke(HRESULT result, ICoreWebView2Environment *env)
{
    auto hr = [=]()
    {
        CHECK_FAILURE(result);
        CHECK_FAILURE(env->CreateCoreWebView2Controller(ref->parent, this));
        ref->m_env = env;
        return S_OK;
    }();
    ref->CreateCoreWebView2EnvironmentError = hr;
    if (FAILED(hr))
        ref->waitforloadflag.clear();
    return hr;
}
// ICoreWebView2PermissionRequestedEventHandler
HRESULT STDMETHODCALLTYPE WebView2ComHandler::Invoke(ICoreWebView2 *, ICoreWebView2PermissionRequestedEventArgs *args)
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
HRESULT STDMETHODCALLTYPE WebView2ComHandler::Invoke(ICoreWebView2 *sender, ICoreWebView2WebMessageReceivedEventArgs *args)
{
    CComHeapPtr<WCHAR> message{};
    CHECK_FAILURE(args->get_WebMessageAsJson(&message));
    if (wcscmp(L"\"FilesDropped\"", message) == 0)
    {
        if (!ref->FilesDropped_callback)
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
            CHECK_FAILURE_CONTINUE(objectsCollection->GetValueAtIndex(i, &object));
            // Note that objects can be null.
            if (!object)
                continue;
            CComPtr<ICoreWebView2File> file;
            CHECK_FAILURE_CONTINUE(object.QueryInterface(&file));
            // Add the file to message to be sent back to webview
            CComHeapPtr<WCHAR> path;
            CHECK_FAILURE_CONTINUE(file->get_Path(&path));
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
HRESULT STDMETHODCALLTYPE WebView2ComHandler::Invoke(ICoreWebView2Controller *sender, IUnknown *args)
{
    double zoomFactor;
    CHECK_FAILURE(sender->get_ZoomFactor(&zoomFactor));
    if (ref->zoomchange_callback)
        ref->zoomchange_callback(zoomFactor);
    return S_OK;
}
class ContextMenuCallback : public ComImpl<ICoreWebView2CustomItemSelectedEventHandler>
{
public:
    COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND targetKind;
    std::wstring CurrSelectText;
    contextmenu_callback_t_ex callback;
    ContextMenuCallback(COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND targetKind, LPCWSTR CurrSelectText_1, contextmenu_callback_t_ex callback) : targetKind(targetKind), callback(callback)
    {
        if (targetKind == COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND_SELECTED_TEXT)
            CurrSelectText = CurrSelectText_1;
    }
    HRESULT STDMETHODCALLTYPE Invoke(ICoreWebView2ContextMenuItem *sender, IUnknown *args)
    {
        if (targetKind == COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND_SELECTED_TEXT)
        {
            auto f = std::get<contextmenu_callback_t>(callback);
            if (f)
                f(CurrSelectText.c_str());
        }
        else
        {
            auto f = std::get<contextmenu_notext_callback_t>(callback);
            if (f)
                f();
        }
        return S_OK;
    }
};
// ICoreWebView2ContextMenuRequestedEventHandler
HRESULT STDMETHODCALLTYPE WebView2ComHandler::Invoke(ICoreWebView2 *sender, ICoreWebView2ContextMenuRequestedEventArgs *args)
{
    CComPtr<ICoreWebView2ContextMenuTarget> target;
    CHECK_FAILURE(args->get_ContextMenuTarget(&target));
    BOOL hasselection;
    CHECK_FAILURE(target->get_Kind(&targetKind));
    CHECK_FAILURE(target->get_HasSelection(&hasselection));
    if (!(((hasselection && (targetKind == COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND_SELECTED_TEXT))) ||
          (targetKind == COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND_PAGE)))
        return S_OK;
    CComPtr<ICoreWebView2ContextMenuItemCollection> items;
    CHECK_FAILURE(args->get_MenuItems(&items));
    CComHeapPtr<WCHAR> CurrSelectText;
    if (targetKind == COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND_SELECTED_TEXT)
        CHECK_FAILURE(target->get_SelectionText(&CurrSelectText));
    CComPtr<ICoreWebView2Environment9> webviewEnvironment_5;
    CHECK_FAILURE(ref->m_env.QueryInterface(&webviewEnvironment_5));
    EventRegistrationToken token;
    UINT idx = 0;
    for (auto &&context : (targetKind == COREWEBVIEW2_CONTEXT_MENU_TARGET_KIND_SELECTED_TEXT ? ref->menus : ref->menus_noselect))
    {
        if (context.getuse && !context.getuse())
            continue;
        CComPtr<ICoreWebView2ContextMenuItem> newMenuItem;
        if (context.gettext && AutoFreeString(context.gettext()) && wcslen(AutoFreeString(context.gettext())))
        {
            CComPtr<ContextMenuCallback> callbackhandler = new ContextMenuCallback(targetKind, CurrSelectText, context.callback);
            CHECK_FAILURE_CONTINUE(webviewEnvironment_5->CreateContextMenuItem(AutoFreeString(context.gettext()), nullptr, context.checkable ? COREWEBVIEW2_CONTEXT_MENU_ITEM_KIND_CHECK_BOX : COREWEBVIEW2_CONTEXT_MENU_ITEM_KIND_COMMAND, &newMenuItem));
            newMenuItem->add_CustomItemSelected(callbackhandler, &token);
            if (context.checkable && context.getchecked)
                newMenuItem->put_IsChecked(context.getchecked());
        }
        else
        {
            CHECK_FAILURE_CONTINUE(webviewEnvironment_5->CreateContextMenuItem(L"", nullptr, COREWEBVIEW2_CONTEXT_MENU_ITEM_KIND_SEPARATOR, &newMenuItem));
        }
        CHECK_FAILURE_CONTINUE(items->InsertValueAtIndex(idx++, newMenuItem));
    }
    return S_OK;
}
void WebView2::WaitForLoad()
{
    // win7上CoWaitForMultipleHandles似乎有点毛病
    MSG msg;
    while (waitforloadflag.test_and_set() && GetMessageW(&msg, nullptr, 0, 0) >= 0)
    {
        if (msg.message == WM_QUIT || msg.message == WM_DESTROY)
            break;
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }
}
std::optional<std::wstring> WebView2::UserDir(bool loadextension)
{
    wchar_t dataPath[MAX_PATH];
    if (!SUCCEEDED(SHGetFolderPathW(nullptr, CSIDL_APPDATA, nullptr, 0, dataPath)))
        return {};
    wchar_t userDataFolder[MAX_PATH];
    PathCombineW(userDataFolder, dataPath, loadextension ? L"LunaTranslator" : L"LunaTranslator_noext");
    return userDataFolder;
}

#include <WebView2EnvironmentOptions.h>

HRESULT WebView2::init(bool loadextension_)
{
    loadextension = loadextension_;
    waitforloadflag.test_and_set();
    handler = new WebView2ComHandler{this};
    auto dir = UserDir(loadextension);
    ICoreWebView2EnvironmentOptions *optionptr = nullptr;
    auto ext = loadextension ? L"--embedded-browser-webview-enable-extension" : L"";
    CComPtr<CoreWebView2EnvironmentOptions> options;
#ifndef WINXP
    options.Attach(Microsoft::WRL::Make<CoreWebView2EnvironmentOptions>().Detach());
#else
    options = new CoreWebView2EnvironmentOptions();
#endif
    // 必须用这个才能进行add，否则只能list/remove/enable
    if (options && SUCCEEDED(options->put_AreBrowserExtensionsEnabled(loadextension)) && SUCCEEDED(options->put_AdditionalBrowserArguments(ext)))
        optionptr = options;
    else
        SetEnvironmentVariableW(L"WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS", ext);
    CHECK_FAILURE(CreateCoreWebView2EnvironmentWithOptions(nullptr, dir ? dir.value().c_str() : nullptr, optionptr, handler));
    WaitForLoad();
    CHECK_FAILURE(CreateCoreWebView2EnvironmentError);
    CHECK_FAILURE(CreateCoreWebView2ControllerError);
    return (m_env && m_webView && m_webViewController) ? S_OK : E_FAIL;
}
WebView2::WebView2(HWND parent, bool backgroundtransparent) : parent(parent), backgroundtransparent(backgroundtransparent)
{
}
std::wstring WebView2::GetUserDataFolder()
{
    std::wstring result;
    auto hr = [&]()
    {
        CComPtr<ICoreWebView2Environment7> env;
        CHECK_FAILURE(m_env.QueryInterface(&env));
        CComHeapPtr<WCHAR> data;
        CHECK_FAILURE(env->get_UserDataFolder(&data));
        result = data;
        return S_OK;
    }();
    if (SUCCEEDED(hr))
        return result;
    return UserDir(loadextension).value_or(L"");
}
void WebView2::AddMenu(int index, contextmenu_gettext gettext, contextmenu_callback_t_ex callback, bool checkable, contextmenu_getchecked getchecked, contextmenu_getuse getuse)
{
    auto &whichmenu = (std::get_if<contextmenu_callback_t>(&callback)) ? menus : menus_noselect;
    whichmenu.insert(whichmenu.begin() + index, {gettext, callback, checkable, getchecked, getuse});
}
HRESULT WebView2::ExtensionGetProfile7(ICoreWebView2Profile7 **profile7)
{
    CComPtr<ICoreWebView2_13> web13;
    CHECK_FAILURE(m_webView.QueryInterface(&web13));
    CComPtr<ICoreWebView2Profile> profile;
    CHECK_FAILURE(web13->get_Profile(&profile));
    CHECK_FAILURE(profile.QueryInterface(profile7));
    return S_OK;
}
HRESULT WebView2::AddExtension(LPCWSTR extpath)
{
    CComPtr<ICoreWebView2Profile7> profile7;
    CHECK_FAILURE(ExtensionGetProfile7(&profile7));
    CComPtr<AddExtCallback> callback = new AddExtCallback();
    CHECK_FAILURE(profile7->AddBrowserExtension(extpath, callback));
    callback->waitforexec.Wait();
    CHECK_FAILURE(callback->error);
    return S_OK;
}
HRESULT WebView2::ListExtensionDoSomething(List_Ext_callback_t cb, LPCWSTR id, BOOL remove, BOOL enable)
{
    CComPtr<ICoreWebView2Profile7> profile7;
    CHECK_FAILURE(ExtensionGetProfile7(&profile7));
    CComPtr<ListExtCallback> exts = new ListExtCallback(cb, id, remove, enable);
    CHECK_FAILURE(profile7->GetBrowserExtensions(exts));
    exts->waitforexec.Wait();
    CHECK_FAILURE(exts->listerror);
    CHECK_FAILURE(exts->editerror);
    return S_OK;
}
void WebView2::put_PreferredColorScheme(COREWEBVIEW2_PREFERRED_COLOR_SCHEME scheme)
{
    CComPtr<ICoreWebView2_13> webView2_13;
    CHECK_FAILURE_NORET(m_webView.QueryInterface(&webView2_13));
    CComPtr<ICoreWebView2Profile> profile;
    CHECK_FAILURE_NORET(webView2_13->get_Profile(&profile));
    CHECK_FAILURE_NORET(profile->put_PreferredColorScheme(scheme));
}

void WebView2::Resize(int w, int h)
{
    RECT rect{0, 0, w, h};
    m_webViewController->put_Bounds(rect);
}

double WebView2::get_ZoomFactor()
{
    double zoomFactor;
    m_webViewController->get_ZoomFactor(&zoomFactor);
    return zoomFactor;
}
void WebView2::put_ZoomFactor(double zoomFactor)
{
    m_webViewController->put_ZoomFactor(zoomFactor);
}

void WebView2::EvalJS(const wchar_t *js, evaljs_callback_t cb)
{
    if (!cb)
        m_webView->ExecuteScript(js, nullptr);
    else
    {
        CComPtr<JSEvalCallback> callback = new JSEvalCallback{cb};
        CHECK_FAILURE_NORET(m_webView->ExecuteScript(js, callback));
        callback->waitforexec.Wait();
    }
}

void WebView2::Navigate(LPCWSTR uri)
{
    m_webView->Navigate(uri);
}
void WebView2::SetHTML(LPCWSTR html)
{
    m_webView->NavigateToString(html);
}
void WebView2::Bind(LPCWSTR funcname)
{
    std::wstring js = std::wstring{} + L"window.LUNAJSObject." + funcname + L" = function(){window.chrome.webview.postMessage({    method: '" + funcname + L"',    args: Array.prototype.slice.call(arguments)});};";
    CHECK_FAILURE_NORET(m_webView->AddScriptToExecuteOnDocumentCreated(js.c_str(), nullptr));
}
void WebView2::Reload()
{
    m_webView->Reload();
}