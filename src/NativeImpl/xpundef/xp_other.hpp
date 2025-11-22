
// Ro initialization flags; passed to Windows::Runtime::Initialize
typedef enum RO_INIT_TYPE
{
#pragma region Desktop Family
#if WINAPI_FAMILY_PARTITION(WINAPI_PARTITION_DESKTOP)
    RO_INIT_SINGLETHREADED = 0, // Single-threaded application
#endif                          // WINAPI_FAMILY_PARTITION(WINAPI_PARTITION_DESKTOP)
    RO_INIT_MULTITHREADED = 1,  // COM calls objects on any thread.
} RO_INIT_TYPE;

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