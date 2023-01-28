// minmaxmoveobserve.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <iostream>
#include<windows.h>

DWORD getprocessid(DWORD event, HWND hwnd) {
    DWORD pid;
    /*HANDLE hthread=OpenThread(THREAD_QUERY_LIMITED_INFORMATION, 0, event);
    
    if (hthread) {
        pid = GetProcessIdOfThread(hthread);
        CloseHandle(hthread);
        std::cout << 12121 << ' ' << pid << std::endl;
    }
    else {*/
        DWORD tid = GetWindowThreadProcessId(hwnd, &pid);
        //std::cout << 3333 << ' ' << pid << std::endl;
        
    //}
    return pid;
}
void callback(HWINEVENTHOOK hHandle, DWORD event, HWND hwnd, LONG _, LONG __, DWORD dweventthread, DWORD tm) {

    DWORD pid = getprocessid(event, hwnd);
     
    if (event == EVENT_SYSTEM_MOVESIZESTART) {
        RECT rect;
        GetWindowRect(hwnd, &rect);
        printf_s("%d %d %d %d %d %d\n", pid, 1, rect.left, rect.top, rect.right, rect.bottom); 
    }
    else if (event == EVENT_SYSTEM_MOVESIZEEND) {
        RECT rect;
        GetWindowRect(hwnd, &rect);
        printf_s("%d %d %d %d %d %d\n", pid, 2, rect.left, rect.top, rect.right, rect.bottom);
    }
    else if (event == EVENT_SYSTEM_MINIMIZESTART) {
        printf_s("%d %d\n", pid,3);
    }
    else if (event == EVENT_SYSTEM_MINIMIZEEND) {
        RECT rect;
        GetWindowRect(hwnd, &rect);
        printf_s("%d %d\n", pid, 4);
    }
    else if (event == EVENT_SYSTEM_FOREGROUND) {
        RECT rect;
        GetWindowRect(hwnd, &rect);
        printf_s("%d %d\n", pid, 5);
    }

    fflush(stdout);
}
int main()
{
    HRESULT r=CoInitialize(NULL);
     
    HWINEVENTHOOK h1 =SetWinEventHook(EVENT_SYSTEM_MOVESIZESTART, EVENT_SYSTEM_MOVESIZEEND, 0, callback, 0, 0, WINEVENT_OUTOFCONTEXT);
    if (h1 == 0) { 
        exit(0);
    }
    HWINEVENTHOOK h2 = SetWinEventHook(EVENT_SYSTEM_MINIMIZESTART, EVENT_SYSTEM_MINIMIZEEND, 0, callback, 0, 0, WINEVENT_OUTOFCONTEXT);
    if (h2 == 0) { 
        exit(0);
    }
    HWINEVENTHOOK h3 = SetWinEventHook(EVENT_SYSTEM_FOREGROUND, EVENT_SYSTEM_FOREGROUND, 0, callback, 0, 0, WINEVENT_OUTOFCONTEXT);
    if (h3 == 0) {
        exit(0);
    }
    HWINEVENTHOOK h4 = SetWinEventHook(EVENT_SYSTEM_DRAGDROPEND, EVENT_SYSTEM_DRAGDROPEND, 0, callback, 0, 0, WINEVENT_OUTOFCONTEXT);
    if (h4 == 0) {
        exit(0);
    }
    MSG msg;
    BOOL bRet;
    while ((bRet=GetMessage(&msg, 0, 0, 0) != 0)) {
        if (bRet == -1) {
            return -1;
        }
        else {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }
    }
    UnhookWinEvent(h1);
    UnhookWinEvent(h2);
    UnhookWinEvent(h3);
    UnhookWinEvent(h4);
    CoUninitialize(); 
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
