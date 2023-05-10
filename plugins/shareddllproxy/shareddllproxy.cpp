// shared32dllproxy.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//
#include<Windows.h>
#include <iostream>
#include"define.h"
#include<string>
#pragma comment( linker, "/subsystem:windows /entry:wmainCRTStartup" )
int wmain(int argc, wchar_t* argv[])
{
    auto argv0 = std::wstring(argv[1]);
    if (argv0 == L"dllinject")
        return dllinjectwmain(argc - 1, argv + 1);
#ifndef _WIN64
    else if (argv0 == L"le")
        return lewmain(argc - 1, argv + 1);
    else if (argv0 == L"jbj7")
        return jbjwmain(argc - 1, argv + 1);
    else if (argv0 == L"dreye")
        return dreyewmain(argc - 1, argv + 1);
    else if (argv0 == L"kingsoft")
        return kingsoftwmain(argc - 1, argv + 1);
    else if (argv0 == L"voiceroid2")
        return voiceroid2wmain(argc - 1, argv + 1);
#else
    else if (argv0 == L"magpie")
        return magpiewmain(argc - 1, argv + 1);
#endif // !_WIN64

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
