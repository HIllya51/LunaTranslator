#include <commoncontrols.h>
#include <shellapi.h>
#include "BMP.h"
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
std::mutex lockshfunction;
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
std::optional<BMP> getbmp(HBITMAP hBitmap)
{
    if (!hBitmap)
        return {};
    BITMAP bmp;
    GetObject(hBitmap, sizeof(BITMAP), &bmp);
    BMP bmpp(bmp.bmWidth, bmp.bmHeight, bmp.bmBitsPixel == 32);
    bmpp.bmp_info_header.height = -bmpp.bmp_info_header.height;
    if (!GetBitmapBits(hBitmap, bmpp.data.size(), bmpp.data.data()))
        return {};
    DeleteObject(hBitmap);
    return std::move(bmpp);
}
std::optional<BMP> getbmp(HICON hicon)
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
    return std::move(getbmp(hBitmap));
}
#ifdef WINXP
extern "C" WINUSERAPI
    UINT
        WINAPI
        GetDpiForWindow(
            _In_ HWND hwnd);
#endif
extern HWND globalmessagehwnd;
DECLARE_API bool extracticon2data(bool large, const wchar_t *name, void (*cb)(const char *, size_t))
{
    // if (UINT_MAX == ExtractIconExW(name, 0, &h1, &h2, 1))
    //     return false;
    auto returner = [&](BMP &bmpp)
    {
        std::string data;
        bmpp.write_tomem(data);
        cb(data.c_str(), data.size());
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
        uint32_t channels = bmpp.bmp_info_header.bit_count / 8;
        int checkx = 48 * GetDpiForWindow(globalmessagehwnd) / USER_DEFAULT_SCREEN_DPI;
        for (int y0 = 0; issmall && (y0 < -bmpp.bmp_info_header.height); y0++)
        {
            for (int x0 = 0; issmall && (x0 < bmpp.bmp_info_header.width); x0++)
            {
                if (x0 < checkx && y0 < checkx)
                    continue;
                if (memcmp(bmpp.data.data() + channels * (y0 * bmpp.bmp_info_header.width + x0), zero, channels) != 0)
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