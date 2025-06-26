// https://github.com/microsoft/PowerToys/tree/main/src/modules/FileLocksmith/FileLocksmithLibInterop
#include "FileLocksmithLibInterop/FileLocksmith.h"

int updatewmain(int argc, wchar_t *argv[])
{
    if (argc <= 1)
        return 0;
    SetProcessDPIAware();
    CHandle hMutex{CreateMutex(NULL, FALSE, L"LUNA_UPDATER_SINGLE")};

    if (GetLastError() == ERROR_ALREADY_EXISTS)
        return 0;
    auto pid = _wtoi(argv[3]);
    CHandle hProcess{OpenProcess(SYNCHRONIZE, FALSE, pid)};
    if (hProcess)
    {
        WaitForSingleObject(hProcess, INFINITE);
    }
    for (int i = 0; i < 2; i++)
    {
        CHandle semaphore{CreateMutex(NULL, FALSE, L"LUNA_UPDATER_BLOCK")};
        if (GetLastError() != ERROR_ALREADY_EXISTS)
            break;
        Sleep(1000);
    }
    WCHAR path[MAX_PATH];
    GetModuleFileNameW(GetModuleHandle(0), path, MAX_PATH);

    *(wcsrchr(path, '\\')) = 0;
    *(wcsrchr(path, '\\')) = 0;

    SetCurrentDirectory(path);
    int needreload = std::stoi(argv[1]);
    auto processes = find_processes_recursive({L".\\files"});
    auto mapname = argv[4];
    CHandle fm{OpenFileMappingW(FILE_MAP_READ | FILE_MAP_WRITE, FALSE, mapname)};
    auto ptr = (BYTE)MapViewOfFile(fm, FILE_MAP_READ | FILE_MAP_WRITE, 0, 0, 5 * 1024);
    auto text_error = (LPCWSTR)ptr;
    ptr += 1024;
    auto text_succ = (LPCWSTR)ptr;
    ptr += 1024;
    auto text_update_failed = (LPCWSTR)ptr;
    ptr += 1024;
    auto text_update_succ = (LPCWSTR)ptr;
    ptr += 1024;
    std::wstring text_failed_occupied = (LPCWSTR)ptr;

    if (processes.size())
    {
        std::wstring result;
        for (auto &&proc : processes)
        {
            result += proc.name + L"\t" + std::to_wstring(proc.pid) + L"\n";
            for (auto &&f : proc.files)
            {
                result += L"\t\t" + f + L"\n";
            }
            result += L"\n";
        }
        result = text_failed_occupied + L"\n\n" + result;
        auto checked = MessageBoxW(GetForegroundWindow(), result.c_str(), text_error, MB_YESNO | MB_ICONQUESTION);
        if (checked != IDYES)
            return 0;
        for (auto &&proc : processes)
        {
            CHandle hProcess{OpenProcess(PROCESS_TERMINATE, FALSE, proc.pid)};
            if (!hProcess)
                continue;
            TerminateProcess(hProcess, 0);
        }
    }
    try
    {
        std::filesystem::remove_all(L".\\files_old");
        std::filesystem::rename(L".\\files", L".\\files_old");
        std::filesystem::copy(argv[2], L".\\", std::filesystem::copy_options::recursive | std::filesystem::copy_options::overwrite_existing);
        try
        {
            std::filesystem::remove_all(L".\\files_old");
        }
        catch (...)
        {
        }
    }
    catch (std::exception &e)
    {
        try
        {
            std::filesystem::rename(L".\\files_old", L".\\files");
        }
        catch (...)
        {
        }
        MessageBoxW(GetForegroundWindow(), (std::wstring(text_update_failed) + L"\n\n" + StringToWideString(e.what(), CP_ACP)).c_str(), text_error, 0);
        return 0;
    }
    try
    {
        std::filesystem::remove_all(argv[2]);
    }
    catch (std::exception &e)
    {
    }
    MessageBoxW(GetForegroundWindow(), text_update_succ, text_succ, 0);
    if (needreload)
    {
        ShellExecute(0, L"open", L".\\LunaTranslator.exe", NULL, NULL, SW_SHOWNORMAL);
    }
    return 0;
}