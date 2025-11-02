#include "pluginmanager.h"
#include <filesystem>
#include "Plugin/extension.h"
#include <fstream>
#include <commdlg.h>
#include "LunaHost.h"
#include "host.h"

std::optional<std::wstring> SelectFile(HWND hwnd, LPCWSTR lpstrFilter)
{
    OPENFILENAME ofn;
    wchar_t szFileName[MAX_PATH] = {0};

    ZeroMemory(&ofn, sizeof(ofn));
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner = hwnd;
    ofn.lpstrFilter = lpstrFilter;
    ofn.lpstrFile = szFileName;
    ofn.nMaxFile = sizeof(szFileName);
    ofn.Flags = OFN_EXPLORER | OFN_FILEMUSTEXIST | OFN_HIDEREADONLY | OFN_NOCHANGEDIR;

    if (GetOpenFileName(&ofn))
    {
        return szFileName;
    }
    else
        return {};
}
typedef std::vector<HMODULE> *(*QtLoadLibrary_t)(std::vector<std::wstring> *dlls);
typedef std::vector<HMODULE> *(*QtLoadLibraryBatch_t)(std::vector<std::wstring> *dlls);
typedef void (*QtFreeLibrary_t)(HMODULE hd);
void tryaddqttoenv(std::vector<std::wstring> &collectQtplugs)
{
    static HMODULE qt5core = 0;
    if (qt5core == 0)
    {
        wchar_t env[65535];
        GetEnvironmentVariableW(L"PATH", env, 65535);
        auto envs = std::wstring(env);
        for (auto &p : collectQtplugs)
        {
            envs += L";";
            envs += std::filesystem::path(p).parent_path();
        }
        SetEnvironmentVariableW(L"PATH", envs.c_str());
        qt5core = LoadLibrary(L"Qt5Core.dll");
    }
}
std::vector<HMODULE> loadqtdllsX(std::vector<std::wstring> &collectQtplugs)
{
    if (collectQtplugs.empty())
        return {};
    tryaddqttoenv(collectQtplugs);
#if 1
    HMODULE base = GetModuleHandle(0);
#else
    HMODULE base = LoadLibrary((std::filesystem::current_path() / (x64 ? "plugin64" : "plugin32") / "QtLoader.dll").wstring().c_str());
#endif

    // auto QtLoadLibrary = (QtLoadLibrary_t)GetProcAddress(base, "QtLoadLibrary");
    auto QtLoadLibrary = (QtLoadLibrary_t)GetProcAddress(base, "QtLoadLibraryBatch");

    auto modules = QtLoadLibrary(&collectQtplugs);

    std::vector<HMODULE> _{*modules};
    delete modules;
    return _;
}
HMODULE loadqtdllsX(const std::wstring &collectQtplugs)
{
    std::vector<std::wstring> _{collectQtplugs};
    return loadqtdllsX(_)[0];
}
void Pluginmanager::loadqtdlls(std::vector<std::wstring> &collectQtplugs)
{
    auto modules = loadqtdllsX(collectQtplugs);
    for (int i = 0; i < collectQtplugs.size(); i++)
    {
        OnNewSentenceS[collectQtplugs[i]] = {collectQtplugs[i], this, true, modules[i]};
    }
}
Pluginmanager::Pluginmanager(LunaHost *_host) : host(_host), configs(_host->configs)
{
    try
    {
        std::scoped_lock lock(OnNewSentenceSLock);

        std::vector<std::wstring> collectQtplugs;
        for (auto i = 0; i < count(); i++)
        {
            auto plg = get(i);
            bool isqt = plg.isQt;
            auto path = plg.wpath();
            OnNewSentenceS[path] = {};
            if (isqt)
            {
                if (plg.enable == false)
                    continue;
                collectQtplugs.push_back((path));
            }
            else
            {
                auto base = LoadLibraryW(path.c_str());
                OnNewSentenceS[path] = {path, this, false, base};
            }
        }
        loadqtdlls(collectQtplugs);

        OnNewSentenceS[L"InternalClipBoard"] = {L"", this, false, GetModuleHandle(0)}; // 内部链接的剪贴板插件
    }
    catch (const std::exception &ex)
    {
        std::wcerr << "Error: " << ex.what() << std::endl;
    }
}

bool Pluginmanager::dispatch(TextThread &thread, std::wstring &sentence)
{
    auto sentenceInfo = GetSentenceInfo(thread).data();
    wchar_t *sentenceBuffer = (wchar_t *)HeapAlloc(GetProcessHeap(), HEAP_GENERATE_EXCEPTIONS, (sentence.size() + 1) * sizeof(wchar_t));
    wcscpy_s(sentenceBuffer, sentence.size() + 1, sentence.c_str());
    concurrency::reader_writer_lock::scoped_lock_read readLock(OnNewSentenceSLock);

    for (int i = 0; i < count() + 1; i++)
    {
        std::wstring path;
        if (i == count())
            path = L"InternalClipBoard";
        else
        {
            if (getenable(i) == false)
                continue;
            path = getname(i);
        }

        auto funptr = OnNewSentenceS[path].OnNewSentence;
        if (funptr == 0)
            continue;
        if (!*(sentenceBuffer = funptr(sentenceBuffer, sentenceInfo)))
            break;
    }

    sentence = sentenceBuffer;
    HeapFree(GetProcessHeap(), 0, sentenceBuffer);
    return !sentence.empty();
}

void Pluginmanager::add(const pluginitem &item)
{
    configs->configs[pluginkey].push_back(item.dump());
}
int Pluginmanager::count()
{
    return configs->configs[pluginkey].size();
}
pluginitem Pluginmanager::get(int i)
{
    return pluginitem{configs->configs[pluginkey][i]};
}
void Pluginmanager::set(int i, const pluginitem &item)
{
    configs->configs[pluginkey][i] = item.dump();
}

pluginitem::pluginitem(const nlohmann::json &js)
{
    path = js["path"];
    isQt = safequeryjson(js, "isQt", false);
    enable = safequeryjson(js, "enable", true);
    vissetting = safequeryjson(js, "vissetting", true);
}
std::wstring pluginitem::wpath()
{
    auto wp = StringToWideString(path);
    return std::filesystem::absolute(wp);
}

std::wstring castabs2ref(const std::wstring &p)
{
    auto curr = std::filesystem::current_path().wstring();
    if (startWith(p, curr))
    {
        return p.substr(curr.size() + 1);
    }
    return p;
}
pluginitem::pluginitem(const std::wstring &pabs, bool _isQt)
{
    isQt = _isQt;
    path = WideStringToString(castabs2ref(pabs));
    enable = true;
    vissetting = true;
}
nlohmann::json pluginitem::dump() const
{
    return {
        {"path", path},
        {"isQt", isQt},
        {"enable", enable},
        {"vissetting", vissetting}};
}
bool Pluginmanager::getvisible_setable(int idx)
{
    return OnNewSentenceS[getname(idx)].VisSetting;
}
bool Pluginmanager::getvisible(int idx)
{
    return get(idx).vissetting;
}
void Pluginmanager::setvisible(int idx, bool vis)
{
    auto item = get(idx);
    item.vissetting = vis;
    set(idx, item);
    OnNewSentenceS[getname(idx)].VisSetting(vis);
}
bool Pluginmanager::getenable(int idx)
{
    return get(idx).enable;
}
void Pluginmanager::setenable(int idx, bool en)
{
    auto item = get(idx);
    item.enable = en;
    set(idx, item);
}
std::wstring Pluginmanager::getname(int idx)
{
    return get(idx).wpath();
}
bool Pluginmanager::checkisdump(const std::wstring &dll)
{
    for (auto &p : OnNewSentenceS)
    {
        if (p.first == dll)
            return true;
    }
    return false;
}
void Pluginmanager::unload(const std::wstring &wss)
{
    auto hm = OnNewSentenceS[wss].hmodule;
    if (OnNewSentenceS[wss].isQt && hm)
    {
        ((QtFreeLibrary_t)GetProcAddress(GetModuleHandle(0), "QtFreeLibrary"))(hm);
    }
    else
        FreeLibrary(hm);

    OnNewSentenceS[wss].clear();
}
void plugindata::clear()
{
    hmodule = 0;
    OnNewSentence = 0;
    VisSetting = 0;
}
void Pluginmanager::remove(const std::wstring &wss)
{
    unload(wss);

    auto s = WideStringToString(wss);
    auto &plgs = configs->configs[pluginkey];
    auto it = std::remove_if(plgs.begin(), plgs.end(), [&](auto &t)
                             {
        std::string p=t["path"];
        return std::filesystem::absolute(p)==std::filesystem::absolute(s); });
    plgs.erase(it, plgs.end());
    OnNewSentenceS.erase(wss);
}
std::optional<std::wstring> Pluginmanager::selectpluginfile()
{
    return SelectFile(0, L"Plugin Files\0*.dll;*.xdll\0");
}
void Pluginmanager::swaprank(int a, int b)
{
    auto &plgs = configs->configs[pluginkey];
    auto _b = plgs[b];
    plgs[b] = plgs[a];
    plgs[a] = _b;
}
DWORD Rva2Offset(DWORD rva, PIMAGE_SECTION_HEADER psh, PIMAGE_NT_HEADERS pnt)
{
    size_t i = 0;
    PIMAGE_SECTION_HEADER pSeh;
    if (rva == 0)
    {
        return (rva);
    }
    pSeh = psh;
    for (i = 0; i < pnt->FileHeader.NumberOfSections; i++)
    {
        if (rva >= pSeh->VirtualAddress && rva < pSeh->VirtualAddress +
                                                     pSeh->Misc.VirtualSize)
        {
            break;
        }
        pSeh++;
    }
    if (pSeh->VirtualAddress == 0 || pSeh->PointerToRawData == 0)
        return -1;
    return (rva - pSeh->VirtualAddress + pSeh->PointerToRawData);
}
std::set<std::string> getimporttable(const std::wstring &pe)
{
    AutoHandle handle = CreateFile(pe.c_str(), GENERIC_READ, 0, 0, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0);
    if (!handle)
        return {};
    DWORD byteread, size = GetFileSize(handle, NULL);
    PVOID virtualpointer = VirtualAlloc(NULL, size, MEM_COMMIT, PAGE_READWRITE);
    if (!virtualpointer)
        return {};
    ReadFile(handle, virtualpointer, size, &byteread, NULL);

    struct __
    {
        PVOID _ptr;
        DWORD size;
        __(PVOID ptr, DWORD sz) : _ptr(ptr), size(sz) {}
        ~__()
        {
            VirtualFree(_ptr, size, MEM_DECOMMIT);
        }
    } _(virtualpointer, size);

    if (PIMAGE_DOS_HEADER(virtualpointer)->e_magic != 0x5a4d)
        return {};

    PIMAGE_NT_HEADERS ntheaders = (PIMAGE_NT_HEADERS)(PCHAR(virtualpointer) + PIMAGE_DOS_HEADER(virtualpointer)->e_lfanew);

    auto magic = ntheaders->OptionalHeader.Magic;
    if (x64 && (magic != IMAGE_NT_OPTIONAL_HDR64_MAGIC))
        return {};
    if ((!x64) && (magic != IMAGE_NT_OPTIONAL_HDR32_MAGIC))
        return {};

    PIMAGE_SECTION_HEADER pSech = IMAGE_FIRST_SECTION(ntheaders); // Pointer to first section header
    PIMAGE_IMPORT_DESCRIPTOR pImportDescriptor;                   // Pointer to import descriptor

    if (ntheaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].Size == 0) /*if size of the table is 0 - Import Table does not exist */
        return {};

    std::set<std::string> ret;
    pImportDescriptor = (PIMAGE_IMPORT_DESCRIPTOR)((DWORD_PTR)virtualpointer +
                                                   Rva2Offset(ntheaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress, pSech, ntheaders));

    while (pImportDescriptor->Name != NULL)
    {
        // Get the name of each DLL
        auto nameoffset = Rva2Offset(pImportDescriptor->Name, pSech, ntheaders);
        if (nameoffset == (DWORD)-1)
            // 无导入
            return {};
        ret.insert((PCHAR)((DWORD_PTR)virtualpointer + nameoffset));

        pImportDescriptor++; // advance to next IMAGE_IMPORT_DESCRIPTOR
    }
    return ret;
}
bool qtchecker(const std::set<std::string> &dll)
{
    for (auto qt5 : {"Qt5Widgets.dll", "Qt5Gui.dll", "Qt5Core.dll"})
        if (dll.find(qt5) != dll.end())
            return true;
    return false;
}
addpluginresult Pluginmanager::load(const std::wstring &p, bool *isqt)
{
    auto importtable = getimporttable(p);
    if (importtable.empty())
        return addpluginresult::invaliddll;
    auto isQt = qtchecker(importtable);
    if (isqt)
        *isqt = isQt;
    HMODULE base;
    if (isQt)
    {
        base = loadqtdllsX(p);
    }
    else
    {
        base = LoadLibraryW(p.c_str());
    }

    if (base == 0)
        return addpluginresult::invaliddll;

    std::scoped_lock lock(OnNewSentenceSLock);

    OnNewSentenceS[p] = {p, this, isQt, base};
    if (!OnNewSentenceS[p].valid())
        return addpluginresult::isnotaplugins;
    return addpluginresult::success;
}
bool plugindata::valid()
{
    return OnNewSentence;
}
plugindata::plugindata(const std::wstring &p, Pluginmanager *manager, bool _isQt, HMODULE hm)
{
    hmodule = hm;
    isQt = _isQt;
    OnNewSentence = (OnNewSentence_t)GetProcAddress(hm, "OnNewSentence");
    VisSetting = (VisSetting_t)GetProcAddress(hm, "VisSetting");
    refpath = p;
    if (VisSetting)
    {
        auto vis = true;
        if (auto plg = manager->get(p))
            vis = plg.value().vissetting;
        VisSetting(vis);
    }
}
void plugindata::initstatus(const pluginitem &plg)
{
    if (plg.vissetting && VisSetting)
        VisSetting(true);
}
std::optional<pluginitem> Pluginmanager::get(const std::wstring &p)
{
    for (int i = 0; i < count(); i++)
    {
        if (getname(i) == p)
        {
            return get(i);
        }
    }
    return {};
}
addpluginresult Pluginmanager::addplugin(const std::wstring &p)
{
    if (checkisdump(p))
        return addpluginresult::dumplicate;
    bool isQt;
    auto ret = load(p, &isQt);
    if (ret == addpluginresult::success)
    {
        add({p, isQt});
    }
    return ret;
}

std::array<InfoForExtension, 20> Pluginmanager::GetSentenceInfo(TextThread &thread)
{
    void (*AddText)(int64_t, const wchar_t *) = [](int64_t number, const wchar_t *text)
    {
        if (TextThread *thread = Host::GetThread(number))
            thread->Push(text);
    };
    void (*AddSentence)(int64_t, const wchar_t *) = [](int64_t number, const wchar_t *sentence)
    {
        if (TextThread *thread = Host::GetThread(number))
            thread->AddSentence(sentence);
        ;
    };
    static DWORD SelectedProcessId;
    auto currthread = (TextThread *)host->currentselect;
    SelectedProcessId = (currthread != 0) ? currthread->tp.processId : 0;
    DWORD(*GetSelectedProcessId)
    () = []
    { return SelectedProcessId; };

    return {{
        {"HostHWND", (int64_t)host->winId},
        {"toclipboard", host->check_toclipboard},
        {"current select", &thread == currthread},
        {"text number", thread.handle},
        {"process id", thread.tp.processId},
        {"hook address", (int64_t)thread.tp.addr},
        {"text handle", thread.handle},
        {"text name", (int64_t)thread.name.c_str()},
        {"add sentence", (int64_t)AddSentence},
        {"add text", (int64_t)AddText},
        {"get selected process id", (int64_t)GetSelectedProcessId},
        {"void (*AddSentence)(int64_t number, const wchar_t* sentence)", (int64_t)AddSentence},
        {"void (*AddText)(int64_t number, const wchar_t* text)", (int64_t)AddText},
        {"DWORD (*GetSelectedProcessId)()", (int64_t)GetSelectedProcessId},
        {nullptr, 0} // nullptr marks end of info array
    }};
}