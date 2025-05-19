#include <commoncontrols.h>
#include <shellapi.h>
#include "bmpx.hpp"
#include "osversion.hpp"

struct AutoHICON
{
    HICON hi;
    AutoHICON(HICON hi1) : hi(hi1) {}
    ~AutoHICON()
    {
        if (hi)
            DestroyIcon(hi);
    }
    void operator=(HICON hi1)
    {
        hi = hi1;
    }
    operator HICON()
    {
        return hi;
    }
};
static std::mutex lockshfunction;
HICON GetExeIcon(LPCWSTR pszPath)
{
    std::unique_lock _(lockshfunction);
    SHFILEINFO fileInfo;
    HICON hIcon = NULL;
    if (SHGetFileInfo(pszPath, 0, &fileInfo, sizeof(fileInfo), SHGFI_ICON | SHGFI_LARGEICON))
    {
        hIcon = fileInfo.hIcon;
    }
    return hIcon;
}

HICON GetHighResolutionIcon(LPCWSTR pszPath)
{
    std::unique_lock _(lockshfunction);
    // Get the image list index of the icon
    SHFILEINFO sfi;
    if (!SHGetFileInfo(pszPath, 0, &sfi, sizeof(sfi), SHGFI_SYSICONINDEX))
        return NULL;
    // Get the jumbo image list
    CComPtr<IImageList> piml;
    if (FAILED(SHGetImageList(SHIL_JUMBO, IID_PPV_ARGS(&piml))))
        return NULL;

    // Extract an icon
    HICON hico;
    if (FAILED(piml->GetIcon(sfi.iIcon, ILD_TRANSPARENT, &hico)))
        return NULL;
    return hico;
}
std::optional<SimpleBMP> getbmp(HICON hicon)
{
    if (!hicon)
        return {};
    ICONINFO iconInfo;
    AutoHICON __ = hicon;
    if (!GetIconInfo(hicon, &iconInfo))
        return {};
    int iconWidth = iconInfo.xHotspot * 2,
        iconHeight = iconInfo.yHotspot * 2;

    HDC hdc = GetDC(NULL);
    if (!hdc)
        return {};
    HDC memDC = CreateCompatibleDC(hdc);
    if (!memDC)
        return {};
    HBITMAP hBitmap = CreateCompatibleBitmap(hdc, iconWidth, iconHeight);
    if (!hBitmap)
        return {};
    HBITMAP hOldBitmap = (HBITMAP)SelectObject(memDC, hBitmap);
    if (!hOldBitmap)
        return {};
    if (!DrawIconEx(memDC, 0, 0, hicon, iconWidth, iconHeight, 0, NULL, DI_NORMAL))
        return {};
    SelectObject(memDC, hOldBitmap);
    DeleteDC(memDC);
    return CreateBMP(hBitmap);
}
extern HWND globalmessagehwnd;
DECLARE_API bool ExtractExeIconData(bool large, const wchar_t *name, void (*cb)(const byte *, size_t))
{
    // if (UINT_MAX == ExtractIconExW(name, 0, &h1, &h2, 1))
    //     return false;
    auto returner = [&](SimpleBMP &bf)
    {
        cb(bf.data.get(), bf.size);
        return true;
    };
    do
    {
        if (!large)
            break;
#ifdef WINXP
        if (GetOSVersion().IsleWinXP())
            break;
#endif
        auto bmppo = getbmp(GetHighResolutionIcon(name));
        if (!bmppo)
            break;
        auto bmpp = bmppo.value();
        bool issmall = true;
        char zero[4] = {0, 0, 0, 0};
        uint32_t channels = bmpp.bitCount / 8;
        int checkx = 48 * GetDpiForWindow(globalmessagehwnd) / USER_DEFAULT_SCREEN_DPI;
        for (int y0 = 0; issmall && (y0 < bmpp.h); y0++)
        {
            for (int x0 = 0; issmall && (x0 < bmpp.w); x0++)
            {
                if (x0 < checkx && y0 < checkx)
                    continue;
                if (memcmp(bmpp.pixels + channels * (y0 * bmpp.w + x0), zero, channels) != 0)
                    issmall = false;
            }
        }
        if (issmall)
            break;
        return returner(bmpp);
    } while (0);
    auto bmpp = getbmp(GetExeIcon(name));
    if (!bmpp)
        return false;
    return returner(bmpp.value());
}