#pragma once
#define DECLARE extern "C" __declspec(dllexport)
extern "C"
{

    __declspec(dllexport) HANDLE startdarklistener();
    __declspec(dllexport) bool queryversion(const wchar_t *exe, WORD *_1, WORD *_2, WORD *_3, WORD *_4);

    __declspec(dllexport) wchar_t **SAPI_List(int version, size_t *);
    __declspec(dllexport) BOOL SetProcessMute(DWORD Pid, bool mute);
    __declspec(dllexport) bool GetProcessMute(DWORD Pid);

    __declspec(dllexport) size_t levenshtein_distance(size_t len1, const wchar_t *string1,
                                                      size_t len2, const wchar_t *string2);
    __declspec(dllexport) double levenshtein_ratio(size_t len1, const wchar_t *string1,
                                                   size_t len2, const wchar_t *string2);

    __declspec(dllexport) void freewstringlist(wchar_t **, int);
    __declspec(dllexport) void free_all(void *str);
    __declspec(dllexport) void freestringlist(char **, int);

    __declspec(dllexport) void *mecab_init(char *utf8path, wchar_t *);
    __declspec(dllexport) bool mecab_parse(void *trigger, char *utf8string, char ***surface, char ***features, int *num);
    __declspec(dllexport) void mecab_end(void *trigger);

    __declspec(dllexport) wchar_t *clipboard_get();
    __declspec(dllexport) bool clipboard_set(HWND hwnd, wchar_t *text);
    __declspec(dllexport) void GetLnkTargetPath(wchar_t *lnkFilePath, wchar_t *path, wchar_t *tgtpath, wchar_t *iconpath, wchar_t *dirpath);
    __declspec(dllexport) bool otsu_binary(const void *image, int thresh);

    __declspec(dllexport) void *extracticon2data(const wchar_t *name, size_t *l);

    __declspec(dllexport) void c_free(void *);
}