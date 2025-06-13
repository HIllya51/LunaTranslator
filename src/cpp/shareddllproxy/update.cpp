#pragma comment(linker, "/subsystem:windows /entry:wmainCRTStartup")

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
        MessageBoxA(GetForegroundWindow(), (std::string("Update failed!\r\n") + e.what()).c_str(), "Error", 0);
        return 0;
    }
    try
    {
        std::filesystem::remove_all(argv[2]);
    }
    catch (std::exception &e)
    {
    }
    MessageBoxW(GetForegroundWindow(), L"Update success", L"Success", 0);
    if (needreload)
    {
        ShellExecute(0, L"open", L".\\LunaTranslator.exe", NULL, NULL, SW_SHOWNORMAL);
    }
    return 0;
}