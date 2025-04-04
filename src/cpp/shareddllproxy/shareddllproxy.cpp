#pragma comment(linker, "/subsystem:windows /entry:wmainCRTStartup")

int dllinjectwmain(int argc, wchar_t *argv[]);
int updatewmain(int argc, wchar_t *wargv[]);
bool checkisapatch();
int voiceroid2wmain(int argc, wchar_t *argv[]);
#ifndef _WIN64
int lecwmain(int argc, wchar_t *argv[]);
int jbjwmain(int argc, wchar_t *argv[]);
int dreyewmain(int argc, wchar_t *argv[]);
int kingsoftwmain(int argc, wchar_t *argv[]);
int neospeech(int argc, wchar_t *argv[]);
int neospeechlist(int argc, wchar_t *argv[]);
int eztrans(int argc, wchar_t *argv[]);
int atlaswmain(int argc, wchar_t *argv[]);
#else
int SnippingTool(int argc, wchar_t *argv[]);
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
    auto argv0 = std::wstring(argv[1]);
    typedef int (*wmaint)(int, wchar_t **);
    std::map<std::wstring, wmaint> fm = {
        {L"dllinject", dllinjectwmain},
        {L"listpm", listprocessmodule},
        {L"update", updatewmain},
        {L"voiceroid2", voiceroid2wmain},
#ifndef _WIN64
        {L"lec", lecwmain},
        {L"jbj7", jbjwmain},
        {L"dreye", dreyewmain},
        {L"kingsoft", kingsoftwmain},
        {L"neospeech", neospeech},
        {L"neospeechlist", neospeechlist},
        {L"eztrans", eztrans},
        {L"atlaswmain", atlaswmain},
#else

        {L"SnippingTool", SnippingTool},
#endif // !_WIN64
    };
    return fm[argv0](argc - 1, argv + 1);
}
