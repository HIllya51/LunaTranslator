#include "bmpx.hpp"

HBITMAP GetBitmap(RECT &rect, HDC hDC)
{
    HDC hMemDC;
    HBITMAP hBitmap, hOldBitmap;

    hMemDC = CreateCompatibleDC(hDC);
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
std::optional<SimpleBMP> parseBMP(std::optional<SimpleBMP> &bmp, bool needcheck = false)
{
    if (!bmp)
        return {};
    if (needcheck)
    {
        bool checkempty = false;
        if (bmp.value().bitCount == 32)
        {
            checkempty = std::all_of((uint32_t *)bmp.value().pixels, (uint32_t *)bmp.value().pixels + bmp.value().pixelsize / 4, std::bind(std::equal_to<uint32_t>(), std::placeholders::_1, *(uint32_t *)bmp.value().pixels));
        }
        else
        {
            checkempty = std::all_of(bmp.value().pixels, bmp.value().pixels + bmp.value().pixelsize, std::bind(std::equal_to<unsigned char>(), std::placeholders::_1, 0));
        }
        if (checkempty)
            return {};
    }
    return std::move(bmp);
}
std::optional<SimpleBMP> __gdi_screenshot(HWND hwnd, RECT rect)
{
    if (checkempty(hwnd, rect))
        return {};
    bool needcheck = hwnd;
    if (!hwnd)
    {
        hwnd = GetDesktopWindow();
    }
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
    return parseBMP(CreateBMP(bm, false), needcheck);
}
DECLARE_API void GdiGrabWindow(HWND hwnd, void (*cb)(byte *, size_t))
{
    RECT rect{-1, -1, -1, -1};
    auto bf = __gdi_screenshot(hwnd, rect);
    if (bf)
        cb(bf.value().data.get(), bf.value().size);
}
DECLARE_API bool GdiCropImage(HWND hwnd, RECT rect, void (*cb)(byte *, size_t))
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
            {
                cb(bf.value().data.get(), bf.value().size);
                return true;
            }
        }
        break;
        case 1:
        {
            auto bf = __gdi_screenshot(NULL, rect);
            if (bf)
            {
                cb(bf.value().data.get(), bf.value().size);
                return !hwnd;
            }
        }
        }
    }
    return false;
}

DECLARE_API float GetDevicePixelRatioF(HWND hwnd)
{
    return 1.0f * GetDpiForWindow(hwnd) / USER_DEFAULT_SCREEN_DPI;
}
std::pair<HWND, WNDCLASS> CreateWindowForWndProc(WNDPROC WNDPROC_1, HWND parent, int x, int y, int, int h, HCURSOR cursor, DWORD style, DWORD exstyle);
namespace
{
    HDC hMemDCBitmapmask;
    HDC hMemDCBitmap;
    HBITMAP g_hScreenBitmap = NULL;
    HBITMAP g_hScreenBitmapmask = NULL;
    HBITMAP g_hMemBitmap = NULL; // 用于双缓冲的内存位图
    HDC g_hMemDC = NULL;         // 用于双缓冲的内存DC
    POINT g_startPoint = {0, 0};
    POINT g_endPoint = {0, 0};
    BOOL g_isSelecting = FALSE;
    float ocrselectalpha;
    float ocrrangewidth;
    int range_r;
    int range_g;
    int range_b;
    typedef void (*callback_t)(int x1, int y1, int x2, int y2, int xoff, int yoff, byte *, size_t);
    callback_t callback;
}
static LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);
static std::atomic<bool> onlyonewindow = false;
DECLARE_API void CreateSelectRangeWindow(HWND parent, float _ocrselectalpha, int _range_r, int _range_g, int _range_b, float _ocrrangewidth, callback_t _callback)
{
    {
        bool _ = false;
        if (!onlyonewindow.compare_exchange_strong(_, true))
            return;
    }
    /*
    QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    由于它的存在，Qt方无法正常创建截图窗口。
    */
    callback = _callback;
    ocrrangewidth = _ocrrangewidth;
    ocrselectalpha = _ocrselectalpha;
    range_r = _range_r;
    range_g = _range_g;
    range_b = _range_b;
    g_hMemBitmap = NULL; // 用于双缓冲的内存位图
    g_hMemDC = NULL;     // 用于双缓冲的内存DC
    g_startPoint = {0, 0};
    g_endPoint = {0, 0};
    g_isSelecting = FALSE;

    int screenWidth = GetSystemMetrics(SM_CXVIRTUALSCREEN);
    int screenHeight = GetSystemMetrics(SM_CYVIRTUALSCREEN);
    int screenX = GetSystemMetrics(SM_XVIRTUALSCREEN);
    int screenY = GetSystemMetrics(SM_YVIRTUALSCREEN);

    HDC hScreenDC = GetDC(NULL);
    hMemDCBitmap = CreateCompatibleDC(hScreenDC);
    g_hScreenBitmap = CreateCompatibleBitmap(hScreenDC, screenWidth, screenHeight);
    SelectObject(hMemDCBitmap, g_hScreenBitmap);
    BitBlt(hMemDCBitmap, 0, 0, screenWidth, screenHeight, hScreenDC, screenX, screenY, SRCCOPY);

    hMemDCBitmapmask = CreateCompatibleDC(hScreenDC);
    g_hScreenBitmapmask = CreateCompatibleBitmap(hScreenDC, screenWidth, screenHeight);
    SelectObject(hMemDCBitmapmask, g_hScreenBitmapmask);
    BitBlt(hMemDCBitmapmask, 0, 0, screenWidth, screenHeight, hMemDCBitmap, 0, 0, SRCCOPY);

    BLENDFUNCTION blendFunction = {0};
    blendFunction.BlendOp = AC_SRC_OVER;
    blendFunction.BlendFlags = 0;
    blendFunction.SourceConstantAlpha = 255 * ocrselectalpha; // 设置全局透明度为 128 (约50%)
    blendFunction.AlphaFormat = 0;                            // 使用 SourceConstantAlpha

    // 创建一个临时的黑色位图用于混合
    HDC hdcBlack = CreateCompatibleDC(hMemDCBitmapmask);
    HBITMAP hbmBlack = CreateCompatibleBitmap(hMemDCBitmapmask, 1, 1); // 1x1像素就够了
    SelectObject(hdcBlack, hbmBlack);
    SetBkColor(hdcBlack, RGB(0, 0, 0));                          // 设置背景为黑色
    ExtTextOut(hdcBlack, 0, 0, ETO_OPAQUE, NULL, NULL, 0, NULL); // 填充这个1x1像素

    // 将这个1x1的黑色位图拉伸并半透明地混合到整个内存DC上
    StretchBlt(hdcBlack, 0, 0, screenWidth, screenHeight, hdcBlack, 0, 0, 1, 1, SRCCOPY);
    AlphaBlend(hMemDCBitmapmask, 0, 0, screenWidth, screenHeight, hdcBlack, 0, 0, 1, 1, blendFunction);

    DeleteObject(hbmBlack);
    DeleteDC(hdcBlack);

    ReleaseDC(NULL, hScreenDC);
    auto &&[hwnd, _] = CreateWindowForWndProc(WindowProc, parent, screenX, screenY, screenWidth, screenHeight, LoadCursor(NULL, IDC_CROSS), WS_POPUP, WS_EX_TOPMOST);

    ShowWindow(hwnd, SW_SHOW);
    UpdateWindow(hwnd);

    MSG msg = {}; // 必须这里加上事件循环，否则会直接PostQuitMessage(0)会退出Qt的事件循环然后退出程序。
    while (GetMessage(&msg, NULL, 0, 0))
    {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    onlyonewindow = false;
}

static LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam)
{
    switch (uMsg)
    {
    case WM_CREATE:
    {
        // 为双缓冲创建内存DC和位图
        HDC hdc = GetDC(hwnd);
        g_hMemDC = CreateCompatibleDC(hdc);
        RECT rc;
        GetClientRect(hwnd, &rc);
        g_hMemBitmap = CreateCompatibleBitmap(hdc, rc.right - rc.left, rc.bottom - rc.top);
        SelectObject(g_hMemDC, g_hMemBitmap);
        ReleaseDC(hwnd, hdc);
    }
    break;

    case WM_DESTROY:
    {
        // 清理GDI资源
        DeleteObject(g_hScreenBitmapmask);
        DeleteObject(g_hScreenBitmap);
        DeleteObject(g_hMemBitmap);
        DeleteDC(g_hMemDC);
        DeleteDC(hMemDCBitmapmask);
        DeleteDC(hMemDCBitmap);
        PostQuitMessage(0);
    }
    break;

    case WM_PAINT:
    {
        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(hwnd, &ps);

        RECT clientRect;
        GetClientRect(hwnd, &clientRect);
        int width = clientRect.right - clientRect.left;
        int height = clientRect.bottom - clientRect.top;

        BitBlt(g_hMemDC, clientRect.left, clientRect.top, width, height, hMemDCBitmapmask, 0, 0, SRCCOPY);

        if (g_isSelecting)
        {
            int r_left = std::min(g_startPoint.x, g_endPoint.x);
            int r_top = std::min(g_startPoint.y, g_endPoint.y);
            int r_right = std::max(g_startPoint.x, g_endPoint.x);
            int r_bottom = std::max(g_startPoint.y, g_endPoint.y);
            int r_width = r_right - r_left;
            int r_height = r_bottom - r_top;
            auto scale = GetDevicePixelRatioF(hwnd);
            auto __ocrrangewidth = scale * ocrrangewidth;

            BitBlt(g_hMemDC, r_left - ceil(__ocrrangewidth), r_top - ceil(__ocrrangewidth), r_width + 2 * floor(__ocrrangewidth), r_height + 2 * floor(__ocrrangewidth), hMemDCBitmap, r_left - ceil(__ocrrangewidth), r_top - ceil(__ocrrangewidth), SRCCOPY);

            HPEN hPen = CreatePen(PS_SOLID, ceil(__ocrrangewidth), RGB(range_r, range_g, range_b));
            HPEN hOldPen = (HPEN)SelectObject(g_hMemDC, hPen);
            HBRUSH hOldBrush = (HBRUSH)SelectObject(g_hMemDC, GetStockObject(NULL_BRUSH));

            Rectangle(g_hMemDC, r_left - ceil(__ocrrangewidth / 2), r_top - ceil(__ocrrangewidth / 2), r_right + ceil(__ocrrangewidth / 2), r_bottom + ceil(__ocrrangewidth / 2));

            SelectObject(g_hMemDC, hOldPen);
            SelectObject(g_hMemDC, hOldBrush);
            DeleteObject(hPen);
        }

        BitBlt(hdc, 0, 0, width, height, g_hMemDC, 0, 0, SRCCOPY);

        EndPaint(hwnd, &ps);
    }
    break;

    case WM_LBUTTONDOWN:
    {
        g_startPoint.x = LOWORD(lParam);
        g_startPoint.y = HIWORD(lParam);
        g_endPoint = g_startPoint;
        g_isSelecting = TRUE;
        SetCapture(hwnd);
    }
    break;

    case WM_MOUSEMOVE:
    {
        if (g_isSelecting)
        {
            g_endPoint.x = LOWORD(lParam);
            g_endPoint.y = HIWORD(lParam);
            InvalidateRect(hwnd, NULL, FALSE);
        }
    }
    break;

    case WM_LBUTTONUP:
    {
        if (g_isSelecting)
        {
            if ((g_endPoint.x == g_startPoint.x) || (g_endPoint.y == g_startPoint.y))
            {
                DestroyWindow(hwnd);
                return 0;
            }
            auto &&bmp = CreateBMP(g_hScreenBitmap, false).value_or({});
            RECT rect;
            GetWindowRect(hwnd, &rect);
            ReleaseCapture();
            DestroyWindow(hwnd);
            callback(g_startPoint.x, g_startPoint.y, g_endPoint.x, g_endPoint.y, rect.left, rect.top, bmp.data.get(), bmp.size);
        }
    }
    break;

    case WM_RBUTTONUP:
    {
        DestroyWindow(hwnd);
    }
    break;
    case WM_KEYDOWN:
    {
        if (wParam == VK_ESCAPE)
        {
            DestroyWindow(hwnd);
        }
    }
    break;
    default:
        return DefWindowProc(hwnd, uMsg, wParam, lParam);
    }
    return 0;
}