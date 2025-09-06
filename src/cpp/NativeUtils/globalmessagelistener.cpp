#include "clipboard.hpp"
static auto LUNA_UPDATE_PREPARED_OK = RegisterWindowMessage(L"LUNA_UPDATE_PREPARED_OK");
static auto WM_MAGPIE_SCALINGCHANGED = RegisterWindowMessage(L"MagpieScalingChanged");
static auto Magpie_Core_CLI_ToastMessage = RegisterWindowMessage(L"Magpie_Core_CLI_ToastMessage");
static auto Magpie_Core_CLI_ScalingOptions_Save = RegisterWindowMessage(L"Magpie_Core_CLI_ScalingOptions_Save");
static auto WM_SYS_HOTKEY = RegisterWindowMessage(L"SYS_HOTKEY_REG_UNREG");
bool IsColorSchemeChangeMessage(LPARAM lParam)
{
    return lParam && CompareStringOrdinal(reinterpret_cast<LPCWCH>(lParam), -1, L"ImmersiveColorSet", -1, TRUE) == CSTR_EQUAL;
}
typedef void (*WindowMessageCallback_t)(UINT, WPARAM, LPARAM);
static int unique_id = 1;
typedef void (*hotkeycallback_t)();
static std::map<int, hotkeycallback_t> keybinds;
struct hotkeymessageLP
{
    UINT fsModifiers;
    UINT vk;
    hotkeycallback_t callback;
};
static LRESULT CALLBACK WNDPROC_1(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
    auto callback = (WindowMessageCallback_t)GetWindowLongPtrW(hWnd, GWLP_USERDATA);
    if (!callback)
        return DefWindowProc(hWnd, message, wParam, lParam);
    switch (message)
    {
    case WM_SETTINGCHANGE:
    {
        static int idx = 1;
        if (IsColorSchemeChangeMessage(lParam) && ((idx++) % 2))
            callback(0, false, NULL);
    }
    break;
    case WM_CLIPBOARDUPDATE:
    {
        auto data = clipboard_get_internal();
        if (data)
            callback(3, (WPARAM)iscurrentowndclipboard(), (LPARAM)data.value().c_str());
    }
    break;
    case WM_HOTKEY:
    {
        auto _unique_id = (int)(wParam);
        auto _ = keybinds.find(_unique_id);
        if (_ == keybinds.end())
            return 0;
        _->second();
    }
    break;
    case WM_QUERYENDSESSION:
    {
        callback(-1, false, NULL);
    }
    break;
    }
    if (message == Magpie_Core_CLI_ToastMessage || message == Magpie_Core_CLI_ScalingOptions_Save)
    {
        ATOM atom = (ATOM)wParam;
        WCHAR buffer[256];
        if (GlobalGetAtomName(atom, buffer, ARRAYSIZE(buffer)))
        {
            GlobalDeleteAtom(atom);
            callback(message == Magpie_Core_CLI_ToastMessage ? 4 : 5, false, (LPARAM)buffer);
        }
    }
    else if (message == WM_MAGPIE_SCALINGCHANGED)
    {
        callback(1, wParam, lParam);
    }
    else if (message == LUNA_UPDATE_PREPARED_OK)
    {
        callback(2, false, NULL);
    }
    else if (message == WM_SYS_HOTKEY)
    {
        if ((UINT)wParam == 1)
        {
            auto info = (hotkeymessageLP *)(lParam);
            unique_id += 1;
            auto succ = RegisterHotKey(hWnd, unique_id, info->fsModifiers, info->vk);
            if (succ)
            {
                keybinds[unique_id] = info->callback;
                return unique_id;
            }
            return 0;
        }
        else
        {
            UnregisterHotKey(hWnd, (int)lParam);
            auto _ = keybinds.find((int)lParam);
            if (_ != keybinds.end())
                keybinds.erase(_);
        }
    }
    return DefWindowProc(hWnd, message, wParam, lParam);
}
HWND globalmessagehwnd;
DECLARE_API void ClipBoardListenerStart()
{
    addClipboardFormatListener(globalmessagehwnd);
}
DECLARE_API void ClipBoardListenerStop()
{
    removeClipboardFormatListener(globalmessagehwnd);
}
typedef void (*WinEventHookCALLBACK_t)(DWORD event, HWND hwnd, LONG idObject);
static WinEventHookCALLBACK_t WinEventHookCALLBACK = nullptr;
static VOID CALLBACK WinEventHookPROC(
    HWINEVENTHOOK hWinEventHook,
    DWORD event,
    HWND hwnd,
    LONG idObject,
    LONG idChild,
    DWORD idEventThread,
    DWORD dwmsEventTime)
{
    if (WinEventHookCALLBACK)
        WinEventHookCALLBACK(event, hwnd, idObject);
}
static std::wstring get_unique_classname()
{
    const wchar_t CLASS_NAME[] = L"luna_unique_classname_";
    static int idx = 0;
    std::wstringstream wss;
    wss << CLASS_NAME << idx++;
    return wss.str();
}
static std::pair<HWND, WNDCLASS> CreateWindowForWndProc(WNDPROC WNDPROC_1)
{
    auto CLASS_NAME = get_unique_classname();
    WNDCLASS wc = {};
    wc.lpfnWndProc = WNDPROC_1;
    wc.lpszClassName = CLASS_NAME.c_str();
    GetModuleHandleEx(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS, (LPCTSTR)wc.lpfnWndProc, &wc.hInstance);
    RegisterClass(&wc);
    HWND hWnd = CreateWindowEx(0, CLASS_NAME.c_str(), NULL, 0, 0, 0, 0, 0, 0, nullptr, wc.hInstance, nullptr); // HWND_MESSAGE会收不到。
    return std::make_pair(hWnd, wc);
}
DECLARE_API void globalmessagelistener(WinEventHookCALLBACK_t callback1, WindowMessageCallback_t callback)
{
    auto &&[hWnd, wc] = CreateWindowForWndProc(WNDPROC_1);
    globalmessagehwnd = hWnd;
    SetWindowLongPtrW(hWnd, GWLP_USERDATA, (LONG_PTR)callback);
    ChangeWindowMessageFilterEx(hWnd, LUNA_UPDATE_PREPARED_OK, MSGFLT_ALLOW, nullptr);
    ChangeWindowMessageFilterEx(hWnd, WM_MAGPIE_SCALINGCHANGED, MSGFLT_ALLOW, nullptr);
    ChangeWindowMessageFilterEx(hWnd, Magpie_Core_CLI_ToastMessage, MSGFLT_ALLOW, nullptr);
    WinEventHookCALLBACK = callback1;
    SetWinEventHook(EVENT_SYSTEM_FOREGROUND, EVENT_SYSTEM_FOREGROUND, wc.hInstance, WinEventHookPROC, 0, 0, 0);
    SetWinEventHook(EVENT_OBJECT_DESTROY, EVENT_OBJECT_DESTROY, wc.hInstance, WinEventHookPROC, 0, 0, 0);
}
DECLARE_API void dispatchcloseevent()
{
    PostMessage(HWND_BROADCAST, LUNA_UPDATE_PREPARED_OK, 0, 0);
}
DECLARE_API int SysRegisterHotKey(UINT fsModifiers, UINT vk, hotkeycallback_t callback)
{
    auto info = new hotkeymessageLP{fsModifiers, vk, callback};
    auto ret = SendMessage(globalmessagehwnd, WM_SYS_HOTKEY, 1, (LPARAM)info);
    delete info;
    return ret;
}
DECLARE_API void SysUnRegisterHotKey(int _id)
{
    SendMessage(globalmessagehwnd, WM_SYS_HOTKEY, 0, (LPARAM)_id);
}

DECLARE_API void RunMessageLoop()
{
    MSG msg = {};
    while (GetMessage(&msg, NULL, 0, 0))
    {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
}
static LRESULT CALLBACK WNDPROC_2(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
    auto callback = (WindowMessageCallback_t)GetWindowLongPtrW(hWnd, GWLP_USERDATA);
    if (!callback)
        return DefWindowProc(hWnd, message, wParam, lParam);
    callback(message, wParam, lParam);
    return DefWindowProc(hWnd, message, wParam, lParam);
}
DECLARE_API HWND CreateMessageWindow(WindowMessageCallback_t callback)
{
    auto &&[hWnd, wc] = CreateWindowForWndProc(WNDPROC_2);
    SetWindowLongPtrW(hWnd, GWLP_USERDATA, (LONG_PTR)callback);
    return hWnd;
}