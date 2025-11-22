#ifndef WINXP
#include <roapi.h>
#else
#include "../xpundef/xp_winrt.hpp"
#include "../xpundef/xp_other.hpp"
#endif

#include <speechapi_cxx.h>
#include "../NativeUtils/applicationloopbackaudio/LoopbackCapture.h"

using namespace Microsoft::CognitiveServices::Speech;
using namespace Microsoft::CognitiveServices::Speech::Audio;

const WCHAR syspath1[] = LR"(C:\Windows\SystemApps\MicrosoftWindows.Client.Core_cw5n1h2txyewy\LiveCaptions)";
const WCHAR syspath2[] = LR"(C:\Windows\SystemApps\MicrosoftWindows.Client.Core_cw5n1h2txyewy)";
std::string parsekey(std::string key);
static std::string getkey()
{
    return "\x4b\x65\x79\x3a\x58\x55\x77\x37\x43\x30\x72\x63\x5a\x41\x49\x51\x76\x47\x38\x33\x37\x59\x50\x34\x46\x31\x4b\x48\x7a\x32\x52\x71\x59\x75\x51\x67\x74\x79\x58\x72\x63\x62\x46\x68\x73\x57\x46\x4e\x47\x6a\x47\x30\x38\x48\x4a\x45\x6c\x6d\x50\x47\x65\x73\x78\x4e\x4d\x62\x69\x62\x30\x73\x38\x79\x33\x39\x4e\x45\x74\x69\x33\x71\x33\x52\x77\x50\x4e\x52\x62\x75\x44\x76\x37\x35\x65\x6a\x5a\x62\x54\x61\x39\x79\x4c\x63\x54\x41\x55\x69\x78\x43";
}
int mssr(int argc, wchar_t *argv[])
{

    HANDLE hPipe = CreateNamedPipe(argv[1], PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, PIPE_UNLIMITED_INSTANCES, 65535, 65535, NMPWAIT_WAIT_FOREVER, 0);

    SetEvent(CreateEvent(&allAccess, FALSE, FALSE, argv[2]));
    if (!ConnectNamedPipe(hPipe, NULL))
        return 0;

    RoInitialize(RO_INIT_MULTITHREADED); // 系统的版本必须roinit

    // WCHAR env[65535];
    // GetEnvironmentVariableW(L"PATH", env, 65535);
    // auto newenv = std::wstring(env) + L";" + syspath1 + L";" + syspath2 + L";" + argv[6];
    // SetEnvironmentVariableW(L"PATH", newenv.c_str());
    SetDefaultDllDirectories(LOAD_LIBRARY_SEARCH_DEFAULT_DIRS);
    AddDllDirectory(argv[6]);
    AddDllDirectory(syspath1);
    AddDllDirectory(syspath2);
    std::string extra = WideStringToString(argv[7]);
    auto config = EmbeddedSpeechConfig::FromPath(WideStringToString(argv[4], CP_ACP));

    for (auto &m : config->GetSpeechRecognitionModels())
    {
        config->SetSpeechRecognitionModel(m->Name, extra.empty() ? parsekey(getkey()) : extra);
    }
    config->SetProfanity(ProfanityOption::Raw);
    CEvent recognitionEnd{FALSE, FALSE};
    std::mutex writelock;
    auto create_recognizer = [&](auto audioConfig, auto callback)
    {
        auto recognizer = SpeechRecognizer::FromConfig(config, audioConfig);

        // promise for synchronization of recognition end.

        // Subscribes to events.
        recognizer->Recognizing.Connect([&](const SpeechRecognitionEventArgs &e)
                                        { callback(false, e.Result); });
        auto Recognized = [&](const SpeechRecognitionEventArgs &e)
        {
            switch (e.Result->Reason)
            {
            case ResultReason::RecognizedSpeech:
                callback(true, e.Result);
                break;
            }
        };
        recognizer->Recognized.Connect(Recognized);
        auto Canceled = [&](const SpeechRecognitionCanceledEventArgs &e)
        {
            switch (e.Reason)
            {
            case CancellationReason::EndOfStream:
                break;

            case CancellationReason::Error:

                callback(true, std::exception{e.ErrorDetails.c_str()});
                recognitionEnd.Set();
                break;
            }
        };
        recognizer->Canceled.Connect(Canceled);

        recognizer->SessionStarted.Connect([&](const SessionEventArgs &e) {});

        recognizer->SessionStopped.Connect([&](const SessionEventArgs &e)
                                           { recognitionEnd.Set();  callback(true, 3); });

        return recognizer;
    };
    auto callback = [&](bool ok, std::variant<const std::shared_ptr<SpeechRecognitionResult>, const std::exception, int> result)
    {
        std::unique_lock __(writelock);
        if (auto *ext = std::get_if<const std::exception>(&result))
        {
            DWORD _;
            int __1 = 1;
            WriteFile(hPipe, &__1, 4, &_, NULL);
            std::string err = ext->what();
            __1 = err.size();
            WriteFile(hPipe, &__1, 4, &_, NULL);
            WriteFile(hPipe, err.c_str(), err.size(), &_, NULL);
        }
        else if (auto *str = std::get_if<int>(&result))
        {
            DWORD _;
            int __1 = 0;
            WriteFile(hPipe, &__1, 4, &_, NULL);
            WriteFile(hPipe, str, 4, &_, NULL);
        }
        else if (auto *res = std::get_if<const std::shared_ptr<SpeechRecognitionResult>>(&result))
        {
            DWORD _;
            int __1 = 0;
            WriteFile(hPipe, &__1, 4, &_, NULL);
            __1 = 0;
            WriteFile(hPipe, &__1, 4, &_, NULL);
            __1 = ok;
            WriteFile(hPipe, &__1, 4, &_, NULL);
            __1 = (*res)->Offset();
            WriteFile(hPipe, &__1, 4, &_, NULL);
            __1 = (*res)->Duration();
            WriteFile(hPipe, &__1, 4, &_, NULL);
            __1 = (*res)->Text.size();
            WriteFile(hPipe, &__1, 4, &_, NULL);
            WriteFile(hPipe, (*res)->Text.c_str(), (*res)->Text.size(), &_, NULL);
        }
    };
    try
    {
        std::shared_ptr<AudioConfig> audioConfig;
        CComPtr<CLoopbackCapture> capture;
        // Creates a push stream
        std::shared_ptr<PushAudioInputStream> pushStream;

        if (wcscmp(argv[5], L"loopback") == 0)
        {
            capture = new CLoopbackCapture{16000, 16, 1};
            if (!capture)
                throw std::runtime_error("??");
            pushStream = AudioInputStream::CreatePushStream();
            capture->OnDataCallback = [&](std::string &&data)
            {
                pushStream->Write((uint8_t *)data.data(), data.size());
            };
            // Creates a speech recognizer from stream input;
            audioConfig = AudioConfig::FromStreamInput(pushStream);
        }
        else if (argv[5][0] == L'i')
        {
            audioConfig = (wcscmp(argv[5], L"i") == 0) ? AudioConfig::FromDefaultMicrophoneInput() : AudioConfig::FromMicrophoneInput(WideStringToString(argv[5] + 1));
        }
        else if (argv[5][0] == L'o')
        {
            audioConfig = (wcscmp(argv[5], L"o") == 0) ? AudioConfig::FromDefaultSpeakerOutput() : AudioConfig::FromSpeakerOutput(WideStringToString(argv[5] + 1));
        }
        callback(true, 4);
        auto recognizer = create_recognizer(audioConfig, callback);
        callback(true, 1);
        // Starts continuous recognition. Uses StopContinuousRecognitionAsync() to stop recognition.
        do
        {
            int action;
            DWORD _;
            recognitionEnd.Reset();
            WaitForSingleObject(CreateEvent(&allAccess, FALSE, FALSE, argv[3]), INFINITE);
            recognizer->StartContinuousRecognitionAsync().wait();
            if (capture)
            {
                auto hr = capture->StartCaptureAsync(GetCurrentProcessId(), false);
                if (FAILED(hr))
                    throw std::runtime_error(std::string("??") + std::to_string((DWORD)hr));
            }
            WaitForSingleObject(CreateEvent(&allAccess, FALSE, FALSE, argv[3]), INFINITE);
            // Stops recognition.
            if (capture)
                capture->StopCaptureAsync();
            recognizer->StopContinuousRecognitionAsync().get();
            WaitForSingleObject(recognitionEnd, INFINITE);
        } while (true);
    }
    catch (std::exception &e)
    {
        callback(true, e);
    }
    return 0;
}