// win32dllforward.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <iostream>
#include<Windows.h>  
#include<string>
#include <io.h>
#include <fcntl.h>
#include<locale.h>
extern "C" { 
    typedef int(__stdcall* MTInitCJ)(int);
    typedef int(__stdcall* TranTextFlowCJ)(char* src,char* dest,int,int); 
}



int wmain(int argc, wchar_t* argv[])
{ 
    
    SetCurrentDirectory(argv[1]);
    HMODULE h = LoadLibrary(argv[2]);
    
    if (h) {
        MTInitCJ _MTInitCJ = (MTInitCJ)::GetProcAddress(h, "MTInitCJ");
        TranTextFlowCJ _TranTextFlowCJ = (TranTextFlowCJ)::GetProcAddress(h, "TranTextFlowCJ"); 
        _MTInitCJ(10);

        char buffer[3000]={0};
        char src[3000] = { 0 }; 
        for (int i = 3; i < argc; i += 1) {
            int tmp;
            swscanf_s(argv[i],L"%d", &tmp);
            src[i-3] = tmp;
             
        }
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
        _TranTextFlowCJ(src, buffer, 3000, 10);
        for (int i = 0; i < 500; i += 1) {
            printf("%d ", (unsigned char)buffer[i]);
        }
        printf("\n");
        fflush(stdout);

    }
    return 0;
}