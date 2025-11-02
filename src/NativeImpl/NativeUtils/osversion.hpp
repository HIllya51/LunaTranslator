
struct OSVersion
{
    bool Isge20H1() const noexcept
    {
        return version.dwBuildNumber >= 19041;
    }

    // 下面为 Win11
    // 不考虑代号相同的 Win10

    bool IsWin11() const noexcept
    {
        return Isge21H2();
    }

    bool Isge21H2() const noexcept
    {
        return version.dwBuildNumber >= 22000;
    }

    bool Isge22H2() const noexcept
    {
        return version.dwBuildNumber >= 22621;
    }
    bool IsleWin8() const noexcept
    {
        return version.dwMajorVersion <= 6;
    }
    bool IsleWinVista() const noexcept
    {
        return (version.dwMajorVersion < 6) || (version.dwMajorVersion == 6 && version.dwMinorVersion == 0);
    }
    bool IsleWinXP() const noexcept
    {
        return version.dwMajorVersion <= 5;
    }
    RTL_OSVERSIONINFOW version;
};
namespace
{
    RTL_OSVERSIONINFOW _GetOSversion() noexcept
    {
        HMODULE hNtDll = GetModuleHandle(L"ntdll.dll");
        if (!hNtDll)
        {
            return {};
        }

        auto rtlGetVersion = (LONG(WINAPI *)(PRTL_OSVERSIONINFOW))GetProcAddress(hNtDll, "RtlGetVersion");
        if (rtlGetVersion == nullptr)
        {
            // assert(false);
            return {};
        }

        RTL_OSVERSIONINFOW version{};
        version.dwOSVersionInfoSize = sizeof(version);
        rtlGetVersion(&version);

        return version;
    }
}
static OSVersion GetOSVersion()
{
    {
        static OSVersion version = {_GetOSversion()};
        return version;
    }
}

#ifndef WINXP
#define FUCKPRIVI PROCESS_QUERY_LIMITED_INFORMATION
#else
#define FUCKPRIVI (GetOSVersion().IsleWinXP() ? PROCESS_QUERY_INFORMATION : PROCESS_QUERY_LIMITED_INFORMATION)
#endif