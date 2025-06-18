
#include "bmpx.hpp"

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
std::optional<SimpleBMP> __gdi_screenshot(HWND hwnd, RECT rect)
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
    ReleaseDC(hwnd, hdc);
    auto bmp = CreateBMP(bm, false);
    if (!bmp)
        return {};
    if (std::all_of(bmp.value().pixels, bmp.value().pixels + bmp.value().pixelsize, std::bind(std::equal_to<unsigned char>(), std::placeholders::_1, 0)))
        return {};
    return bmp;
}
DECLARE_API void GdiGrabWindow(HWND hwnd, void (*cb)(byte *, size_t))
{
    RECT rect{-1, -1, -1, -1};
    auto bf = __gdi_screenshot(hwnd, rect);
    if (bf)
        cb(bf.value().data.get(), bf.value().size);
}
DECLARE_API void GdiCropImage(HWND hwnd, RECT rect, void (*cb)(byte *, size_t))
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
            if (bf)
                return cb(bf.value().data.get(), bf.value().size);
        }
        break;
        case 1:
        {
            auto bf = __gdi_screenshot(NULL, rect);
            if (bf)
                return cb(bf.value().data.get(), bf.value().size);
        }
        }
    }
}

DECLARE_API void MaximumWindow(HWND hwnd)
{
    RECT rect;
    GetVirtualDesktopRect(rect);
    MoveWindow(hwnd, rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top, TRUE);
}
DECLARE_API float GetDevicePixelRatioF(HWND hwnd)
{
    return 1.0f * GetDpiForWindow(hwnd) / USER_DEFAULT_SCREEN_DPI;
}