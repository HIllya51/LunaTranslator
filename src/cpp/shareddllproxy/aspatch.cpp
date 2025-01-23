
#include <nlohmann/json.hpp>

HANDLE runexe(const std::wstring &exe, const std::optional<std::wstring> &startup_argument)
{
    STARTUPINFOW si;
    PROCESS_INFORMATION pi;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    std::vector<wchar_t> argu;
    if (startup_argument.has_value())
    {
        argu.resize(startup_argument.value().size() + 1);
        wcscpy(argu.data(), startup_argument.value().c_str());
    }
    CreateProcessW(exe.c_str(), // No module name (use command line)
                   startup_argument.has_value() ? argu.data() : NULL,
                   NULL,  // Process handle not inheritable
                   NULL,  // Thread handle not inheritable
                   FALSE, // Set handle inheritance to FALSE
                   0,     // No creation flags
                   NULL,  // Use parent's environment block
                   NULL,  // Use parent's starting directory
                   &si,   // Pointer to STARTUPINFO structure
                   &pi);  // Pointer to PROCESS_INFORMATION structure

    return pi.hProcess;
}

std::wstring stolower(const std::wstring &s1)
{
    auto s = s1;
    std::transform(s.begin(), s.end(), s.begin(), tolower);
    return s;
}
std::vector<DWORD> EnumerateProcesses(const std::wstring &exe)
{

    CHandle hSnapshot{CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)};
    if (hSnapshot == INVALID_HANDLE_VALUE)
    {
        return {};
    }

    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);

    if (!Process32First(hSnapshot, &pe32))
    {
        return {};
    }
    std::vector<DWORD> pids;
    do
    {
        if (stolower(exe) == stolower(pe32.szExeFile))
            pids.push_back(pe32.th32ProcessID);
    } while (Process32Next(hSnapshot, &pe32));

    return pids;
}
enum
{
    STRING = 12,
    MESSAGE_SIZE = 500,
    PIPE_BUFFER_SIZE = 50000,
    SHIFT_JIS = 932,
    MAX_MODULE_SIZE = 120,
    PATTERN_SIZE = 30,
    HOOK_NAME_SIZE = 60,
    FIXED_SPLIT_VALUE = 0x10001,
    HOOKCODE_LEN = 500
};
struct ThreadParam
{
    bool operator==(ThreadParam other) const { return processId == other.processId && addr == other.addr && ctx == other.ctx && ctx2 == other.ctx2; }
    DWORD processId;
    uint64_t addr;
    uint64_t ctx;  // The context of the hook: by default the first value on stack, usually the return address
    uint64_t ctx2; // The subcontext of the hook: 0 by default, generated in a method specific to the hook
};

typedef void (*ProcessEvent)(DWORD pid);
typedef void (*HookInsertHandler)(DWORD pid, uint64_t address, const wchar_t *hookcode);
typedef void (*EmbedCallback)(const wchar_t *text, ThreadParam);
nlohmann::json config;
std::map<std::string, std::string> translation;
std::unordered_set<DWORD> connectedpids;
void (*Luna_Start)(ProcessEvent Connect, ProcessEvent Disconnect, void *, void *, void *, void *, HookInsertHandler hookinsert, EmbedCallback embed);
void (*Luna_Inject)(DWORD pid, LPCWSTR basepath);
void (*Luna_EmbedSettings)(DWORD pid, UINT32 waittime, UINT8 fontCharSet, bool fontCharSetEnabled, wchar_t *fontFamily, int displaymode, bool fastskipignore);
void (*Luna_useembed)(ThreadParam, bool use);
void (*Luna_embedcallback)(ThreadParam, LPCWSTR text, LPCWSTR trans);
std::set<std::string> notranslation;
HANDLE hsema;
class lunapatch
{
public:
    HANDLE hMessage;
    HANDLE hwait;

    lunapatch(std::wstring dll, nlohmann::json &&_translation, nlohmann::json &&_config)
    {
        translation = _translation;
        config = _config;
        auto LunaHost = LoadLibraryW(dll.c_str());

        Luna_Start = (decltype(Luna_Start))GetProcAddress(LunaHost, "Luna_Start");
        Luna_EmbedSettings = (decltype(Luna_EmbedSettings))GetProcAddress(LunaHost, "Luna_EmbedSettings");
        Luna_Inject = (decltype(Luna_Inject))GetProcAddress(LunaHost, "Luna_Inject");
        Luna_useembed = (decltype(Luna_useembed))GetProcAddress(LunaHost, "Luna_useembed");
        Luna_embedcallback = (decltype(Luna_embedcallback))GetProcAddress(LunaHost, "Luna_embedcallback");
        hsema = CreateSemaphore(NULL, 0, 100, NULL);
        Luna_Start(
            [](DWORD pid)
            {
                Luna_EmbedSettings(pid, 1000 * config["embedsettings"]["timeout_translate"], 2, false, config["embedsettings"]["changefont"] ? (StringToWideString(config["embedsettings"]["changefont_font"]).data()) : L"", config["embedsettings"]["displaymode"], false);
                connectedpids.insert(pid);
            },
            [](DWORD pid)
            {
                connectedpids.erase(pid);
                ReleaseSemaphore(hsema, 1, NULL);
            },
            0,
            0,
            0,
            0,
            [](DWORD pid, uint64_t addr, const wchar_t *output)
            {
                std::wstring newhookcode = output;
                for (auto hook : config["embedhook"])
                {
                    auto hookcode = StringToWideString(hook[0]);
                    uint64_t _addr = hook[1];
                    uint64_t _ctx1 = hook[2];
                    uint64_t _ctx2 = hook[3];
                    if (hookcode == newhookcode)
                    {
                        ThreadParam tp{pid, addr, _ctx1, _ctx2};
                        Luna_useembed(tp, true);
                    }
                }
            },
            [](const wchar_t *output, ThreadParam tp)
            {
                std::wstring text = output;
                auto trans = findtranslation(text);
                Luna_embedcallback(tp, output, trans.c_str());
            });
    }
    void run()
    {
        auto target_exe = StringToWideString(config["target_exe"]);

        auto _startup_argument = config["startup_argument"];

        std::optional<std::wstring> startup_argument;
        if (_startup_argument.is_null())
            startup_argument = {};
        else
            startup_argument = StringToWideString(config["startup_argument"]);
        hwait = runexe(target_exe, startup_argument);
    }
    ~lunapatch()
    {
        if (notranslation.size())
        {
            for (auto &text : notranslation)
            {
                translation[text] = "";
            }
            auto notrs = nlohmann::json(translation).dump(4);
            std::ofstream of;
            of.open(std::string(config["translation_file"]));
            of << notrs;
            of.close();
        }
    }
    void wait()
    {
        WaitForSingleObject(hwait, INFINITE);
        while (connectedpids.size())
            WaitForSingleObject(hsema, INFINITE);
    }
    void inject()
    {
        // chrome has multi process
        Sleep(config["inject_timeout"]);
        for (auto exe : std::set<std::string>{config["target_exe"], config["target_exe2"]})
        {
            auto pids = EnumerateProcesses(StringToWideString(exe));
            for (auto pid : pids)
            {
                wprintf(L"%d\n", pid);
                Luna_Inject(pid, L"");
            }
        }
    }
    static std::wstring findtranslation(const std::wstring &text)
    {
        auto utf8text = WideStringToString(text);
        if (translation.find(utf8text) == translation.end())
        {
            // wprintf(L"%s\n",text.c_str());
            notranslation.insert(utf8text);
            return {};
        }
        return StringToWideString(translation.at(utf8text));
    }
};
std::wstring GetExecutablePath()
{
    WCHAR buffer[MAX_PATH];
    GetModuleFileNameW(NULL, buffer, MAX_PATH);

    std::wstring fullPath(buffer);
    size_t pos = fullPath.find_last_of(L"\\/");
    if (pos != std::wstring::npos)
    {
        return fullPath.substr(0, pos);
    }

    return L"";
}
bool checkisapatch()
{
    auto curr = std::filesystem::path(GetExecutablePath());
    auto config = curr / "LunaPatch.json";
    if (std::filesystem::exists(config) == false)
    {
        return false;
    }
    std::ifstream jsonfile;
    jsonfile.open(config);
    auto configjson = nlohmann::json::parse(jsonfile);
    jsonfile.close();
    std::string translation_file = configjson["translation_file"];

    jsonfile.open(translation_file);
    std::map<std::string, std::string> translation = nlohmann::json::parse(jsonfile);
    jsonfile.close();

    auto LunaHost = (curr / (std::wstring(L"LunaHost") + std::to_wstring(8 * sizeof(void *)))).wstring();

    lunapatch _lunapatch(LunaHost, std::move(translation), std::move(configjson));
    _lunapatch.run();
    _lunapatch.inject();
    _lunapatch.wait();
    return true;
}