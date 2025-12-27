
typedef PVOID DLL_DIRECTORY_COOKIE, *PDLL_DIRECTORY_COOKIE;

extern "C" DLL_DIRECTORY_COOKIE
    WINAPI
    AddDllDirectory(
        _In_ PCWSTR NewDirectory);

extern "C" BOOL
    WINAPI
    SetDefaultDllDirectories(
        _In_ DWORD DirectoryFlags);

#define LOAD_LIBRARY_SEARCH_DEFAULT_DIRS 0x00001000

extern "C" _Check_return_
    HRESULT
        WINAPI
        RoInitialize(
            _In_ RO_INIT_TYPE initType);