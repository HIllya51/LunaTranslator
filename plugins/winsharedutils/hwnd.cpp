#include "define.h"

DECLARE void showintab(HWND hwnd, bool show)
{
    // WS_EX_TOOLWINDOW可以立即生效，WS_EX_APPWINDOW必须切换焦点才生效。但是WS_EX_TOOLWINDOW会改变窗口样式，因此只对无边框窗口使用。
    LONG style = GetWindowLong(hwnd, GWL_STYLE);
    auto style_ex = GetWindowLong(hwnd, GWL_EXSTYLE);
    if (show)
    {
        style_ex |= WS_EX_APPWINDOW;
        if ((style & WS_OVERLAPPEDWINDOW) != WS_OVERLAPPEDWINDOW)
            style_ex &= ~WS_EX_TOOLWINDOW;
    }
    else
    {
        style_ex &= ~WS_EX_APPWINDOW;
        if ((style & WS_OVERLAPPEDWINDOW) != WS_OVERLAPPEDWINDOW)
            style_ex |= WS_EX_TOOLWINDOW;
    }
    SetWindowLong(hwnd, GWL_EXSTYLE, style_ex);
}

struct windowstatus
{
    WINDOWPLACEMENT wpc;
    LONG HWNDStyle, HWNDStyleEx;
};

DECLARE windowstatus letfullscreen(HWND hwnd)
{
    WINDOWPLACEMENT wpc;
    GetWindowPlacement(hwnd, &wpc);
    auto HWNDStyle = GetWindowLong(hwnd, GWL_STYLE);
    auto HWNDStyleEx = GetWindowLong(hwnd, GWL_EXSTYLE);
    auto NewHWNDStyle = HWNDStyle;
    NewHWNDStyle &= ~WS_BORDER;
    NewHWNDStyle &= ~WS_DLGFRAME;
    NewHWNDStyle &= ~WS_THICKFRAME;
    auto NewHWNDStyleEx = HWNDStyleEx;
    NewHWNDStyleEx &= ~WS_EX_WINDOWEDGE;
    SetWindowLong(hwnd, GWL_STYLE, NewHWNDStyle | WS_POPUP);
    SetWindowLong(
        hwnd, GWL_EXSTYLE, NewHWNDStyleEx | WS_EX_TOPMOST);
    ShowWindow(hwnd, SW_SHOWMAXIMIZED);
    return {wpc, HWNDStyle, HWNDStyleEx};
}

DECLARE void recoverwindow(HWND hwnd, windowstatus status)
{
    SetWindowLong(hwnd, GWL_STYLE, status.HWNDStyle);
    SetWindowLong(hwnd, GWL_EXSTYLE, status.HWNDStyleEx);
    ShowWindow(hwnd, SW_SHOWNORMAL);
    SetWindowPlacement(hwnd, &status.wpc);
}
DECLARE bool pid_running(DWORD pid)
{
    DWORD code;
    GetExitCodeProcess(AutoHandle(OpenProcess(PROCESS_QUERY_INFORMATION, FALSE, pid)), &code);
    return code == STILL_ACTIVE;
    // auto process = AutoHandle(OpenProcess(SYNCHRONIZE, FALSE, pid));
    // DWORD ret = WaitForSingleObject(process, 0);
    // return ret == WAIT_TIMEOUT;
}

struct __EnumWindowsProc
{
    DWORD pid;
    HWND hwnd;
};
BOOL CALLBACK EnumWindowsProc(HWND hwnd, LPARAM lParam)
{
    if (IsWindow(hwnd) && IsWindowEnabled(hwnd) & IsWindowVisible(hwnd))
    {
        auto info = (__EnumWindowsProc *)lParam;

        DWORD processId;
        GetWindowThreadProcessId(hwnd, &processId);
        if (info->pid == processId && info->hwnd == 0)
        {
            info->hwnd = hwnd;
        }
    }
    return TRUE;
}
DECLARE HWND getpidhwndfirst(DWORD pid)
{
    __EnumWindowsProc info = {pid, 0};
    EnumWindows(EnumWindowsProc, (LPARAM)&info);
    return info.hwnd;
}

DECLARE bool Is64bit(DWORD pid)
{
    SYSTEM_INFO sysinfo;
    GetNativeSystemInfo(&sysinfo);
    if (sysinfo.wProcessorArchitecture == 9 || sysinfo.wProcessorArchitecture == 6)
    {
        auto hprocess = AutoHandle(OpenProcess(PROCESS_QUERY_INFORMATION, FALSE, pid));
        BOOL b;
        IsWow64Process(hprocess, &b);
        return !b;
    }
    else
        return false;
}