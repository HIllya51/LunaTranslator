#include "python.h"
#include <dwrite.h>
extern "C" __declspec(dllexport) const wchar_t *internal_renpy_call_host(const wchar_t *text, int split)
{
    return text;
}
bool Luna_checkisusingembed(uint64_t address, uint64_t ctx2, bool usingsplit)
{
    auto sm = commonsharedmem;
    if (!sm)
        return false;
    for (int i = 0; i < ARRAYSIZE(sm->embedtps); i++)
    {
        if (sm->embedtps[i].use)
        {
            if (!usingsplit)
                return true;
            if ((sm->embedtps[i].tp.addr == address) && (sm->embedtps[i].tp.ctx2 == ctx2))
                return true;
        }
    }
    return false;
}
extern "C" __declspec(dllexport) bool internal_renpy_call_is_embed_using(int split, bool usingsplit)
{
    return Luna_checkisusingembed((uint64_t)internal_renpy_call_host, split, usingsplit);
}
namespace
{

    typedef enum
    {
        PyGILState_LOCKED,
        PyGILState_UNLOCKED
    } PyGILState_STATE;
    typedef PyGILState_STATE (*PyGILState_Ensure_t)(void);
    typedef void (*PyGILState_Release_t)(PyGILState_STATE);
    typedef int (*PyRun_SimpleString_t)(const char *command);

    PyRun_SimpleString_t PyRun_SimpleString;
    PyGILState_Release_t PyGILState_Release;
    PyGILState_Ensure_t PyGILState_Ensure;

    bool LoadPyRun(HMODULE module)
    {
        PyGILState_Ensure = (PyGILState_Ensure_t)GetProcAddress(module, "PyGILState_Ensure");
        PyGILState_Release = (PyGILState_Release_t)GetProcAddress(module, "PyGILState_Release");
        PyRun_SimpleString = (PyRun_SimpleString_t)GetProcAddress(module, "PyRun_SimpleString");
        return PyGILState_Ensure && PyGILState_Release && PyRun_SimpleString;
    }

    void PyRunScript(const char *script)
    {
        if (!(PyGILState_Ensure && PyGILState_Release && PyRun_SimpleString))
            return;

        auto state = PyGILState_Ensure();
        PyRun_SimpleString(script);
        PyGILState_Release(state);
    }

    void hook_internal_renpy_call_host()
    {
        HookParam hp_internal;
        hp_internal.address = (uintptr_t)internal_renpy_call_host;
        hp_internal.offset = GETARG1;
        hp_internal.split = GETARG2;
        hp_internal.type = USING_SPLIT | USING_STRING | CODEC_UTF16 | EMBED_ABLE |  EMBED_AFTER_NEW | NO_CONTEXT;
        NewHook(hp_internal, "internal_renpy_call_host");
        PyRunScript(LoadResData(L"renpy_hook_text", L"PYSOURCE").c_str());
    }

    typedef BOOL(WINAPI *PGFRI)(LPCWSTR, LPDWORD, LPVOID, DWORD);
#define QFR_LOGFONT (2)
#define LOADFONTTHREADNUM 4
    std::unordered_map<std::wstring, std::wstring> loadfontfiles()
    {

        PWSTR localAppDataPath;
        HRESULT result = SHGetKnownFolderPath(FOLDERID_LocalAppData, 0, NULL, &localAppDataPath);
        std::unordered_map<std::wstring, std::wstring> fnts;

        std::vector<std::wstring> collectfile;
        for (auto fontdir : {std::wstring(LR"(C:\Windows\Fonts)"), std::wstring(localAppDataPath) + LR"(\Microsoft\Windows\Fonts)"})
        {
            if (!std::filesystem::exists(fontdir))
                continue;
            for (auto entry : std::filesystem::directory_iterator(fontdir))
            {
                collectfile.emplace_back(entry.path());
            }
        }
        std::vector<std::thread> ts;
        std::vector<decltype(fnts)> fntss(LOADFONTTHREADNUM);
        auto singletask = [&](int i)
        {
            HINSTANCE hGdi32 = GetModuleHandleA("gdi32.dll");
            if (hGdi32 == 0)
                return;
            PGFRI GetFontResourceInfo = (PGFRI)GetProcAddress(hGdi32, "GetFontResourceInfoW");
            for (auto j = i; j < collectfile.size(); j += LOADFONTTHREADNUM)
            {
                auto fontfile = collectfile[j];
                DWORD dwFontsLoaded = AddFontResourceExW(fontfile.c_str(), FR_PRIVATE, 0);
                if (dwFontsLoaded == 0)
                {
                    continue;
                }

                auto lpLogfonts = std::make_unique<LOGFONTW[]>(dwFontsLoaded);
                DWORD cbBuffer = dwFontsLoaded * sizeof(LOGFONTW);
                auto succ = GetFontResourceInfo(fontfile.c_str(), &cbBuffer, lpLogfonts.get(), QFR_LOGFONT);
                RemoveFontResourceExW(fontfile.c_str(), FR_PRIVATE, 0);
                if (!succ)
                    continue;
                for (int k = 0; k < dwFontsLoaded; k++)
                    fntss[i].insert(std::make_pair(lpLogfonts[k].lfFaceName, fontfile));
            }
        };
        for (int i = 0; i < LOADFONTTHREADNUM; i++)
        {
            ts.emplace_back(std::thread(singletask, i));
        }
        for (int i = 0; i < LOADFONTTHREADNUM; i++)
            ts[i].join();
        for (int i = 0; i < LOADFONTTHREADNUM; i++)
        {
            for (auto p : fntss[i])
                fnts.insert(std::move(p));
        }
        return fnts;
    }

    // https://stackoverflow.com/questions/16769758/get-a-font-filename-based-on-the-font-handle-hfont
    HRESULT(*fnDWriteCreateFactory)
    (
        _In_ DWRITE_FACTORY_TYPE factoryType,
        _In_ REFIID iid,
        _COM_Outptr_ IUnknown **factory);
    std::list<WCHAR *> get_fonts_path(LPCWSTR family_name, BOOL is_bold, BOOL is_italic, BYTE charset)
    {
        std::list<WCHAR *> fonts_filename_list;
        HRESULT hr;

        IDWriteFactory *dwrite_factory;
        hr = fnDWriteCreateFactory(DWRITE_FACTORY_TYPE_ISOLATED, __uuidof(IDWriteFactory), reinterpret_cast<IUnknown **>(&dwrite_factory));
        if (FAILED(hr))
        {
            return fonts_filename_list;
        }

        IDWriteGdiInterop *gdi_interop;
        hr = dwrite_factory->GetGdiInterop(&gdi_interop);
        if (FAILED(hr))
        {
            dwrite_factory->Release();
            return fonts_filename_list;
        }

        LOGFONT lf;
        memset(&lf, 0, sizeof(lf));
        wcscpy_s(lf.lfFaceName, LF_FACESIZE, family_name);
        lf.lfWeight = is_bold ? FW_BOLD : FW_REGULAR; // TODO Change with the real ass weight
        lf.lfItalic = is_italic;
        lf.lfCharSet = charset;
        lf.lfOutPrecision = OUT_TT_PRECIS;
        lf.lfClipPrecision = CLIP_DEFAULT_PRECIS;
        lf.lfQuality = ANTIALIASED_QUALITY;
        lf.lfPitchAndFamily = DEFAULT_PITCH | FF_DONTCARE;

        HFONT hFont = CreateFontIndirect(&lf);
        HDC hdc = CreateCompatibleDC(NULL);
        HFONT hOldFont = SelectFont(hdc, hFont);

        IDWriteFontFace *font_face;
        hr = gdi_interop->CreateFontFaceFromHdc(hdc, &font_face);
        if (FAILED(hr))
        {
            gdi_interop->Release();
            dwrite_factory->Release();
            return fonts_filename_list;
        }

        UINT file_count;
        hr = font_face->GetFiles(&file_count, NULL);
        if (FAILED(hr))
        {
            font_face->Release();
            gdi_interop->Release();
            dwrite_factory->Release();
            return fonts_filename_list;
        }

        IDWriteFontFile **font_files = new IDWriteFontFile *[file_count];
        hr = font_face->GetFiles(&file_count, font_files);
        if (FAILED(hr))
        {
            font_face->Release();
            gdi_interop->Release();
            dwrite_factory->Release();
            return fonts_filename_list;
        }

        for (int i = 0; i < file_count; i++)
        {
            LPCVOID font_file_reference_key;
            UINT font_file_reference_key_size;
            hr = font_files[i]->GetReferenceKey(&font_file_reference_key, &font_file_reference_key_size);
            if (FAILED(hr))
            {
                font_files[i]->Release();
                continue;
            }

            IDWriteFontFileLoader *loader;
            hr = font_files[i]->GetLoader(&loader);
            if (FAILED(hr))
            {
                font_files[i]->Release();
                continue;
            }

            IDWriteLocalFontFileLoader *local_loader;
            hr = loader->QueryInterface(__uuidof(IDWriteLocalFontFileLoader), (void **)&local_loader);
            if (FAILED(hr))
            {
                loader->Release();
                font_files[i]->Release();
                continue;
            }

            UINT32 path_length;
            hr = local_loader->GetFilePathLengthFromKey(font_file_reference_key, font_file_reference_key_size, &path_length);
            if (FAILED(hr))
            {
                local_loader->Release();
                loader->Release();
                font_files[i]->Release();
                continue;
            }

            WCHAR *path = new WCHAR[path_length + 1];
            hr = local_loader->GetFilePathFromKey(font_file_reference_key, font_file_reference_key_size, path, path_length + 1);
            if (FAILED(hr))
            {
                local_loader->Release();
                loader->Release();
                font_files[i]->Release();
                continue;
            }

            fonts_filename_list.push_back(path);

            local_loader->Release();
            loader->Release();
            font_files[i]->Release();
        }

        font_face->Release();
        gdi_interop->Release();
        SelectObject(hdc, hOldFont);
        ReleaseDC(NULL, hdc);
        DeleteObject(hFont);

        dwrite_factory->Release();

        return fonts_filename_list;
    }

}
extern "C" __declspec(dllexport) const wchar_t *internal_renpy_get_font()
{
    if (wcslen(commonsharedmem->fontFamily) == 0)
        return NULL;

    fnDWriteCreateFactory = (decltype(fnDWriteCreateFactory))GetProcAddress(LoadLibrary(L"Dwrite.dll"), "DWriteCreateFactory");
    if (fnDWriteCreateFactory)
    {
        auto fonts_filename_list = get_fonts_path(commonsharedmem->fontFamily, false, false, DEFAULT_CHARSET);
        if (fonts_filename_list.size() == 0)
            return NULL;
        return *fonts_filename_list.begin();
    }
    else
    {
        static auto fontname2fontfile = std::move(loadfontfiles());
        if (fontname2fontfile.find(commonsharedmem->fontFamily) == fontname2fontfile.end())
            return NULL;
        else
            return fontname2fontfile.at(commonsharedmem->fontFamily).c_str();
    }
}
bool hookrenpy(HMODULE module)
{
    if (!LoadPyRun(module))
        return false;
    patch_fun = []()
    {
        PyRunScript(LoadResData(L"renpy_hook_font", L"PYSOURCE").c_str());
    };
    hook_internal_renpy_call_host();
    dont_detach = true;
    return true;
}