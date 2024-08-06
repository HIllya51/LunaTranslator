#pragma comment(linker, "/subsystem:windows /entry:wmainCRTStartup")

int updatewmain(int argc, wchar_t *argv[])
{
    if (argc <= 1)
        return 0;
    SetProcessDPIAware();
    AutoHandle hMutex = CreateMutex(NULL, FALSE, L"LUNA_UPDATER_SINGLE");

    if (GetLastError() == ERROR_ALREADY_EXISTS)
        return 0;
    while (true)
    {
        AutoHandle semaphore = CreateMutex(NULL, FALSE, L"LUNA_UPDATER_BLOCK");
        if (GetLastError() != ERROR_ALREADY_EXISTS)
            break;
        Sleep(1000);
    }
    WCHAR path[MAX_PATH];
    GetModuleFileNameW(GetModuleHandle(0), path, MAX_PATH);

    *(wcsrchr(path, '\\')) = 0;
    *(wcsrchr(path, '\\')) = 0;

    SetCurrentDirectory(path);
    try
    {
        std::filesystem::copy(argv[1], L".\\", std::filesystem::copy_options::recursive | std::filesystem::copy_options::overwrite_existing);
        MessageBoxW(GetForegroundWindow(), L"Update success", L"Success", 0);
    }
    catch (std::exception &e)
    {
        MessageBoxA(GetForegroundWindow(), (std::string("Update failed!\r\n") + e.what()).c_str(), "Error", 0);
        ShellExecute(0, L"open", (std::wstring(argv[2]) + L"/Github/LunaTranslator/releases").c_str(), NULL, NULL, SW_SHOWNORMAL);
        return 0;
    }
    try
    {
        wcscat(path, L"\\cache\\update");
        std::filesystem::remove_all(path);
    }
    catch (std::exception &e)
    {
    }
    return 0;
}