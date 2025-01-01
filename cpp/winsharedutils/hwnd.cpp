#ifndef WINXP
#include <wil/com.h>
#include <uiautomation.h>
#endif
DECLARE_API void showintab(HWND hwnd, bool show, bool tool)
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

DECLARE_API bool pid_running(DWORD pid)
{
    DWORD code;
#ifndef WINXP
    GetExitCodeProcess(AutoHandle(OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid)), &code);
#else
    GetExitCodeProcess(AutoHandle(OpenProcess(PROCESS_QUERY_INFORMATION, FALSE, pid)), &code);
#endif
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
DECLARE_API HWND getpidhwndfirst(DWORD pid)
{
    __EnumWindowsProc info = {pid, 0};
    EnumWindows(EnumWindowsProc, (LPARAM)&info);
    return info.hwnd;
}
namespace
{
    BOOL Is64BitOS()
    {
        SYSTEM_INFO systemInfo = {0};
        GetNativeSystemInfo(&systemInfo);
        return systemInfo.wProcessorArchitecture == PROCESSOR_ARCHITECTURE_AMD64 || systemInfo.wProcessorArchitecture == PROCESSOR_ARCHITECTURE_IA64;
    }
}
DECLARE_API bool Is64bit(DWORD pid)
{
    if (!Is64BitOS())
        return false;
#ifndef WINXP
    auto hprocess = AutoHandle(OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid));
#else
    auto hprocess = AutoHandle(OpenProcess(PROCESS_QUERY_INFORMATION, FALSE, pid));
#endif
    // 進程的控制碼。 控制碼必須具有PROCESS_QUERY_INFORMATION或PROCESS_QUERY_LIMITED_INFORMATION存取權限。 如需詳細資訊，請參閱 處理安全性和存取權限。
    // Windows Server 2003 和 Windows XP： 控制碼必須具有PROCESS_QUERY_INFORMATION存取權限。
    BOOL f64bitProc = false;
    f64bitProc = !(IsWow64Process(hprocess, &f64bitProc) && f64bitProc);
    return f64bitProc;
}

DECLARE_API void getprocesses(void (*cb)(DWORD, const wchar_t *))
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

typedef enum MONITOR_DPI_TYPE
{
    MDT_EFFECTIVE_DPI = 0,
    MDT_ANGULAR_DPI = 1,
    MDT_RAW_DPI = 2,
    MDT_DEFAULT = MDT_EFFECTIVE_DPI
} MONITOR_DPI_TYPE;
DECLARE_API UINT GetMonitorDpiScaling(HWND hwnd)
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

DECLARE_API bool check_window_viewable(HWND hwnd)
{
    RECT windowRect;
    if (!GetWindowRect(hwnd, &windowRect))
        return false;
    HMONITOR hMonitor = MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST);
    if (!hMonitor)
        return false;
    MONITORINFO monitorInfo;
    monitorInfo.cbSize = sizeof(MONITORINFO);
    if (!GetMonitorInfo(hMonitor, &monitorInfo))
        return false;
    RECT _;
    return IntersectRect(&_, &windowRect, &monitorInfo.rcWork);
}

DECLARE_API void GetSelectedText(void (*cb)(const wchar_t *))
{
#ifndef WINXP
    CO_INIT co;
    CHECK_FAILURE_NORET(co);
    try
    {
        // 初始化 COM
        wil::com_ptr<IUIAutomation> automation;
        if (FAILED(CoCreateInstance(CLSID_CUIAutomation, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&automation))) || !automation)
        {
            throw std::runtime_error("无法初始化 UI Automation.");
        }

        // 获取焦点元素
        wil::com_ptr<IUIAutomationElement> focusedElement;
        if (FAILED(automation->GetFocusedElement(&focusedElement)) || !focusedElement)
        {
            throw std::runtime_error("无法获取当前焦点元素.");
        }

        // 检查是否支持 TextPattern
        wil::com_ptr<IUIAutomationTextPattern> textPattern;
        if (FAILED(focusedElement->GetCurrentPatternAs(UIA_TextPatternId, IID_PPV_ARGS(&textPattern))) || !textPattern)
        {
            throw std::runtime_error("当前元素不支持 TextPattern.");
        }

        // 获取选定的文本范围
        wil::com_ptr<IUIAutomationTextRangeArray> selection;
        if (FAILED(textPattern->GetSelection(&selection)) || !selection)
        {
            throw std::runtime_error("无法获取选定的文本范围.");
        }

        // 获取第一个选定范围
        wil::com_ptr<IUIAutomationTextRange> range;
        if (FAILED(selection->GetElement(0, &range)) || !range)
        {
            throw std::runtime_error("没有选定文本.");
        }

        // 提取文本
        wil::unique_bstr text;
        if (FAILED(range->GetText(-1, &text)) || !text)
        {
            throw std::runtime_error("无法提取选定的文本.");
        }
        cb(text.get());
    }
    catch (std::exception &e)
    {
        printf(e.what());
    }
#endif
}
