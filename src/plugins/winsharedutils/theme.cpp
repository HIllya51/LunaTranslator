#include "define.h"
// https://github.com/Blinue/Xaml-Islands-Cpp/blob/main/src/XamlIslandsCpp/XamlWindow.h

static uint32_t GetOSversion() noexcept
{
    HMODULE hNtDll = GetModuleHandle(L"ntdll.dll");
    if (!hNtDll)
    {
        return 0;
    }

    auto rtlGetVersion = (LONG(WINAPI *)(PRTL_OSVERSIONINFOW))GetProcAddress(hNtDll, "RtlGetVersion");
    if (rtlGetVersion == nullptr)
    {
        // assert(false);
        return 0;
    }

    RTL_OSVERSIONINFOW version{};
    version.dwOSVersionInfoSize = sizeof(version);
    rtlGetVersion(&version);

    return version.dwMajorVersion;
}

static uint32_t GetOSBuild() noexcept
{
    HMODULE hNtDll = GetModuleHandle(L"ntdll.dll");
    if (!hNtDll)
    {
        return 0;
    }

    auto rtlGetVersion = (LONG(WINAPI *)(PRTL_OSVERSIONINFOW))GetProcAddress(hNtDll, "RtlGetVersion");
    if (rtlGetVersion == nullptr)
    {
        // assert(false);
        return 0;
    }

    RTL_OSVERSIONINFOW version{};
    version.dwOSVersionInfoSize = sizeof(version);
    rtlGetVersion(&version);

    return version.dwBuildNumber;
}
struct Win32Helper
{
    struct OSVersion
    {
        constexpr OSVersion(uint32_t build) : _build(build) {}

        bool Is20H1OrNewer() const noexcept
        {
            return _build >= 19041;
        }

        // 下面为 Win11
        // 不考虑代号相同的 Win10

        bool IsWin11() const noexcept
        {
            return Is21H2OrNewer();
        }

        bool Is21H2OrNewer() const noexcept
        {
            return _build >= 22000;
        }

        bool Is22H2OrNewer() const noexcept
        {
            return _build >= 22621;
        }

    private:
        uint32_t _build = 0;
    };

    static OSVersion GetOSVersion() noexcept;
};
Win32Helper::OSVersion Win32Helper::GetOSVersion() noexcept
{
    static OSVersion version = GetOSBuild();
    return version;
}

enum class PreferredAppMode
{
    Default,
    AllowDark,
    ForceDark,
    ForceLight,
    Max
};

using fnSetPreferredAppMode = PreferredAppMode(WINAPI *)(PreferredAppMode appMode);
using fnAllowDarkModeForWindow = bool(WINAPI *)(HWND hWnd, bool allow);
using fnRefreshImmersiveColorPolicyState = void(WINAPI *)();
using fnFlushMenuThemes = void(WINAPI *)();
// using fnDwmSetWindowAttribute=HRESULT (WINAPI*)(HWND,DWORD,LPCVOID,DWORD);

static fnSetPreferredAppMode SetPreferredAppMode = nullptr;
static fnAllowDarkModeForWindow AllowDarkModeForWindow = nullptr;
static fnRefreshImmersiveColorPolicyState RefreshImmersiveColorPolicyState = nullptr;
static fnFlushMenuThemes FlushMenuThemes = nullptr;
// static fnDwmSetWindowAttribute DwmSetWindowAttribute=nullptr;
static bool initok()
{
    return SetPreferredAppMode && AllowDarkModeForWindow && RefreshImmersiveColorPolicyState && FlushMenuThemes; //&&DwmSetWindowAttribute;
}
static bool InitApis() noexcept
{
    if (initok())
        return true;

    HMODULE hUxtheme = LoadLibrary(L"uxtheme.dll");
    // assert(hUxtheme);

    SetPreferredAppMode = (fnSetPreferredAppMode)GetProcAddress(hUxtheme, MAKEINTRESOURCEA(135));
    AllowDarkModeForWindow = (fnAllowDarkModeForWindow)GetProcAddress(hUxtheme, MAKEINTRESOURCEA(133));
    RefreshImmersiveColorPolicyState = (fnRefreshImmersiveColorPolicyState)GetProcAddress(hUxtheme, MAKEINTRESOURCEA(104));
    FlushMenuThemes = (fnFlushMenuThemes)GetProcAddress(hUxtheme, MAKEINTRESOURCEA(136));

    // HMODULE hdwmapi = LoadLibrary(L"dwmapi.dll");

    // DwmSetWindowAttribute = (fnDwmSetWindowAttribute)GetProcAddress(hdwmapi, "DwmSetWindowAttribute");
    return initok();
}

static void SetWindowTheme(HWND hWnd, bool darkBorder, bool darkMenu) noexcept
{
    if (!InitApis())
        return;

    SetPreferredAppMode(darkMenu ? PreferredAppMode::ForceDark : PreferredAppMode::ForceLight);
    AllowDarkModeForWindow(hWnd, darkMenu);

    // 使标题栏适应黑暗模式
    // build 18985 之前 DWMWA_USE_IMMERSIVE_DARK_MODE 的值不同
    // https://github.com/MicrosoftDocs/sdk-api/pull/966/files
    constexpr const DWORD DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1 = 19;
    BOOL value = darkBorder;
    DwmSetWindowAttribute(
        hWnd,
        Win32Helper::GetOSVersion().Is20H1OrNewer() ? DWMWA_USE_IMMERSIVE_DARK_MODE : DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1,
        &value,
        sizeof(value));

    RefreshImmersiveColorPolicyState();
    FlushMenuThemes();
}
DECLARE void setdwmextendframe(HWND hwnd)
{
    MARGINS mar{-1, -1, -1, -1};
    DwmExtendFrameIntoClientArea(hwnd, &mar);
}

DECLARE void _SetTheme(
    HWND _hWnd,
    bool dark,
    int backdrop)
{
    // printf("%d %d\n",GetOSversion(),GetOSBuild());
    if (GetOSversion() <= 6) // win7 x32 DwmSetWindowAttribute会崩，直接禁了反正没用。不知道win8怎么样。
        return;
    // auto _isBackgroundSolidColor = backdrop == WindowBackdrop::SolidColor;
    // if (Win32Helper::GetOSVersion().Is22H2OrNewer() &&
    //     _isBackgroundSolidColor != (backdrop == WindowBackdrop::SolidColor))
    // {
    //     return true;
    // }

    //  Win10 中即使在亮色主题下我们也使用暗色边框，这也是 UWP 窗口的行为
    SetWindowTheme(
        _hWnd,
        Win32Helper::GetOSVersion().IsWin11() ? dark : true,
        dark);

    // if (!Win32Helper::GetOSVersion().Is22H2OrNewer())
    // {
    //     return false;
    // }

    // https://learn.microsoft.com/zh-cn/windows/win32/api/dwmapi/ne-dwmapi-dwm_systembackdrop_type
    // 设置背景
    static const DWM_SYSTEMBACKDROP_TYPE BACKDROP_MAP[] = {
        DWMSBT_AUTO, DWMSBT_TRANSIENTWINDOW, DWMSBT_MAINWINDOW, DWMSBT_TABBEDWINDOW};
    DWM_SYSTEMBACKDROP_TYPE value = BACKDROP_MAP[backdrop];
    // 不管操作系统版本了，硬设置就行，测试不会崩溃，让系统自己处理。
    DwmSetWindowAttribute(_hWnd, DWMWA_SYSTEMBACKDROP_TYPE, &value, sizeof(value));
}

DECLARE bool isDark()
{
    HKEY hKey;
    const char *subKey = "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize";
    if (RegOpenKeyExA(HKEY_CURRENT_USER, subKey, 0, KEY_READ, &hKey) == ERROR_SUCCESS)
    {
        DWORD value;
        DWORD dataSize = sizeof(DWORD);
        if (RegQueryValueExA(hKey, "AppsUseLightTheme", 0, NULL, (LPBYTE)&value, &dataSize) == ERROR_SUCCESS)
        {
            RegCloseKey(hKey);
            return 1 - value;
        }
        RegCloseKey(hKey);
    }
    return false;
}