

void GetVirtualDesktopRect(RECT &rect)
{
    // 获取虚拟桌面的尺寸和位置
    rect.left = GetSystemMetrics(SM_XVIRTUALSCREEN);
    rect.top = GetSystemMetrics(SM_YVIRTUALSCREEN);
    rect.right = rect.left + GetSystemMetrics(SM_CXVIRTUALSCREEN);
    rect.bottom = rect.top + GetSystemMetrics(SM_CYVIRTUALSCREEN);
}

HBITMAP GetBitmap(RECT &rect, HDC hDC)
{
    HDC hMemDC;
    int x, y;
    int nWidth, nHeight;
    HBITMAP hBitmap, hOldBitmap;

    hMemDC = CreateCompatibleDC(hDC);
    // RECT rect;
    // GetVirtualDesktopRect(rect);
    hBitmap = CreateCompatibleBitmap(hDC, rect.right - rect.left, rect.bottom - rect.top);
    hOldBitmap = (HBITMAP)SelectObject(hMemDC, hBitmap);

    BitBlt(hMemDC, 0, 0, rect.right - rect.left, rect.bottom - rect.top, hDC, rect.left, rect.top, SRCCOPY);

    hBitmap = (HBITMAP)SelectObject(hMemDC, hOldBitmap);

    DeleteDC(hMemDC);

    return hBitmap;
}
std::vector<byte> SaveBitmapToBuffer(HBITMAP hBitmap)
{
    WORD wBitCount; // 位图中每个像素所占字节数
    // 定义调色板大小，位图中像素字节大小，位图文件大小，写入文件字节数
    DWORD dwPaletteSize = 0, dwBmBitsSize, dwDIBSize, dwWritten;
    BITMAP Bitmap;           // 位图属性结构
    BITMAPFILEHEADER bmfHdr; // 位图文件头结构
    BITMAPINFOHEADER bi;     // 位图信息头结构

    LPSTR lpbk, lpmem;

    wBitCount = 32;
    // 设置位图信息头结构
    GetObject(hBitmap, sizeof(BITMAP), (LPSTR)&Bitmap);
    bi.biSize = sizeof(BITMAPINFOHEADER);
    bi.biWidth = Bitmap.bmWidth;
    bi.biHeight = -Bitmap.bmHeight; // 为负,正向的位图;为正,倒向的位图
    bi.biPlanes = 1;
    bi.biBitCount = wBitCount;
    bi.biCompression = BI_RGB;
    bi.biSizeImage = 0;
    bi.biXPelsPerMeter = 0;
    bi.biYPelsPerMeter = 0;
    bi.biClrUsed = 0;
    bi.biClrImportant = 0;
    dwBmBitsSize = ((Bitmap.bmWidth * wBitCount + 31) / 32) * 4 * Bitmap.bmHeight;

    // 设置位图文件头
    bmfHdr.bfType = 0x4D42; //   "BM"
    dwDIBSize = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER) + dwBmBitsSize;
    bmfHdr.bfSize = dwDIBSize;
    bmfHdr.bfReserved1 = 0;
    bmfHdr.bfReserved2 = 0;
    bmfHdr.bfOffBits = (DWORD)sizeof(BITMAPFILEHEADER) + (DWORD)sizeof(BITMAPINFOHEADER);
    std::vector<byte> data;
    data.resize(sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER) + dwBmBitsSize);
    auto buffer = data.data();
    // 写入位图文件头
    // WriteFile(fh, (LPSTR)&bmfHdr, sizeof(BITMAPFILEHEADER), &dwWritten, NULL);
    // 写入位图信息头
    // WriteFile(fh, (LPSTR)&bi, sizeof(BITMAPINFOHEADER), &dwWritten, NULL);

    memcpy(buffer, &bmfHdr, sizeof(BITMAPFILEHEADER));
    buffer += sizeof(BITMAPFILEHEADER);
    memcpy(buffer, &bi, sizeof(BITMAPINFOHEADER));
    buffer += sizeof(BITMAPINFOHEADER);
    // 获取位图阵列
    if (!GetBitmapBits(hBitmap, dwBmBitsSize, buffer))
        return {}; // 正向的内存图象数据
    if (std::all_of(buffer, buffer + dwBmBitsSize, std::bind(std::equal_to<unsigned char>(), std::placeholders::_1, 0)))
        return {};
    // for (int i = 0; i < Bitmap.bmHeight; i++)
    // {
    //     memcpy(buffer + sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER) + Bitmap.bmWidth * i * 4, lpmem + Bitmap.bmWidth * (Bitmap.bmHeight - i - 1) * 4, Bitmap.bmWidth * 4);
    // }
    // 写位图数据
    // WriteFile(fh, lpbk, dwBmBitsSize, &dwWritten, NULL);

    return std::move(data);
}
namespace
{
    bool checkempty(HWND hwnd, RECT &rect)
    {
        if (rect.bottom != rect.top && rect.left != rect.right)
            return false;
        if (rect.top != -1 || rect.left != -1)
            return true;
        if (!hwnd)
            return true;
        if (!GetClientRect(hwnd, &rect))
            return true;
        return rect.bottom == rect.top || rect.left == rect.right;
    }
}
extern HWND globalmessagehwnd;
#ifdef WINXP
extern "C" WINUSERAPI
    UINT
        WINAPI
        GetDpiForWindow(
            _In_ HWND hwnd);
#endif
std::vector<byte> __gdi_screenshot(HWND hwnd, RECT rect)
{
    if (checkempty(hwnd, rect))
        return {};
    if (!hwnd)
        hwnd = GetDesktopWindow();
    else
    {
        auto dpi = GetDpiForWindow(hwnd); // 链接到yythunks里的实现也是一样的
        auto thisdpi = GetDpiForWindow(globalmessagehwnd);
        rect.bottom = MulDiv(rect.bottom, dpi, thisdpi);
        rect.right = MulDiv(rect.right, dpi, thisdpi);
        rect.left = MulDiv(rect.left, dpi, thisdpi);
        rect.top = MulDiv(rect.top, dpi, thisdpi);
    }
    auto hdc = GetDC(hwnd);
    if (!hdc)
        return {};
    auto bm = GetBitmap(rect, hdc);
    auto bf = SaveBitmapToBuffer(bm);
    DeleteObject(bm);
    ReleaseDC(hwnd, hdc);
    return std::move(bf);
}
DECLARE_API void gdi_screenshot(HWND hwnd, void (*cb)(byte *, size_t))
{
    RECT rect{-1, -1, -1, -1};
    auto bf = __gdi_screenshot(hwnd, rect);
    if (bf.size())
        cb(bf.data(), bf.size());
}
DECLARE_API void crop_image(HWND hwnd, RECT rect, void (*cb)(byte *, size_t))
{
    for (int i = 0; i < 2; i++)
    {
        switch (i)
        {
        case 0:
        {
            if (!hwnd)
                continue;
            RECT r;
            if (!GetWindowRect(hwnd, &r))
                continue;
            POINT p1{rect.left, rect.top}, p2{rect.right, rect.bottom};
            if (!ScreenToClient(hwnd, &p1))
                continue;
            if (!ScreenToClient(hwnd, &p2))
                continue;
            RECT check{0, 0, r.right - r.left, r.bottom - r.top};
            if (!(PtInRect(&check, p1) && PtInRect(&check, p2)))
                continue;
            RECT r2{p1.x, p1.y, p2.x, p2.y};
            auto bf = __gdi_screenshot(hwnd, r2);
            if (bf.size())
                return cb(bf.data(), bf.size());
        }
        break;
        case 1:
        {
            auto bf = __gdi_screenshot(NULL, rect);
            if (bf.size())
                return cb(bf.data(), bf.size());
        }
        }
    }
}

DECLARE_API void maximum_window(HWND hwnd)
{
    RECT rect;
    GetVirtualDesktopRect(rect);
    MoveWindow(hwnd, rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top, TRUE);
}