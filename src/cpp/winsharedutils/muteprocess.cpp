
typedef void (*MonitorPidVolume_callback_t)(BOOL);
namespace
{
    DWORD currentprocess = 0;
    MonitorPidVolume_callback_t MonitorPidVolume_callback = nullptr;
    CComPtr<IAudioSessionManager2> sessionManager = nullptr;
    CComPtr<IAudioSessionControl2> savesession2 = nullptr;
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
class AudioSessionNotification : public ComImpl<IAudioSessionNotification>
{
public:
    STDMETHODIMP OnSessionCreated(IAudioSessionControl *pNewSession)
    {
        CComPtr<IAudioSessionControl2> session2;
        CHECK_FAILURE(pNewSession->QueryInterface(&session2));
        DWORD pid;
        CHECK_FAILURE(session2->GetProcessId(&pid));
        if (currentprocess == pid)
        {
            savesession2 = session2;
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
    CHECK_FAILURE_NORET(GetSessionForPid(currentprocess, savesession2));
    CComPtr<ISimpleAudioVolume> pSimpleAudioVolume;
    CHECK_FAILURE_NORET(savesession2.QueryInterface(&pSimpleAudioVolume));
    pSimpleAudioVolume->SetMute(mute, NULL);
}
DECLARE_API void MonitorPidVolume(DWORD Pid)
{
    currentprocess = Pid;
    CHECK_FAILURE_NORET(GetSessionForPid(Pid, savesession2));
    CHECK_FAILURE_NORET(savesession2->RegisterAudioSessionNotification(sessionEvents));
    NotifyDirectly(savesession2);
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
    CComPtr<IAudioSessionEnumerator> pAudioSessionEnumerator;
    CHECK_FAILURE_NORET(sessionManager->GetSessionEnumerator(&pAudioSessionEnumerator)); // 必须的，否则不管用，不知道为何。
}