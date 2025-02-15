
#include "BMP.h"
HICON GetExeIcon(const std::wstring &filePath)
{
    SHFILEINFO fileInfo;
    HICON hIcon = NULL;
    if (SHGetFileInfo(filePath.c_str(), 0, &fileInfo, sizeof(fileInfo), SHGFI_ICON | SHGFI_LARGEICON))
    {
        hIcon = fileInfo.hIcon;
    }
    return hIcon;
}
DECLARE_API bool extracticon2data(const wchar_t *name, void (*cb)(const char *, size_t))
{
    // if (UINT_MAX == ExtractIconExW(name, 0, &h1, &h2, 1))
    //     return false;
    HICON h1 = GetExeIcon(name);
    if (!h1)
        return false;
    HDC hdc = GetDC(NULL);
    if (!hdc)
        return false;
    HDC memDC = CreateCompatibleDC(hdc);
    if (!memDC)
        return false;
    ICONINFO iconInfo;
    if (!GetIconInfo(h1, &iconInfo))
        return false;
    int iconWidth = iconInfo.xHotspot * 2;
    int iconHeight = iconInfo.yHotspot * 2;
    HBITMAP hBitmap = CreateCompatibleBitmap(hdc, iconWidth, iconHeight);
    if (!hBitmap)
        return false;
    HBITMAP hOldBitmap = (HBITMAP)SelectObject(memDC, hBitmap);
    if (!hOldBitmap)
        return false;
    if (!DrawIconEx(memDC, 0, 0, h1, iconWidth, iconHeight, 0, NULL, DI_NORMAL))
        return false;
    SelectObject(memDC, hOldBitmap);
    DeleteDC(memDC);

    BMP bmpp(iconWidth, iconHeight);
    BITMAP bmp;
    GetObject(hBitmap, sizeof(BITMAP), &bmp);
    bmpp.bmp_info_header.bit_count = bmp.bmBitsPixel;
    bmpp.bmp_info_header.height = -bmpp.bmp_info_header.height;
    bmpp.data.resize(bmp.bmWidthBytes * bmp.bmHeight);
    if (!GetBitmapBits(hBitmap, bmpp.data.size(), bmpp.data.data()))
        return false;
    DeleteObject(hBitmap);
    std::string data;
    bmpp.write_tomem(data);
    cb(data.c_str(), data.size());
    return true;
}