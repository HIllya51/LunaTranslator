#include "define.h"
#include <shellscalingapi.h>
DECLARE void showintab(HWND hwnd, bool show, bool tool)
{
    // WS_EX_TOOLWINDOW可以立即生效，WS_EX_APPWINDOW必须切换焦点才生效。但是WS_EX_TOOLWINDOW会改变窗口样式，因此只对无边框窗口使用。
    LONG style = GetWindowLong(hwnd, GWL_STYLE);
    auto style_ex = GetWindowLong(hwnd, GWL_EXSTYLE);
    if (show)
    {
        style_ex |= WS_EX_APPWINDOW;
        // if ((style & WS_OVERLAPPEDWINDOW) != WS_OVERLAPPEDWINDOW)
        if (tool)
            style_ex &= ~WS_EX_TOOLWINDOW;
    }
    else
    {
        style_ex &= ~WS_EX_APPWINDOW;
        // if ((style & WS_OVERLAPPEDWINDOW) != WS_OVERLAPPEDWINDOW)
        if (tool)
            style_ex |= WS_EX_TOOLWINDOW;
    }
    SetWindowLong(hwnd, GWL_EXSTYLE, style_ex);
}

DECLARE bool pid_running(DWORD pid)
{
    DWORD code;
    GetExitCodeProcess(AutoHandle(OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid)), &code);
    // 句柄必須具有 PROCESS_QUERY_INFORMATION 或 PROCESS_QUERY_LIMITED_INFORMATION 訪問許可權。 如需詳細資訊，請參閱 處理安全性和訪問許可權。
    // Windows Server 2003 和 Windows XP： 句柄必須具有 PROCESS_QUERY_INFORMATION 訪問許可權。
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
        auto hprocess = AutoHandle(OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid));
        // 進程的控制碼。 控制碼必須具有PROCESS_QUERY_INFORMATION或PROCESS_QUERY_LIMITED_INFORMATION存取權限。 如需詳細資訊，請參閱 處理安全性和存取權限。
        // Windows Server 2003 和 Windows XP： 控制碼必須具有PROCESS_QUERY_INFORMATION存取權限。
        BOOL b;
        IsWow64Process(hprocess, &b);
        return !b;
    }
    else
        return false;
}

DECLARE void getprocesses(void (*cb)(DWORD, const wchar_t *))
{
    std::unordered_map<std::wstring, std::vector<int>> exe_pid;
    AutoHandle hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnapshot == INVALID_HANDLE_VALUE)
        return;

    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);
    auto currpid = GetCurrentProcessId();
    if (Process32First(hSnapshot, &pe32))
    {
        do
        {
            cb(pe32.th32ProcessID, pe32.szExeFile);
        } while (Process32Next(hSnapshot, &pe32));
    }
}
DECLARE UINT GetMonitorDpiScaling(HWND hwnd)
{
    HMONITOR hMonitor = MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST);
    if (!hMonitor)
        return 96;
    auto pGetDpiForMonitor = (HRESULT(STDAPICALLTYPE *)(HMONITOR, MONITOR_DPI_TYPE, UINT *, UINT *))GetProcAddress(GetModuleHandleA("Shcore.dll"), "GetDpiForMonitor");
    if (pGetDpiForMonitor)
    {
        UINT dpiX = 0;
        UINT dpiY = 0;
        HRESULT hr = pGetDpiForMonitor(hMonitor, MDT_EFFECTIVE_DPI, &dpiX, &dpiY);
        if (FAILED(hr))
            return 96;
        else
            return dpiX;
    }
    else
    {
        MONITORINFOEX info;
        info.cbSize = sizeof(MONITORINFOEX);
        if (!GetMonitorInfo(hMonitor, &info))
            return 96;
        HDC hdc = GetDC(NULL);
        HDC hdcMonitor = CreateCompatibleDC(hdc);
        HDC hdcMonitorScreen = CreateIC(TEXT("DISPLAY"), info.szDevice, NULL, 0);
        int dpiX = GetDeviceCaps(hdcMonitorScreen, LOGPIXELSX);
        DeleteDC(hdcMonitor);
        DeleteDC(hdcMonitorScreen);
        ReleaseDC(NULL, hdc);
        return dpiX;
    }
}
