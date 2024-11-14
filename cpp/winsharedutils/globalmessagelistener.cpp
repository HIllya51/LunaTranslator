#ifndef WINXP

static auto LUNA_UPDATE_PREPARED_OK = RegisterWindowMessage(L"LUNA_UPDATE_PREPARED_OK");
static auto WM_MAGPIE_SCALINGCHANGED = RegisterWindowMessage(L"MagpieScalingChanged");
bool IsColorSchemeChangeMessage(LPARAM lParam)
{
    return lParam && CompareStringOrdinal(reinterpret_cast<LPCWCH>(lParam), -1, L"ImmersiveColorSet", -1, TRUE) == CSTR_EQUAL;
}
void globalmessagelistener_1(void *callback)
{

    const wchar_t CLASS_NAME[] = L"globalmessagelistener";

    WNDCLASS wc = {};
    wc.lpfnWndProc = [](HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
    {
        void (*callback)(int, void *);
        callback = (decltype(callback))GetWindowLongPtrW(hWnd, GWLP_USERDATA);
        if (callback)
        {
            if (WM_SETTINGCHANGE == message)
            {
                if (IsColorSchemeChangeMessage(lParam))
                    callback(0, 0);
            }
            else if (message == WM_MAGPIE_SCALINGCHANGED)
            {
                callback(1, (void *)wParam);
            }
            else if (message == LUNA_UPDATE_PREPARED_OK)
            {
                callback(2, 0);
            }
        }
        return DefWindowProc(hWnd, message, wParam, lParam);
    };
    wc.hInstance = GetModuleHandle(0);
    wc.lpszClassName = CLASS_NAME;

    static auto _ = RegisterClass(&wc);
    HWND hWnd = CreateWindowEx(
        WS_EX_CLIENTEDGE, CLASS_NAME, CLASS_NAME, WS_OVERLAPPEDWINDOW,
        0, 0, 0, 0,
        NULL, NULL, GetModuleHandle(0), 0);
    SetWindowLongPtrW(hWnd, GWLP_USERDATA, (LONG_PTR)callback);
    ChangeWindowMessageFilterEx(hWnd, LUNA_UPDATE_PREPARED_OK, MSGFLT_ALLOW, nullptr);
    ChangeWindowMessageFilterEx(hWnd, WM_MAGPIE_SCALINGCHANGED, MSGFLT_ALLOW, nullptr);
    MSG msg = {};
    while (GetMessage(&msg, NULL, 0, 0))
    {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
}
#endif
DECLARE_API void globalmessagelistener(void *callback)
{
#ifndef WINXP
    std::thread(std::bind(globalmessagelistener_1, callback)).detach();
#endif
}

DECLARE_API void dispatchcloseevent()
{
#ifndef WINXP
    PostMessage(HWND_BROADCAST, LUNA_UPDATE_PREPARED_OK, 0, 0);
#endif
}