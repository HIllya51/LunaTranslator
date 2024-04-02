
#include "ebyroid.h"
#include <Windows.h>
#include "api_adapter.h"
#include "ebyutil.h"
#include <io.h>
#include <fcntl.h>
using ebyroid::Ebyroid;
#include "types.h"
#pragma comment(lib, "winmm.lib")

int voiceroid2wmain(int argc, wchar_t *wargv[])
{
    UINT codepage = GetACP();

    char **argv = new char *[argc];
    for (int i = 0; i < argc; i++)
    {
        int length = WideCharToMultiByte(codepage, 0, wargv[i], -1, NULL, 0, NULL, NULL);
        argv[i] = new char[length];
        WideCharToMultiByte(codepage, 0, wargv[i], -1, argv[i], length, NULL, NULL);
    }

    HANDLE hPipe = CreateNamedPipeA(argv[7], PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, PIPE_UNLIMITED_INSTANCES, 65535, 65535, NMPWAIT_WAIT_FOREVER, 0);

    Ebyroid *ebyroid;

    printf("argc %d \n", argc);
    for (int i = 0; i < argc; i++)
    {
        printf("%d %s\n", i, argv[i]);
    }
    ebyroid = Ebyroid::Create((const char *)argv[1], //"C:\\dataH\\Yukari2",
                              (const char *)argv[2],
                              (const char *)argv[3],        //"yukari_emo_44",
                              2,                            // �̶��������
                              atof((const char *)argv[5])); // 1); //0.1-2,0.5-4
    SECURITY_DESCRIPTOR sd = {};
    InitializeSecurityDescriptor(&sd, SECURITY_DESCRIPTOR_REVISION);
    SetSecurityDescriptorDacl(&sd, TRUE, NULL, FALSE);
    SECURITY_ATTRIBUTES allAccess = SECURITY_ATTRIBUTES{sizeof(SECURITY_ATTRIBUTES), &sd, FALSE};
    SetEvent(CreateEventA(&allAccess, FALSE, FALSE, argv[8]));
    if (ConnectNamedPipe(hPipe, NULL) != NULL)
    {
        DWORD len = 0;
    }
    int freq1 = atoi(argv[4]);
    printf("pipe connected");
    int II = 0;
    while (true)
    {
        II += 1;
        unsigned char *out;
        size_t output_size;
        int16_t *out2;

        unsigned char input_j[4096] = {0};
        DWORD _;
        if (!ReadFile(hPipe, input_j, 4096, &_, NULL))
            break;

        printf("%s\n", input_j);
        // int result = ebyroid->Hiragana((const unsigned char*)UnicodeToShift_jis(input), &out, &output_size);
        int result = ebyroid->Hiragana((const unsigned char *)input_j, &out, &output_size);

        printf("%s\n", out);
        result = ebyroid->Speech(out, &out2, &output_size);
        char newname[1024] = {0};
        sprintf(newname, "%s%d.wav", argv[6], II);
        FILE *F = fopen(newname, "wb");

        int fsize = output_size + 44;
        fseek(F, 0, SEEK_SET);
        fwrite("RIFF", 1, 4, F);
        fwrite(&fsize, 4, 1, F);
        fwrite("WAVEfmt ", 1, 8, F);
        fwrite("\x10\x00\x00\x00\x01\x00\x01\x00", 1, 8, F);
        int freq = freq1;
        fwrite(&freq, 4, 1, F);
        freq = freq * 2;
        fwrite(&freq, 4, 1, F);
        fwrite("\x02\x00\x10\x00", 1, 4, F);
        fwrite("data", 1, 4, F);
        int sz = fsize - 44;
        fwrite(&sz, 4, 1, F);
        printf("%d \n", ftell(F));
        fwrite((char *)out2, 1, output_size, F);
        fclose(F);
        WriteFile(hPipe, newname, strlen(newname), &_, NULL);
        free(out);
        free(out2);
    }
    // sndPlaySound((const char*)argv[6], SND_SYNC);
    return 0;
}
