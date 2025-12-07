#ifndef _WIN64

// https://stackoverflow.com/questions/59287991/how-to-get-remote-proc-address-of-injected-dll-into-another-process
#define ReCa reinterpret_cast
std::uintptr_t GetModuleBaseEx(DWORD pid, const wchar_t *modul)
{
    HANDLE snapshot_handle = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, pid);

    MODULEENTRY32W me32;
    me32.dwSize = sizeof(MODULEENTRY32W);
    if (!Module32FirstW(snapshot_handle, &me32))
        return 0;

    do
    {
        if (!lstrcmpiW(me32.szModule, modul))
            return reinterpret_cast<std::uintptr_t>(me32.modBaseAddr);
    } while (Module32NextW(snapshot_handle, &me32));

    CloseHandle(snapshot_handle);
    return 0;
}
uintptr_t GetProcAddressEx(HANDLE hProcess, DWORD pid, const wchar_t *module, const char *function)
{
    if (!module || !function || !pid || !hProcess)
        return 0;

    uintptr_t moduleBase = GetModuleBaseEx(pid, module); // toolhelp32snapshot method

    if (!moduleBase)
        return 0;

    IMAGE_DOS_HEADER Image_Dos_Header = {0};

    if (!ReadProcessMemory(hProcess, ReCa<LPCVOID>(moduleBase), &Image_Dos_Header, sizeof(IMAGE_DOS_HEADER), nullptr))
        return 0;

    if (Image_Dos_Header.e_magic != IMAGE_DOS_SIGNATURE)
        return 0;

    IMAGE_NT_HEADERS Image_Nt_Headers = {0};

    if (!ReadProcessMemory(hProcess, ReCa<LPCVOID>(moduleBase + Image_Dos_Header.e_lfanew), &Image_Nt_Headers, sizeof(IMAGE_NT_HEADERS), nullptr))
        return 0;

    if (Image_Nt_Headers.Signature != IMAGE_NT_SIGNATURE)
        return 0;

    IMAGE_EXPORT_DIRECTORY Image_Export_Directory = {0};
    uintptr_t img_exp_dir_rva = 0;

    if (!(img_exp_dir_rva = Image_Nt_Headers.OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress))
        return 0;

    if (!ReadProcessMemory(hProcess, ReCa<LPCVOID>(moduleBase + img_exp_dir_rva), &Image_Export_Directory, sizeof(IMAGE_EXPORT_DIRECTORY), nullptr))
        return 0;

    uintptr_t EAT = moduleBase + Image_Export_Directory.AddressOfFunctions;
    uintptr_t ENT = moduleBase + Image_Export_Directory.AddressOfNames;
    uintptr_t EOT = moduleBase + Image_Export_Directory.AddressOfNameOrdinals;

    WORD ordinal = 0;
    SIZE_T len_buf = strlen(function) + 1;
    auto temp_buf = std::make_unique<char[]>(len_buf);

    for (size_t i = 0; i < Image_Export_Directory.NumberOfNames; i++)
    {
        uintptr_t tempRvaString = 0;

        if (!ReadProcessMemory(hProcess, ReCa<LPCVOID>(ENT + (i * sizeof(uintptr_t))), &tempRvaString, sizeof(uintptr_t), nullptr))
            return 0;

        if (!ReadProcessMemory(hProcess, ReCa<LPCVOID>(moduleBase + tempRvaString), temp_buf.get(), len_buf, nullptr))
            return 0;

        if (!lstrcmpiA(function, temp_buf.get()))
        {
            if (!ReadProcessMemory(hProcess, ReCa<LPCVOID>(EOT + (i * sizeof(WORD))), &ordinal, sizeof(WORD), nullptr))
                return 0;

            uintptr_t temp_rva_func = 0;

            if (!ReadProcessMemory(hProcess, ReCa<LPCVOID>(EAT + (ordinal * sizeof(uintptr_t))), &temp_rva_func, sizeof(uintptr_t), nullptr))
                return 0;

            return moduleBase + temp_rva_func;
        }
    }
    return 0;
}
static bool checkiswolf(HANDLE hProcess, DWORD pid)
{
    auto check1 = [=]() -> bool
    {
        WCHAR path[MAX_PATH];
        if (!GetModuleFileNameExW(hProcess, NULL, path, MAX_PATH))
            return false;
        return PathFileExistsW((std::filesystem::path(path).parent_path() / L"GuruGuruSMF4.dll").c_str());
    };
    auto check2 = [=]() -> bool
    {
        return GetModuleBaseEx(pid, L"GuruguruSMF4.dll");
    };
    return check1() || check2();
}
void bypass_wolf_WinVerifyTrust(HANDLE hProcess, DWORD pid)
{
    if (!checkiswolf(hProcess, pid))
        return;
    auto pWinVerifyTrust = GetProcAddressEx(hProcess, pid, L"Wintrust.dll", "WinVerifyTrust");
    if (!pWinVerifyTrust)
        return;
    BYTE hook[] = {
#ifndef _WIN64
        0xB8, 0x00, 0x00, 0x00, 0x00, // mov eax, 0
        0xC2, 0x0C, 0x00              // retn 0Ch
#else
        0x31, 0xC0, // xor eax, eax
        0xC3        // ret
#endif
    };
    WriteProcessMemory(hProcess, (LPVOID)pWinVerifyTrust, hook, sizeof(hook), NULL);
}
#else
#define bypass_wolf_WinVerifyTrust(_, __) \
    {                                     \
        (void)_;                          \
        (void)__;                         \
    };
#endif

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
        if (!hProcess)
            return 0;
        bypass_wolf_WinVerifyTrust(hProcess, pid);
        auto size = (wcslen(argv[argc - 1]) + 1) * sizeof(wchar_t);
        auto remoteData = VirtualAllocEx(hProcess,
                                         nullptr,
                                         size,
                                         MEM_RESERVE | MEM_COMMIT,
                                         PAGE_READWRITE);
        if (remoteData == 0)
            return 0;
        WriteProcessMemory(hProcess, remoteData, argv[argc - 1], size, 0);
        auto pThreadProc = (LPTHREAD_START_ROUTINE)GetProcAddress(GetModuleHandle(TEXT("kernel32.dll")), "LoadLibraryW");
        // yythunks似乎会修改导入表，导致地址不是共享的地址
        auto hThread = CreateRemoteThread(hProcess, 0, 0, pThreadProc, remoteData, 0, 0);
        // if (hThread == 0) return 0;很奇怪，为0但是成功
        WaitForSingleObject(hThread, 10000);
        CloseHandle(hThread);
        VirtualFreeEx(hProcess, remoteData, size, MEM_RELEASE);
        CloseHandle(hProcess);
    }
    return 1;
}
