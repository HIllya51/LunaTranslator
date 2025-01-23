#ifndef WINXP
#include <shlobj.h>
#include <wchar.h>
#include <iostream>
#include <audioclientactivationparams.h>

#include "LoopbackCapture.h"

#define BITS_PER_BYTE 8

HRESULT CLoopbackCapture::SetDeviceStateErrorIfFailed(HRESULT hr)
{
    if (FAILED(hr))
    {
        m_DeviceState = DeviceState::Error;
    }
    return hr;
}

HRESULT CLoopbackCapture::InitializeLoopbackCapture()
{
    // Create events for sample ready or user stop
    RETURN_IF_FAILED(m_SampleReadyEvent.create(wil::EventOptions::None));

    // Initialize MF
    RETURN_IF_FAILED(MFStartup(MF_VERSION, MFSTARTUP_LITE));

    // Register MMCSS work queue
    DWORD dwTaskID = 0;
    RETURN_IF_FAILED(MFLockSharedWorkQueue(L"Capture", 0, &dwTaskID, &m_dwQueueID));

    // Set the capture event work queue to use the MMCSS queue
    m_xSampleReady.SetQueueID(m_dwQueueID);

    // Create the completion event as auto-reset
    RETURN_IF_FAILED(m_hActivateCompleted.create(wil::EventOptions::None));

    // Create the capture-stopped event as auto-reset
    RETURN_IF_FAILED(m_hCaptureStopped.create(wil::EventOptions::None));

    return S_OK;
}

CLoopbackCapture::~CLoopbackCapture()
{
    if (m_dwQueueID != 0)
    {
        MFUnlockWorkQueue(m_dwQueueID);
    }
}

HRESULT CLoopbackCapture::ActivateAudioInterface(DWORD processId, bool includeProcessTree)
{
    return SetDeviceStateErrorIfFailed([&]() -> HRESULT
                                       {
            AUDIOCLIENT_ACTIVATION_PARAMS audioclientActivationParams = {};
            audioclientActivationParams.ActivationType = AUDIOCLIENT_ACTIVATION_TYPE_PROCESS_LOOPBACK;
            audioclientActivationParams.ProcessLoopbackParams.ProcessLoopbackMode = includeProcessTree ?
                PROCESS_LOOPBACK_MODE_INCLUDE_TARGET_PROCESS_TREE : PROCESS_LOOPBACK_MODE_EXCLUDE_TARGET_PROCESS_TREE;
            audioclientActivationParams.ProcessLoopbackParams.TargetProcessId = processId;

            PROPVARIANT activateParams = {};
            activateParams.vt = VT_BLOB;
            activateParams.blob.cbSize = sizeof(audioclientActivationParams);
            activateParams.blob.pBlobData = (BYTE*)&audioclientActivationParams;

            wil::com_ptr_nothrow<IActivateAudioInterfaceAsyncOperation> asyncOp;
            RETURN_IF_FAILED(ActivateAudioInterfaceAsync(VIRTUAL_AUDIO_DEVICE_PROCESS_LOOPBACK, __uuidof(IAudioClient), &activateParams, this, &asyncOp));

            // Wait for activation completion
            m_hActivateCompleted.wait();

            return m_activateResult; }());
}

//
//  ActivateCompleted()
//
//  Callback implementation of ActivateAudioInterfaceAsync function.  This will be called on MTA thread
//  when results of the activation are available.
//
HRESULT CLoopbackCapture::ActivateCompleted(IActivateAudioInterfaceAsyncOperation *operation)
{
    m_activateResult = SetDeviceStateErrorIfFailed([&]() -> HRESULT
                                                   {
            // Check for a successful activation result
            HRESULT hrActivateResult = E_UNEXPECTED;
            wil::com_ptr_nothrow<IUnknown> punkAudioInterface;
            RETURN_IF_FAILED(operation->GetActivateResult(&hrActivateResult, &punkAudioInterface));
            RETURN_IF_FAILED(hrActivateResult);

            // Get the pointer for the Audio Client
            RETURN_IF_FAILED(punkAudioInterface.copy_to(&m_AudioClient));

            // The app can also call m_AudioClient->GetMixFormat instead to get the capture format.
            // 16 - bit PCM format.
            m_CaptureFormat.wFormatTag = WAVE_FORMAT_PCM;
            m_CaptureFormat.nChannels = 2;
            m_CaptureFormat.nSamplesPerSec = 44100;
            m_CaptureFormat.wBitsPerSample = 16;
            m_CaptureFormat.nBlockAlign = m_CaptureFormat.nChannels * m_CaptureFormat.wBitsPerSample / BITS_PER_BYTE;
            m_CaptureFormat.nAvgBytesPerSec = m_CaptureFormat.nSamplesPerSec * m_CaptureFormat.nBlockAlign;

            // Initialize the AudioClient in Shared Mode with the user specified buffer
            RETURN_IF_FAILED(m_AudioClient->Initialize(AUDCLNT_SHAREMODE_SHARED,
                AUDCLNT_STREAMFLAGS_LOOPBACK | AUDCLNT_STREAMFLAGS_EVENTCALLBACK,
                200000,
                AUDCLNT_STREAMFLAGS_AUTOCONVERTPCM,
                &m_CaptureFormat,
                nullptr));

            // Get the maximum size of the AudioClient Buffer
            RETURN_IF_FAILED(m_AudioClient->GetBufferSize(&m_BufferFrames));

            // Get the capture client
            RETURN_IF_FAILED(m_AudioClient->GetService(IID_PPV_ARGS(&m_AudioCaptureClient)));

            // Create Async callback for sample events
            RETURN_IF_FAILED(MFCreateAsyncResult(nullptr, &m_xSampleReady, nullptr, &m_SampleReadyAsyncResult));

            // Tell the system which event handle it should signal when an audio buffer is ready to be processed by the client
            RETURN_IF_FAILED(m_AudioClient->SetEventHandle(m_SampleReadyEvent.get()));

            // Creates the WAV file.
            RETURN_IF_FAILED(CreateWAVFile());

            // Everything is ready.
            m_DeviceState = DeviceState::Initialized;

            return S_OK; }());

    // Let ActivateAudioInterface know that m_activateResult has the result of the activation attempt.
    m_hActivateCompleted.SetEvent();
    return S_OK;
}

//
//  CreateWAVFile()
//
//  Creates a WAV file in music folder
//
HRESULT CLoopbackCapture::CreateWAVFile()
{
    return SetDeviceStateErrorIfFailed([&]() -> HRESULT
                                       {

            // Create and write the WAV header

                // 1. RIFF chunk descriptor
            DWORD header[] = {
                                FCC('RIFF'),        // RIFF header
                                0,                  // Total size of WAV (will be filled in later)
                                FCC('WAVE'),        // WAVE FourCC
                                FCC('fmt '),        // Start of 'fmt ' chunk
                                sizeof(m_CaptureFormat) // Size of fmt chunk
            };
            DWORD dwBytesWritten = 0;
            std::lock_guard _(bufferlock);
            buffer+=std::string((char*)header, sizeof(header));
            m_cbHeaderSize += sizeof(header);

            // 2. The fmt sub-chunk
            WI_ASSERT(m_CaptureFormat.cbSize == 0);
            buffer+=std::string((char*) &m_CaptureFormat, sizeof(m_CaptureFormat));
            m_cbHeaderSize += sizeof(m_CaptureFormat);

            // 3. The data sub-chunk
            DWORD data[] = { FCC('data'), 0 };  // Start of 'data' chunk
            buffer+=std::string((char*) data, sizeof(data));
            m_cbHeaderSize += sizeof(data);

            return S_OK; }());
}

//
//  FixWAVHeader()
//
//  The size values were not known when we originally wrote the header, so now go through and fix the values
//
HRESULT CLoopbackCapture::FixWAVHeader()
{

    std::lock_guard _(bufferlock);
    // Write the size of the 'data' chunk first
    auto offset = m_cbHeaderSize - sizeof(DWORD);
    memcpy(buffer.data() + offset, &m_cbDataSize, sizeof(DWORD));
    // Write the total file size, minus RIFF chunk and size
    // sizeof(DWORD) == sizeof(FOURCC)

    DWORD cbTotalSize = m_cbDataSize + m_cbHeaderSize - 8;

    offset = sizeof(DWORD);
    memcpy(buffer.data() + offset, &cbTotalSize, sizeof(DWORD));

    return S_OK;
}

HRESULT CLoopbackCapture::StartCaptureAsync(DWORD processId, bool includeProcessTree)
{

    RETURN_IF_FAILED(InitializeLoopbackCapture());
    RETURN_IF_FAILED(ActivateAudioInterface(processId, includeProcessTree));

    // We should be in the initialzied state if this is the first time through getting ready to capture.
    if (m_DeviceState == DeviceState::Initialized)
    {
        m_DeviceState = DeviceState::Starting;
        return MFPutWorkItem2(MFASYNC_CALLBACK_QUEUE_MULTITHREADED, 0, &m_xStartCapture, nullptr);
    }

    return S_OK;
}

//
//  OnStartCapture()
//
//  Callback method to start capture
//
HRESULT CLoopbackCapture::OnStartCapture(IMFAsyncResult *pResult)
{
    return SetDeviceStateErrorIfFailed([&]() -> HRESULT
                                       {
            // Start the capture
            RETURN_IF_FAILED(m_AudioClient->Start());

            m_DeviceState = DeviceState::Capturing;
            MFPutWaitingWorkItem(m_SampleReadyEvent.get(), 0, m_SampleReadyAsyncResult.get(), &m_SampleReadyKey);

            return S_OK; }());
}

//
//  StopCaptureAsync()
//
//  Stop capture asynchronously via MF Work Item
//
HRESULT CLoopbackCapture::StopCaptureAsync()
{
    RETURN_HR_IF(E_NOT_VALID_STATE, (m_DeviceState != DeviceState::Capturing) &&
                                        (m_DeviceState != DeviceState::Error));

    m_DeviceState = DeviceState::Stopping;

    RETURN_IF_FAILED(MFPutWorkItem2(MFASYNC_CALLBACK_QUEUE_MULTITHREADED, 0, &m_xStopCapture, nullptr));

    // Wait for capture to stop
    m_hCaptureStopped.wait();

    return S_OK;
}

//
//  OnStopCapture()
//
//  Callback method to stop capture
//
HRESULT CLoopbackCapture::OnStopCapture(IMFAsyncResult *pResult)
{
    // Stop capture by cancelling Work Item
    // Cancel the queued work item (if any)
    if (0 != m_SampleReadyKey)
    {
        MFCancelWorkItem(m_SampleReadyKey);
        m_SampleReadyKey = 0;
    }

    m_AudioClient->Stop();
    m_SampleReadyAsyncResult.reset();

    return FinishCaptureAsync();
}

//
//  FinishCaptureAsync()
//
//  Finalizes WAV file on a separate thread via MF Work Item
//
HRESULT CLoopbackCapture::FinishCaptureAsync()
{
    // We should be flushing when this is called
    return MFPutWorkItem2(MFASYNC_CALLBACK_QUEUE_MULTITHREADED, 0, &m_xFinishCapture, nullptr);
}

//
//  OnFinishCapture()
//
//  Because of the asynchronous nature of the MF Work Queues and the DataWriter, there could still be
//  a sample processing.  So this will get called to finalize the WAV header.
//
HRESULT CLoopbackCapture::OnFinishCapture(IMFAsyncResult *pResult)
{
    // FixWAVHeader will set the DeviceStateStopped when all async tasks are complete
    HRESULT hr = FixWAVHeader();

    m_DeviceState = DeviceState::Stopped;

    m_hCaptureStopped.SetEvent();

    return hr;
}

//
//  OnSampleReady()
//
//  Callback method when ready to fill sample buffer
//
HRESULT CLoopbackCapture::OnSampleReady(IMFAsyncResult *pResult)
{
    if (SUCCEEDED(OnAudioSampleRequested()))
    {
        // Re-queue work item for next sample
        if (m_DeviceState == DeviceState::Capturing)
        {
            // Re-queue work item for next sample
            return MFPutWaitingWorkItem(m_SampleReadyEvent.get(), 0, m_SampleReadyAsyncResult.get(), &m_SampleReadyKey);
        }
    }
    else
    {
        m_DeviceState = DeviceState::Error;
    }

    return S_OK;
}

//
//  OnAudioSampleRequested()
//
//  Called when audio device fires m_SampleReadyEvent
//
HRESULT CLoopbackCapture::OnAudioSampleRequested()
{
    UINT32 FramesAvailable = 0;
    BYTE *Data = nullptr;
    DWORD dwCaptureFlags;
    UINT64 u64DevicePosition = 0;
    UINT64 u64QPCPosition = 0;
    DWORD cbBytesToCapture = 0;

    auto lock = m_CritSec.lock();

    // If this flag is set, we have already queued up the async call to finialize the WAV header
    // So we don't want to grab or write any more data that would possibly give us an invalid size
    if (m_DeviceState == DeviceState::Stopping)
    {
        return S_OK;
    }

    // A word on why we have a loop here;
    // Suppose it has been 10 milliseconds or so since the last time
    // this routine was invoked, and that we're capturing 48000 samples per second.
    //
    // The audio engine can be reasonably expected to have accumulated about that much
    // audio data - that is, about 480 samples.
    //
    // However, the audio engine is free to accumulate this in various ways:
    // a. as a single packet of 480 samples, OR
    // b. as a packet of 80 samples plus a packet of 400 samples, OR
    // c. as 48 packets of 10 samples each.
    //
    // In particular, there is no guarantee that this routine will be
    // run once for each packet.
    //
    // So every time this routine runs, we need to read ALL the packets
    // that are now available;
    //
    // We do this by calling IAudioCaptureClient::GetNextPacketSize
    // over and over again until it indicates there are no more packets remaining.
    while (SUCCEEDED(m_AudioCaptureClient->GetNextPacketSize(&FramesAvailable)) && FramesAvailable > 0)
    {
        cbBytesToCapture = FramesAvailable * m_CaptureFormat.nBlockAlign;

        // WAV files have a 4GB (0xFFFFFFFF) size limit, so likely we have hit that limit when we
        // overflow here.  Time to stop the capture
        if ((m_cbDataSize + cbBytesToCapture) < m_cbDataSize)
        {
            StopCaptureAsync();
            break;
        }

        // Get sample buffer
        RETURN_IF_FAILED(m_AudioCaptureClient->GetBuffer(&Data, &FramesAvailable, &dwCaptureFlags, &u64DevicePosition, &u64QPCPosition));

        // Write File
        if (m_DeviceState != DeviceState::Stopping)
        {
            std::lock_guard _(bufferlock);
            buffer += std::string((char *)Data, cbBytesToCapture);
        }

        // Release buffer back
        m_AudioCaptureClient->ReleaseBuffer(FramesAvailable);

        // Increase the size of our 'data' chunk.  m_cbDataSize needs to be accurate
        m_cbDataSize += cbBytesToCapture;
    }

    return S_OK;
}
#endif