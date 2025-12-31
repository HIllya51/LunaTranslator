#include "osversion.hpp"

typedef void (*MonitorPidVolume_callback_t)(BOOL);
namespace
{
    MonitorPidVolume_callback_t MonitorPidVolume_callback = nullptr;
    CComPtr<IAudioSessionManager2> sessionManager = nullptr;
    std::mutex sessionforpid_lock;
    std::map<DWORD, CComPtr<IAudioSessionControl2>> sessionforpid;
    std::optional<std::wstring> processname;
}
class AudioSessionEvents : public ComImpl<IAudioSessionEvents>
{
public:
    HRESULT STDMETHODCALLTYPE OnDisplayNameChanged(LPCWSTR, LPCGUID) { return S_OK; }
    HRESULT STDMETHODCALLTYPE OnIconPathChanged(LPCWSTR, LPCGUID) { return S_OK; }
    HRESULT STDMETHODCALLTYPE OnSimpleVolumeChanged(float volume, BOOL mute, LPCGUID context)
    {
        if (MonitorPidVolume_callback)
            MonitorPidVolume_callback(mute);
        return S_OK;
    }
    HRESULT STDMETHODCALLTYPE OnChannelVolumeChanged(DWORD, float[], DWORD, LPCGUID) { return S_OK; }
    HRESULT STDMETHODCALLTYPE OnGroupingParamChanged(LPCGUID, LPCGUID) { return S_OK; }
    HRESULT STDMETHODCALLTYPE OnStateChanged(AudioSessionState) { return S_OK; }
    HRESULT STDMETHODCALLTYPE OnSessionDisconnected(AudioSessionDisconnectReason) { return S_OK; }
};
static CComPtr<AudioSessionEvents> sessionEvents;
static void NotifyDirectly(const CComPtr<IAudioSessionControl2> &sess2)
{
    if (!MonitorPidVolume_callback)
        return;
    CComPtr<ISimpleAudioVolume> pSimpleAudioVolume;
    CHECK_FAILURE_NORET(sess2.QueryInterface(&pSimpleAudioVolume));
    BOOL mute = FALSE;
    CHECK_FAILURE_NORET(pSimpleAudioVolume->GetMute(&mute));
    MonitorPidVolume_callback(mute);
}
std::optional<std::wstring> _getprocname(DWORD pid)
{
    CHandle hprocess{OpenProcess(FUCKPRIVI, FALSE, pid)};
    if (!hprocess)
        return {};
    WCHAR path[MAX_PATH];
    if (!GetProcessImageFileNameW(hprocess, path, MAX_PATH))
        return {};
    return path;
}
class AudioSessionNotification : public ComImpl<IAudioSessionNotification>
{
public:
    STDMETHODIMP OnSessionCreated(IAudioSessionControl *pNewSession)
    {
        CComPtr<IAudioSessionControl2> session2;
        CHECK_FAILURE(pNewSession->QueryInterface(&session2));
        DWORD pid;
        CHECK_FAILURE(session2->GetProcessId(&pid));
        std::lock_guard _(sessionforpid_lock);
        if (sessionforpid.count(pid) || (processname && (processname == _getprocname(pid))))
        {
            sessionforpid[pid] = session2;
            CHECK_FAILURE(session2->RegisterAudioSessionNotification(sessionEvents));
            NotifyDirectly(session2);
        }
        return S_OK;
    }
};
static CComPtr<AudioSessionNotification> notification;

static HRESULT GetSessionForPid(DWORD pid, CComPtr<IAudioSessionControl2> &sess2)
{
    if (!sessionManager)
        return E_FAIL;
    CComPtr<IAudioSessionEnumerator> pAudioSessionEnumerator;
    CHECK_FAILURE(sessionManager->GetSessionEnumerator(&pAudioSessionEnumerator));

    int nCount = 0;
    CHECK_FAILURE(pAudioSessionEnumerator->GetCount(&nCount));

    for (int i = 0; i < nCount; ++i)
    {
        CComPtr<IAudioSessionControl> pAudioSessionControl;
        CHECK_FAILURE_CONTINUE(pAudioSessionEnumerator->GetSession(i, &pAudioSessionControl));

        CComPtr<IAudioSessionControl2> pAudioSessionControl2;
        CHECK_FAILURE_CONTINUE(pAudioSessionControl->QueryInterface(&pAudioSessionControl2));
        DWORD dwPid = 0;
        CHECK_FAILURE_CONTINUE(pAudioSessionControl2->GetProcessId(&dwPid));
        if (dwPid == pid)
        {
            sess2 = pAudioSessionControl2;
            return S_OK;
        }
    }
    return E_FAIL;
}
DECLARE_API void SetCurrProcessMute(bool mute)
{
    std::lock_guard _(sessionforpid_lock);
    for (auto &[pid, session] : sessionforpid)
    {
        if (!session)
            continue;
        CComPtr<ISimpleAudioVolume> pSimpleAudioVolume;
        CHECK_FAILURE_CONTINUE(session.QueryInterface(&pSimpleAudioVolume));
        pSimpleAudioVolume->SetMute(mute, NULL);
    }
}
std::vector<DWORD> _getsamenamepids(const std::optional<std::wstring> &proc)
{
    std::vector<DWORD> ret;
    if (!proc)
        return ret;
    CHandle hSnapshot{CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)};
    if (hSnapshot == INVALID_HANDLE_VALUE)
        return ret;

    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);
    if (Process32First(hSnapshot, &pe32))
    {
        do
        {
            auto path = _getprocname(pe32.th32ProcessID);
            if (!path)
                continue;
            if (proc == path)
                ret.push_back(pe32.th32ProcessID);
        } while (Process32Next(hSnapshot, &pe32));
    }
    return ret;
}
DECLARE_API void MonitorPidVolume(DWORD pid)
{
    // 监控pid时，同时一起监控同exe的所有pids，和音量合成器合并所有pid那样
    processname = _getprocname(pid);
    auto pids = _getsamenamepids(processname);
    pids.push_back(pid);
    std::lock_guard _(sessionforpid_lock);
    sessionforpid.clear();
    for (auto pid : pids)
    {
        sessionforpid[pid] = {};
        CHECK_FAILURE_CONTINUE(GetSessionForPid(pid, sessionforpid[pid]));
        CHECK_FAILURE_CONTINUE(sessionforpid[pid]->RegisterAudioSessionNotification(sessionEvents));
        NotifyDirectly(sessionforpid[pid]);
    }
}
DECLARE_API void StartMonitorVolume(MonitorPidVolume_callback_t callback)
{
    MonitorPidVolume_callback = callback;
    notification = new AudioSessionNotification{};
    sessionEvents = new AudioSessionEvents{};
    CComPtr<IMMDeviceEnumerator> enumerator;
    CHECK_FAILURE_NORET(enumerator.CoCreateInstance(__uuidof(MMDeviceEnumerator), NULL, CLSCTX_ALL));
    CComPtr<IMMDevice> device;
    CHECK_FAILURE_NORET(enumerator->GetDefaultAudioEndpoint(eRender, eConsole, &device));
    CHECK_FAILURE_NORET(device->Activate(__uuidof(IAudioSessionManager2), CLSCTX_ALL, NULL, (void **)&sessionManager));
    CHECK_FAILURE_NORET(sessionManager->RegisterSessionNotification(notification));
}
namespace
{
    typedef LONG(NTAPI *pNtSuspendProcess)(HANDLE ProcessHandle);
    pNtSuspendProcess NtSuspendProcess;
    typedef LONG(NTAPI *pNtResumeProcess)(HANDLE ProcessHandle);
    pNtResumeProcess NtResumeProcess;
}
DECLARE_API void SuspendResumeProcess(DWORD pid)
{
    static bool flag = true;
    static auto _ = []()
    {
        HMODULE ntdll = ::GetModuleHandleA("ntdll.dll");
        if (!ntdll)
            return 0;
        NtSuspendProcess = (pNtSuspendProcess)::GetProcAddress(ntdll, "NtSuspendProcess");
        NtResumeProcess = (pNtResumeProcess)::GetProcAddress(ntdll, "NtResumeProcess");
        return 0;
    }();
    if (!NtSuspendProcess || !NtResumeProcess)
        return;
    auto proc = _getprocname(pid);
    auto pids = _getsamenamepids(proc);
    pids.push_back(pid);
    for (auto pid : pids)
    {
        CHandle hprocess{OpenProcess(PROCESS_SUSPEND_RESUME, FALSE, pid)};
        if (!hprocess)
            continue;
        flag ? NtSuspendProcess(hprocess) : NtResumeProcess(hprocess);
    }
    flag = !flag;
}