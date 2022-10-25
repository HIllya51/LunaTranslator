// win32dllforward.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <iostream>
#include<Windows.h>  
#include<string>
#include <io.h>
#include <fcntl.h>
#define CODEPAGE_JA  932
#define CODEPAGE_GB  936 

#define CODEPAGE_BIG5 950
 
int wmain(int argc, wchar_t* argv[])
{ 
    //_setmode(_fileno(stdout), _O_U16TEXT);
    //setlocale(LC_CTYPE, "");
    //wprintf(argv[1]);
    HMODULE module = LoadLibrary(argv[1]);


    typedef int(*JC_Transfer_Unicode)(int, UINT , UINT, int, int, LPCWSTR, LPWSTR, int&, LPWSTR, int& );
    if (module == 0) {
        return 0;
    }
    UINT code;
    /*if (argv[2][0] == '0') {
        code = CODEPAGE_GB;
    }
    else {
        code = CODEPAGE_BIG5;
    }*/
    code = CODEPAGE_GB;
    JC_Transfer_Unicode _JC_Transfer_Unicode = (JC_Transfer_Unicode)GetProcAddress(module, "JC_Transfer_Unicode");
    std::wstring ss = L"";
    for (int j = 2; j < argc; j++) {
        ss.append(argv[j]);
        ss.append(L" ");
    }
    LPCWSTR fr =ss.c_str();

    //LPCWSTR fr= argv[2];
     
    wchar_t to[3000]={0};
    wchar_t buf[3000] = { 0 };
    int a = 3000;
    int b = 3000;

    _JC_Transfer_Unicode(0, CODEPAGE_JA, code, 1, 1, fr,  to, a,  buf, b);
     

    //wprintf(L"%s\n", to);
    for (int i = 0; i < 500; i += 1) {
        printf("%d ", (wchar_t)to[i]);
    }
    printf("\n");
    fflush(stdout);
}

// 运行程序: Ctrl + F5 或调试 >“开始执行(不调试)”菜单
// 调试程序: F5 或调试 >“开始调试”菜单

// 入门使用技巧: 
//   1. 使用解决方案资源管理器窗口添加/管理文件
//   2. 使用团队资源管理器窗口连接到源代码管理
//   3. 使用输出窗口查看生成输出和其他消息
//   4. 使用错误列表窗口查看错误
//   5. 转到“项目”>“添加新项”以创建新的代码文件，或转到“项目”>“添加现有项”以将现有代码文件添加到项目
//   6. 将来，若要再次打开此项目，请转到“文件”>“打开”>“项目”并选择 .sln 文件
