#pragma once
extern "C"
{
    __declspec(dllexport) void winrt_capture_window(HWND hwnd, void (*cb)(byte *, size_t));

    __declspec(dllexport) bool check_language_valid(wchar_t *);
    __declspec(dllexport) void getlanguagelist(void (*cb)(LPCWSTR));
    __declspec(dllexport) void OCR(void *ptr, size_t size, wchar_t *lang, wchar_t *, void (*)(int, int, int, int, LPCWSTR));

}