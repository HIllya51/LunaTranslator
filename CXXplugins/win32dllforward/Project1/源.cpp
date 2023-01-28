// win32dllforward.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include<Windows.h>  
#include <iostream>
#include<string> 
extern "C" {
    typedef int(__stdcall* MTInitCJ)(int);
    typedef int(__stdcall* TranTextFlowCJ)(char* src, char* dest, int, int);
}
std::string WStrToStr(wchar_t* xx, UINT uCodePage)
{
    std::wstring wstrString = xx;
    int lenStr = 0;
    std::string result;

    lenStr = WideCharToMultiByte(uCodePage, NULL, wstrString.c_str(), wstrString.size(), NULL, NULL, NULL, NULL);
    char* buffer = new char[lenStr + 1];
    WideCharToMultiByte(uCodePage, NULL, wstrString.c_str(), wstrString.size(), buffer, lenStr, NULL, NULL);
    buffer[lenStr] = '\0';

    result.append(buffer);
    delete[] buffer;
    return result;
}


int wmain(int argc, wchar_t* argv[])
{

    SetCurrentDirectory(L"C:\\dataH\\DR.eye\\DreyeMT\\SDK\\bin");
    SetDllDirectory(L"C:\\dataH\\DR.eye\\DreyeMT\\SDK\\bin");
    HMODULE h = LoadLibrary(L"C:\\dataH\\DR.eye\\DreyeMT\\SDK\\bin\\TransCOMEC.dll");
    /*wchar_t* apiinit = argv[3];
    wchar_t* apitrans = argv[4];*/
    if (h) {


        MTInitCJ _MTInitCJ;
        TranTextFlowCJ _TranTextFlowCJ;
         
            _MTInitCJ = (MTInitCJ)GetProcAddress(h, "MTInitEC");// WStrToStr(apiinit, 936).c_str());
            _TranTextFlowCJ = (TranTextFlowCJ)GetProcAddress(h, "TranTextFlowEC");// WStrToStr(apitrans, 936).c_str());
        
            
        printf("%d\n",_MTInitCJ(1));
        char buffer[3000] = { 0 };
        char src[3000] = "happy";
        printf("%s\n", src);
        /*while (true) {
            int tmp;
            scanf_s("%d", &tmp);

            if (tmp != 999) {
                src[i] = tmp;
            }
            else {
                break;
            }
            i += 1;

        }*/
        //char src[3000] = "おはよう"; //{ 0x82, 0xa8, 0x82, 0xcd, 0x82, 0xe6, 0x82, 0xa4 };

        _TranTextFlowCJ(src, buffer, 3000,1);
        printf("xxxx\n");
      
        printf("%s\n", buffer);
        for (int i = 0; i < 500; i += 1) {
            printf("%d ", (unsigned char)buffer[i]);
        }
        printf("\n");
        fflush(stdout);

    }
    return 0;
}