// https://github.com/microsoft/PowerToys/tree/main/src/modules/FileLocksmith/FileLocksmithLibInterop
#include "FileLocksmithLibInterop/FileLocksmith.h"

std::wstring readfile(const wchar_t *fname)
{
    FILE *f;
    _wfopen_s(&f, fname, L"rb");
    if (f == 0)
        return {};
    fseek(f, 0, SEEK_END);
    auto len = ftell(f);
    fseek(f, 0, SEEK_SET);
    std::wstring buff;
    buff.resize(len / 2);
    fread(buff.data(), 1, len, f);
    fclose(f);
    return buff;
}
template <class StringT>
inline std::vector<StringT> strSplit_impl(const StringT &s, const StringT &delim)
{
    StringT item;
    std::vector<StringT> tokens;

    StringT str = s;

    size_t pos = 0;
    while ((pos = str.find(delim)) != StringT::npos)
    {
        item = str.substr(0, pos);
        tokens.push_back(item);
        str.erase(0, pos + delim.length());
    }
    tokens.push_back(str);
    return tokens;
}

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
    *(wcsrchr(path, '\\')) = 0;

    SetCurrentDirectory(path);
    int needreload = std::stoi(argv[1]);
    auto processes = find_processes_recursive({L".\\files"});
    auto file = readfile(argv[4]);
    auto ss = strSplit_impl<std::wstring>(file, L"\n");
    std::wstring text_error = ss[0], text_succ = ss[1], text_update_failed = ss[2], text_update_succ = ss[3], text_failed_occupied = ss[4];
    if (processes.size())
    {
        std::wstring result;
        for (auto &&proc : processes)
        {
            result += proc.name + L"\t" + std::to_wstring(proc.pid) + L"\n";
            for (auto &&f : proc.files)
            {
                result += L"\t=>\t" + f + L"\n";
            }
            result += L"\n";
        }
        result = (text_failed_occupied) + L"\n\n" + result;
        auto checked = MessageBoxW(GetForegroundWindow(), result.c_str(), text_error.c_str(), MB_YESNO | MB_ICONQUESTION);
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
        MessageBoxW(GetForegroundWindow(), (std::wstring(text_update_failed) + L"\n\n" + StringToWideString(e.what(), CP_ACP)).c_str(), text_error.c_str(), 0);
        return 0;
    }
    try
    {
        std::filesystem::remove_all(argv[2]);
    }
    catch (std::exception &e)
    {
    }
    MessageBoxW(GetForegroundWindow(), text_update_succ.c_str(), text_succ.c_str(), 0);
    if (needreload)
    {
        ShellExecute(0, L"open", L".\\LunaTranslator.exe", NULL, NULL, SW_SHOWNORMAL);
    }
    return 0;
}