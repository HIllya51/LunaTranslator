
DECLARE_API void OCR(void *ptr, size_t size, wchar_t *lang, wchar_t *space, void (*cb)(int, int, int, int, LPCWSTR))
{
}
DECLARE_API bool check_language_valid(wchar_t *language)
{
    return false;
}
DECLARE_API void getlanguagelist(void (*cb)(LPCWSTR, LPCWSTR))
{
}
DECLARE_API void winrt_capture_window(HWND hwnd, void (*cb)(byte *, size_t))
{
}