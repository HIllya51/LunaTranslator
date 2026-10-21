#include <uiautomation.h>
#include <iphlpapi.h>
#include "filemapping.hpp"
#include "osversion.hpp"
#ifdef WINXP
#include "../xpundef/xp_shellscalingapi.h"
#else
#include <shellscalingapi.h>
#endif

DECLARE_API DWORD GetParentProcessID(DWORD pid)
{
    CHandle hSnapshot{CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)};
    if (hSnapshot == INVALID_HANDLE_VALUE)
        return 0;

    PROCESSENTRY32 pe32{};
    pe32.dwSize = sizeof(PROCESSENTRY32);
    auto currpid = GetCurrentProcessId();
    if (Process32First(hSnapshot, &pe32))
    {
        do
        {
            if (pe32.th32ProcessID == pid)
                return pe32.th32ParentProcessID;
        } while (Process32Next(hSnapshot, &pe32));
    }
    return 0;
}
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

bool IsInteractiveUserProcess(DWORD processId)
{
    CHandle hProcess{OpenProcess(FUCKPRIVI,
                                 FALSE, processId)};
    if (!hProcess)
        return false;

    CHandle hToken;
    if (!OpenProcessToken(hProcess, TOKEN_QUERY, &hToken.m_h))
    {
        return false;
    }

    DWORD tokenInfoLength = 0;
    GetTokenInformation(hToken, TokenUser, NULL, 0, &tokenInfoLength);

    std::vector<BYTE> tokenInfo(tokenInfoLength);
    if (GetTokenInformation(hToken, TokenUser, tokenInfo.data(),
                            tokenInfoLength, &tokenInfoLength))
    {
        PTOKEN_USER pTokenUser = (PTOKEN_USER)tokenInfo.data();

        SID_IDENTIFIER_AUTHORITY ntAuthority = SECURITY_NT_AUTHORITY;
        PSID systemSid;
        if (!AllocateAndInitializeSid(&ntAuthority, 1, SECURITY_LOCAL_SYSTEM_RID,
                                      0, 0, 0, 0, 0, 0, 0, &systemSid))
            return false;

        BOOL isSystem = EqualSid(pTokenUser->User.Sid, systemSid);
        FreeSid(systemSid);

        return !isSystem;
    }
    return false;
}
// winutils.cpp：进程可执行文件完整路径（多级权限回退 + 路径换算），
// 失败返回空
extern std::wstring GetProcessFileNameCore(DWORD pid);

static std::wstring ToLowerW(std::wstring s)
{
    std::transform(s.begin(), s.end(), s.begin(), towlower);
    return s;
}

// 进程快照枚举（pid, 可执行文件基名），过滤 System/Registry/
// Memory Compression/Secure System 等（ListProcess 用）
template <typename F>
static void forEachProcess(F &&f){
    CHandle hSnapshot{CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)};
    if (hSnapshot == INVALID_HANDLE_VALUE)
        return;

    PROCESSENTRY32 pe32{};
    pe32.dwSize = sizeof(PROCESSENTRY32);
    if (Process32First(hSnapshot, &pe32))
    {
        do
        {
            // 过滤System,Registry,Memory Compression,Secure System等
            if ((!wcschr(pe32.szExeFile, L'.')) && (!IsInteractiveUserProcess(pe32.th32ProcessID)))
            {
                continue;
            }
            f(pe32.th32ProcessID, pe32.szExeFile);
        } while (Process32Next(hSnapshot, &pe32));
    }
}

// 进程按可执行文件完整路径分组（原 myutils/hwnd.py ListProcess 的
// C++ 版）。exe=NULL：全部进程（跳过 Windows/Microsoft/WindowsApps
// 目录下的），逐组回调 cb(完整路径, pids, 数量)，组序=枚举序；
// exe 给定：先按基名（不区分大小写）筛，最终只回调完整路径与 exe
// 完全一致的组（对齐原 Python 的 ret.get(exe, [])，可能一次都不回调）
DECLARE_API void ListProcess(const wchar_t *exe, void (*cb)(const wchar_t *, DWORD *, DWORD))
{
    std::vector<std::pair<std::wstring, std::vector<DWORD>>> groups;
    std::wstring exebase;
    if (exe)
    {
        exebase = exe;
        auto pos = exebase.find_last_of(L"\\/");
        exebase = ToLowerW(exebase.substr(pos == std::wstring::npos ? 0 : pos + 1));
    }
    auto selfpid = GetCurrentProcessId();
    forEachProcess([&](DWORD pid, const wchar_t *exefile)
    {
        if (pid == selfpid)
            return;
        if (exe && ToLowerW(exefile) != exebase)
            return;
        auto name = GetProcessFileNameCore(pid);
        if (name.empty())
            return;
        if (!exe)
        {
            auto namel = ToLowerW(name);
            if (namel.find(L":\\windows\\") != std::wstring::npos ||
                namel.find(L"\\microsoft\\") != std::wstring::npos ||
                namel.find(L"\\windowsapps\\") != std::wstring::npos)
                return;
        }
        for (auto &g : groups)
            if (g.first == name)
            {
                g.second.push_back(pid);
                return;
            }
        groups.emplace_back(name, std::vector<DWORD>{pid});
    });
    for (auto &g : groups)
    {
        if (exe && g.first != exe)
            continue;
        cb(g.first.c_str(), g.second.data(), (DWORD)g.second.size());
    }
}

// 鼠标点击选窗口：轮询 GetKeyState 直到左键或右键按下（必须
// GetKeyState——GetAsyncKeyState/SetWindowHookEx 都检测不到高权限
// 应用上的点击事件）。左键：取光标处顶层窗口回调 cb(pid, hwnd)；
// 右键：取消，回调 cb(0, NULL)。阻塞直至点击，Python 侧仍以 threader
// 丢工作线程（见 NativeUtils.mouseselectwindow）
DECLARE_API void MouseSelectWindow(void (*cb)(DWORD, HWND))
{
    bool left = false;
    while (true)
    {
        if (GetKeyState(VK_RBUTTON) & 0x8000)
            break;
        if (GetKeyState(VK_LBUTTON) & 0x8000)
        {
            left = true;
            break;
        }
        Sleep(10);
    }
    if (!left)
    {
        cb(0, NULL); // 右键取消
        return;
    }
    POINT pos;
    if (!GetCursorPos(&pos))
        return;
    auto hwnd = GetAncestor(WindowFromPoint(pos), GA_ROOT);
    if (!hwnd)
        return;
    DWORD pid = 0;
    GetWindowThreadProcessId(hwnd, &pid);
    if (pid)
        cb(pid, hwnd);
}

DECLARE_API int GetProcessListenPort(LPCWSTR exesubstr)
{
    std::wstring needle = exesubstr;
    std::transform(needle.begin(), needle.end(), needle.begin(), tolower);

    std::unordered_set<DWORD> pids;
    {
        CHandle hSnapshot{CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)};
        if (hSnapshot != INVALID_HANDLE_VALUE)
        {
            PROCESSENTRY32 pe32{};
            pe32.dwSize = sizeof(pe32);
            if (Process32First(hSnapshot, &pe32))
            {
                do
                {
                    std::wstring name = pe32.szExeFile;
                    std::transform(name.begin(), name.end(), name.begin(), towlower);
                    if (name == needle)
                        pids.insert(pe32.th32ProcessID);
                } while (Process32Next(hSnapshot, &pe32));
            }
        }
    }
    if (pids.empty())
        return 0;

    std::vector<BYTE> buf;
    DWORD size = 0;
    for (int attempt = 0; attempt < 3; attempt++)
    {
        DWORD r = GetExtendedTcpTable(nullptr, &size, FALSE, AF_INET,
                                      TCP_TABLE_OWNER_PID_LISTENER, 0);
        if (r != ERROR_INSUFFICIENT_BUFFER && size == 0)
            return 0;
        buf.assign(size, 0);
        r = GetExtendedTcpTable(buf.data(), &size, FALSE, AF_INET,
                                TCP_TABLE_OWNER_PID_LISTENER, 0);
        if (r == NO_ERROR)
            break;
        if (r != ERROR_INSUFFICIENT_BUFFER)
            return 0;
    }
    if (buf.empty())
        return 0;
    auto owners = (MIB_TCPTABLE_OWNER_PID *)buf.data();
    for (DWORD k = 0; k < owners->dwNumEntries; k++)
    {
        auto item = owners->table[k];
        if (pids.count(item.dwOwningPid) == 0)
            continue;
        return _byteswap_ushort(item.dwLocalPort);
    }
    return 0;
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
    FileMapping fm(file);
    if (!fm.mapAddr)
        return {};
    PIMAGE_NT_HEADERS peHdr = GetImageNtHeader(fm.mapAddr);
    if (!peHdr)
        return {};
    return peHdr->FileHeader.Machine;
}

#ifndef IMAGE_FILE_MACHINE_ARM64
#define IMAGE_FILE_MACHINE_ARM64 0xAA64 // ARM64 Little-Endian
#endif

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
    if constexpr (sizeof(size_t) == 8)
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
    if (!file)
        return false;
    auto type = MyGetBinaryType(file);
    if (!type)
        return false;
    return type.value() == IMAGE_FILE_MACHINE_AMD64;
}

DECLARE_API bool IsDLLBitSameAsMe(LPCWSTR file)
{
    if (!file)
        return false;
    auto type = MyGetBinaryType(file);
    if (!type)
        return false;
    if constexpr (sizeof(size_t) == 8)
        return type.value() == IMAGE_FILE_MACHINE_AMD64;
    else
        return type.value() == IMAGE_FILE_MACHINE_I386;
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
DECLARE_API bool CreateUrlProtocol(LPCWSTR exe)
{
    auto base_path = LR"(Software\Classes\lunatranslator)";
    CRegKey hkey;
    if (ERROR_SUCCESS != hkey.Create(HKEY_CURRENT_USER, base_path))
        return false;
    hkey.SetStringValue(L"", L"URL:lunatranslator");
    hkey.SetStringValue(L"URL Protocol", L"");
    CRegKey hkey2;
    if (ERROR_SUCCESS != hkey2.Create(hkey, LR"(shell\open\command)"))
        return false;
    hkey2.SetStringValue(NULL, (L"\"" + std::wstring(exe) + L"\" --URLProtocol \"%1\"").c_str());
    return true;
}