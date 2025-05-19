
#include <dwmapi.h>
#include "osversion.hpp"
typedef enum _WINDOWCOMPOSITIONATTRIB
{
	CA_UNDEFINED = 0,
	WCA_NCRENDERING_ENABLED = 1,
	WCA_NCRENDERING_POLICY = 2,
	WCA_TRANSITIONS_FORCEDISABLED = 3,
	WCA_ALLOW_NCPAINT = 4,
	WCA_CAPTION_BUTTON_BOUNDS = 5,
	WCA_NONCLIENT_RTL_LAYOUT = 6,
	WCA_FORCE_ICONIC_REPRESENTATION = 7,
	WCA_EXTENDED_FRAME_BOUNDS = 8,
	WCA_HAS_ICONIC_BITMAP = 9,
	WCA_THEME_ATTRIBUTES = 10,
	WCA_NCRENDERING_EXILED = 11,
	WCA_NCADORNMENTINFO = 12,
	WCA_EXCLUDED_FROM_LIVEPREVIEW = 13,
	WCA_VIDEO_OVERLAY_ACTIVE = 14,
	WCA_FORCE_ACTIVEWINDOW_APPEARANCE = 15,
	WCA_DISALLOW_PEEK = 16,
	WCA_CLOAK = 17,
	WCA_CLOAKED = 18,
	WCA_ACCENT_POLICY = 19, //
	WCA_FREEZE_REPRESENTATION = 20,
	WCA_EVER_UNCLOAKED = 21,
	WCA_VISUAL_OWNER = 22,
	WCA_LAST = 23,
	WCA_USEDARKMODECOLORS = 26
} WINDOWCOMPOSITIONATTRIB;

typedef struct _WINDOWCOMPOSITIONATTRIBDATA
{
	WINDOWCOMPOSITIONATTRIB Attrib;
	PVOID pvData;
	SIZE_T cbData;
} WINDOWCOMPOSITIONATTRIBDATA;

typedef enum _ACCENT_STATE
{
	ACCENT_DISABLED = 0,
	ACCENT_ENABLE_GRADIENT = 1,
	ACCENT_ENABLE_TRANSPARENTGRADIENT = 2,
	ACCENT_ENABLE_BLURBEHIND = 3,
	ACCENT_ENABLE_ACRYLICBLURBEHIND = 4,
	ACCENT_INVALID_STATE = 5
} ACCENT_STATE;

typedef struct _ACCENT_POLICY
{
	ACCENT_STATE AccentState;
	DWORD AccentFlags;
	DWORD GradientColor;
	DWORD AnimationId;
} ACCENT_POLICY;

WINUSERAPI
BOOL
	WINAPI
	GetWindowCompositionAttribute(
		_In_ HWND hWnd,
		_Inout_ WINDOWCOMPOSITIONATTRIBDATA *pAttrData);

typedef BOOL(WINAPI *pfnGetWindowCompositionAttribute)(HWND, WINDOWCOMPOSITIONATTRIBDATA *);

WINUSERAPI
BOOL
	WINAPI
	SetWindowCompositionAttribute(
		_In_ HWND hWnd,
		_Inout_ WINDOWCOMPOSITIONATTRIBDATA *pAttrData);

typedef BOOL(WINAPI *pfnSetWindowCompositionAttribute)(HWND, WINDOWCOMPOSITIONATTRIBDATA *);

#define common                                                                                                             \
	ACCENT_POLICY accentPolicy;                                                                                            \
	WINDOWCOMPOSITIONATTRIBDATA winCompAttrData;                                                                           \
	ZeroMemory(&accentPolicy, sizeof(accentPolicy));                                                                       \
	ZeroMemory(&winCompAttrData, sizeof(winCompAttrData));                                                                 \
	winCompAttrData.Attrib = WCA_ACCENT_POLICY;                                                                            \
	winCompAttrData.cbData = sizeof(accentPolicy);                                                                         \
	winCompAttrData.pvData = &accentPolicy;                                                                                \
	auto setWindowCompositionAttribute =                                                                                   \
		(pfnSetWindowCompositionAttribute)GetProcAddress(GetModuleHandle(L"user32.dll"), "SetWindowCompositionAttribute"); \
	if (!setWindowCompositionAttribute)                                                                                    \
		return;

DECLARE_API void setAcrylicEffect(HWND hwnd, bool isEnableShadow, DWORD gradientColor)
{
	if (GetOSVersion().IsleWinVista())
		return;
	// win7全都用areo

	if (GetOSVersion().IsleWin8())
	{
		DWM_BLURBEHIND bb = {0};
		bb.dwFlags = DWM_BB_ENABLE;
		bb.fEnable = true;
		bb.hRgnBlur = NULL;
		DwmEnableBlurBehindWindow(hwnd, &bb);
	}
	else
	{
		// DWORD gradientColor = 0x00FfFfFf; // ABGR
		common;
		accentPolicy.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND;
		accentPolicy.GradientColor = gradientColor;
		auto accentFlags = isEnableShadow ? (DWORD(0x20 | 0x40 | 0x80 | 0x100)) : 0;
		accentPolicy.AccentFlags = accentFlags;
		setWindowCompositionAttribute(hwnd, &winCompAttrData);
	}
}
DECLARE_API void setAeroEffect(HWND hwnd, bool isEnableShadow)
{
	if (GetOSVersion().IsleWinVista())
		return;
	if (GetOSVersion().IsleWin8())
	{
		DWM_BLURBEHIND bb = {0};
		bb.dwFlags = DWM_BB_ENABLE;
		bb.fEnable = true;
		bb.hRgnBlur = NULL;
		DwmEnableBlurBehindWindow(hwnd, &bb);
	}
	else
	{
		common;
		accentPolicy.AccentState = ACCENT_ENABLE_BLURBEHIND;
		auto accentFlags = isEnableShadow ? (DWORD(0x20 | 0x40 | 0x80 | 0x100)) : 0;
		accentPolicy.AccentFlags = accentFlags;
		setWindowCompositionAttribute(hwnd, &winCompAttrData);
	}
}
DECLARE_API void clearEffect(HWND hwnd)
{
	if (GetOSVersion().IsleWinVista())
		return;
	if (GetOSVersion().IsleWin8())
	{
		DWM_BLURBEHIND bb = {0};
		bb.dwFlags = DWM_BB_ENABLE;
		bb.fEnable = false;
		bb.hRgnBlur = NULL;
		DwmEnableBlurBehindWindow(hwnd, &bb);
	}
	else
	{
		common;
		accentPolicy.AccentState = ACCENT_DISABLED;
		setWindowCompositionAttribute(hwnd, &winCompAttrData);
	}
}