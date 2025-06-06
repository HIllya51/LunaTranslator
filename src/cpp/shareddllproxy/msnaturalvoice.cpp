#ifndef WINXP
#include <roapi.h>
#else
#include "../xpundef/xp_winrt.hpp"
#endif
#include "../fileversion.hpp"
#include <speechapi_cxx.h>

using namespace Microsoft::CognitiveServices::Speech;
using namespace Microsoft::CognitiveServices::Speech::Audio;

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
std::string searchkey(const char *ff)
{
    FILE *f;
    fopen_s(&f, ff, "rb");
    if (!f)
        return "";
    fseek(f, 0, SEEK_END);
    auto len = ftell(f);
    fseek(f, 0, SEEK_SET);
    std::string s;
    s.resize(len);
    fread(s.data(), 1, len, f);
    auto p = s.find("Key:");
    if (p == s.npos)
        return "";
    return s.data() + p;
}
static std::string getkey()
{
    auto _ = searchkey(R"(C:\Windows\SystemApps\MicrosoftWindows.Client.Core_cw5n1h2txyewy\SpeechSynthesizerExtension.dll)");
    if (_.size())
        return _;
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

    HANDLE hPipe = CreateNamedPipe(argv[1], PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, PIPE_UNLIMITED_INSTANCES, 65535, 65535, NMPWAIT_WAIT_FOREVER, 0);

    auto handle = CreateFileMappingW(INVALID_HANDLE_VALUE, &allAccess, PAGE_EXECUTE_READWRITE, 0, 1024 * 1024 * 16, argv[3]);

    auto mapview = (char *)MapViewOfFile(handle, FILE_MAP_ALL_ACCESS | FILE_MAP_EXECUTE, 0, 0, 1024 * 1024 * 16);
    memset(mapview, 0, 1024 * 1024 * 16);

    SetEvent(CreateEvent(&allAccess, FALSE, FALSE, argv[2]));
    if (!ConnectNamedPipe(hPipe, NULL))
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

    auto config = EmbeddedSpeechConfig::FromPath(WideStringToString(argv[4], CP_ACP));

    config->SetSpeechSynthesisOutputFormat(SpeechSynthesisOutputFormat::Riff24Khz16BitMonoPcm);
    config->SetProperty(PropertyId::SpeechServiceResponse_RequestSentenceBoundary, "true");
    config->SetProperty(PropertyId::SpeechServiceResponse_RequestPunctuationBoundary, "false");
    config->SetSpeechSynthesisVoice(config->GetSpeechSynthesisVoiceName(), parsekey(getkey()));
    auto synthesizer = SpeechSynthesizer::FromConfig(config, nullptr);

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