#include "define.h"
#include "BMP.h"

void *extracticon2data(const wchar_t *name, size_t *l)
{
    HICON h1, h2;

    ExtractIconExW(name, 0, &h1, &h2, 1);
    if (h1 == 0)
        return 0;
    HDC hdc = GetDC(NULL);
    HDC memDC = CreateCompatibleDC(hdc);
    ICONINFO iconInfo;
    GetIconInfo(h1, &iconInfo);
    int iconWidth = iconInfo.xHotspot * 2;
    int iconHeight = iconInfo.yHotspot * 2;
    HBITMAP hBitmap = CreateCompatibleBitmap(hdc, iconWidth, iconHeight);
    HBITMAP hOldBitmap = (HBITMAP)SelectObject(memDC, hBitmap);
    DrawIconEx(memDC, 0, 0, h1, iconWidth, iconHeight, 0, NULL, DI_NORMAL);
    SelectObject(memDC, hOldBitmap);
    DeleteDC(memDC);

    BMP bmpp(iconWidth, iconHeight);

    BITMAP bmp;
    GetObject(hBitmap, sizeof(BITMAP), &bmp);

    bmpp.bmp_info_header.bit_count = bmp.bmBitsPixel;

    auto dwSize = bmp.bmWidthBytes * bmp.bmHeight;
    bmpp.data.resize(dwSize);
    auto dataptr = bmpp.data.data();
    GetBitmapBits(hBitmap, dwSize, dataptr);
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
    auto sdata = new char[data.size()];
    memcpy(sdata, data.data(), data.size());
    *l = data.size();
    return sdata;
}