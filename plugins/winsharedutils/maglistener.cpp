#include "define.h"

static UINT WM_MAGPIE_SCALINGCHANGED = RegisterWindowMessage(L"MagpieScalingChanged");
static HWND listener = 0;
static HANDLE hwrite = 0;

DECLARE HANDLE startmaglistener()
{
    ChangeWindowMessageFilter(WM_MAGPIE_SCALINGCHANGED, MSGFLT_ADD);
    auto CLASS_NAME = L"MagpieWatcher";
    WNDCLASS wc = {};
    wc.lpfnWndProc = [](HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
    {
        if (message == WM_MAGPIE_SCALINGCHANGED && hwrite)
        {
            int send = wParam;
            DWORD _;
            WriteFile(hwrite, &send, 4, &_, 0);
        }
        switch (message)
        {

        case WM_DESTROY:
        {
            CloseHandle(hwrite);
            PostQuitMessage(0);
        }
        }
        return DefWindowProc(hWnd, message, wParam, lParam);
    };
    wc.hInstance = GetModuleHandle(0);
    wc.lpszClassName = CLASS_NAME;
    static auto _ = RegisterClass(&wc);
    HANDLE hread;
    CreatePipe(&hread, &hwrite, 0, 0);

    std::thread([=]()
                {
        listener = CreateWindowEx(
        WS_EX_CLIENTEDGE, CLASS_NAME, CLASS_NAME, WS_OVERLAPPEDWINDOW,
        0, 0, 0, 0,
        NULL, NULL, GetModuleHandle(0), hwrite);;
        MSG msg = {};
        while (GetMessage(&msg, NULL, 0, 0))
        {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        } })
        .detach();

    return hread;
}
DECLARE void endmaglistener(HANDLE hread)
{
    if (listener)
    {
        DestroyWindow(listener);
        listener = 0;
        hwrite = 0;
    }
}