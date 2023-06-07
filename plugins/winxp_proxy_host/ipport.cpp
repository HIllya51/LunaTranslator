#define _CRT_SECURE_NO_WARNINGS
#define _WINSOCK_DEPRECATED_NO_WARNINGS
#include <winsock2.h>
#include <windows.h>
#include <string>
#include"common.h"
#pragma comment(lib, "ws2_32.lib")
HFONT dfhFont;
HINSTANCE g_instance;
int g_nCmdShow;
SOCKET connectSocket = 0;
char* wchar_t_char(const wchar_t* src) {
    std::size_t len = std::wcslen(src) + 1;
    auto dest = new char[len];
    std::wcstombs(dest, src, len);
    return dest;
}
bool ConnectToServer(const wchar_t *ip,const wchar_t *port) {
    WSADATA wsaData;
    int iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (iResult != 0)return false;

    connectSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

    sockaddr_in server;
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = inet_addr(wchar_t_char(ip));
    server.sin_port = htons(std::stoi(port));

    iResult = connect(connectSocket, (SOCKADDR*)&server, sizeof(server));
    if (iResult == SOCKET_ERROR)
    { 
        closesocket(connectSocket);
        WSACleanup();
        return false;
    } 
    return true;

}

void receive(SOCKET socket,char* buff, int torecvsize)
{
    int totalBytesReceived = 0;

    while (totalBytesReceived < torecvsize)
    {
        int bytesReceived = recv(socket, buff + totalBytesReceived, torecvsize - totalBytesReceived, 0);
        if (bytesReceived > 0)
        {
            totalBytesReceived += bytesReceived;
        }
        else if (bytesReceived == 0)
        {
            // 连接关闭
            break;
        }
        else
        {
            // 发生错误
            int errorCode = WSAGetLastError();
            // 处理错误
            break;
        }
    }
}
void recv_binary(){
    try{
         
        std::string path=".";//buff;
        
        for(auto fname:{"LunaHook32.dll"}){
            int size;
            recv(connectSocket,(char*)&size,4,0);
            char* buff=new char[size];
            receive(connectSocket,buff,size);//recv(connectSocket,buff,size,0); 
            FILE* f=fopen((path+"\\"+fname).c_str(),"wb");
            if(f==0)continue;
            fwrite(buff,size,1,f);
            delete buff;
            fclose(f); 
        }
    }
    catch(...){

    }
    
}


// 窗口过程回调函数
LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    switch (msg)
    {
    case WM_CREATE:
    {
        // 创建IP地址输入框控件
        CreateWindow(L"STATIC", L"IP:", WS_VISIBLE | WS_CHILD,
            10, 10, 60, 40, hwnd, NULL, NULL, NULL);
        HWND hEdit1 = CreateWindowEx(WS_EX_CLIENTEDGE, L"EDIT", L"192.168.1.102",
            WS_CHILD | WS_VISIBLE | ES_AUTOHSCROLL,
            70, 10, 250, 40, hwnd, (HMENU)1, NULL, NULL);

        // 创建端口输入框控件
        CreateWindow(L"STATIC", L"Port:", WS_VISIBLE | WS_CHILD,
            10, 60, 60, 40, hwnd, NULL, NULL, NULL);
        HWND hEdit2 = CreateWindowEx(WS_EX_CLIENTEDGE, L"EDIT", L"12345",
            WS_CHILD | WS_VISIBLE | ES_AUTOHSCROLL,
            70, 60, 100, 40, hwnd, (HMENU)2, NULL, NULL);

        // 创建连接按钮控件
        HWND hButton = CreateWindow(L"BUTTON", L"Connect",
            WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
            120, 110,110, 40, hwnd, (HMENU)3, NULL, NULL);
    }
    break;
    case WM_COMMAND:
    {
        // 处理按钮点击事件
        if (LOWORD(wParam) == 3)
        {
            // 获取IP和端口号
            wchar_t ip[256], port[256];
            GetDlgItemText(hwnd, 1, ip, sizeof(ip));
            GetDlgItemText(hwnd, 2, port, sizeof(port));

            // 尝试连接到服务器
            // 这里需要根据具体需求使用相应的库函数来实现TCP连接
            bool success = ConnectToServer(ip, port);

            // 如果连接失败，弹出一个对话框
            if (!success)
            {
                MessageBox(hwnd, L"Failed to connect to server", L"Error", MB_OK);
            }
            else {
                DestroyWindow(hwnd);
                recv_binary();
                WinMain_pl();
            }
        }
    }
    break;
    case WM_CLOSE:
        DestroyWindow(hwnd);
        break;
    case WM_DESTROY:
        PostQuitMessage(0);
        break;
    default:
        return DefWindowProc(hwnd, msg, wParam, lParam);
    }
    return 0;
}
BOOL CALLBACK EnumChildProc(HWND hwndChild, LPARAM lParam)
{
         
    SendMessage(hwndChild, WM_SETFONT, (WPARAM)dfhFont, TRUE);
    //SendMessage(hwndChild, WM_SETFONT, (WPARAM)GetStockObject(DEFAULT_GUI_FONT), MAKELPARAM(FALSE, 0));
    return TRUE;
}
// 程序入口
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow)
{
    SetProcessDPIAware();
    g_instance = hInstance;
    g_nCmdShow = nCmdShow;
    const wchar_t* g_szClassName = L"MyWindowClass";
    // 注册窗口类
    WNDCLASSEX wc;
    memset(&wc, 0, sizeof(wc));
    wc.cbSize = sizeof(WNDCLASSEX);
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW );
    wc.lpszClassName = g_szClassName;
    if (!RegisterClassEx(&wc))
    {
        MessageBox(NULL, L"Window Registration Failed!", L"Error", MB_ICONEXCLAMATION | MB_OK);
        return 0;
    }

    // 创建窗口
    HWND hwnd = CreateWindowEx(WS_EX_CLIENTEDGE, g_szClassName, L"Luna Windows XP HOST",
        WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT, 350, 200,
        NULL, NULL, hInstance, NULL);
    if (hwnd == NULL)
    {
        MessageBox(NULL, L"Window Creation Failed!", L"Error", MB_ICONEXCLAMATION | MB_OK);
        return 0;
    }
    dfhFont= CreateFont(28, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
                            ANSI_CHARSET, OUT_DEFAULT_PRECIS, 
                            CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY,
                            DEFAULT_PITCH | FF_DONTCARE, TEXT("Arial"));

    EnumChildWindows(hwnd, EnumChildProc, 0);
    // 显示窗口
    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);

    // 消息循环
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0) > 0)
    {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    return (int)msg.wParam;
}
