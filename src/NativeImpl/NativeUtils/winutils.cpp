#include "osversion.hpp"
#include <cstdarg>
#include <winnetwk.h>

#ifndef WDA_EXCLUDEFROMCAPTURE
#define WDA_EXCLUDEFROMCAPTURE 0x11
#endif

namespace
{
    // GetModuleFileNameExW 可能莫名其妙得到短路径，导致部分路径无法匹配
    std::wstring GetLongPath(const std::wstring &file)
    {
        auto sz = GetLongPathNameW(file.c_str(), nullptr, 0);
        if (!sz)
            return file;
        std::wstring buff(sz + 1, L'\0');
        GetLongPathNameW(file.c_str(), buff.data(), sz);
        buff.resize(wcslen(buff.c_str()));
        return buff;
    }

    // CreateFile + GetFinalPathNameByHandleW 查询 DOS 路径
    std::wstring ParseUNCEx(const std::wstring &v, DWORD t)
    {
        CHandle hFile{CreateFileW(v.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr,
                                  OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr)};
        if (!hFile)
            return {};
        auto sz = GetFinalPathNameByHandleW(hFile, nullptr, 0, t);
        if (!sz)
            return {};
        std::wstring buff(sz + 1, L'\0');
        GetFinalPathNameByHandleW(hFile, buff.data(), sz, t);
        buff.resize(wcslen(buff.c_str()));
        return buff;
    }

    // NT/UNC 设备路径 → 盘符路径。我操了，使用管理员权限时 QueryDosDevice
    // 会失败，回退 WNetGetUniversalNameW
    std::wstring CheckUNCFile(const std::wstring &v)
    {
        std::wstring drives(300, L'\0');
        auto result = GetLogicalDriveStringsW((DWORD)drives.size(), drives.data());
        if (!result)
            return {};
        if (result > drives.size())
        {
            drives.resize(result + 1);
            result = GetLogicalDriveStringsW((DWORD)drives.size() - 1, drives.data());
        }
        drives.resize(result);
        std::vector<std::wstring> drv;
        for (size_t i = 0; i < drives.size();)
        {
            auto j = drives.find(L'\0', i);
            if (j == std::wstring::npos)
                j = drives.size();
            if (j > i)
                drv.emplace_back(drives.substr(i, j - i));
            i = j + 1;
        }
        for (auto &drive : drv)
        {
            auto letter = drive.substr(0, drive.size() - 1); // 去掉尾部 "\"
            {
                std::wstring buf(65536, L'\0');
                if (QueryDosDeviceW(letter.c_str(), buf.data(), (DWORD)buf.size()))
                {
                    std::wstring prefixdos(buf.data());
                    if (v._Starts_with(prefixdos))
                        return letter + v.substr(prefixdos.size());
                }
            }
            {
                std::wstring buf(65536, L'\0');
                DWORD size = (DWORD)buf.size();
                if (WNetGetUniversalNameW(letter.c_str(), UNIVERSAL_NAME_INFO_LEVEL,
                                          buf.data(), &size) == 0)
                {
                    auto prefixnetwork = ((UNIVERSAL_NAME_INFOW *)buf.data())->lpUniversalName;
                    if (prefixnetwork && prefixnetwork[0] && v._Starts_with(prefixnetwork))
                        return letter + v.substr(wcslen(prefixnetwork));
                }
            }
        }
        return {};
    }

    std::wstring CheckMaybeUNCFile(const std::wstring &v)
    {
        if (!v._Starts_with(L"\\"))
            return v;
        auto res = CheckUNCFile(v);
        if (!res.empty())
            return res;
        // 有时候GetModuleFileNameExW返回的就是VOLUME_NAME_GUID（例如sshfs），
        // 无法CreateFile，但是可以QueryDosDevice查询到；mac上parallel返回的NT
        // 路径无法用QueryDosDevice查询到（应该是需要再额外查注册表处理一下才行，
        // 所以只好用GetFinalPathNameByHandleW去查DOS路径。
        // 获取的结果是\\?\的UNC路径。虽然没办法转成X:\xxxx，但实测可以管用。
        auto dos = ParseUNCEx(v, VOLUME_NAME_DOS);
        if (!dos.empty())
        {
            if (dos._Starts_with(L"\\\\?\\"))
                // 虽然这个东西很真实，但实际上大部分程序根本不适配，
                // 他只在长路径下实际有意义，否则反而使一些东西运行不正常
                dos = dos.substr(4);
            return dos;
        }
        return v;
    }
}

// NT/UNC 设备路径 → 盘符路径（供 os.startfile / 图标提取等无法处理
// NT 路径的场合单独使用）。失败返回原值。
DECLARE_API void CheckMaybeUNCFile(const wchar_t *v, void (*cb)(const wchar_t *))
{
    cb(CheckMaybeUNCFile(std::wstring(v)).c_str());
}

// 进程可执行文件路径核心（递减权限打开进程 + 三级 API 回退
// （GetModuleFileNameExW → QueryFullProcessImageNameW → GetProcessImageFileNameW）
// + NT/UNC 设备路径换算 + 短路径修补）。失败返回空。
// GetProcessFileName 导出与 hwnd.cpp 的 ListProcess 共用
std::wstring GetProcessFileNameCore(DWORD pid)
{
    // 如果能 PROCESS_ALL_ACCESS，那最好，因为一些特殊路径在这个权限下可以不需要处理
    static const DWORD accesses[] = {
        PROCESS_ALL_ACCESS,
        PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, // GetModuleFileNameExW
        PROCESS_QUERY_INFORMATION,                   // XP
        PROCESS_QUERY_LIMITED_INFORMATION,
    };
    for (auto access : accesses)
    {
        CHandle hproc{OpenProcess(access, FALSE, pid)};
        if (!hproc)
            continue;
        std::wstring w(65536, L'\0');
        // 这三者越前面的越直接得到好路径，后面的经常得到辣鸡路径
        DWORD size = (DWORD)w.size();
        if (GetModuleFileNameExW(hproc, nullptr, w.data(), (DWORD)w.size()) == 0 &&
            QueryFullProcessImageNameW(hproc, 0, w.data(), &size) == 0 &&
            GetProcessImageFileNameW(hproc, w.data(), (DWORD)w.size()) == 0)
            continue;
        auto v = CheckMaybeUNCFile(std::wstring(w.data()));
        if (v.empty())
            continue;
        v = GetLongPath(v);
        if (v.empty())
            continue;
        return v;
    }
    return {};
}

// 进程可执行文件路径（cb 形式，失败不回调）
DECLARE_API void GetProcessFileName(DWORD pid, void (*cb)(const wchar_t *))
{
    auto v = GetProcessFileNameCore(pid);
    if (!v.empty())
        cb(v.c_str());
}

// 一组进程是否都能以注入所需权限打开（OpenProcess 成功即视为可注入；
// 权限不足/已退出则失败）。变参：count 后跟 count 个 DWORD pid——
// Python 侧 ctypes 直接变参调用（不设 argtypes），见
// NativeUtils.test_injectable
DECLARE_API bool TestInjectable(int count, ...)
{
    // 与 windows.py 的 PROCESS_INJECT_ACCESS 保持一致
    const DWORD access = PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION |
                         PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE;
    va_list args;
    va_start(args, count);
    bool ok = true;
    for (int i = 0; i < count; i++)
    {
        CHandle hproc{OpenProcess(access, FALSE, va_arg(args, DWORD))};
        if (!hproc)
        {
            ok = false;
            break;
        }
    }
    va_end(args);
    return ok;
}

// FormatMessageW ALLOCATE_BUFFER 杂耍：系统错误码 → 文本
DECLARE_API void WinErrorMessage(DWORD code, HMODULE module, void (*cb)(const wchar_t *))
{
    DWORD flag = FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM |
                 FORMAT_MESSAGE_IGNORE_INSERTS;
    if (module)
        flag |= FORMAT_MESSAGE_FROM_HMODULE;
    wchar_t *mess = nullptr;
    auto length = FormatMessageW(flag, (LPCVOID)module, code, 0x400, (LPWSTR)&mess, 0, nullptr);
    if (!mess)
    {
        cb(L"");
        return;
    }
    std::wstring res(mess, length);
    LocalFree(mess);
    auto a = res.find_first_not_of(L" \t\r\n");
    if (a == std::wstring::npos)
    {
        cb(L"");
        return;
    }
    auto b = res.find_last_not_of(L" \t\r\n");
    cb(res.substr(a, b - a + 1).c_str());
}

// WDA_EXCLUDEFROMCAPTURE（Win10 2004+）：窗口对用户照常可见，但不出现在
// BitBlt/PrintWindow 等截图里（OCR 选框/覆盖层共用，防止识别到自己的界面）。
// 旧系统上 0x11 会被当成黑矩形，不设置。
DECLARE_API bool ExcludeFromCapture(HWND hwnd)
{
    if (!GetOSVersion().Isge20H1())
        return false;
    return SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE);
}

// 取消截图排除（WDA_NONE）：配合 ExcludeFromCapture 的"截图瞬间临时
// 排除、截完恢复"（默认不排除，录屏要能录到译文）
DECLARE_API bool ClearFromCapture(HWND hwnd)
{
    return SetWindowDisplayAffinity(hwnd, WDA_NONE);
}

// 将窗口命中测试区域限制为宽度为 border 的四条边框，内部鼠标穿透。
// SetWindowRgn 后系统接管 rgn，不可再 DeleteObject
DECLARE_API void SetWindowFrameRgn(HWND hwnd, int w, int h, int border)
{
    border = std::max(1, border);
    auto rgn = CreateRectRgn(0, 0, border, h); // 左
    auto tmp = CreateRectRgn(0, 0, w, border); // 上
    CombineRgn(rgn, rgn, tmp, RGN_OR);
    DeleteObject(tmp);
    tmp = CreateRectRgn(std::max(0, w - border), 0, w, h); // 右
    CombineRgn(rgn, rgn, tmp, RGN_OR);
    DeleteObject(tmp);
    tmp = CreateRectRgn(0, std::max(0, h - border), w, h); // 下
    CombineRgn(rgn, rgn, tmp, RGN_OR);
    DeleteObject(tmp);
    SetWindowRgn(hwnd, rgn, TRUE);
}

DECLARE_API void ClearWindowRgn(HWND hwnd)
{
    SetWindowRgn(hwnd, 0, TRUE);
}

// 失败（如 XP 无此 API，yythunk 桩返回失败）返回 false，不回调
DECLARE_API bool LCIDToLocaleNameEx(LCID lcid, void (*cb)(const wchar_t *))
{
    wchar_t buff[LOCALE_NAME_MAX_LENGTH] = {};
    if (!LCIDToLocaleName(lcid, buff, LOCALE_NAME_MAX_LENGTH, 0))
        return false;
    cb(buff);
    return true;
}

// ---- Wine：WebView2 扩展调用的 COM 消息过滤器 ----
// Wine 11 不实现 CoWaitForMultipleHandles 的 COWAIT_DISPATCH_WINDOW_MESSAGES
// 泵消息：扩展 API（list/add/enable/rm）等待 Chromium 应答，而应答是投递到
// Chrome_MessageWindow（message-only 窗口）的任务消息，永远得不到分发 → 死锁。
// 临时注册 IMessageFilter，COM 等待进入 pending 时回调 MessagePending，只泵
// 本线程的 Chrome 任务窗口（不动 Qt 输入事件、不碰 WebView 对象）。
// ntdll 是否带 wine_get_version 导出（在 Wine 上运行）
DECLARE_API bool IsRunningOnWine()
{
    auto h = GetModuleHandleW(L"ntdll.dll");
    if (!h)
        return false;
    return GetProcAddress(h, "wine_get_version") != nullptr;
}

namespace
{
    class ChromeTaskPumpFilter : public IMessageFilter
    {
        std::vector<HWND> windows;
        bool dispatching = false;

    public:
        // 注册用的静态实例，永不被销毁，计数只走形式
        ULONG STDMETHODCALLTYPE AddRef() override { return 2; }
        ULONG STDMETHODCALLTYPE Release() override { return 1; }
        HRESULT STDMETHODCALLTYPE QueryInterface(REFIID riid, void **ppv) override
        {
            if (!ppv)
                return E_POINTER;
            if (IsEqualIID(riid, __uuidof(IUnknown)) ||
                IsEqualIID(riid, __uuidof(IMessageFilter)))
            {
                *ppv = static_cast<IMessageFilter *>(this);
                return S_OK;
            }
            *ppv = nullptr;
            return E_NOINTERFACE;
        }
        // 其余决定交给旧过滤器（有的话），否则用默认值
        DWORD STDMETHODCALLTYPE HandleInComingCall(DWORD dwCallType, HTASK htaskCaller,
                                                   DWORD dwTickCount, LPINTERFACEINFO lpInterfaceInfo) override
        {
            if (previous)
                return previous->HandleInComingCall(dwCallType, htaskCaller, dwTickCount, lpInterfaceInfo);
            return SERVERCALL_ISHANDLED;
        }
        DWORD STDMETHODCALLTYPE RetryRejectedCall(HTASK htaskCallee, DWORD dwTickCount, DWORD dwRejectType) override
        {
            if (previous)
                return previous->RetryRejectedCall(htaskCallee, dwTickCount, dwRejectType);
            return 0xFFFFFFFF; // 直接取消被拒调用，不重试
        }
        DWORD STDMETHODCALLTYPE MessagePending(HTASK htaskCallee, DWORD dwTickCount, DWORD dwPendingType) override
        {
            if (!dispatching)
            {
                dispatching = true;
                MSG msg;
                for (HWND hwnd : windows)
                {
                    for (int i = 0; i < 64; i++)
                    {
                        if (!PeekMessageW(&msg, hwnd, 0, 0, PM_REMOVE))
                            break;
                        if (msg.message == WM_QUIT)
                        {
                            PostQuitMessage((int)msg.wParam); // WM_QUIT 留给调用方
                            break;
                        }
                        DispatchMessageW(&msg);
                    }
                }
                dispatching = false;
            }
            if (previous)
                return previous->MessagePending(htaskCallee, dwTickCount, dwPendingType);
            return PENDINGMSG_WAITDEFPROCESS;
        }

        IMessageFilter *previous = nullptr;

        bool collect()
        {
            // 只收集本线程（宿主 WebView2 的 STA）的 Chrome 任务窗口
            windows.clear();
            auto tid = GetCurrentThreadId();
            for (HWND hwnd = nullptr; (hwnd = FindWindowExW(HWND_MESSAGE, hwnd,
                                                            L"Chrome_MessageWindow", nullptr)) != nullptr;)
            {
                if (GetWindowThreadProcessId(hwnd, nullptr) == tid)
                    windows.push_back(hwnd);
            }
            return SUCCEEDED(CoRegisterMessageFilter(this, &previous));
        }
    };

    ChromeTaskPumpFilter g_chrome_task_pump_filter;
    DWORD g_chrome_task_pump_depth = 0;
}

// 进入/退出成对调用（同线程）。非 Wine 返回 false（无操作）。
DECLARE_API bool WebViewExtensionMessagesEnter()
{
    if (!IsRunningOnWine())
        return false;
    if (g_chrome_task_pump_depth == 0 &&
        !g_chrome_task_pump_filter.collect())
        return false;
    g_chrome_task_pump_depth += 1;
    return true;
}

DECLARE_API void WebViewExtensionMessagesExit()
{
    if (g_chrome_task_pump_depth == 0)
        return;
    g_chrome_task_pump_depth -= 1;
    if (g_chrome_task_pump_depth == 0)
        // CoRegisterMessageFilter 返回的旧过滤器不带引用，不 Release
        CoRegisterMessageFilter(g_chrome_task_pump_filter.previous, nullptr);
}
