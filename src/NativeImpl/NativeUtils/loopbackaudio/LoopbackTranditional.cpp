#include "LoopbackCapture.h"
#include "../../wav.hpp"

static void WriteWavHeader(std::string &file, WAVEFORMATEX *pwfx, size_t dataSize)
{
    // 如果是 FLOAT 格式 (WASAPI 默认通常是 32-bit float)
    unsigned short formatTag;
    if (pwfx->wFormatTag == WAVE_FORMAT_IEEE_FLOAT ||
        (pwfx->wFormatTag == WAVE_FORMAT_EXTENSIBLE && ((WAVEFORMATEXTENSIBLE *)pwfx)->SubFormat == KSDATAFORMAT_SUBTYPE_IEEE_FLOAT))
        formatTag = WAVE_FORMAT_IEEE_FLOAT;
    else
        formatTag = WAVE_FORMAT_PCM;

    file = wav::BuildHeader(formatTag, pwfx->nChannels, pwfx->nSamplesPerSec,
                            pwfx->nAvgBytesPerSec, pwfx->nBlockAlign, pwfx->wBitsPerSample,
                            (unsigned int)dataSize) + file;
}
void LoopbackTranditional::RecordThread()
{
    running = true;
    size_t totalBytesWritten = 0;
    while (running)
    {
        Sleep(10);

        UINT32 FramesAvailable = 0;
        BYTE *Data = nullptr;
        DWORD dwCaptureFlags;
        while (SUCCEEDED(pCaptureClient->GetNextPacketSize(&FramesAvailable)) && FramesAvailable > 0)
        {
            if (FAILED(pCaptureClient->GetBuffer(&Data, &FramesAvailable, &dwCaptureFlags, NULL, NULL)))
            {
                running = false;
                break;
            }
            size_t cbBytesToCapture = FramesAvailable * pwfx->nBlockAlign;
            auto _data = std::string((char *)Data, cbBytesToCapture);
            if (!OnDataCallback)
                buffer += std::move(_data);
            else
            {
                OnDataCallback(std::move(_data));
            }
            totalBytesWritten += cbBytesToCapture;

            pCaptureClient->ReleaseBuffer(FramesAvailable);
        }
    }
    WriteWavHeader(buffer, pwfx, totalBytesWritten);
    threadend.Set();
}
HRESULT LoopbackTranditional::StopCapture()
{
    running = false;
    WaitForSingleObject(threadend, INFINITE);
    return S_OK;
}
LoopbackTranditional::LoopbackTranditional() {}
LoopbackTranditional::LoopbackTranditional(int nSamplesPerSec, int wBitsPerSample, int nChannels)
{
    // The app can also call m_AudioClient->GetMixFormat instead to get the capture format.
    // 16 - bit PCM format.
    WAVEFORMATEX m_CaptureFormat{};
    m_CaptureFormat.wFormatTag = WAVE_FORMAT_PCM;
    m_CaptureFormat.nChannels = nChannels;
    m_CaptureFormat.nSamplesPerSec = nSamplesPerSec;
    m_CaptureFormat.wBitsPerSample = wBitsPerSample;
    m_CaptureFormat.nBlockAlign = m_CaptureFormat.nChannels * m_CaptureFormat.wBitsPerSample / BITS_PER_BYTE;
    m_CaptureFormat.nAvgBytesPerSec = m_CaptureFormat.nSamplesPerSec * m_CaptureFormat.nBlockAlign;
    pwfx.Attach((WAVEFORMATEX *)CoTaskMemAlloc(sizeof(WAVEFORMATEX)));
    memcpy(pwfx, &m_CaptureFormat, sizeof(m_CaptureFormat));
}
HRESULT LoopbackTranditional::StartCaptureAsync()
{
    CHECK_FAILURE(threadend.Create(NULL, FALSE, FALSE, NULL));
    CO_INIT co;
    CHECK_FAILURE(CoCreateInstance(__uuidof(MMDeviceEnumerator), NULL, CLSCTX_ALL, IID_PPV_ARGS(&pEnumerator)));

    CHECK_FAILURE(pEnumerator->GetDefaultAudioEndpoint(
        eRender, eConsole, &pDevice));
    CHECK_FAILURE(pDevice->Activate(
        __uuidof(IAudioClient), CLSCTX_ALL,
        NULL, (void **)&pAudioClient));
    if (!pwfx)
        CHECK_FAILURE(pAudioClient->GetMixFormat(&pwfx));
    auto flag = AUDCLNT_STREAMFLAGS_LOOPBACK | AUDCLNT_STREAMFLAGS_NOPERSIST;
    if (pwfx)
        flag |= AUDCLNT_STREAMFLAGS_AUTOCONVERTPCM;
    CHECK_FAILURE(pAudioClient->Initialize(
        AUDCLNT_SHAREMODE_SHARED,
        flag,     // 环回模式必须加这个 flag
        10000000, // 缓冲区时长: 1秒 (100ns 单位)
        0,
        pwfx,
        NULL));
    CHECK_FAILURE(pAudioClient->GetService(IID_PPV_ARGS(&pCaptureClient)));
    CHECK_FAILURE(pAudioClient->Start());
    std::thread([&]()
                { RecordThread(); })
        .detach();
    return S_OK;
}

SupperRecord::SupperRecord()
{
    capture = new CLoopbackCapture;
    capture_lower = std::make_unique<LoopbackTranditional>();
};

SupperRecord::SupperRecord(int nSamplesPerSec, int wBitsPerSample, int nChannels)
{
    capture = new CLoopbackCapture(nSamplesPerSec, wBitsPerSample, nChannels);
    capture_lower = std::make_unique<LoopbackTranditional>(nSamplesPerSec, wBitsPerSample, nChannels);
};
HRESULT SupperRecord::StopCapture()
{
    if (usefirst)
    {
        CHECK_FAILURE(capture->StopCapture());
        buffer = std::move(capture->buffer);
        return S_OK;
    }
    else
    {
        CHECK_FAILURE(capture_lower->StopCapture());
        buffer = std::move(capture_lower->buffer);
        return S_OK;
    }
}
HRESULT SupperRecord::StartCaptureAsync(DWORD processId, bool includeProcessTree)
{
    if (capture)
    {
        capture->OnDataCallback = OnDataCallback;
        if (SUCCEEDED(capture->StartCaptureAsync(processId, includeProcessTree)))
            return S_OK;
    }
    usefirst = false;
    capture_lower->OnDataCallback = OnDataCallback;
    return capture_lower->StartCaptureAsync();
}