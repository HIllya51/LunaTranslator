#pragma once
struct ocrres
{
    wchar_t **lines;
    int *xs;
    int *ys;
    int *xs2;
    int *ys2;
};
extern "C"
{
    __declspec(dllexport) void winrt_capture_window(wchar_t *savepath, HWND hwnd);

    __declspec(dllexport) bool check_language_valid(wchar_t *);
    __declspec(dllexport) wchar_t **getlanguagelist(int *);
    __declspec(dllexport) ocrres OCR(wchar_t *fname, wchar_t *lang, wchar_t *, int *);

    __declspec(dllexport) void freewstringlist(wchar_t **, int);
    __declspec(dllexport) void freeocrres(ocrres, int);
}
char **vecstr2c(std::vector<std::string> &vs);
int *vecint2c(std::vector<int> &vs);
wchar_t **vecwstr2c(std::vector<std::wstring> &vs);