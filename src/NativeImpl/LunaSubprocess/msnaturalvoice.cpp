
#include <roapi.h>
#include "../fileversion.hpp"
#include <speechapi_cxx.h>
#include "../wav.hpp"
#include "pipehost.hpp"

using namespace Microsoft::CognitiveServices::Speech;
using namespace Microsoft::CognitiveServices::Speech::Audio;

const WCHAR syspath1[] = LR"(C:\Windows\SystemApps\MicrosoftWindows.Client.Core_cw5n1h2txyewy\SpeechSynthesizer)";
const WCHAR syspath2[] = LR"(C:\Windows\SystemApps\MicrosoftWindows.Client.Core_cw5n1h2txyewy)";

std::shared_ptr<SpeechSynthesisCancellationDetails> CheckSynthesisResult(const std::shared_ptr<SpeechSynthesisResult> &result)
{
    if (result->Reason != ResultReason::Canceled)
        return {};

    auto details = SpeechSynthesisCancellationDetails::FromResult(result);
    if (details->Reason != CancellationReason::Error)
        return {};

    return details;
}
// WAV 头改由 wav::BuildHeader 在 msnaturalvoice 主循环里就地构建
static std::string getkey()
{
    return "\x4b\x65\x79\x3a\x5a\x43\x6a\x5a\x37\x6e\x48\x44\x53\x4c\x76\x66\x34\x67\x70\x45\x4c\x74\x65\x4d\x34\x41\x6e\x7a\x61\x57\x55\x6a\x54\x70\x6e\x37\x55\x6b\x56\x37\x44\x40\x76\x76\x6b\x73\x6c\x30\x77\x31\x53\x4e\x67\x6f\x6e\x36\x64\x31\x39\x30\x35\x57\x41\x4e\x62\x6b\x74\x44\x63\x39\x53\x33\x39\x6f\x61\x41\x34\x72\x32\x39\x48\x4a\x4e\x61\x79\x58\x76\x54\x71\x38\x66\x4a\x73\x71";
}

std::string parsekey(std::string key)
{
    HMODULE hmodule = GetModuleHandle(L"Microsoft.CognitiveServices.Speech.core.dll");
    WCHAR path[MAX_PATH];
    GetModuleFileNameW(hmodule, path, MAX_PATH);
    auto vermy = QueryVersion(path);
    if (vermy <= std::make_tuple(1u, 41u, 1u, 0u))
        return key.substr(4);
    return key;
}

int msnaturalvoice(int argc, wchar_t *argv[])
{
    lunasp::PipeHost host(argv[1], argv[2], argv[3]);
    if (!host.ok())
        return 0;

    RoInitialize(RO_INIT_MULTITHREADED); // 系统的版本必须roinit

    // WCHAR env[65535];
    // GetEnvironmentVariableW(L"PATH", env, 65535);
    // auto newenv = std::wstring(env) + L";" + syspath1 + L";" + syspath2 + L";" + argv[5];
    // SetEnvironmentVariableW(L"PATH", newenv.c_str());
    SetDefaultDllDirectories(LOAD_LIBRARY_SEARCH_DEFAULT_DIRS);
    AddDllDirectory(argv[5]);
    AddDllDirectory(syspath1);
    AddDllDirectory(syspath2);

    auto config = EmbeddedSpeechConfig::FromPath(std::filesystem::path(argv[4]).string());
    std::string extra = WideStringToString(argv[6]);
    config->SetSpeechSynthesisOutputFormat(SpeechSynthesisOutputFormat::Riff24Khz16BitMonoPcm);
    config->SetProperty(PropertyId::SpeechServiceResponse_RequestSentenceBoundary, "true");
    config->SetProperty(PropertyId::SpeechServiceResponse_RequestPunctuationBoundary, "false");
    config->SetProperty(PropertyId::SpeechServiceConnection_SynthModelKey, extra.empty() ? parsekey(getkey()) : extra);
    auto synthesizer = SpeechSynthesizer::FromConfig(config, nullptr);
    wchar_t text[10000];
    while (true)
    {
        ZeroMemory(text, sizeof(text));
        if (!host.read(text, 10000 * 2))
            break;
        auto result = synthesizer->SpeakSsml(text);
        uint32_t len = 0;
        if (auto failed = CheckSynthesisResult(result))
        {
            len = -failed->ErrorDetails.size();
            memcpy(host.mem(), failed->ErrorDetails.c_str(), failed->ErrorDetails.size());
            host.write(&len, 4);
            continue;
        }
        auto stream = AudioDataStream::FromResult(result);
        while (auto got = stream->ReadData(len, (uint8_t *)host.mem() + len + sizeof(wav::Header), 1024 * 1024 * 16))
        {
            len += got;
        }
        {
            const uint16_t channels = 1, bits = 16, block_align = 2;
            const uint32_t sample_rate = 24000, byte_rate = 48000;
            auto header = wav::BuildHeader(static_cast<uint16_t>(WAVE_FORMAT_PCM), channels, sample_rate, byte_rate, block_align, bits, len);
            memcpy(host.mem(), header.data(), header.size());
            len += static_cast<uint32_t>(header.size());
        }
        host.write(&len, 4);
    }
    return 0;
}