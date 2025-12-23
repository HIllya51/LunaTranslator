#pragma once

#include <AudioClient.h>
#include <mmdeviceapi.h>
#include <initguid.h>
#include <guiddef.h>
#include <mfapi.h>
#ifndef WINXP
#include <audioclientactivationparams.h>
#else
#include "../../xpundef/xp_waspi.hpp"
#endif

#include "Common.h"
#define BITS_PER_BYTE 8

// https://learn.microsoft.com/zh-cn/windows/uwp/cpp-and-winrt-apis/agile-objects
// https://learn.microsoft.com/en-us/windows/win32/api/mmdeviceapi/nf-mmdeviceapi-activateaudiointerfaceasync
class CLoopbackCapture : public ComImpl<IActivateAudioInterfaceCompletionHandler, IAgileObject>
{
public:
    CLoopbackCapture();
    CLoopbackCapture(int nSamplesPerSec, int wBitsPerSample, int nChannels);
    ~CLoopbackCapture() override;
    HRESULT StartCaptureAsync(DWORD processId, bool includeProcessTree);
    HRESULT StopCapture();

    METHODASYNCCALLBACK(CLoopbackCapture, StartCapture, OnStartCapture);
    METHODASYNCCALLBACK(CLoopbackCapture, StopCapture, OnStopCapture);
    METHODASYNCCALLBACK(CLoopbackCapture, SampleReady, OnSampleReady);
    METHODASYNCCALLBACK(CLoopbackCapture, FinishCapture, OnFinishCapture);

    // IActivateAudioInterfaceCompletionHandler
    STDMETHOD(ActivateCompleted)
    (IActivateAudioInterfaceAsyncOperation *operation);

    std::string buffer;
    std::function<void(std::string &&)> OnDataCallback;

private:
    WAVEFORMATEX m_CaptureFormat{};
    // NB: All states >= Initialized will allow some methods
    // to be called successfully on the Audio Client
    enum class DeviceState
    {
        Uninitialized,
        Error,
        Initialized,
        Starting,
        Capturing,
        Stopping,
        Stopped,
    };

    HRESULT OnStartCapture(IMFAsyncResult *pResult);
    HRESULT OnStopCapture(IMFAsyncResult *pResult);
    HRESULT OnFinishCapture(IMFAsyncResult *pResult);
    HRESULT OnSampleReady(IMFAsyncResult *pResult);

    HRESULT InitializeLoopbackCapture();
    HRESULT CreateWAVFile();
    HRESULT FixWAVHeader();
    HRESULT OnAudioSampleRequested();

    HRESULT ActivateAudioInterface(DWORD processId, bool includeProcessTree);
    HRESULT FinishCaptureAsync();

    HRESULT SetDeviceStateErrorIfFailed(HRESULT hr);

    CComPtr<IAudioClient> m_AudioClient;
    UINT32 m_BufferFrames = 0;
    CComPtr<IAudioCaptureClient> m_AudioCaptureClient;
    CComPtr<IMFAsyncResult> m_SampleReadyAsyncResult;

    CEvent m_SampleReadyEvent;
    MFWORKITEM_KEY m_SampleReadyKey = 0;
    std::mutex m_CritSec;
    DWORD m_dwQueueID = 0;
    DWORD m_cbHeaderSize = 0;
    DWORD m_cbDataSize = 0;
    std::mutex bufferlock;
    // These two members are used to communicate between the main thread
    // and the ActivateCompleted callback.
    HRESULT m_activateResult = E_UNEXPECTED;

    DeviceState m_DeviceState{DeviceState::Uninitialized};
    CEvent m_hActivateCompleted;
    CEvent m_hCaptureStopped;
};

class LoopbackTranditional
{
    CComPtr<IMMDeviceEnumerator> pEnumerator = nullptr;
    CComPtr<IMMDevice> pDevice = nullptr;
    CComPtr<IAudioClient> pAudioClient = nullptr;
    CComPtr<IAudioCaptureClient> pCaptureClient = nullptr;
    CEvent threadend;
    void RecordThread();
    std::atomic<bool> running;
    CComHeapPtr<WAVEFORMATEX> pwfx{};

public:
    std::function<void(std::string &&)> OnDataCallback;
    std::string buffer;
    HRESULT StopCapture();
    HRESULT StartCaptureAsync();
    LoopbackTranditional();
    LoopbackTranditional(int nSamplesPerSec, int wBitsPerSample, int nChannels);
};

class SupperRecord
{
    CComPtr<CLoopbackCapture> capture;
    std::unique_ptr<LoopbackTranditional> capture_lower;
    bool usefirst = true;

public:
    std::function<void(std::string &&)> OnDataCallback;
    std::string buffer;
    HRESULT StopCapture();
    HRESULT StartCaptureAsync(DWORD processId, bool includeProcessTree);
    SupperRecord();
    SupperRecord(int nSamplesPerSec, int wBitsPerSample, int nChannels);
};