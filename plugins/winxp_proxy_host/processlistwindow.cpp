
#include"common.h"
#include <Windows.h>
#include <CommCtrl.h>
#include <TlHelp32.h>
#include<string>
#include<algorithm>
#include<locale>
HWND g_hEdit;
HWND g_hButton;
HWND g_hListBox;
// 获取进程列表并填充到列表框中
void PopulateProcessList()
{
    // 清空列表框
    SendMessage(g_hListBox, LB_RESETCONTENT, 0, 0);

    // 创建进程快照
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnapshot == INVALID_HANDLE_VALUE)
        return;

    // 初始化进程快照结构
    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);
    wchar_t buff[65535];
    // 获取第一个进程的信息
    if (Process32First(hSnapshot, &pe32))
    {
        do
        {
            auto PROCESS_INJECT_ACCESS = (
                PROCESS_CREATE_THREAD |
                PROCESS_QUERY_INFORMATION |
                PROCESS_VM_OPERATION |
                PROCESS_VM_WRITE |
                PROCESS_VM_READ);
            auto handle = OpenProcess(PROCESS_INJECT_ACCESS, 0, pe32.th32ProcessID);
            if (handle == 0)continue;
            DWORD sz = 65535;
            QueryFullProcessImageNameW(handle, 0, buff, &sz);
            CloseHandle(handle);
            auto str=std::wstring(buff);
            std::transform(str.begin(), str.end(), str.begin(), [](wchar_t ch){    return std::tolower(ch, std::locale());});
            if(str.substr(str.size()-4,4)!=L".exe"|| str.find(L"\\windows\\")!=str.npos || str.find(L"\\microsoft")!=str.npos|| str.find(L"\\windowsapps")!=str.npos)continue;
             
            // 将 PID 和 EXE 名添加到列表框中
            wchar_t itemText[256];
            swprintf_s(itemText, L"%d:  %s", pe32.th32ProcessID, buff);
            SendMessage(g_hListBox, LB_ADDSTRING, 0, (LPARAM)itemText);

        } while (Process32Next(hSnapshot, &pe32));
    }

    // 关闭进程快照句柄
    CloseHandle(hSnapshot);
}

LRESULT CALLBACK WndProc_pl(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
    switch (message)
    {
    case WM_CREATE:
    {
        // 创建编辑框
        g_hEdit = CreateWindowEx(0, L"EDIT", L"", WS_CHILD | WS_VISIBLE | WS_BORDER ,
            10, 10, 200, 40, hWnd, NULL, NULL, NULL);

        // 创建按钮
        g_hButton = CreateWindowEx(0, L"BUTTON", L"Attach", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
            220, 10, 100, 40, hWnd, (HMENU)1, NULL, NULL);

        // 创建列表框
        g_hListBox = CreateWindowEx(WS_EX_CLIENTEDGE, L"LISTBOX", L"", WS_CHILD | WS_VISIBLE | WS_VSCROLL | LBS_NOTIFY,
            10, 60, 310, 200, hWnd, NULL, NULL, NULL);

        // 填充进程列表到列表框中
        PopulateProcessList();

        break;
    }
    case WM_SIZE: {
        // 获取窗口的新大小
        int width = LOWORD(lParam);
        int height = HIWORD(lParam);
        // 重新调整子控件的大小和位置
        SetWindowPos(g_hListBox,0, 10, 60, width - 20, height - 70, SWP_NOMOVE);
        //MoveWindow(g_hListBox, 10, 40, width - 20, height - 50, TRUE);
        break;
    } 
    case WM_COMMAND:
    {
        if (HIWORD(wParam) == LBN_SELCHANGE && (HWND)lParam == g_hListBox)
        {
            // 当列表框中的选项改变时，获取当前选中的项的文本
            int selectedIndex = SendMessage(g_hListBox, LB_GETCURSEL, 0, 0);
            wchar_t itemText[256];
            SendMessage(g_hListBox, LB_GETTEXT, selectedIndex, (LPARAM)itemText);

            // 从文本中提取 PID 并在编辑框中显示
            wchar_t pidText[16];
            swscanf_s(itemText, L"%[^:]", pidText, _countof(pidText));
            SetWindowText(g_hEdit, pidText);
        }
        else if (LOWORD(wParam) == 1 && (HWND)lParam == g_hButton)
        {
            // 当按钮被点击时，显示 MessageBox 显示当前选择的 PID
            wchar_t pidText[16];
            GetWindowText(g_hEdit, pidText, _countof(pidText));
            if(std::wstring(pidText)!=L""){

                DestroyWindow(hWnd);
                WinMain_host(std::stoi(pidText));
            }
            
        }

        break;
    }

    case WM_DESTROY:
        PostQuitMessage(0);
        break;

    default:
        return DefWindowProc(hWnd, message, wParam, lParam);
    }
    return 0;
}

int WINAPI WinMain_pl()
{
    const wchar_t CLASS_NAME[] = L"ProcessListWindowClass";
    auto hInstance = g_instance;
    WNDCLASS wc = {};
    wc.lpfnWndProc = WndProc_pl;
    wc.hInstance = hInstance;
    wc.lpszClassName = CLASS_NAME;
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW );
    RegisterClass(&wc);

    HWND hWnd = CreateWindowEx(
        WS_EX_CLIENTEDGE,                          // Optional window styles
        CLASS_NAME,                 // Window class
        L"Process List",            // Window title
        WS_OVERLAPPEDWINDOW,        // Window style

        CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT,

        NULL,                       // Parent window
        NULL,                       // Menu
        hInstance,                  // Instance handle
        NULL                        // Additional application data
    );

    if (hWnd == NULL)
        return 0;
    EnumChildWindows(hWnd, EnumChildProc, 0);
    ShowWindow(hWnd, g_nCmdShow);
    
    MSG msg = {};
    while (GetMessage(&msg, NULL, 0, 0))
    {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return 0;
}
