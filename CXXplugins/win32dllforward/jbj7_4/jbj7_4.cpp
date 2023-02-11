// jbj7.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include<Windows.h>
#include <io.h>
#include <fcntl.h>

#define CODEPAGE_JA  932
#define CODEPAGE_GB  936 

#define CODEPAGE_BIG5 950


int wmain(int argc, wchar_t* argv[])
{
    HANDLE hPipe = CreateNamedPipe(argv[2], PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT
        , PIPE_UNLIMITED_INSTANCES, 0, 0, NMPWAIT_WAIT_FOREVER, 0);
    
    _setmode(_fileno(stdout), _O_U16TEXT);
    _setmode(_fileno(stdin), _O_U16TEXT);

    //system("chcp 932");
    HMODULE module = LoadLibraryW(argv[1]);
    typedef int(*_JC_Transfer_Unicode)(int, UINT, UINT, int, int, LPCWSTR, LPWSTR, int&, LPWSTR, int&);
    typedef int(__cdecl* _DJC_OpenAllUserDic_Unicode)(LPWSTR, int unknown);
    auto JC_Transfer_Unicode = (_JC_Transfer_Unicode)GetProcAddress(module, "JC_Transfer_Unicode");
    auto DJC_OpenAllUserDic_Unicode = (_DJC_OpenAllUserDic_Unicode)GetProcAddress(module, "DJC_OpenAllUserDic_Unicode");


    int USERDIC_PATH_SIZE = 0x204;
    int MAX_USERDIC_COUNT = 3;
    int USERDIC_BUFFER_SIZE = USERDIC_PATH_SIZE * MAX_USERDIC_COUNT;// 1548, sizeof(wchar_t)
    wchar_t cache[1548] = { 0 };
    for (int i = 4; i < argc; i++) {
        wcscpy(cache + (i - 4) * USERDIC_PATH_SIZE, argv[i]);
    }
    DJC_OpenAllUserDic_Unicode(cache, 0);
    wchar_t fr[3000] = { 0 };
    wchar_t to[3000] = { 0 };
    wchar_t buf[3000] = { 0 };
    wchar_t wcode[10] = { 0 };
    SECURITY_DESCRIPTOR sd = {};
    InitializeSecurityDescriptor(&sd, SECURITY_DESCRIPTOR_REVISION);
    SetSecurityDescriptorDacl(&sd, TRUE, NULL, FALSE);
    SECURITY_ATTRIBUTES allAccess = SECURITY_ATTRIBUTES{ sizeof(SECURITY_ATTRIBUTES), &sd, FALSE };
    SetEvent(CreateEvent(&allAccess, FALSE, FALSE, argv[3]));
    if (ConnectNamedPipe(hPipe, NULL) != NULL) {
        DWORD len = 0;

    }
    while (true) {
        memset(fr, 0, 3000 * sizeof(wchar_t));
        memset(to, 0, 3000 * sizeof(wchar_t));
        memset(buf, 0, 3000 * sizeof(wchar_t));
        memset(wcode, 0, 10 * sizeof(wchar_t));
        int a = 3000;
        int b = 3000;
        std::wcin.getline(wcode, 10);
        UINT code = _wtoi(wcode);
        std::wcin.getline(fr, 3000);
        JC_Transfer_Unicode(0, CODEPAGE_JA, code, 1, 1, fr, to, a, buf, b);
        //std::wcout << to << std::endl;
        wprintf(L"%s\n", to);
        //fflush(stdout);
        DWORD _;
        WriteFile(hPipe, to, 2*(wcslen(to)+1), &_, NULL);
    }

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
