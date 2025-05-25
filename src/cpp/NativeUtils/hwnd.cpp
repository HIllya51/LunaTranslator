#include <dbghelp.h>
#include <uiautomation.h>
#include "osversion.hpp"
#ifndef WINXP
#include <shellscalingapi.h>
#else
#include "../xpundef/xp_shellscalingapi.h"
#endif

#ifndef WINXP
#define FUCKPRIVI PROCESS_QUERY_LIMITED_INFORMATION
#else
#define FUCKPRIVI (GetOSVersion().IsleWinXP() ? PROCESS_QUERY_INFORMATION : PROCESS_QUERY_LIMITED_INFORMATION)
#endif

DECLARE_API void SetWindowInTaskbar(HWND hwnd, bool show, bool tool)
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
DECLARE_API bool IsProcessRunning(DWORD pid)
{
    CHandle hprocess{OpenProcess(FUCKPRIVI, FALSE, pid)};
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
DECLARE_API HWND GetProcessFirstWindow(DWORD pid)
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
    CHandle hprocess{OpenProcess(FUCKPRIVI, FALSE, pid)};
    // 進程的控制碼。 控制碼必須具有PROCESS_QUERY_INFORMATION或PROCESS_QUERY_LIMITED_INFORMATION存取權限。 如需詳細資訊，請參閱 處理安全性和存取權限。
    // Windows Server 2003 和 Windows XP： 控制碼必須具有PROCESS_QUERY_INFORMATION存取權限。
    BOOL f64bitProc = false;
    f64bitProc = !(IsWow64Process(hprocess, &f64bitProc) && f64bitProc);
    return f64bitProc;
}

DECLARE_API void ListProcesses(void (*cb)(DWORD, const wchar_t *))
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

DECLARE_API bool IsWindowViewable(HWND hwnd)
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

DECLARE_API bool GetSelectedText(void (*cb)(const wchar_t *))
{
    bool succ = true;
    try
    {
        CO_INIT co;
        if (FAILED(co))
            throw std::runtime_error("");
        // 初始化 COM
        CComPtr<IUIAutomation> automation;
        if (FAILED(CoCreateInstance(CLSID_CUIAutomation, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&automation))) || !automation)
        {
            succ = false;
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
            succ = false;
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
    return succ;
}
DECLARE_API HANDLE SimpleCreateEvent(LPCWSTR N)
{
    return CreateEventW(&allAccess, FALSE, FALSE, N);
}
DECLARE_API HANDLE SimpleCreateMutex(LPCWSTR N)
{
    return CreateMutexW(&allAccess, FALSE, N);
}
DECLARE_API HANDLE CreateAutoKillProcess(LPCWSTR command, LPCWSTR path, DWORD *pid)
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

DECLARE_API void OpenFileEx(LPCWSTR file)
{
    OPENASINFO INFO;
    INFO.pcszFile = file;
    INFO.oaifInFlags = OAIF_EXEC;
    if (FAILED(SHOpenWithDialog(NULL, &INFO)))
    {
        ShellExecuteW(NULL, L"open", file, NULL, NULL, SW_SHOWNORMAL);
    }
}
DECLARE_API bool IsDLLBit64(LPCWSTR file)
{
    CHandle hFile{CreateFileW(file, GENERIC_READ, FILE_SHARE_READ, 0,
                              OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0)};
    if (!hFile)
        return false;
    CHandle hMap{CreateFileMappingW(
        hFile,
        NULL,          // security attrs
        PAGE_READONLY, // protection flags
        0,             // max size - high DWORD
        0,             // max size - low DWORD
        NULL)};        // mapping name - not used
    if (!hMap)
        return false;

    // next, map the file to our address space
    void *mapAddr = MapViewOfFileEx(
        hMap,          // mapping object
        FILE_MAP_READ, // desired access
        0,             // loc to map - hi DWORD
        0,             // loc to map - lo DWORD
        0,             // #bytes to map - 0=all
        NULL);         // suggested map addr
    if (!mapAddr)
        return false;
    auto peHdr = ImageNtHeader(mapAddr);
    auto is64 = peHdr->FileHeader.Machine == IMAGE_FILE_MACHINE_AMD64;
    UnmapViewOfFile(mapAddr);
    return is64;
}

typedef struct
{
    DWORD ExitStatus;
    DWORD PebBaseAddress;
    DWORD AffinityMask;
    DWORD BasePriority;
    ULONG UniqueProcessId;
    ULONG InheritedFromUniqueProcessId;
} PROCESS_BASIC_INFORMATION;

#define ProcessBasicInformation 0
typedef LONG(__stdcall *PROCNTQSIP)(HANDLE, UINT, PVOID, ULONG, PULONG);

DECLARE_API DWORD GetParentProcessID(DWORD dwProcessId)
{
    LONG status;
    DWORD dwParentPID = (DWORD)-1;
    PROCESS_BASIC_INFORMATION pbi;

    PROCNTQSIP NtQueryInformationProcess = (PROCNTQSIP)GetProcAddress(
        GetModuleHandle(L"ntdll"), "NtQueryInformationProcess");

    if (NULL == NtQueryInformationProcess)
    {
        return (DWORD)-1;
    }
    // Get process handle
    CHandle hProcess{OpenProcess(PROCESS_QUERY_INFORMATION, FALSE, dwProcessId)};
    if (!hProcess)
    {
        return (DWORD)-1;
    }

    // Retrieve information
    status = NtQueryInformationProcess(hProcess,
                                       ProcessBasicInformation,
                                       (PVOID)&pbi,
                                       sizeof(PROCESS_BASIC_INFORMATION),
                                       NULL);

    // Copy parent Id on success
    if (!status)
    {
        dwParentPID = pbi.InheritedFromUniqueProcessId;
    }

    return dwParentPID;
}
DECLARE_API void MouseMoveWindow(HWND hwnd)
{
    ReleaseCapture();
    SendMessage(hwnd, WM_SYSCOMMAND, SC_MOVE | HTCAPTION, NULL);
}

DECLARE_API bool NeedUseSysMove()
{
    int numMonitors = GetSystemMetrics(SM_CMONITORS);
    if (numMonitors <= 1)
        return false;
    std::set<UINT> dpis;
    EnumDisplayMonitors(NULL, NULL, [](HMONITOR hMonitor, HDC, LPRECT, LPARAM lp) -> BOOL
                        {
                            auto dpis=(std::set<UINT>*)lp;
                            UINT dpiX, dpiY;
                            if (SUCCEEDED(GetDpiForMonitor(hMonitor, MDT_EFFECTIVE_DPI, &dpiX, &dpiY)))
                            {
                                dpis->insert(dpiX);
                            }
                            return TRUE; }, (LPARAM)&dpis);
    return dpis.size() >= 2;
}