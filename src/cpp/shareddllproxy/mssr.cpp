#ifndef WINXP
#include <roapi.h>
#else
#include "../xpundef/xp_winrt.hpp"
#endif

#include <speechapi_cxx.h>
#include "../NativeUtils/applicationloopbackaudio/LoopbackCapture.h"

using namespace Microsoft::CognitiveServices::Speech;
using namespace Microsoft::CognitiveServices::Speech::Audio;

constexpr inline const char MS_SR_KEY[] = "Key:XUw7C0rcZAIQvG837YP4F1KHz2RqYuQgtyXrcbFhsWFNGjG08HJElmPGesxNMbib0s8y39NEti3q3RwPNRbuDv75ejZbTa9yLcTAUixC";
const WCHAR syspath1[] = LR"(C:\Windows\SystemApps\MicrosoftWindows.Client.Core_cw5n1h2txyewy\LiveCaptions)";
const WCHAR syspath2[] = LR"(C:\Windows\SystemApps\MicrosoftWindows.Client.Core_cw5n1h2txyewy)";

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

    auto config = EmbeddedSpeechConfig::FromPath(WideStringToString(argv[4], CP_ACP));

    for (auto &m : config->GetSpeechRecognitionModels())
    {
        config->SetSpeechRecognitionModel(m->Name, MS_SR_KEY);
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
                throw std::runtime_error("Not Support");
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
                if (FAILED(capture->StartCaptureAsync(GetCurrentProcessId(), false)))
                    throw std::runtime_error("Not Support");
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