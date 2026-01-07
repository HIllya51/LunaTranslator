#include <dbghelp.h>
#include <uiautomation.h>
#include "osversion.hpp"
#ifndef WINXP
#include <shellscalingapi.h>
#else
#include "../xpundef/xp_shellscalingapi.h"
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
    if (!hprocess)
        return false;
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
#define preparelc(pid)                                                                                                          \
    CO_INIT co;                                                                                                                 \
    if (FAILED(co))                                                                                                             \
        return;                                                                                                                 \
    CComPtr<IUIAutomation> automation;                                                                                          \
    if (FAILED(CoCreateInstance(CLSID_CUIAutomation, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&automation))) || !automation) \
        return;                                                                                                                 \
    AutoVariant var_pid;                                                                                                        \
    V_VT(&var_pid) = VT_I4;                                                                                                     \
    V_I4(&var_pid) = pid;                                                                                                       \
    CComPtr<IUIAutomationCondition> condition_pid;                                                                              \
    if (FAILED(automation->CreatePropertyCondition(UIA_ProcessIdPropertyId, var_pid, &condition_pid)) || !condition_pid)        \
        return;                                                                                                                 \
    CComPtr<IUIAutomationElement> pRoot;                                                                                        \
    if (FAILED(automation->GetRootElement(&pRoot)) || !pRoot)                                                                   \
        return;                                                                                                                 \
    CComPtr<IUIAutomationElement> element;                                                                                      \
    if (FAILED(pRoot->FindFirst(TreeScope_Children, condition_pid, &element)) || !element)                                      \
        return;                                                                                                                 \
    CComBSTR className;                                                                                                         \
    if (FAILED(element->get_CurrentClassName(&className)))                                                                      \
        return;                                                                                                                 \
    if (className != L"LiveCaptionsDesktopWindow")                                                                              \
        return;
DECLARE_API void ShowLiveCaptionsWindow(DWORD pid, bool show)
{
    preparelc(pid);

    UIA_HWND hwnd;
    if (FAILED(element->get_CurrentNativeWindowHandle(&hwnd)))
        return;
    if (show)
    {
        SetWindowLong((HWND)hwnd, GWL_EXSTYLE, GetWindowLong((HWND)hwnd, GWL_EXSTYLE) & ~WS_EX_TOOLWINDOW);
        ShowWindow((HWND)hwnd, SW_RESTORE);
    }
    else
    {
        ShowWindow((HWND)hwnd, SW_MINIMIZE);
        SetWindowLong((HWND)hwnd, GWL_EXSTYLE, GetWindowLong((HWND)hwnd, GWL_EXSTYLE) | WS_EX_TOOLWINDOW);
    }
}
DECLARE_API void GetLiveCaptionsText(DWORD pid, void (*cb)(const wchar_t *))
{
    preparelc(pid);

    AutoVariant CaptionsTextBlock;
    V_VT(&CaptionsTextBlock) = VT_BSTR;
    CComBSTR BSCaptionsTextBlock = L"CaptionsTextBlock";
    V_BSTR(&CaptionsTextBlock) = BSCaptionsTextBlock;
    CComPtr<IUIAutomationCondition> condition;
    if (FAILED(automation->CreatePropertyCondition(UIA_AutomationIdPropertyId, CaptionsTextBlock, &condition)) || !condition)
        return;

    CComPtr<IUIAutomationElementArray> elements;
    if (FAILED(element->FindAll(TreeScope_Descendants, condition, &elements)) || !elements)
        return;
    int length;
    if (FAILED(elements->get_Length(&length)))
        return;
    std::wstring result;
    for (int i = 0; i < length; i++)
    {
        CComPtr<IUIAutomationElement> subele;
        if (FAILED(elements->GetElement(i, &subele)) || !subele)
            continue;
        CComBSTR subres;
        if (FAILED(subele->get_CurrentName(&subres)))
            continue;
        result += subres;
    }
    cb(result.c_str());
}
DECLARE_API bool GetSelectedText(void (*cb)(const wchar_t *))
{
    CO_INIT co;
    if (FAILED(co))
        return false;
    // 初始化 COM
    CComPtr<IUIAutomation> automation;
    if (FAILED(CoCreateInstance(CLSID_CUIAutomation, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&automation))) || !automation)
    {
        return false;
    }

    // 获取焦点元素
    CComPtr<IUIAutomationElement> focusedElement;
    if (FAILED(automation->GetFocusedElement(&focusedElement)) || !focusedElement)
    {
        return true;
    }

    // 检查是否支持 TextPattern
    CComPtr<IUIAutomationTextPattern> textPattern;
    if (FAILED(focusedElement->GetCurrentPatternAs(UIA_TextPatternId, IID_PPV_ARGS(&textPattern))) || !textPattern)
    {
        return false;
    }

    // 获取选定的文本范围
    CComPtr<IUIAutomationTextRangeArray> selection;
    if (FAILED(textPattern->GetSelection(&selection)) || !selection)
    {
        return true;
    }

    // 获取第一个选定范围
    CComPtr<IUIAutomationTextRange> range;
    if (FAILED(selection->GetElement(0, &range)) || !range)
    {
        return true;
    }

    // 提取文本
    CComBSTR text;
    if (FAILED(range->GetText(-1, &text)) || !text)
    {
        return true;
    }
    cb(text);
    return true;
}
DECLARE_API LPSECURITY_ATTRIBUTES GetSecurityAttributes()
{
    return &allAccess;
}
DECLARE_API void SetJobAutoKill(HANDLE hJob, bool kill)
{
    if (!hJob)
        return;
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION jeli = {0};
    jeli.BasicLimitInformation.LimitFlags = kill ? JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE : 0;
    SetInformationJobObject(hJob, JobObjectExtendedLimitInformation, &jeli, sizeof(jeli));
}
static HANDLE CreateJobAndAssignProcess(HANDLE hp, bool kill)
{
    if (!hp)
        return NULL;
    HANDLE hJob = CreateJobObject(NULL, NULL);
    if (!hJob)
        return NULL;
    if (!AssignProcessToJobObject(hJob, hp))
        return NULL;
    // 设置Job Object选项，使父进程退出时子进程自动终止
    SetJobAutoKill(hJob, kill);
    // closehandle会关闭子进程
    return hJob;
}
DECLARE_API HANDLE CreateJobForProcess(DWORD pid, bool kill)
{
    CHandle hp{OpenProcess(PROCESS_SET_QUOTA | PROCESS_TERMINATE, FALSE, pid)};
    return CreateJobAndAssignProcess(hp, kill);
}
DECLARE_API HANDLE CreateProcessWithJob(LPCWSTR command, LPCWSTR path, DWORD *pid, bool hide, bool kill)
{
    // 防止进程意外退出时，子进程僵死
    std::wstring _ = command;
    STARTUPINFO si = {sizeof(si)};
    if (hide)
    {
        si.dwFlags |= STARTF_USESHOWWINDOW;
        si.wShowWindow = SW_HIDE;
    }
    PROCESS_INFORMATION pi;
    if (!CreateProcessW(NULL, _.data(), NULL, NULL, FALSE, 0, NULL, path, &si, &pi))
        return NULL;
    CHandle _1{pi.hProcess}, _2{pi.hThread};
    *pid = pi.dwProcessId;
    return CreateJobAndAssignProcess(pi.hProcess, kill);
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

std::optional<WORD> MyGetBinaryType(LPCWSTR file)
{
    CHandle hFile{CreateFileW(file, GENERIC_READ, FILE_SHARE_READ, 0,
                              OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0)};
    if (!hFile)
        return {};
    CHandle hMap{CreateFileMappingW(
        hFile,
        NULL,          // security attrs
        PAGE_READONLY, // protection flags
        0,             // max size - high DWORD
        0,             // max size - low DWORD
        NULL)};        // mapping name - not used
    if (!hMap)
        return {};

    // next, map the file to our address space
    void *mapAddr = MapViewOfFileEx(
        hMap,          // mapping object
        FILE_MAP_READ, // desired access
        0,             // loc to map - hi DWORD
        0,             // loc to map - lo DWORD
        0,             // #bytes to map - 0=all
        NULL);         // suggested map addr
    if (!mapAddr)
        return {};
    auto peHdr = ImageNtHeader(mapAddr);
    auto type = peHdr->FileHeader.Machine;
    UnmapViewOfFile(mapAddr);
    return type;
}

SHAREFUNCTION std::optional<std::wstring> SearchDllPath(const std::wstring &dll)
{
    auto len = SearchPathW(NULL, dll.c_str(), NULL, 0, NULL, NULL);
    if (!len)
        return {};
    std::wstring buff;
    buff.resize(len);
    len = SearchPathW(NULL, dll.c_str(), NULL, len, buff.data(), NULL);
    if (!len)
        return {};
    auto type = MyGetBinaryType(buff.c_str());
    if (!type)
        return {};
    if (type.value() == IMAGE_FILE_MACHINE_ARM64)
        return {};
    return buff;
}

DECLARE_API void SearchDllPath(LPCWSTR file, void (*cb)(LPCWSTR))
{
    if (auto _ = SearchDllPath(file))
    {
        cb(_.value().c_str());
    }
}

DECLARE_API bool IsDLLBit64(LPCWSTR file)
{
    auto type = MyGetBinaryType(file);
    if (!type)
        return false;
    return type.value() == IMAGE_FILE_MACHINE_AMD64;
}

typedef struct
{
    DWORD ExitStatus;
    DWORD PebBaseAddress;
    DWORD AffinityMask;
    DWORD BasePriority;
    ULONG UniqueProcessId;
    ULONG InheritedFromUniqueProcessId;
} __PROCESS_BASIC_INFORMATION;

#define ProcessBasicInformation 0
typedef LONG(__stdcall *PROCNTQSIP)(HANDLE, UINT, PVOID, ULONG, PULONG);

DECLARE_API DWORD GetParentProcessID(DWORD dwProcessId)
{
    LONG status;
    DWORD dwParentPID = (DWORD)-1;
    __PROCESS_BASIC_INFORMATION pbi;

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
                                       sizeof(__PROCESS_BASIC_INFORMATION),
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

DECLARE_API bool IsMultiDifferentDPI()
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