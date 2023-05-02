// dllinject32.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//
#pragma comment( linker, "/subsystem:windows /entry:wmainCRTStartup" )

#include <iostream>
#include<Windows.h>
int wmain(int argc,wchar_t*argv[])
{


    auto PROCESS_INJECT_ACCESS = (
        PROCESS_CREATE_THREAD |
        PROCESS_QUERY_INFORMATION |
        PROCESS_VM_OPERATION |
        PROCESS_VM_WRITE |
        PROCESS_VM_READ);
    auto pid = _wtoi(argv[1]);
    auto hProcess = OpenProcess(PROCESS_INJECT_ACCESS, 0, pid);
    if (hProcess == 0)return 1;
    for (int i = 2; i < argc; i += 1) {
        auto size = (wcslen(argv[i]) + 1) * sizeof(wchar_t);
        auto remoteData=VirtualAllocEx(hProcess,
            nullptr,
            size,
            MEM_RESERVE | MEM_COMMIT,
            PAGE_READWRITE
        );
        if (remoteData == 0)break;
        WriteProcessMemory(hProcess, remoteData, argv[i], size, 0);
        auto hThread=CreateRemoteThread(hProcess, 0, 0, (LPTHREAD_START_ROUTINE)LoadLibraryW, remoteData, 0, 0);
        if (hThread == 0) break;
        WaitForSingleObject(hThread, 10000);
        CloseHandle(hThread);
        VirtualFreeEx(hProcess, remoteData, size, MEM_RELEASE); 
    }
    CloseHandle(hProcess);
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
