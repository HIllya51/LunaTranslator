
#include "define.h"

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
int SaveBitmapToFile(HBITMAP hBitmap, LPCWSTR lpFileName)
{
    WORD wBitCount; // 位图中每个像素所占字节数
    // 定义调色板大小，位图中像素字节大小，位图文件大小，写入文件字节数
    DWORD dwPaletteSize = 0, dwBmBitsSize, dwDIBSize, dwWritten;
    BITMAP Bitmap;           // 位图属性结构
    BITMAPFILEHEADER bmfHdr; // 位图文件头结构
    BITMAPINFOHEADER bi;     // 位图信息头结构
    HANDLE fh;               // 定义文件，分配内存句柄，调色板句柄
    LPSTR lpbk, lpmem;

    wBitCount = 32;
    // 设置位图信息头结构
    GetObject(hBitmap, sizeof(BITMAP), (LPSTR)&Bitmap);
    bi.biSize = sizeof(BITMAPINFOHEADER);
    bi.biWidth = Bitmap.bmWidth;
    bi.biHeight = Bitmap.bmHeight; // 为负,正向的位图;为正,倒向的位图
    bi.biPlanes = 1;
    bi.biBitCount = wBitCount;
    bi.biCompression = BI_RGB;
    bi.biSizeImage = 0;
    bi.biXPelsPerMeter = 0;
    bi.biYPelsPerMeter = 0;
    bi.biClrUsed = 0;
    bi.biClrImportant = 0;
    dwBmBitsSize = ((Bitmap.bmWidth * wBitCount + 31) / 32) * 4 * Bitmap.bmHeight;

    // 创建位图文件
    fh = CreateFile(lpFileName, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
                    FILE_ATTRIBUTE_NORMAL | FILE_FLAG_SEQUENTIAL_SCAN, NULL);
    if (fh == INVALID_HANDLE_VALUE)
        return FALSE;
    // 设置位图文件头
    bmfHdr.bfType = 0x4D42; //   "BM"
    dwDIBSize = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER) + dwBmBitsSize;
    bmfHdr.bfSize = dwDIBSize;
    bmfHdr.bfReserved1 = 0;
    bmfHdr.bfReserved2 = 0;
    bmfHdr.bfOffBits = (DWORD)sizeof(BITMAPFILEHEADER) + (DWORD)sizeof(BITMAPINFOHEADER);

    // 写入位图文件头
    WriteFile(fh, (LPSTR)&bmfHdr, sizeof(BITMAPFILEHEADER), &dwWritten, NULL);
    // 写入位图信息头
    WriteFile(fh, (LPSTR)&bi, sizeof(BITMAPINFOHEADER), &dwWritten, NULL);

    // 获取位图阵列
    lpmem = new char[dwBmBitsSize];
    lpbk = (LPSTR) new char[dwBmBitsSize];
    GetBitmapBits(hBitmap, dwBmBitsSize, lpmem); // 正向的内存图象数据

    // 转化为倒向数据(仅在bmHeight为正时需要)
    for (int i = 0; i < Bitmap.bmHeight; i++)
    {
        memcpy(lpbk + Bitmap.bmWidth * i * 4, lpmem + Bitmap.bmWidth * (Bitmap.bmHeight - i - 1) * 4, Bitmap.bmWidth * 4);
    }
    // 写位图数据
    WriteFile(fh, lpbk, dwBmBitsSize, &dwWritten, NULL);

    // 清除
    delete[] lpbk;
    delete[] lpmem;

    CloseHandle(fh);
    return TRUE;
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

    return data;
}
DECLARE void gdi_screenshot(HWND hwnd, RECT rect, void (*cb)(byte *, size_t))
{
    if (rect.bottom == rect.top || rect.left == rect.right)
        return;
    if (!hwnd)
        hwnd = GetDesktopWindow();
    auto hdc = GetDC(hwnd);
    if (!hdc)
        return;
    auto bm = GetBitmap(rect, hdc);
    // SaveBitmapToFile(bm, LR"(.\2.bmp)");
    size_t size;
    auto bf = std::move(SaveBitmapToBuffer(bm));
    if (bf.size())
        cb(bf.data(), bf.size());
    DeleteObject(bm);
    ReleaseDC(hwnd, hdc);
}

DECLARE void maximum_window(HWND hwnd)
{
    RECT rect;
    GetVirtualDesktopRect(rect);
    MoveWindow(hwnd, rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top, TRUE);
}