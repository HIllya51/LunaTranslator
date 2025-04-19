
typedef LONG NTSTATUS;
#include "yapi.hpp"
#include "host.h"
namespace
{

    constexpr auto PROCESS_INJECT_ACCESS = (PROCESS_CREATE_THREAD |
                                            PROCESS_QUERY_INFORMATION |
                                            PROCESS_VM_OPERATION |
                                            PROCESS_VM_WRITE |
                                            PROCESS_VM_READ);
    bool SafeInject(HANDLE process, const std::wstring &location)
    {
// #ifdef _WIN64
#if 0
			BOOL invalidProcess = FALSE;
			IsWow64Process(process, &invalidProcess);
			if (invalidProcess) return AddConsoleOutput(NEED_32_BIT);
#endif
        bool succ = false;
        if (LPVOID remoteData = VirtualAllocEx(process, nullptr, (location.size() + 1) * sizeof(wchar_t), MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE))
        {
            WriteProcessMemory(process, remoteData, location.c_str(), (location.size() + 1) * sizeof(wchar_t), nullptr);
            auto pThreadProc = (LPTHREAD_START_ROUTINE)GetProcAddress(GetModuleHandle(TEXT("kernel32.dll")), "LoadLibraryW");
            if (AutoHandle<> thread = CreateRemoteThread(process, nullptr, 0, pThreadProc, remoteData, 0, nullptr))
            {
                WaitForSingleObject(thread, INFINITE);
                succ = true;
            }
            else if (GetLastError() == ERROR_ACCESS_DENIED)
            {
                // Host::AddConsoleOutput(TR[NEED_64_BIT]); // https://stackoverflow.com/questions/16091141/createremotethread-access-denied
                succ = false;
            }
            VirtualFreeEx(process, remoteData, 0, MEM_RELEASE);
        }
        return succ;
    }

    bool UnSafeInject(HANDLE process, const std::wstring &location)
    {

        DWORD64 injectedDll;
        yapi::YAPICall LoadLibraryW(process, _T("kernel32.dll"), "LoadLibraryW");
        if (x64)
            injectedDll = LoadLibraryW.Dw64()(location.c_str());
        else
            injectedDll = LoadLibraryW(location.c_str());
        if (injectedDll)
            return true;
        return false;
    }
    BOOL Is64BitProcess(HANDLE ph)
    {
        BOOL f64bitProc = FALSE;
        if (detail::Is64BitOS())
        {
            f64bitProc = !(IsWow64Process(ph, &f64bitProc) && f64bitProc);
        }
        return f64bitProc;
    }
    bool InjectDll(DWORD processId)
    {
        AutoHandle<> process = OpenProcess(PROCESS_INJECT_ACCESS, FALSE, processId);
        if (!process)
            return false;
        bool proc64 = Is64BitProcess(process);
        auto dllname = proc64 ? LUNA_HOOK_DLL_64 : LUNA_HOOK_DLL_32;
        std::wstring location = std::filesystem::path(getModuleFilename().value()).replace_filename(dllname);
        if (proc64 == x64)
        {
            return (SafeInject(process, location));
        }
        else
        {
            return (UnSafeInject(process, location));
        }
    }
}
namespace Host
{

    void ConnectAndInjectProcess(DWORD processId)
    {
        Host::ConnectProcess(processId);
        if (!Host::CheckIfNeedInject(processId))
            return;

        std::thread([=]
                    {
			if(InjectDll(processId))return ;
			Host::AddConsoleOutput(TR[INJECT_FAILED]); })
            .detach();
    }

}