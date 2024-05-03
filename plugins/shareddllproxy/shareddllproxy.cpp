#pragma comment(linker, "/subsystem:windows /entry:wmainCRTStartup")

int dllinjectwmain(int argc, wchar_t *argv[]);
int ntleaswmain(int argc, wchar_t *wargv[]);
bool checkisapatch();
#ifndef _WIN64
int LRwmain(int argc, wchar_t *argv[]);
int jbjwmain(int argc, wchar_t *argv[]);
int dreyewmain(int argc, wchar_t *argv[]);
int kingsoftwmain(int argc, wchar_t *argv[]);
int voiceroid2wmain(int argc, wchar_t *argv[]);
int lewmain(int argc, wchar_t *argv[]);
int neospeech(int argc, wchar_t *argv[]);
int neospeechlist(int argc, wchar_t *argv[]);
#else
int magpiewmain(int argc, wchar_t *wargv[]);
#endif // !_WIN64

void listprocessmodule_1(std::ofstream &of, DWORD processPID)
{
    DWORD need;
    HMODULE modules1[1] = {};
    HANDLE hProcess = ::OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, processPID);
    if (hProcess)
    {
        if (EnumProcessModules(hProcess, modules1, sizeof(modules1), &need) == 0)
            return;
        auto modules = std::make_unique<HMODULE[]>(need / sizeof(HMODULE));
        if (EnumProcessModules(hProcess, modules.get(), need, &need) == 0)
            return;
        for (int i = 0; i < need / sizeof(HMODULE); i++)
        {
            wchar_t fileName[MAX_PATH] = {0};
            GetModuleFileNameExW(hProcess, modules.get()[i], fileName, sizeof(fileName));
            auto s = std::wstring(fileName);
            of.write((char *)s.c_str(), s.size() * 2);
            of.write((char *)L"\n", 2);
        }
    }
}
int listprocessmodule(int argc, wchar_t *argv[])
{
    std::ofstream of(argv[1], std::ios_base::binary);
    for (int i = 2; i < argc; i++)
    {

        auto pid = std::stoi(argv[i]);
        listprocessmodule_1(of, pid);
    }
    of.close();
    return 0;
}

int wmain(int argc, wchar_t *argv[])
{
    if (checkisapatch())
        return 1;
    auto argv0 = std::wstring(argv[1]);
    if (argv0 == L"dllinject")
        return dllinjectwmain(argc - 1, argv + 1);
    if (argv0 == L"ntleas")
        return ntleaswmain(argc - 1, argv + 1);
    if (argv0 == L"listpm")
        return listprocessmodule(argc - 1, argv + 1);

#ifndef _WIN64
    else if (argv0 == L"LR")
        return LRwmain(argc - 1, argv + 1);
    else if (argv0 == L"le")
        return lewmain(argc - 1, argv + 1);
    else if (argv0 == L"jbj7")
        return jbjwmain(argc - 1, argv + 1);
    else if (argv0 == L"dreye")
        return dreyewmain(argc - 1, argv + 1);
    else if (argv0 == L"kingsoft")
        return kingsoftwmain(argc - 1, argv + 1);
    else if (argv0 == L"voiceroid2")
        return voiceroid2wmain(argc - 1, argv + 1);
    else if (argv0 == L"neospeech")
        return neospeech(argc - 1, argv + 1);
    else if (argv0 == L"neospeechlist")
        return neospeechlist(argc - 1, argv + 1);
#else
    else if (argv0 == L"magpie")
        return magpiewmain(argc - 1, argv + 1);
#endif // !_WIN64
}
