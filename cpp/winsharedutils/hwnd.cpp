
#include <uiautomation.h>

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
    CHandle hprocess{OpenProcess(
#ifndef WINXP
        PROCESS_QUERY_LIMITED_INFORMATION,
#else
        PROCESS_QUERY_INFORMATION,
#endif
        FALSE, pid)};
    if (!hprocess)
        return false;
    DWORD code;
    GetExitCodeProcess(hprocess, &code);
    // 句柄必須具有 PROCESS_QUERY_INFORMATION 或 PROCESS_QUERY_LIMITED_INFORMATION 訪問許可權。 如需詳細資訊，請參閱 處理安全性和訪問許可權。
    // Windows Server 2003 和 Windows XP： 句柄必須具有 PROCESS_QUERY_INFORMATION 訪問許可權。
    return code == STILL_ACTIVE;
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
    CHandle hprocess{OpenProcess(
#ifndef WINXP
        PROCESS_QUERY_LIMITED_INFORMATION,
#else
        PROCESS_QUERY_INFORMATION,
#endif
        FALSE, pid)};
    // 進程的控制碼。 控制碼必須具有PROCESS_QUERY_INFORMATION或PROCESS_QUERY_LIMITED_INFORMATION存取權限。 如需詳細資訊，請參閱 處理安全性和存取權限。
    // Windows Server 2003 和 Windows XP： 控制碼必須具有PROCESS_QUERY_INFORMATION存取權限。
    BOOL f64bitProc = false;
    f64bitProc = !(IsWow64Process(hprocess, &f64bitProc) && f64bitProc);
    return f64bitProc;
}

DECLARE_API void getprocesses(void (*cb)(DWORD, const wchar_t *))
{
    std::unordered_map<std::wstring, std::vector<int>> exe_pid;
    CHandle hSnapshot{CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)};
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
    CO_INIT co;
    CHECK_FAILURE_NORET(co);
    try
    {
        // 初始化 COM
        CComPtr<IUIAutomation> automation;
        if (FAILED(CoCreateInstance(CLSID_CUIAutomation, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&automation))) || !automation)
        {
            throw std::runtime_error("无法初始化 UI Automation.");
        }

        // 获取焦点元素
        CComPtr<IUIAutomationElement> focusedElement;
        if (FAILED(automation->GetFocusedElement(&focusedElement)) || !focusedElement)
        {
            throw std::runtime_error("无法获取当前焦点元素.");
        }

        // 检查是否支持 TextPattern
        CComPtr<IUIAutomationTextPattern> textPattern;
        if (FAILED(focusedElement->GetCurrentPatternAs(UIA_TextPatternId, IID_PPV_ARGS(&textPattern))) || !textPattern)
        {
            throw std::runtime_error("当前元素不支持 TextPattern.");
        }

        // 获取选定的文本范围
        CComPtr<IUIAutomationTextRangeArray> selection;
        if (FAILED(textPattern->GetSelection(&selection)) || !selection)
        {
            throw std::runtime_error("无法获取选定的文本范围.");
        }

        // 获取第一个选定范围
        CComPtr<IUIAutomationTextRange> range;
        if (FAILED(selection->GetElement(0, &range)) || !range)
        {
            throw std::runtime_error("没有选定文本.");
        }

        // 提取文本
        CComBSTR text;
        if (FAILED(range->GetText(-1, &text)) || !text)
        {
            throw std::runtime_error("无法提取选定的文本.");
        }
        cb(text);
    }
    catch (std::exception &e)
    {
        printf(e.what());
    }
}

DECLARE_API void *get_allAccess_ptr()
{
    return &allAccess;
}
DECLARE_API HANDLE createprocess(LPCWSTR command, LPCWSTR path, DWORD *pid)
{
    // 防止进程意外退出时，子进程僵死
    std::wstring _ = command;
    STARTUPINFO si = {sizeof(si)};
    si.dwFlags |= STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;
    PROCESS_INFORMATION pi;
    HANDLE hJob = CreateJobObject(NULL, NULL);
    if (!hJob)
        return NULL;
    if (!CreateProcessW(NULL, _.data(), NULL, NULL, FALSE, 0, NULL, path, &si, &pi))
        return NULL;
    CHandle _1{pi.hProcess}, _2{pi.hThread};
    *pid = pi.dwProcessId;
    if (!AssignProcessToJobObject(hJob, pi.hProcess))
        return NULL;
    // 设置Job Object选项，使父进程退出时子进程自动终止
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION jeli = {0};
    jeli.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
    if (!SetInformationJobObject(hJob, JobObjectExtendedLimitInformation, &jeli, sizeof(jeli)))
        return NULL;
    // closehandle会关闭子进程
    return hJob;
}