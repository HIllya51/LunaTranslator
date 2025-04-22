
// https://github.com/Blinue/Xaml-Islands-Cpp/blob/main/src/XamlIslandsCpp/XamlWindow.h
#include "osversion.hpp"
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

#ifdef WINXP
#define DWMWCP_DEFAULT 0
#define DWMWCP_DONOTROUND 1
#define DWMWA_WINDOW_CORNER_PREFERENCE 33
#define DWMWA_SYSTEMBACKDROP_TYPE 38
#define DWMWA_USE_IMMERSIVE_DARK_MODE 20
// Types used with DWMWA_SYSTEMBACKDROP_TYPE
enum DWM_SYSTEMBACKDROP_TYPE
{
    DWMSBT_AUTO,            // [Default] Let DWM automatically decide the system-drawn backdrop for this window.
    DWMSBT_NONE,            // Do not draw any system backdrop.
    DWMSBT_MAINWINDOW,      // Draw the backdrop material effect corresponding to a long-lived window.
    DWMSBT_TRANSIENTWINDOW, // Draw the backdrop material effect corresponding to a transient window.
    DWMSBT_TABBEDWINDOW,    // Draw the backdrop material effect corresponding to a window with a tabbed title bar.
};

#endif
static void SetWindowTheme(HWND hWnd, bool darkBorder, bool darkMenu) noexcept
{
    if (GetOSVersion().IsleWin8())
        return;
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
        GetOSVersion().Isge20H1() ? DWMWA_USE_IMMERSIVE_DARK_MODE : DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1,
        &value,
        sizeof(value));

    RefreshImmersiveColorPolicyState();
    FlushMenuThemes();
}
DECLARE_API void SetWindowExtendFrame(HWND hwnd)
{
    MARGINS mar{-1, -1, -1, -1};
    DwmExtendFrameIntoClientArea(hwnd, &mar);
}

DECLARE_API void SetTheme(
    HWND _hWnd,
    bool dark,
    int backdrop,
    bool rect)
{
    // printf("%d %d\n",GetOSversion(),GetOSBuild());
    if (GetOSVersion().IsleWin8()) // win7 x32 DwmSetWindowAttribute会崩，直接禁了反正没用。不知道win8怎么样。
        return;

    auto value1 = rect ? DWMWCP_DONOTROUND : DWMWCP_DEFAULT;
    DwmSetWindowAttribute(_hWnd, DWMWA_WINDOW_CORNER_PREFERENCE, &value1, sizeof(value1));
    // auto _isBackgroundSolidColor = backdrop == WindowBackdrop::SolidColor;
    // if (Win32Helper::GetOSVersion().Isge22H2() &&
    //     _isBackgroundSolidColor != (backdrop == WindowBackdrop::SolidColor))
    // {
    //     return true;
    // }

    //  Win10 中即使在亮色主题下我们也使用暗色边框，这也是 UWP 窗口的行为
    SetWindowTheme(
        _hWnd,
        GetOSVersion().IsWin11() ? dark : true,
        dark);

    // if (!Win32Helper::GetOSVersion().Isge22H2())
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

DECLARE_API bool IsDark()
{
    constexpr auto subKey = LR"(Software\Microsoft\Windows\CurrentVersion\Themes\Personalize)";
    CRegKey hKey;
    if (ERROR_SUCCESS != hKey.Open(HKEY_CURRENT_USER, subKey, KEY_READ))
        return false;

    DWORD value;
    if (ERROR_SUCCESS != hKey.QueryDWORDValue(L"AppsUseLightTheme", value))
        return false;
    return 1 - value;
}