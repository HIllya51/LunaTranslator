
#include "ebyroid.h"
#include "api_adapter.h"
#include "ebyutil.h"
using ebyroid::Ebyroid;
#include "types.h"

int voiceroid2wmain(int argc, wchar_t *wargv[])
{

    char **argv = new char *[argc];
    for (int i = 0; i < argc; i++)
    {
        int length = WideCharToMultiByte(CP_ACP, 0, wargv[i], -1, NULL, 0, NULL, NULL);
        argv[i] = new char[length];
        WideCharToMultiByte(CP_ACP, 0, wargv[i], -1, argv[i], length, NULL, NULL);
    }
    HANDLE hPipe = CreateNamedPipeA(argv[3], PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, PIPE_UNLIMITED_INSTANCES, 65535, 65535, NMPWAIT_WAIT_FOREVER, 0);

    Ebyroid *ebyroid = nullptr;

    std::string last;
    float rate = -1;
    auto handle = CreateFileMappingA(INVALID_HANDLE_VALUE, &allAccess, PAGE_EXECUTE_READWRITE, 0, 1024 * 1024 * 10, argv[5]);

    auto mapview = (char *)MapViewOfFile(handle, FILE_MAP_ALL_ACCESS | FILE_MAP_EXECUTE, 0, 0, 1024 * 1024 * 10);
    memset(mapview, 0, 1024 * 1024 * 10);
    SetEvent(CreateEventA(&allAccess, FALSE, FALSE, argv[4]));
    ConnectNamedPipe(hPipe, NULL);
    int freq1;
    unsigned char input_j[4096] = {0};
    DWORD _;
    while (true)
    {
        ZeroMemory(input_j, sizeof(input_j));
        unsigned char *out;
        size_t output_size;
        int16_t *out2;

        if (!ReadFile(hPipe, input_j, 4096, &_, NULL))
            break;
        std::string voice = (char *)input_j;
        float _rate;
        if (!ReadFile(hPipe, &_rate, 4, &_, NULL))
            break;
        if ((voice != last) || (rate != _rate))
        {
            last = voice;
            rate = _rate;
            if (ebyroid)
            {
                delete ebyroid;
            }
            ebyroid = Ebyroid::Create((const char *)argv[1], //"C:\\dataH\\Yukari2",
                                      (const char *)argv[2],
                                      voice.c_str(),
                                      2,
                                      rate); // 1); //0.1-2,0.5-4
        }

        ZeroMemory(input_j, sizeof(input_j));
        if (!ReadFile(hPipe, input_j, 4096, &_, NULL))
            break;
        if (voice.find("_44") != voice.npos)
            freq1 = 44100;
        else
            freq1 = 22050;
        // int result = ebyroid->Hiragana((const unsigned char*)UnicodeToShift_jis(input), &out, &output_size);
        int result = ebyroid->Hiragana((const unsigned char *)input_j, &out, &output_size);

        result = ebyroid->Speech(out, &out2, &output_size);
        int fsize = output_size + 44;
        if (fsize > 1024 * 1024 * 10)
        {
            fsize = 0;
        }
        else
        {

            int ptr = 0;
            memcpy(mapview, "RIFF", 4);
            ptr += 4;
            memcpy(mapview + ptr, &fsize, 4);
            ptr += 4;
            memcpy(mapview + ptr, "WAVEfmt ", 8);
            ptr += 8;
            memcpy(mapview + ptr, "\x10\x00\x00\x00\x01\x00\x01\x00", 8);
            ptr += 8;
            int freq = freq1;
            memcpy(mapview + ptr, &freq, 4);
            ptr += 4;
            freq = freq * 2;
            memcpy(mapview + ptr, &freq, 4);
            ptr += 4;
            memcpy(mapview + ptr, "\x02\x00\x10\x00", 4);
            ptr += 4;
            memcpy(mapview + ptr, "data", 4);
            ptr += 4;
            memcpy(mapview + ptr, &output_size, 4);
            ptr += 4;
            memcpy(mapview + ptr, out2, output_size);
        }
        WriteFile(hPipe, &fsize, 4, &_, NULL);

        free(out);
        free(out2);
    }
    return 0;
}
