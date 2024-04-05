#include <windows.h>
#include <thread>
#include <string>
#include "define.h"
HANDLE hsema;
void IsColorSchemeChangeMessage(LPARAM lParam)
{
    if (lParam && CompareStringOrdinal(reinterpret_cast<LPCWCH>(lParam), -1, L"ImmersiveColorSet", -1, TRUE) == CSTR_EQUAL)
    {
        ReleaseSemaphore(hsema, 1, 0);
    }
}
void startdarklistener_1()
{
    const wchar_t CLASS_NAME[] = L"LunaDarkListener";

    WNDCLASS wc = {};
    wc.lpfnWndProc = [](HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
    {
        if (WM_SETTINGCHANGE == message)
            IsColorSchemeChangeMessage(lParam);
        return DefWindowProc(hWnd, message, wParam, lParam);
    };
    wc.hInstance = GetModuleHandle(0);
    wc.lpszClassName = CLASS_NAME;

    static auto _ = RegisterClass(&wc);
    HWND hWnd = CreateWindowEx(
        WS_EX_CLIENTEDGE, CLASS_NAME, CLASS_NAME, WS_OVERLAPPEDWINDOW,
        0, 0, 0, 0,
        NULL, NULL, GetModuleHandle(0), 0);
    MSG msg = {};
    while (GetMessage(&msg, NULL, 0, 0))
    {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
}
HANDLE startdarklistener()
{
    hsema = CreateSemaphoreW(0, 0, 10, 0);
    std::thread(startdarklistener_1).detach();
    return hsema;
}