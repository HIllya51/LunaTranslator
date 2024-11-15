

bool tryopenclipboard(HWND hwnd = 0)
{
    bool success = false;
    for (int i = 0; i < 50; i++)
    {
        if (OpenClipboard(hwnd))
        {
            success = true;
            break;
        }
        else
        {
            Sleep(10);
        }
    }
    return success;
}

std::optional<std::wstring> clipboard_get_internal()
{
    std::optional<std::wstring> data = {};
    if (tryopenclipboard() == false)
        return {};
    do
    {
        HANDLE hData = GetClipboardData(CF_UNICODETEXT);
        if (hData == 0)
            break;
        LPWSTR pszText = static_cast<LPWSTR>(GlobalLock(hData));
        if (pszText == 0)
            break;
        data = std::move(std::wstring(pszText));
        GlobalUnlock(hData);
    } while (false);
    CloseClipboard();
    return data;
}

DECLARE_API bool clipboard_get(void (*cb)(const wchar_t *))
{
    auto data = std::move(clipboard_get_internal());
    if (!data)
        return false;
    cb(data.value().c_str());
    return true;
}

DECLARE_API bool clipboard_set(HWND hwnd, wchar_t *text)
{
    bool success = false;
    // static HWND hwnd=CreateWindowExA(0,"STATIC",0,0,0,0,0,0,0,0,0,0);
    if (tryopenclipboard(hwnd) == false)
        return false;
    EmptyClipboard();
    do
    {
        HGLOBAL hClipboardData;
        size_t len = wcslen(text) + 1;
        hClipboardData = GlobalAlloc(GMEM_MOVEABLE, len * sizeof(wchar_t));
        if (hClipboardData == 0)
            break;
        auto pchData = (wchar_t *)GlobalLock(hClipboardData);
        if (pchData == 0)
        {
            GlobalFree(hClipboardData);
            break;
        }
        wcscpy_s(pchData, len, text);
        GlobalUnlock(hClipboardData);
        if (SetClipboardData(CF_UNICODETEXT, hClipboardData))
            success = true;
        else
        {
            GlobalFree(hClipboardData);
        }

    } while (false);
    CloseClipboard();
    return success;
}

static void clipboard_callback_1(void (*callback)(const wchar_t *, bool), HANDLE hsema, HWND *hwnd)
{
    const wchar_t CLASS_NAME[] = L"LunaClipboardListener";

    WNDCLASS wc = {};
    wc.lpfnWndProc = [](HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
    {
        static auto callbackx = [](HWND hWnd)
        {
            auto data = clipboard_get_internal();
            auto callback_ = reinterpret_cast<decltype(callback)>(GetWindowLongPtrW(hWnd, GWLP_USERDATA));
            if (data && callback_)
            {
                auto ohwnd = GetClipboardOwner();
                DWORD pid;
                GetWindowThreadProcessId(ohwnd, &pid);
                callback_(data.value().c_str(), pid == GetCurrentProcessId());
            }
        };
#ifndef WINXP
        if (WM_CLIPBOARDUPDATE == message)
        {
            callbackx(hWnd);
        }
#else
        // 根据文档，这样做是正确的，且在win11下管用。但到xp上就读不到了。。
        static HWND nextviewer;
        switch (message)
        {
        case WM_CREATE:
        {
            nextviewer = SetClipboardViewer(hWnd);
        }
        break;
        case WM_CHANGECBCHAIN:
        {
            if ((HWND)wParam == nextviewer)
                nextviewer = (HWND)lParam;
            if (nextviewer)
                SendMessage(nextviewer, message, wParam, lParam);
        }
        break;
        case WM_DESTROY:
        {
            ChangeClipboardChain(hWnd, nextviewer);
        }
        break;
        case WM_DRAWCLIPBOARD:
        {
            callbackx(hWnd);
            if (nextviewer)
                SendMessage(nextviewer, message, wParam, lParam);
        }
        }
#endif
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

    *hwnd = hWnd;
    ReleaseSemaphore(hsema, 1, 0);
    MSG msg = {};
    while (GetMessage(&msg, NULL, 0, 0))
    {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
}
#ifndef WINXP
DECLARE_API HWND clipboard_callback(void (*callback)(const wchar_t *, bool))
{
    HANDLE hsema = CreateSemaphoreW(0, 0, 10, 0);
    HWND hwnd;

    std::thread(std::bind(clipboard_callback_1, callback, hsema, &hwnd)).detach();

    WaitForSingleObject(hsema, INFINITE);
    CloseHandle(hsema);
    if (AddClipboardFormatListener(hwnd))
        return hwnd;
    else
        return NULL;
}
#else
static int running = false;
DECLARE_API HWND clipboard_callback(void (*callback)(const wchar_t *, bool))
{
    running = true;
    std::thread([=]()
                {
        std::wstring last;
        while(running){
            Sleep(100);
            auto data = clipboard_get_internal();
            if(data){
                if(last==data.value())continue;
                last=data.value();
                auto ohwnd = GetClipboardOwner();
                DWORD pid;
                GetWindowThreadProcessId(ohwnd, &pid);
                callback(data.value().c_str(), pid == GetCurrentProcessId());
            }
        } })
        .detach();
    return NULL;
}
#endif
DECLARE_API void clipboard_callback_stop(HWND hwnd)
{
#ifndef WINXP
    if (!hwnd)
        return;
    RemoveClipboardFormatListener(hwnd);
    DestroyWindow(hwnd);
#else
    running = false;
#endif
}

DECLARE_API bool clipboard_set_image(HWND hwnd, void *ptr, size_t size)
{
    size -= sizeof(BITMAPFILEHEADER);
    HGLOBAL hDib = GlobalAlloc(GMEM_MOVEABLE, size);
    if (!hDib)
        return false;
    void *pDib = GlobalLock(hDib);
    if (!pDib)
    {
        GlobalFree(hDib);
        return false;
    }
    memcpy((char *)pDib, (char *)ptr + sizeof(BITMAPFILEHEADER), size);
    if (tryopenclipboard(hwnd) == false)
        return false;
    EmptyClipboard();
    if (!SetClipboardData(CF_DIB, hDib))
    {
        GlobalFree(hDib);
        CloseClipboard();
        return false;
    }
    CloseClipboard();
    return true;
}
