
MIDL_INTERFACE("94ea2b94-e9cc-49e0-c0ff-ee64ca8f5b90")
IAgileObject : public IUnknown{
    public :
};
MIDL_INTERFACE("72A22D78-CDE4-431D-B8CC-843A71199B6D")
IActivateAudioInterfaceAsyncOperation : public IUnknown
{
public:
    virtual HRESULT STDMETHODCALLTYPE GetActivateResult(
        /* [annotation][out] */
        _Out_ HRESULT * activateResult,
        /* [annotation][out] */
        _Outptr_result_maybenull_ IUnknown * *activatedInterface) = 0;
};
MIDL_INTERFACE("41D949AB-9862-444A-80F6-C261334DA5EB")
IActivateAudioInterfaceCompletionHandler : public IUnknown
{
public:
    virtual HRESULT STDMETHODCALLTYPE ActivateCompleted(
        /* [annotation][in] */
        _In_ IActivateAudioInterfaceAsyncOperation * activateOperation) = 0;
};
#define MFASYNC_CALLBACK_QUEUE_MULTITHREADED 0x00000005

typedef /* [v1_enum] */
    enum AUDIOCLIENT_ACTIVATION_TYPE
{
    AUDIOCLIENT_ACTIVATION_TYPE_DEFAULT = 0,
    AUDIOCLIENT_ACTIVATION_TYPE_PROCESS_LOOPBACK = 1
} AUDIOCLIENT_ACTIVATION_TYPE;
typedef /* [v1_enum] */
    enum PROCESS_LOOPBACK_MODE
{
    PROCESS_LOOPBACK_MODE_INCLUDE_TARGET_PROCESS_TREE = 0,
    PROCESS_LOOPBACK_MODE_EXCLUDE_TARGET_PROCESS_TREE = 1
} PROCESS_LOOPBACK_MODE;
typedef struct AUDIOCLIENT_PROCESS_LOOPBACK_PARAMS
{
    DWORD TargetProcessId;
    PROCESS_LOOPBACK_MODE ProcessLoopbackMode;
} AUDIOCLIENT_PROCESS_LOOPBACK_PARAMS;
typedef struct AUDIOCLIENT_ACTIVATION_PARAMS
{
    AUDIOCLIENT_ACTIVATION_TYPE ActivationType;
    union
    {
        AUDIOCLIENT_PROCESS_LOOPBACK_PARAMS ProcessLoopbackParams;
    } DUMMYUNIONNAME;
} AUDIOCLIENT_ACTIVATION_PARAMS;
#define VIRTUAL_AUDIO_DEVICE_PROCESS_LOOPBACK L"VAD\\Process_Loopback"

#define AUDCLNT_STREAMFLAGS_AUTOCONVERTPCM 0x80000000

STDAPI ActivateAudioInterfaceAsync(
    _In_ LPCWSTR deviceInterfacePath,
    _In_ REFIID riid,
    _In_opt_ PROPVARIANT *activationParams,
    _In_ IActivateAudioInterfaceCompletionHandler *completionHandler,
    _COM_Outptr_ IActivateAudioInterfaceAsyncOperation **activationOperation);

STDAPI MFPutWorkItem2(
    DWORD dwQueue,
    LONG Priority,
    _In_ IMFAsyncCallback *pCallback,
    _In_opt_ IUnknown *pState);
STDAPI MFPutWaitingWorkItem(
    HANDLE hEvent,
    LONG Priority,
    void *pResult,
    void *pKey);
STDAPI MFLockSharedWorkQueue(
    _In_ PCWSTR wszClass,
    _In_ LONG BasePriority,
    _Inout_ DWORD *pdwTaskId,
    _Out_ DWORD *pID);