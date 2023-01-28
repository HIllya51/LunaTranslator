// win32dllforward.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <iostream>
#include<Windows.h>  
#include<string>
#include <io.h>
#include <fcntl.h>
#include <codecvt>
#include <locale>
extern "C" {
    typedef DWORD(__stdcall* MTInitCJ)(int);
    typedef DWORD(__stdcall* TranTextFlowCJ)(char*, char*,int,int);
}
const int EC_DAT = 1;   //英中
const int CE_DAT = 2;   //中英
const int CJ_DAT = 3;   //中日
const int JC_DAT = 10;  //日中
std::string StringToUTF8(const std::string& gbkData)
{
    const char* GBK_LOCALE_NAME = "CHS";  //GBK在windows下的locale name(.936, CHS ), linux下的locale名可能是"zh_CN.GBK"

    std::wstring_convert<std::codecvt<wchar_t, char, mbstate_t>>
        conv(new std::codecvt<wchar_t, char, mbstate_t>(GBK_LOCALE_NAME));
    std::wstring wString = conv.from_bytes(gbkData);    // string => wstring

    std::wstring_convert<std::codecvt_utf8<wchar_t>> convert;
    std::string utf8str = convert.to_bytes(wString);     // wstring => utf-8

    return utf8str;
}  
int main(int argc, char* argv[])
{ 
    setlocale(LC_ALL, "");
    wchar_t path[] = L"C:/dataH/DR.eye/DreyeMT/SDK/bin/TransCOM.dll";
   //HMODULE h = LoadLibrary(argv[1]);
    HMODULE h = LoadLibrary(path); 
    if (h) { 
        SetCurrentDirectory(L"C:/dataH/DR.eye/DreyeMT/SDK/bin/");
        MTInitCJ _MTInitCJ = (MTInitCJ)::GetProcAddress(h, "MTInitCJ");
        TranTextFlowCJ _TranTextFlowCJ = (TranTextFlowCJ)::GetProcAddress(h, "TranTextFlowCJ"); 
         

        int ret = _MTInitCJ(JC_DAT);
         
        char to[3000] = {};
        char src[] = "おはようございます";
        
        _TranTextFlowCJ(src, to, 3000, JC_DAT);
      //  setlocale(LC_ALL, "zh_CN.GBK");
        FILE  *f;
        fopen_s(&f,"1.txt", "w");

        printf("%d\n", f);
        fwrite(to, strlen(to), 1,f);
        fclose(f);
        printf("%s\n", to); 
        std::string gbkstr = StringToUTF8(to);
        printf("%s\n", gbkstr.c_str());
        fflush(stdout);
    }
    return 0;
}