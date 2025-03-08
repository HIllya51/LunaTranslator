#pragma once

#include <AudioClient.h>
#include <mmdeviceapi.h>
#include <initguid.h>
#include <guiddef.h>
#include <mfapi.h>
#ifndef WINXP
#include <audioclientactivationparams.h>
#else
#include "xpdef.hpp"
#endif

#include "Common.h"
#define BITS_PER_BYTE 8

// https://learn.microsoft.com/zh-cn/windows/uwp/cpp-and-winrt-apis/agile-objects
// https://learn.microsoft.com/en-us/windows/win32/api/mmdeviceapi/nf-mmdeviceapi-activateaudiointerfaceasync
class CLoopbackCapture : public ComImpl<IActivateAudioInterfaceCompletionHandler, IAgileObject>
{
public:
    ~CLoopbackCapture() override;
    HRESULT StartCaptureAsync(DWORD processId, bool includeProcessTree);
    HRESULT StopCaptureAsync();

    METHODASYNCCALLBACK(CLoopbackCapture, StartCapture, OnStartCapture);
    METHODASYNCCALLBACK(CLoopbackCapture, StopCapture, OnStopCapture);
    METHODASYNCCALLBACK(CLoopbackCapture, SampleReady, OnSampleReady);
    METHODASYNCCALLBACK(CLoopbackCapture, FinishCapture, OnFinishCapture);

    // IActivateAudioInterfaceCompletionHandler
    STDMETHOD(ActivateCompleted)
    (IActivateAudioInterfaceAsyncOperation *operation);

    std::string buffer;

private:
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
    WAVEFORMATEX m_CaptureFormat{};
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
