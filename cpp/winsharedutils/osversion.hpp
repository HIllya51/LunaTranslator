
struct OSVersion
{
    bool Is20H1OrNewer() const noexcept
    {
        return version.dwBuildNumber >= 19041;
    }

    // 下面为 Win11
    // 不考虑代号相同的 Win10

    bool IsWin11() const noexcept
    {
        return Is21H2OrNewer();
    }

    bool Is21H2OrNewer() const noexcept
    {
        return version.dwBuildNumber >= 22000;
    }

    bool Is22H2OrNewer() const noexcept
    {
        return version.dwBuildNumber >= 22621;
    }
    bool IsWin7or8() const noexcept
    {
        return version.dwMajorVersion <= 6;
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
