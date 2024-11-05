
#include "BMP.h"

DECLARE_API bool extracticon2data(const wchar_t *name, void (*cb)(const char *, size_t))
{
    HICON h1, h2;

    if (UINT_MAX == ExtractIconExW(name, 0, &h1, &h2, 1))
        return false;
    if (h1 == 0)
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

    auto dwSize = bmp.bmWidthBytes * bmp.bmHeight;
    bmpp.data.resize(dwSize);
    auto dataptr = bmpp.data.data();
    if (!GetBitmapBits(hBitmap, dwSize, dataptr))
        return false;
    DeleteObject(hBitmap);

    std::vector<LONG> tmp;
    tmp.resize(bmp.bmWidthBytes);
    if (bmp.bmWidthBytes == bmp.bmHeight * 4)
    {
        bool allalpha0 = true;
        for (int i = 0; i < bmpp.data.size() / 4; i++)
        {
            if (dataptr[i * 4 + 3] != 0)
            {
                allalpha0 = false;
                break;
            }
        }
        if (allalpha0)
        {
            for (int i = 0; i < bmpp.data.size() / 4; i++)
            {
                dataptr[i * 4 + 3] = 0xff;
            }
        }
    }

    for (int i = 0; i < bmp.bmHeight / 2; i++)
    {
        memcpy(tmp.data(), dataptr + i * bmp.bmWidthBytes, bmp.bmWidthBytes);
        memcpy(dataptr + i * bmp.bmWidthBytes, dataptr + (bmp.bmHeight - 1 - i) * bmp.bmWidthBytes, bmp.bmWidthBytes);
        memcpy(dataptr + (bmp.bmHeight - 1 - i) * bmp.bmWidthBytes, tmp.data(), bmp.bmWidthBytes);
    }
    std::string data;
    bmpp.write_tomem(data);
    cb(data.c_str(), data.size());
    return true;
}