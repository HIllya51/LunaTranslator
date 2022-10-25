
#include "ebyroid.h"
#include<Windows.h>
#include"api_adapter.h"
#include "ebyutil.h"
#include <io.h>
#include <fcntl.h>
using ebyroid::Ebyroid; 
#include"types.h"
#pragma comment(lib,"winmm.lib")
int main(int argc,char *argv[]) { 
	Ebyroid* ebyroid;
    printf("%d \n", argc);
    printf("%s \n", argv[0]);
    printf("%s \n", argv[1]);
    printf("%s \n", argv[2]);
    printf("%s \n", argv[3]);
    printf("%s \n", argv[4]);
    printf("%s \n", argv[5]);
    printf("%s \n", argv[6]);

    ebyroid = Ebyroid::Create((const char*)argv[1],//"C:\\dataH\\Yukari2",
        //(const char*)argv[2],
        "C:\\Users\\11737\\Documents\\GitHub\\LunaTranslator\\LunaTranslator\\files\\voiceroid2\\aitalked.dll", 
        (const char*)argv[3],//"yukari_emo_44",
        2,//atof((const char*)argv[4]),// 2, 
        atof((const char*)argv[5]));//1); //0.1-2,0.5-4


    unsigned char* out; 
    size_t output_size;
    int16_t* out2;
    wchar_t input[4096];
    unsigned char input_j[4096] = { 0 };
    printf("%d\n", argc);
    if (argc - 7 > 4096) {
        return 0;
    }
    else {
        for (int i = 7; i < argc; i += 1) {
            printf("%s ", argv[i]);
            input_j[i - 7] = atoi((const char*)argv[i]);
            
        }
    }
    printf("%s\n", input_j);
    //int result = ebyroid->Hiragana((const unsigned char*)UnicodeToShift_jis(input), &out, &output_size);
    int result = ebyroid->Hiragana((const unsigned char*)input_j, &out, &output_size);

    printf("%s\n", out);
    result = ebyroid->Speech(out, &out2, &output_size); 

    FILE* F = fopen((const char*)argv[6]//"C:\\Users\\11737\\source\\repos\\voice2\\Release\\1.wav"
        , "wb");
     
   
    int fsize = output_size+44;
    fseek(F, 0,SEEK_SET);
    fwrite("RIFF", 1, 4, F);
    fwrite(&fsize, 4, 1, F);
    fwrite("WAVEfmt ", 1, 8, F);
    fwrite( "\x10\x00\x00\x00\x01\x00\x01\x00", 1, 8, F);
    int freq = 44100;
    fwrite(&freq, 4, 1, F);
    freq = freq *2;
    fwrite(&freq, 4, 1, F);
    fwrite("\x02\x00\x10\x00", 1, 4, F);
    fwrite("data", 1,4, F);
    int sz = fsize - 44;
    fwrite(&sz, 4, 1, F);
    printf("%d \n", ftell(F));
    fwrite((char*)out2, 1, output_size, F);
    fclose(F);
    sndPlaySound((const char*)argv[6], SND_SYNC);
    return 0;
}
