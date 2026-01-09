#include "filemapping.hpp"
#ifdef WINXP
#include "../xpundef/xp_winnt.hpp"
#endif

using ImportInfoS = std::vector<std::pair<std::string, DWORD>>;
using ImportAnalysisResult = std::pair<ImportInfoS, ImportInfoS>;

inline PVOID Rva2Va(DWORD rva, PIMAGE_NT_HEADERS pNtHeaders, PVOID base)
{
    if constexpr (1)
    {
        return (DWORD *)ImageRvaToVa(pNtHeaders, base, rva, NULL);
    }
    else
    {
        if (auto sec = ImageRvaToSection(pNtHeaders, base, rva))
        {
            return rva - sec->VirtualAddress + sec->PointerToRawData + (BYTE *)base;
        }
        return nullptr;
    }
}
template <typename PIMAGE_X_DESCRIPTOR, size_t namefieldoffset>
inline void loadNames(ImportInfoS &r, PIMAGE_X_DESCRIPTOR pImportDescriptor, PVOID data, PIMAGE_NT_HEADERS pNtHeaders)
{
    if (!pImportDescriptor)
        return;
    while (auto namerva = *(DWORD *)((BYTE *)pImportDescriptor + namefieldoffset))
    {
        if (auto name = (char *)Rva2Va(namerva, pNtHeaders, data))
        {
            r.push_back({name, (DWORD)(name - (char *)data)});
        }
        pImportDescriptor++;
    }
}
template <typename PIMAGE_IMPORT_DESCRIPTOR, typename PIMAGE_NT_HEADERS_X, DWORD which>
inline PIMAGE_IMPORT_DESCRIPTOR GeDesc(PIMAGE_NT_HEADERS pNtHeaders, PVOID data)
{
    auto pNtHeaders64 = reinterpret_cast<PIMAGE_NT_HEADERS_X>(pNtHeaders);
    if (pNtHeaders64->OptionalHeader.NumberOfRvaAndSizes <= which)
        return NULL;
    DWORD importDirectoryRva = pNtHeaders64->OptionalHeader.DataDirectory[which].VirtualAddress;
    if (!importDirectoryRva)
        return NULL;

    return (PIMAGE_IMPORT_DESCRIPTOR)Rva2Va(importDirectoryRva, pNtHeaders, data);
}
template <typename PIMAGE_IMPORT_DESCRIPTOR, DWORD which>
inline PIMAGE_IMPORT_DESCRIPTOR GeDesc(PIMAGE_NT_HEADERS pNtHeaders, PVOID data)
{
    switch (pNtHeaders->OptionalHeader.Magic)
    {
    case IMAGE_NT_OPTIONAL_HDR64_MAGIC:
        return GeDesc<PIMAGE_IMPORT_DESCRIPTOR, PIMAGE_NT_HEADERS64, which>(pNtHeaders, data);
    case IMAGE_NT_OPTIONAL_HDR32_MAGIC:
        return GeDesc<PIMAGE_IMPORT_DESCRIPTOR, PIMAGE_NT_HEADERS32, which>(pNtHeaders, data);
    }
    return nullptr;
}
static ImportAnalysisResult importAnalysis(LPCWSTR file)
{
    ImportAnalysisResult result;
    FileMapping fm(file);
    if (!fm.mapAddr)
        return result;
    PIMAGE_NT_HEADERS pNtHeaders = GetImageNtHeader(fm.mapAddr);
    if (!pNtHeaders)
        return {};
    PIMAGE_IMPORT_DESCRIPTOR imports;
    PIMAGE_DELAYLOAD_DESCRIPTOR delayimports;
    if constexpr (1)
    {
        DWORD cDirSize;
        imports = (PIMAGE_IMPORT_DESCRIPTOR)ImageDirectoryEntryToData(fm.mapAddr, false, IMAGE_DIRECTORY_ENTRY_IMPORT, &cDirSize);
        delayimports = (PIMAGE_DELAYLOAD_DESCRIPTOR)ImageDirectoryEntryToData(fm.mapAddr, false, IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT, &cDirSize);
    }
    else
    {
        imports = GeDesc<PIMAGE_IMPORT_DESCRIPTOR, IMAGE_DIRECTORY_ENTRY_IMPORT>(pNtHeaders, fm.mapAddr);
        delayimports = GeDesc<PIMAGE_DELAYLOAD_DESCRIPTOR, IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT>(pNtHeaders, fm.mapAddr);
    }
    loadNames<PIMAGE_IMPORT_DESCRIPTOR, offsetof(IMAGE_IMPORT_DESCRIPTOR, Name)>(result.first, imports, fm.mapAddr, pNtHeaders);
    loadNames<PIMAGE_DELAYLOAD_DESCRIPTOR, offsetof(IMAGE_DELAYLOAD_DESCRIPTOR, DllNameRVA)>(result.second, delayimports, fm.mapAddr, pNtHeaders);
    return result;
}
using ExportInfoS = std::vector<std::string>;

static ExportInfoS exportAnalysis(LPCWSTR file)
{
    ExportInfoS result;
    FileMapping fm(file);
    if (!fm.mapAddr)
        return {};
    PIMAGE_NT_HEADERS ntHeaders = GetImageNtHeader(fm.mapAddr);
    if (!ntHeaders)
        return {};
    DWORD cDirSize;
    auto exportDir = (PIMAGE_EXPORT_DIRECTORY)ImageDirectoryEntryToData(fm.mapAddr, false, IMAGE_DIRECTORY_ENTRY_EXPORT, &cDirSize);
    if (!exportDir)
        return {};
    auto dNameRVAs = (DWORD *)ImageRvaToVa(ntHeaders, fm.mapAddr, exportDir->AddressOfNames, NULL);
    for (size_t i = 0; i < exportDir->NumberOfNames; i++)
    {
        auto sName = (char *)ImageRvaToVa(ntHeaders, fm.mapAddr, dNameRVAs[i], NULL);
        result.push_back(sName);
    }
    return result;
}
DECLARE_API void AnalysisDllImports(LPCWSTR file, void (*cb)(const char *, DWORD, bool))
{
    auto &&[import, delay] = importAnalysis(file);
    for (auto &&[fn, off] : import)
    {
        cb(fn.c_str(), off, true);
    }
    for (auto &&[fn, off] : delay)
    {
        cb(fn.c_str(), off, false);
    }
}

DECLARE_API void AnalysisDllExports(LPCWSTR file, void (*cb)(const char *))
{
    auto &&_ = exportAnalysis(file);
    for (auto &&name : _)
    {
        // Oridinal， RVA就先不输出了，反正用不着。
        cb(name.c_str());
    }
}