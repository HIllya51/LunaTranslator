#include "host.h"
#define C_LUNA_API extern "C" __declspec(dllexport)
BOOL APIENTRY DllMain(HMODULE hModule,
                      DWORD ul_reason_for_call,
                      LPVOID lpReserved)
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}

typedef void (*ProcessEvent)(DWORD pid);
typedef void (*ThreadEvent_maybe_embed)(const wchar_t *hookcode, const char *hookname, ThreadParam, bool isembedable);
typedef void (*ThreadEvent)(const wchar_t *hookcode, const char *hookname, ThreadParam);
typedef void (*OutputCallback)(const wchar_t *hookcode, const char *hookname, ThreadParam, const wchar_t *text);
typedef void (*HostInfoHandler)(HOSTINFO type, const wchar_t *log);
typedef void (*HookInsertHandler)(DWORD pid, uint64_t address, const wchar_t *hookcode);
typedef void (*EmbedCallback)(const wchar_t *text, ThreadParam);
typedef wchar_t *(*I18NQueryCallback)(const wchar_t *text);
typedef void (*findhookcallback_t)(wchar_t *hookcode, const wchar_t *text);
template <typename T>
std::optional<T> checkoption(bool check, T &&t)
{
    if (check)
        return std::move(t);
    return {};
}

C_LUNA_API void Luna_Start(ProcessEvent Connect, ProcessEvent Disconnect, ThreadEvent_maybe_embed Create, ThreadEvent Destroy, OutputCallback Output, HostInfoHandler hostinfo, HookInsertHandler hookinsert, EmbedCallback embed, I18NQueryCallback i18nQueryCallback)
{
    Host::Start(
        checkoption(Connect, std::function<void(DWORD)>(Connect)),
        checkoption(Disconnect, std::function<void(DWORD)>(Disconnect)),
        checkoption(Create, [=](const TextThread &thread)
                    { Create(thread.hp.hookcode, thread.hp.name, thread.tp, thread.hp.type & EMBED_ABLE); }),
        checkoption(Destroy, [=](const TextThread &thread)
                    { Destroy(thread.hp.hookcode, thread.hp.name, thread.tp); }),
        checkoption(Output, [=](const TextThread &thread, std::wstring &output)
                    { Output(thread.hp.hookcode, thread.hp.name, thread.tp, output.c_str()); }),
        checkoption(hostinfo, [=](HOSTINFO type, const std::wstring &output)
                    { hostinfo(type, output.c_str()); }),
        checkoption(hookinsert, [=](DWORD pid, uint64_t addr, const std::wstring &hookcode)
                    { hookinsert(pid, addr, hookcode.c_str()); }),
        checkoption(embed, [=](const std::wstring &output, const ThreadParam &tp)
                    { embed(output.c_str(), tp); }),
        checkoption(i18nQueryCallback,
                    [=](const std::wstring &str) -> std::optional<std::wstring>
                    {
                        auto s = i18nQueryCallback(str.c_str());
                        if (!s)
                            return std::nullopt;
                        std::wstring ret = s;
                        delete s;
                        return ret;
                    }));
}
#if 0
C_LUNA_API void Luna_ConnectAndInjectProcess(DWORD pid)
{
    Host::ConnectAndInjectProcess(pid);
}
#endif
C_LUNA_API bool Luna_CheckIfNeedInject(DWORD pid)
{
    return Host::CheckIfNeedInject(pid);
}
C_LUNA_API void Luna_ConnectProcess(DWORD pid)
{
    Host::ConnectProcess(pid);
}
C_LUNA_API void Luna_DetachProcess(DWORD pid)
{
    Host::DetachProcess(pid);
}
C_LUNA_API void *Luna_AllocString(const wchar_t *str)
{
    if (!str)
        return nullptr;
    auto _ = new WCHAR[wcslen(str) + 1];
    wcscpy(_, str);
    return _;
}
C_LUNA_API void Luna_Settings(int flushDelay, bool filterRepetition, int defaultCodepage, int maxBufferSize, int maxHistorySize)
{
    TextThread::flushDelay = flushDelay;
    TextThread::filterRepetition = filterRepetition;
    Host::defaultCodepage = defaultCodepage;
    TextThread::maxBufferSize = maxBufferSize;
    TextThread::maxHistorySize = maxHistorySize;
}
C_LUNA_API void Luna_ResetLang()
{
    Host::ResetLanguage();
}
C_LUNA_API void Luna_InsertPCHooks(DWORD pid, int which)
{
    Host::InsertPCHooks(pid, which);
}
C_LUNA_API bool Luna_InsertHookCode(DWORD pid, LPCWSTR hookcode)
{
    auto hp = HookCode::Parse(hookcode);
    if (hp)
        Host::InsertHook(pid, hp.value());
    return hp.has_value();
}
C_LUNA_API void Luna_QueryThreadHistory(ThreadParam tp, bool latest, void (*callback)(const wchar_t *))
{
    if (latest)
        callback(Host::GetThread(tp).latest->c_str());
    else
        callback(Host::GetThread(tp).storage->c_str());
}
C_LUNA_API void Luna_RemoveHook(DWORD pid, uint64_t addr)
{
    Host::RemoveHook(pid, addr);
}
C_LUNA_API void Luna_FindHooks(DWORD pid, SearchParam sp, findhookcallback_t findhookcallback, LPCWSTR addresses)
{
    Host::FindHooks(pid, sp, [=](HookParam hp, std::wstring text)
                    {
                            wchar_t hookcode[HOOKCODE_LEN];
                            wcscpy_s(hookcode,HOOKCODE_LEN, hp.hookcode);
                            findhookcallback(hookcode,text.c_str()); }, addresses);
}
C_LUNA_API void Luna_EmbedSettings(DWORD pid, UINT32 waittime, UINT8 fontCharSet, bool fontCharSetEnabled, wchar_t *fontFamily, Displaymode displaymode, bool fastskipignore, bool clearText)
{
    auto sm = Host::GetCommonSharedMem(pid);
    if (!sm)
        return;
    sm->waittime = waittime;
    sm->fontCharSet = fontCharSet;
    sm->fontCharSetEnabled = fontCharSetEnabled;
    wcscpy_s(sm->fontFamily, ARRAYSIZE(sm->fontFamily), fontFamily);
    sm->displaymode = displaymode;
    sm->fastskipignore = fastskipignore;
    sm->clearText = clearText;
}
C_LUNA_API bool Luna_CheckIsUsingEmbed(ThreadParam tp)
{
    return Host::CheckIsUsingEmbed(tp);
}
C_LUNA_API void Luna_UseEmbed(ThreadParam tp, bool use)
{
    auto sm = Host::GetCommonSharedMem(tp.processId);
    if (!sm)
        return;
    sm->codepage = Host::defaultCodepage;
    for (int i = 0; i < ARRAYSIZE(sm->embedtps); i++)
    {
        if (sm->embedtps[i].use && (sm->embedtps[i].tp == tp))
            if (!use)
                ZeroMemory(sm->embedtps + i, sizeof(sm->embedtps[i]));
    }
    if (use)
        for (int i = 0; i < ARRAYSIZE(sm->embedtps); i++)
        {
            if (!sm->embedtps[i].use)
            {
                sm->embedtps[i].use = true;
                sm->embedtps[i].tp = tp;
                break;
            }
        }
}

C_LUNA_API void Luna_EmbedCallback(ThreadParam tp, LPCWSTR text, LPCWSTR trans)
{
    auto sm = Host::GetCommonSharedMem(tp.processId);
    if (!sm)
        return;
    wcsncpy(sm->text, trans, ARRAYSIZE(sm->text));
    char eventname[1000];
    sprintf(eventname, LUNA_EMBED_notify_event, tp.processId, simplehash::djb2_n2((const unsigned char *)(text), wcslen(text) * 2));
    win_event event1(eventname);
    event1.signal(true);
}

C_LUNA_API void Luna_SyncThread(ThreadParam tp, bool sync)
{
    // 必须放到线程里去异步做，不然GetThread死锁
    std::thread([=]()
                {
    try
    {
        auto &&t=Host::GetThread(tp);
        if (sync)
            TextThread::syncThreads->insert(&t);
        else
            TextThread::syncThreads->erase(&t);
    }
    catch (...)
    {
    } })
        .detach();
}