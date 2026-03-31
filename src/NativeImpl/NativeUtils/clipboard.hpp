
struct clipboardcloser
{
    ~clipboardcloser() { CloseClipboard(); }
};
std::unique_ptr<clipboardcloser> tryopenclipboard(HWND hwnd = 0)
{
    bool success = false;
    for (int i = 0; i < 50; i++)
    {
        if (OpenClipboard(hwnd))
        {
            success = true;
            break;
        }
        else
        {
            Sleep(10);
        }
    }
    if (success)
        return std::make_unique<clipboardcloser>();
    return {};
}

std::optional<std::wstring> clipboard_get_internal()
{
    if (!IsClipboardFormatAvailable(CF_UNICODETEXT))
        return {};
    auto clip = tryopenclipboard();
    if (!clip)
        return {};
    HANDLE hData = GetClipboardData(CF_UNICODETEXT);
    if (hData == 0)
        return {};
    LPWSTR pszText = static_cast<LPWSTR>(GlobalLock(hData));
    if (pszText == 0)
        return {};
    std::wstring data = pszText;
    GlobalUnlock(hData);
    return data;
}

DECLARE_API bool ClipBoardGetText(void (*cb)(const wchar_t *))
{
    auto data = std::move(clipboard_get_internal());
    if (!data)
        return false;
    cb(data.value().c_str());
    return true;
}
extern HWND globalmessagehwnd;

DECLARE_API bool ClipBoardSetText(wchar_t *text)
{
    auto clip = tryopenclipboard(globalmessagehwnd);
    if (!clip)
        return false;
    EmptyClipboard();
    HGLOBAL hClipboardData;
    size_t len = wcslen(text) + 1;
    hClipboardData = GlobalAlloc(GMEM_MOVEABLE, len * sizeof(wchar_t));
    if (hClipboardData == 0)
        return false;
    auto pchData = (wchar_t *)GlobalLock(hClipboardData);
    if (pchData == 0)
    {
        GlobalFree(hClipboardData);
        return false;
    }
    wcscpy_s(pchData, len, text);
    GlobalUnlock(hClipboardData);
    if (!SetClipboardData(CF_UNICODETEXT, hClipboardData))
    {
        GlobalFree(hClipboardData);
        return false;
    }
    return true;
}
inline bool iscurrentowndclipboard()
{
    auto ohwnd = GetClipboardOwner();
    DWORD pid;
    GetWindowThreadProcessId(ohwnd, &pid);
    return pid == GetCurrentProcessId();
}

#ifndef WINXP
#define addClipboardFormatListener AddClipboardFormatListener
#define removeClipboardFormatListener RemoveClipboardFormatListener
#else
#ifndef __C65AB19A_FFA2_4BB6_B2D2_508A6509AD7A__
#define __C65AB19A_FFA2_4BB6_B2D2_508A6509AD7A__
struct INFO_EFB07CE8_C478_475C_9B6D_1862D6400474
{
    HWND hwndNextViewer = NULL;
    HWND Listener = NULL;
};
auto KLASS_4420FB75_2931_459E_BA36_B2484F6DC9EE = TEXT("4420FB75_2931_459E_BA36_B2484F6DC9EE");
auto PROP_5B7BE8DE_E87B_4FC7_8562_48E4E42880DB = TEXT("5B7BE8DE_E87B_4FC7_8562_48E4E42880DB");
LRESULT CALLBACK WNDPROC_8DDD0332_D337_4F76_AF3C_D0CF23E94191(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    switch (msg)
    {
    case WM_DRAWCLIPBOARD:
    case WM_CHANGECBCHAIN:
    case WM_DESTROY:
    {
        auto info = reinterpret_cast<INFO_EFB07CE8_C478_475C_9B6D_1862D6400474 *>(GetWindowLongPtrW(hwnd, GWLP_USERDATA));
        if (!info)
            return DefWindowProc(hwnd, msg, wParam, lParam);
        switch (msg)
        {
        case WM_DRAWCLIPBOARD:
        {
            if (info->hwndNextViewer)
                SendMessage(info->hwndNextViewer, msg, wParam, lParam);
            PostMessage(info->Listener, WM_CLIPBOARDUPDATE, 0, 0);
        }
        break;
        case WM_CHANGECBCHAIN:
        {
            if (((HWND)wParam == info->hwndNextViewer))
                info->hwndNextViewer = (HWND)lParam;
            else if (info->hwndNextViewer)
                SendMessage(info->hwndNextViewer, msg, wParam, lParam);
        }
        break;
        case WM_DESTROY:
        {
            if (info->hwndNextViewer)
                ChangeClipboardChain(hwnd, info->hwndNextViewer);
            delete info;
        }
        break;
        }
    }
    break;
    default:
        return DefWindowProc(hwnd, msg, wParam, lParam);
    }
    return 0;
}
#endif
BOOL addClipboardFormatListener(HWND _hWnd)
{
    WNDCLASS wc = {};
    ZeroMemory(&wc, sizeof(WNDCLASS));
    wc.lpfnWndProc = WNDPROC_8DDD0332_D337_4F76_AF3C_D0CF23E94191;
    GetModuleHandleEx(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS, (LPCTSTR)wc.lpfnWndProc, &wc.hInstance);
    wc.lpszClassName = KLASS_4420FB75_2931_459E_BA36_B2484F6DC9EE;
    RegisterClass(&wc);
    auto hwnd = CreateWindowEx(0, KLASS_4420FB75_2931_459E_BA36_B2484F6DC9EE, NULL, 0, 0, 0, 0, 0, HWND_MESSAGE, nullptr, wc.hInstance, nullptr);
    if (!hwnd)
        return FALSE;
    auto info = new INFO_EFB07CE8_C478_475C_9B6D_1862D6400474{};
    info->Listener = _hWnd;
    info->hwndNextViewer = SetClipboardViewer(hwnd); // WM_DRAWCLIPBOARD会立即通知一次，但AddClipboardFormatListener不会
    SetWindowLongPtrW(hwnd, GWLP_USERDATA, (LONG_PTR)info);
    SetProp(_hWnd, PROP_5B7BE8DE_E87B_4FC7_8562_48E4E42880DB, hwnd);
    return TRUE;
}
BOOL removeClipboardFormatListener(HWND _hWnd)
{
    auto hwnd = (HWND)GetProp(_hWnd, PROP_5B7BE8DE_E87B_4FC7_8562_48E4E42880DB);
    if (!hwnd)
        return TRUE;
    DestroyWindow(hwnd);
    RemoveProp(_hWnd, PROP_5B7BE8DE_E87B_4FC7_8562_48E4E42880DB);
    return TRUE;
}
#endif

DECLARE_API bool ClipBoardSetImage(void *ptr, size_t size)
{
    size -= sizeof(BITMAPFILEHEADER);
    HGLOBAL hDib = GlobalAlloc(GMEM_MOVEABLE, size);
    if (!hDib)
        return false;
    void *pDib = GlobalLock(hDib);
    if (!pDib)
    {
        GlobalFree(hDib);
        return false;
    }
    memcpy((char *)pDib, (char *)ptr + sizeof(BITMAPFILEHEADER), size);
    auto clip = tryopenclipboard(globalmessagehwnd);
    if (!clip)
        return false;
    EmptyClipboard();
    if (!SetClipboardData(CF_DIB, hDib))
    {
        GlobalFree(hDib);
        return false;
    }
    return true;
}

DECLARE_API bool ClipBoardGetImage(void (*cb)(void *ptr, size_t size))
{
    if (!IsClipboardFormatAvailable(CF_DIB))
        return false;
    auto clip = tryopenclipboard();
    if (!clip)
        return false;
    bool success = false;

    HANDLE hClipboardData = GetClipboardData(CF_DIB);
    if (!hClipboardData)
        return false;
    BYTE *pDib = (BYTE *)GlobalLock(hClipboardData);
    SIZE_T dibSize = GlobalSize(hClipboardData);

    if (!pDib)
        return false;
    std::vector<BYTE> fullBmp;
    fullBmp.resize(sizeof(BITMAPFILEHEADER) + dibSize);
    BITMAPFILEHEADER *bfh = (BITMAPFILEHEADER *)fullBmp.data();
    bfh->bfType = 0x4D42;
    bfh->bfSize = (DWORD)fullBmp.size();
    bfh->bfReserved1 = 0;
    bfh->bfReserved2 = 0;
    BITMAPINFOHEADER *pHeader = (BITMAPINFOHEADER *)pDib;
    DWORD dwPaletteSize = (pHeader->biBitCount <= 8) ? (1 << pHeader->biBitCount) * sizeof(RGBQUAD) : 0;
    bfh->bfOffBits = sizeof(BITMAPFILEHEADER) + pHeader->biSize + dwPaletteSize;

    memcpy(fullBmp.data() + sizeof(BITMAPFILEHEADER), pDib, dibSize);

    GlobalUnlock(hClipboardData);
    cb(fullBmp.data(), fullBmp.size());
    return true;
}

DECLARE_API bool ClipBoardGetFileNames(void (*cb)(const wchar_t *))
{
    if (!IsClipboardFormatAvailable(CF_HDROP))
        return false;
    auto clip = tryopenclipboard();
    if (!clip)
        return false;
    HGLOBAL hGlobal = GetClipboardData(CF_HDROP);
    if (!hGlobal)
        return false;
    HDROP hDrop = (HDROP)GlobalLock(hGlobal);
    if (!hDrop)
        return false;
    UINT fileCount = DragQueryFile(hDrop, 0xFFFFFFFF, NULL, 0);

    bool succ = false;
    for (UINT i = 0; i < fileCount; ++i)
    {
        UINT pathLen = DragQueryFile(hDrop, i, NULL, 0);
        auto pszFileName = std::make_unique<WCHAR[]>(pathLen + 1);
        DragQueryFile(hDrop, i, pszFileName.get(), pathLen + 1);
        succ = true;
        cb(pszFileName.get());
    }
    GlobalUnlock(hGlobal);
    return succ;
}
