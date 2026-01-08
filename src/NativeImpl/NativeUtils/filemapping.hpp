#include<dbghelp.h>

struct FileMapping
{
    void *mapAddr = nullptr;
    ~FileMapping()
    {
        if (mapAddr)
            UnmapViewOfFile(mapAddr);
    }
    FileMapping(LPCWSTR file)
    {
        CHandle hFile{CreateFileW(file, GENERIC_READ, FILE_SHARE_READ, 0,
                                  OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0)};
        if (!hFile)
            return;
        CHandle hMap{CreateFileMappingW(
            hFile,
            NULL,          // security attrs
            PAGE_READONLY, // protection flags
            0,             // max size - high DWORD
            0,             // max size - low DWORD
            NULL)};        // mapping name - not used
        if (!hMap)
            return;

        mapAddr = MapViewOfFileEx(
            hMap,          // mapping object
            FILE_MAP_READ, // desired access
            0,             // loc to map - hi DWORD
            0,             // loc to map - lo DWORD
            0,             // #bytes to map - 0=all
            NULL);         // suggested map addr
        if (!mapAddr)
            return;
    }
};

inline PIMAGE_NT_HEADERS GetImageNtHeader(PVOID base)
{
    PIMAGE_DOS_HEADER pDosHeader = reinterpret_cast<PIMAGE_DOS_HEADER>(base);

    if (pDosHeader->e_magic != IMAGE_DOS_SIGNATURE)
        return nullptr;

    PIMAGE_NT_HEADERS pNtHeaders = ImageNtHeader(base);

    if (pNtHeaders->Signature != IMAGE_NT_SIGNATURE)
        return nullptr;
    return pNtHeaders;
}