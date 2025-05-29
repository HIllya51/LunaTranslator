#ifndef WINXP
#include <roapi.h>
#else
#include "../xpundef/xp_winrt.hpp"
#endif

#include <speechapi_cxx.h>

using namespace Microsoft::CognitiveServices::Speech;
using namespace Microsoft::CognitiveServices::Speech::Audio;

constexpr inline const char MS_TTS_KEY[] = "Key:ZCjZ7nHDSLvf4gpELteM4AnzaWUjTpn7UkV7D@vvksl0w1SNgon6d1905WANbktDc9S39oaA4r29HJNayXvTq8fJsq";
const WCHAR syspath1[] = LR"(C:\Windows\SystemApps\MicrosoftWindows.Client.Core_cw5n1h2txyewy\SpeechSynthesizer)";
const WCHAR syspath2[] = LR"(C:\Windows\SystemApps\MicrosoftWindows.Client.Core_cw5n1h2txyewy)";

std::optional<std::string> CheckSynthesisResult(const std::shared_ptr<SpeechSynthesisResult> &result)
{
    if (result->Reason != ResultReason::Canceled)
        return {};

    auto details = SpeechSynthesisCancellationDetails::FromResult(result);
    if (details->Reason != CancellationReason::Error)
        return {};

    return details->ErrorDetails;
}
void writewavheader(char *pBuffer, int sSize)
{
    int fsize = sSize + 46;
    int ptr = 0;
    memcpy(pBuffer, "RIFF", 4);
    ptr += 4;
    memcpy(pBuffer + ptr, &fsize, 4);
    ptr += 4;
    memcpy(pBuffer + ptr, "WAVEfmt ", 8);
    ptr += 8;
    memcpy(pBuffer + ptr, "\x12\x00\x00\x00", 4);
    ptr += 4;
    memcpy(pBuffer + ptr, "\x01\x00\x01\x00\xc0\x5d\x00\x00\x80\xbb\x00\x00\x02\x00\x10\x00\x00\x00", sizeof(WAVEFORMATEX));
    ptr += sizeof(WAVEFORMATEX);
    memcpy(pBuffer + ptr, "data", 4);
    ptr += 4;
    memcpy(pBuffer + ptr, &sSize, 4);
    ptr += 4;
}
int msnaturalvoice(int argc, wchar_t *argv[])
{

    HANDLE hPipe = CreateNamedPipe(argv[1], PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, PIPE_UNLIMITED_INSTANCES, 65535, 65535, NMPWAIT_WAIT_FOREVER, 0);

    auto handle = CreateFileMappingW(INVALID_HANDLE_VALUE, &allAccess, PAGE_EXECUTE_READWRITE, 0, 1024 * 1024 * 16, argv[3]);

    auto mapview = (char *)MapViewOfFile(handle, FILE_MAP_ALL_ACCESS | FILE_MAP_EXECUTE, 0, 0, 1024 * 1024 * 16);
    memset(mapview, 0, 1024 * 1024 * 16);

    SetEvent(CreateEvent(&allAccess, FALSE, FALSE, argv[2]));
    if (!ConnectNamedPipe(hPipe, NULL))
        return 0;

    RoInitialize(RO_INIT_MULTITHREADED); // 系统的版本必须roinit

    WCHAR env[65535];
    GetEnvironmentVariableW(L"PATH", env, 65535);
    auto newenv = std::wstring(env) + L";" + syspath1 + L";" + syspath2;
    SetEnvironmentVariableW(L"PATH", newenv.c_str());

    auto config = EmbeddedSpeechConfig::FromPath(WideStringToString(argv[4], CP_ACP));

    config->SetSpeechSynthesisOutputFormat(SpeechSynthesisOutputFormat::Riff24Khz16BitMonoPcm);
    config->SetProperty(PropertyId::SpeechServiceResponse_RequestSentenceBoundary, "true");
    config->SetProperty(PropertyId::SpeechServiceResponse_RequestPunctuationBoundary, "false");
    config->SetSpeechSynthesisVoice(config->GetSpeechSynthesisVoiceName(), MS_TTS_KEY);
    std::shared_ptr<Microsoft::CognitiveServices::Speech::SpeechSynthesizer> synthesizer;
    synthesizer = SpeechSynthesizer::FromConfig(config, nullptr);

    wchar_t text[10000];
    DWORD _;
    while (true)
    {
        ZeroMemory(text, sizeof(text));
        if (!ReadFile(hPipe, (unsigned char *)text, 10000 * 2, &_, NULL))
            break;
        auto result = synthesizer->SpeakSsml(text);
        uint32_t len = 0;
        if (auto failed = CheckSynthesisResult(result))
        {
            len = -failed.value().size();
            memcpy(mapview, failed.value().c_str(), failed.value().size());
            WriteFile(hPipe, &len, 4, &_, NULL);
            continue;
        }
        auto stream = AudioDataStream::FromResult(result);
        while (auto read = stream->ReadData(len, (uint8_t *)mapview + len + 46, 1024 * 1024 * 16))
        {
            len += read;
        }
        writewavheader(mapview, len);
        len += 46;
        WriteFile(hPipe, &len, 4, &_, NULL);
    }
    return 0;
}