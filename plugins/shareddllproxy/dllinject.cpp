#include <iostream>
#include <Windows.h>
int dllinjectwmain(int argc, wchar_t *argv[])
{

    for (int i = 1; i < argc - 1; i += 1)
    {
        auto PROCESS_INJECT_ACCESS = (PROCESS_CREATE_THREAD |
                                      PROCESS_QUERY_INFORMATION |
                                      PROCESS_VM_OPERATION |
                                      PROCESS_VM_WRITE |
                                      PROCESS_VM_READ);
        auto pid = _wtoi(argv[i]);
        auto hProcess = OpenProcess(PROCESS_INJECT_ACCESS, 0, pid);
        if (hProcess == 0)
            return 0;
        auto size = (wcslen(argv[argc - 1]) + 1) * sizeof(wchar_t);
        auto remoteData = VirtualAllocEx(hProcess,
                                         nullptr,
                                         size,
                                         MEM_RESERVE | MEM_COMMIT,
                                         PAGE_READWRITE);
        if (remoteData == 0)
            return 0;
        WriteProcessMemory(hProcess, remoteData, argv[argc - 1], size, 0);
        auto hThread = CreateRemoteThread(hProcess, 0, 0, (LPTHREAD_START_ROUTINE)LoadLibraryW, remoteData, 0, 0);
        // if (hThread == 0) return 0;很奇怪，为0但是成功
        WaitForSingleObject(hThread, 10000);
        CloseHandle(hThread);
        VirtualFreeEx(hProcess, remoteData, size, MEM_RELEASE);
        CloseHandle(hProcess);
    }
    return 1;
}
