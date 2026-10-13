#include "osversion.hpp"
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

// 进程可执行文件路径：递减权限打开进程 + 三级 API 回退
// （GetModuleFileNameExW → QueryFullProcessImageNameW → GetProcessImageFileNameW）
// + NT/UNC 设备路径换算 + 短路径修补。失败不回调。
DECLARE_API void GetProcessFileName(DWORD pid, void (*cb)(const wchar_t *))
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
        cb(v.c_str());
        return;
    }
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
