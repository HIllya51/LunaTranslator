
#include "ebyroid.h"
#include<Windows.h>
#include"api_adapter.h"
#include "ebyutil.h"
#include <io.h>
#include <fcntl.h>
using ebyroid::Ebyroid; 
#include"types.h"
#pragma comment(lib,"winmm.lib")

#pragma comment( linker, "/subsystem:windows /entry:mainCRTStartup" )
int main(int argc,char *argv[]) { 
    HANDLE hPipe = CreateNamedPipe(argv[7], PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT
        , PIPE_UNLIMITED_INSTANCES, 65535, 65535, NMPWAIT_WAIT_FOREVER, 0);

	Ebyroid* ebyroid;

    printf("argc %d \n", argc);
    printf("argv %s \n", argv[0]);
    printf("argv %s \n", argv[1]);
    printf("argv %s \n", argv[2]);
    printf("argv %s \n", argv[3]);
    printf("argv %s \n", argv[4]);
    printf("argv %s \n", argv[5]);
    printf("argv %s \n", argv[6]);
    printf("argv %s \n", argv[7]);
    printf("argv %s \n", argv[8]);
    ebyroid = Ebyroid::Create((const char*)argv[1],//"C:\\dataH\\Yukari2",
        (const char*)argv[2],
        //"C:\\Users\\11737\\Documents\\GitHub\\LunaTranslator\\LunaTranslator\\files\\voiceroid2\\aitalked.dll", 
        (const char*)argv[3],//"yukari_emo_44",
        2,//atof((const char*)argv[4]),// 2, 
        atof((const char*)argv[5]));//1); //0.1-2,0.5-4
    SECURITY_DESCRIPTOR sd = {};
    InitializeSecurityDescriptor(&sd, SECURITY_DESCRIPTOR_REVISION);
    SetSecurityDescriptorDacl(&sd, TRUE, NULL, FALSE);
    SECURITY_ATTRIBUTES allAccess = SECURITY_ATTRIBUTES{ sizeof(SECURITY_ATTRIBUTES), &sd, FALSE };
    SetEvent(CreateEvent(&allAccess, FALSE, FALSE, argv[8]));
    if (ConnectNamedPipe(hPipe, NULL) != NULL) {
        DWORD len = 0;

    }
    printf("pipe connected");
    int II = 0;
    while (true) {
        II += 1;
        unsigned char* out;
        size_t output_size;
        int16_t* out2;

        unsigned char input_j[4096] = { 0 };
        DWORD _;
        if(!ReadFile(hPipe, input_j,4096, &_, NULL))break;
         
        printf("%s\n", input_j);
        //int result = ebyroid->Hiragana((const unsigned char*)UnicodeToShift_jis(input), &out, &output_size);
        int result = ebyroid->Hiragana((const unsigned char*)input_j, &out, &output_size);

        printf("%s\n", out);
        result = ebyroid->Speech(out, &out2, &output_size);
        char newname[1024] = { 0 };
        sprintf(newname, "%s%d.wav", argv[6], II);
        FILE* F = fopen(newname//"C:\\Users\\11737\\source\\repos\\voice2\\Release\\1.wav"
            , "wb");


        int fsize = output_size + 44;
        fseek(F, 0, SEEK_SET);
        fwrite("RIFF", 1, 4, F);
        fwrite(&fsize, 4, 1, F);
        fwrite("WAVEfmt ", 1, 8, F);
        fwrite("\x10\x00\x00\x00\x01\x00\x01\x00", 1, 8, F);
        int freq = 44100;
        fwrite(&freq, 4, 1, F);
        freq = freq * 2;
        fwrite(&freq, 4, 1, F);
        fwrite("\x02\x00\x10\x00", 1, 4, F);
        fwrite("data", 1, 4, F);
        int sz = fsize - 44;
        fwrite(&sz, 4, 1, F);
        printf("%d \n", ftell(F));
        fwrite((char*)out2, 1, output_size, F);
        fclose(F);
        WriteFile(hPipe, newname, strlen(newname), &_, NULL);
        free(out);
        free(out2);
    }
    //sndPlaySound((const char*)argv[6], SND_SYNC);
    return 0;
}
