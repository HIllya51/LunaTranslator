
#include "define.h"
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
wchar_t *clipboard_get()
{
    wchar_t *data = 0;
    if (tryopenclipboard() == false)
        return 0;
    do
    {
        HANDLE hData = GetClipboardData(CF_UNICODETEXT);
        if (hData == 0)
            break;
        LPWSTR pszText = static_cast<LPWSTR>(GlobalLock(hData));
        if (pszText == 0)
            break;
        int sz = GlobalSize(hData);
        data = new wchar_t[sz + 1];
        wcscpy_s(data, sz, pszText);
        data[sz] = 0;
        GlobalUnlock(hData);
    } while (false);
    CloseClipboard();
    return data;
}
bool clipboard_set(HWND hwnd, wchar_t *text)
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
            break;
        wcscpy_s(pchData, len, text);
        GlobalUnlock(hClipboardData);
        SetClipboardData(CF_UNICODETEXT, hClipboardData);
        success = true;

    } while (false);
    CloseClipboard();
    return success;
}

static void clipboard_callback_1(void (*callback)(wchar_t *, bool), HANDLE hsema, HWND *hwnd)
{
    const wchar_t CLASS_NAME[] = L"LunaClipboardListener";

    WNDCLASS wc = {};
    wc.lpfnWndProc = [](HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
    {
        if (WM_CLIPBOARDUPDATE == message)
        {
            auto data = clipboard_get();
            auto callback_ = reinterpret_cast<decltype(callback)>(GetWindowLongPtrW(hWnd, GWLP_USERDATA));
            if (data && callback_)
            {
                auto ohwnd = GetClipboardOwner();
                DWORD pid;
                GetWindowThreadProcessId(ohwnd, &pid);
                callback_(data, pid == GetCurrentProcessId());
                delete data;
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

    *hwnd = hWnd;
    ReleaseSemaphore(hsema, 1, 0);
    MSG msg = {};
    while (GetMessage(&msg, NULL, 0, 0))
    {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
}

DECLARE HWND clipboard_callback(void (*callback)(wchar_t *, bool))
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
DECLARE void clipboard_callback_stop(HWND hwnd)
{
    if (!hwnd)
        return;
    RemoveClipboardFormatListener(hwnd);
    DestroyWindow(hwnd);
}
