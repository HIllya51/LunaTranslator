#include "osversion.hpp"
#include <pdh.h>
#include <pdhmsg.h>

DECLARE_API uint64_t GetProcessMemory(DWORD pid)
{
    auto hProcess = CHandle{OpenProcess(FUCKPRIVI | PROCESS_VM_READ, FALSE, pid)};
    if (!hProcess)
        return 0;

    PROCESS_MEMORY_COUNTERS_EX pmc;
    if (GetProcessMemoryInfo(hProcess, reinterpret_cast<PROCESS_MEMORY_COUNTERS *>(&pmc), sizeof(pmc)))
    {
        return (pmc.WorkingSetSize == ((SIZE_T)-1)) ? 0 : pmc.WorkingSetSize;
    }
    return 0;
}

DECLARE_API uint64_t GetProcessVRAM(DWORD pid, bool Dedicated)
{
    PDH_HQUERY hQuery;
    PDH_STATUS status = PdhOpenQuery(NULL, 0, &hQuery);
    if (status != ERROR_SUCCESS)
        return 0;

    uint64_t totalBytes = 0;
    auto returnX = [=]()
    { PdhCloseQuery(hQuery);return totalBytes; };

    std::wstring path = L"\\GPU Process Memory(pid_" + std::to_wstring(pid) + (Dedicated ? L"_*)\\Dedicated Usage" : L"_*)\\Shared Usage");

    PDH_HCOUNTER hCounter;
    PDH_HCOUNTER hCounterShared;

    PdhAddEnglishCounterW(hQuery, path.c_str(), 0, &hCounter);

    status = PdhCollectQueryData(hQuery);
    if (status != ERROR_SUCCESS)
        return returnX();

    DWORD dwBufferSize = 0;
    DWORD dwItemCount = 0;

    PDH_STATUS stat = PdhGetFormattedCounterArrayW(hCounter, PDH_FMT_LARGE, &dwBufferSize, &dwItemCount, NULL);

    if (!(stat == PDH_MORE_DATA || stat == ERROR_SUCCESS))
        return returnX();
    if (dwBufferSize == 0 || dwItemCount == 0)
        return returnX();

    std::vector<BYTE> buffer(dwBufferSize);
    PPDH_FMT_COUNTERVALUE_ITEM_W pItems = (PPDH_FMT_COUNTERVALUE_ITEM_W)buffer.data();

    stat = PdhGetFormattedCounterArrayW(hCounter, PDH_FMT_LARGE, &dwBufferSize, &dwItemCount, pItems);

    if (stat != ERROR_SUCCESS)
        return returnX();

    for (DWORD i = 0; i < dwItemCount; i++)
    {
        totalBytes += pItems[i].FmtValue.largeValue;
    }
    return returnX();
}