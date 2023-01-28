// win32dllforward.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <iostream>
#include<Windows.h>  
#include<string>
#include <io.h>
#include <fcntl.h>
 
 
extern "C" {
    typedef DWORD(__stdcall* StartSession)(wchar_t* path, void* bufferStart, void* bufferStop, const wchar_t* app);
    typedef DWORD(__stdcall* OpenEngine)(int key);
    typedef DWORD(__stdcall* SimpleTransSentM)(int key, const wchar_t* fr, wchar_t* t, int, int);
    typedef DWORD(__stdcall* SetBasicDictPathW)(int key, const wchar_t* fr);
}

int wmain(int argc, wchar_t* argv[])
{
    //_setmode(_fileno(stdout), _O_U16TEXT);
    //wchar_t path[] = L"C:\\dataH\\金山快译.2009.专业版\\FastAIT09_Setup.25269.4101\\GTS\\JapaneseSChinese\\DCT";
    wchar_t *path  = argv[2];
    HMODULE h =  LoadLibrary(argv[1]);
    enum { key = 0x4f4 };
    if (h) {
        StartSession startSession = (StartSession)::GetProcAddress(h, "StartSession");
        OpenEngine openEngine = (OpenEngine)::GetProcAddress(h, "OpenEngine");
        SimpleTransSentM simpleTransSentM = (SimpleTransSentM)::GetProcAddress(h, "SimpleTransSentM");
        SetBasicDictPathW setBasicDictPathW = (SetBasicDictPathW)::GetProcAddress(h, "SetBasicDictPathW");

        enum { bufferSize = key };
        char buffer[bufferSize];

        int ret = startSession(path, buffer, buffer + bufferSize, L"DCT");

        ret = openEngine(key);
        ret = setBasicDictPathW(key, path);

        wchar_t *fr= argv[3];
        wchar_t to[0x400] = {};
        ret = simpleTransSentM(key, fr, to, 0x28, 0x4);

       // wprintf(L"%s\n", to);
        for (int i = 0; i < 500; i += 1) {
            printf("%d ", (wchar_t)to[i]);
        }
        printf("\n");
        fflush(stdout);
    }
    return 0;
}