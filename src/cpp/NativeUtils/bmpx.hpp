#pragma once

#pragma pack(push, 1)
struct BMPColorHeader
{
    uint32_t red_mask{0x00ff0000};         // Bit mask for the red channel
    uint32_t green_mask{0x0000ff00};       // Bit mask for the green channel
    uint32_t blue_mask{0x000000ff};        // Bit mask for the blue channel
    uint32_t alpha_mask{0xff000000};       // Bit mask for the alpha channel
    uint32_t color_space_type{0x73524742}; // Default "sRGB" (0x73524742)
    uint32_t unused[16]{0};                // Unused data for sRGB color space
};
#pragma pack(pop)
struct SimpleBMP
{
    std::shared_ptr<byte[]> data;
    size_t size;
    byte *pixels;
    size_t pixelsize;
    int w, h, bitCount;
};
inline SimpleBMP CreateBMP(int w, int h, int biBitCount = 32, bool alpha = true)
{
    BITMAPINFO l_bmp_info;
    // BMP 32 bpp
    ZeroMemory(&l_bmp_info, sizeof(BITMAPINFO));
    l_bmp_info.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    l_bmp_info.bmiHeader.biBitCount = biBitCount;
    l_bmp_info.bmiHeader.biCompression = alpha ? BI_BITFIELDS : BI_RGB;
    l_bmp_info.bmiHeader.biWidth = w;
    l_bmp_info.bmiHeader.biHeight = -h;
    l_bmp_info.bmiHeader.biPlanes = 1;
    l_bmp_info.bmiHeader.biSizeImage = ((w * biBitCount + 31) / 32) * 4 * h; // h * w * 4;

    BITMAPFILEHEADER bmfh;
    ZeroMemory(&bmfh, sizeof(BITMAPFILEHEADER));
    bmfh.bfType = 0x4D42; // 'BM'
    bmfh.bfSize = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER) + l_bmp_info.bmiHeader.biSizeImage;
    bmfh.bfOffBits = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);
    if (alpha)
    {
        l_bmp_info.bmiHeader.biSize += sizeof(BMPColorHeader);
        bmfh.bfSize += sizeof(BMPColorHeader);
        bmfh.bfOffBits += sizeof(BMPColorHeader);
    }
    std::shared_ptr<byte[]> data(new byte[bmfh.bfSize]());
    auto ptr = data.get();
    memcpy(ptr, &bmfh, sizeof(BITMAPFILEHEADER));
    ptr += sizeof(BITMAPFILEHEADER);
    memcpy(ptr, (char *)&l_bmp_info.bmiHeader, sizeof(BITMAPINFOHEADER));
    ptr += sizeof(BITMAPINFOHEADER);
    if (alpha)
    {
        BMPColorHeader color;
        memcpy(ptr, (char *)&color, sizeof(BMPColorHeader));
        ptr += sizeof(BMPColorHeader);
    }
    return SimpleBMP{data, bmfh.bfSize, ptr, l_bmp_info.bmiHeader.biSizeImage, w, h, biBitCount};
}
inline std::optional<SimpleBMP> CreateBMP(HBITMAP hBitmap, bool alpha = true)
{
    BITMAP bmp;
    if (!GetObject(hBitmap, sizeof(BITMAP), &bmp))
        return {};
    auto bmpx = CreateBMP(bmp.bmWidth, bmp.bmHeight, bmp.bmBitsPixel, alpha && (bmp.bmBitsPixel == 32));
    if (!GetBitmapBits(hBitmap, bmpx.pixelsize, bmpx.pixels))
        return {};
    DeleteObject(hBitmap);
    return bmpx;
}