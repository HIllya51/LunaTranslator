
#include"common.h"
#include <Windows.h>
#include <CommCtrl.h>
#include <TlHelp32.h>
#include<string>
#include<algorithm>
#include<locale>
#include<stdio.h>
#include"host.h"
#include"hookcode.h"
#include"textthread.h"
HWND g_hEdit_userhook;
HWND g_hButton_insert;
HWND g_hListBox_listtext;
HWND g_showtexts;
HWND g_timeout;
HWND g_codepage;
int g_pid;
bool attached=false;
std::wstring currentselect=L"";
bool is64bit(HANDLE handle){
    SYSTEM_INFO sysinfo;
    GetNativeSystemInfo(&sysinfo);
    BOOL wow;
    IsWow64Process(handle,&wow);
    if(sysinfo.wProcessorArchitecture==9 || sysinfo.wProcessorArchitecture==6)
        return ! wow;
    else
        return false;
}
 
void injectdll(int pid){
    auto handle=OpenProcess(PROCESS_QUERY_INFORMATION,0,pid);
    auto is64=is64bit(handle);
    CloseHandle(handle);
    wchar_t path[65535];
    GetModuleFileNameW(NULL, path, 65535);
	std::wstring _s = path;
	_s = _s.substr(0, _s.find_last_of(L"\\"));
	 

    // wchar_t cmd[65535]={0};
    // if(is64){
    //     //swprintf(cmd,L"\"%s\" dllinject %d \"%s\"",(_s+L"\\shareddllproxy64.exe").c_str(),pid,(_s+L"\\LunaHook64.dll").c_str()); 
    //     //xp only 32
    // }
    // else{
    //     swprintf(cmd,L"\"%s\" dllinject %d \"%s\"",(_s+L"\\shareddllproxy32.exe").c_str(),pid,(_s+L"\\LunaHook32.dll").c_str()); 
    // }
    // // FILE*f=fopen("./1.txt","wb");
    // // fwrite((char*)cmd,wcslen(cmd)*2,1,f);
    // // fclose(f);
    
    // STARTUPINFO _1 = {};
	// PROCESS_INFORMATION _2;
	// CreateProcessW(NULL,cmd,NULL,NULL,FALSE,0,NULL, L".\\",&_1,&_2); 
    
}
#include<map>
#include<vector>
std::map<std::wstring,std::vector<std::wstring>>savetext;

void send_x(SOCKET sock, void* buff, int size) {
    char* ptr = (char*)buff;
    int total_sent = 0;
    int bytes_left = size;
    send(sock, (char*)&size, 4, 0);
    while (total_sent < size) {
        int bytes_sent = send(sock, ptr + total_sent, bytes_left, 0);
        if (bytes_sent == SOCKET_ERROR) {
            // handle error
            break;
        }
        total_sent += bytes_sent;
        bytes_left -= bytes_sent;
    }
}
LRESULT CALLBACK WndProc_host(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
    switch (message)
    {
    case WM_CREATE:
    {
        
        // 创建编辑框
        g_hEdit_userhook = CreateWindowEx(0, L"EDIT", L"", WS_CHILD | WS_VISIBLE | WS_BORDER |ES_AUTOHSCROLL,
            610, 10, 400, 40, hWnd, NULL, NULL, NULL);

        // 创建按钮
        g_hButton_insert = CreateWindowEx(0, L"BUTTON", L"Insert UserHook", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
            1010, 10, 200, 40, hWnd, (HMENU)1, NULL, NULL);

        CreateWindowEx(0, L"STATIC", L"flushDelay", WS_CHILD | WS_VISIBLE | WS_BORDER ,
             10, 10, 150, 40, hWnd, NULL, NULL, NULL);

        g_timeout = CreateWindowEx(0, L"EDIT", L"100", WS_CHILD | WS_VISIBLE | WS_BORDER ,
             160, 10, 100, 40, hWnd, NULL, NULL, NULL);

        CreateWindowEx(0, L"STATIC", L"CodePage", WS_CHILD | WS_VISIBLE | WS_BORDER ,
             260, 10, 150, 40, hWnd, NULL, NULL, NULL);

        g_codepage = CreateWindowEx(0, L"EDIT", L"932", WS_CHILD | WS_VISIBLE | WS_BORDER ,
             410, 10, 100, 40, hWnd, NULL, NULL, NULL);

        // 创建列表框
        g_hListBox_listtext = CreateWindowEx(WS_EX_CLIENTEDGE, L"LISTBOX", L"", WS_CHILD | WS_VISIBLE | WS_VSCROLL | LBS_NOTIFY,
            10, 50, 310, 200, hWnd, NULL, NULL, NULL);

        // 创建列表框
        g_showtexts = CreateWindowEx(0, L"EDIT", L"", WS_CHILD | WS_VISIBLE | WS_BORDER | ES_READONLY|ES_MULTILINE |ES_AUTOVSCROLL| WS_VSCROLL,
            10, 10, 200, 20, hWnd, NULL, NULL, NULL);
            
        Host::Start([](auto) {attached=true;}, [](auto) {}, 
            [](TextThread& thread) {
                wchar_t buff[65535];
                swprintf_s(buff,L"[%I64X:%I32X:%I64X:%I64X:%I64X:%s:%s]",
                    thread.handle,
                    thread.tp.processId,
                    thread.tp.addr,
                    thread.tp.ctx,
                    thread.tp.ctx2,
                    thread.name.c_str(),
                    HookCode::Generate(thread.hp, thread.tp.processId).c_str() 
                );
                std::wstring _=buff;
                savetext.insert({_,{}});
                SendMessage(g_hListBox_listtext, LB_ADDSTRING, 0, (LPARAM)buff);
                
            }, 
            [](auto&) {}, 
            [](TextThread& thread, std::wstring& output)
                {
                    wchar_t buff[65535];
                    swprintf_s(buff,L"[%I64X:%I32X:%I64X:%I64X:%I64X:%s:%s]",
                        thread.handle,
                        thread.tp.processId,
                        thread.tp.addr,
                        thread.tp.ctx,
                        thread.tp.ctx2,
                        thread.name.c_str(),
                        HookCode::Generate(thread.hp, thread.tp.processId).c_str() 
                    );
                    std::wstring _=buff;
                    savetext.at(_).push_back(output);
                    if(currentselect==_){
                        send_x(connectSocket,(void*)output.c_str(),output.size()*2);
                        int len = GetWindowTextLength(g_showtexts);

                        // 将光标位置设置到最后
                        SendMessage(g_showtexts, EM_SETSEL, (WPARAM)len, (LPARAM)len);
                        
                        // 插入新文本
                        SendMessage(g_showtexts, EM_REPLACESEL, 0, (LPARAM)(L"\r\n"+output).c_str()); 
                    }
                    return false;
            }
        );
        Host::InjectProcess( g_pid);
        break;
    }
    case WM_SIZE: {
        // 获取窗口的新大小
        int width = LOWORD(lParam);
        int height = HIWORD(lParam)-90;
        // 重新调整子控件的大小和位置
        MoveWindow(g_hListBox_listtext, 10, 60, width - 20, height/2 ,1);
        MoveWindow(g_showtexts, 10, 60+height/2, width - 20, height/2 ,1);
        //MoveWindow(g_hListBox_listtext, 10, 40, width - 20, height - 50, TRUE);
        break;
    } 
    case WM_COMMAND:
    {
        if (HIWORD(wParam) == LBN_SELCHANGE && (HWND)lParam == g_hListBox_listtext)
        {
            // 当列表框中的选项改变时，获取当前选中的项的文本
            int selectedIndex = SendMessage(g_hListBox_listtext, LB_GETCURSEL, 0, 0);
            wchar_t itemText[65535];
            SendMessage(g_hListBox_listtext, LB_GETTEXT, selectedIndex, (LPARAM)itemText);

            std::wstring get;
            for(auto& _:savetext.at(itemText)){
                get+=_;
                get+=L"\r\n";
            }
            SetWindowText(g_showtexts, get.c_str());
            currentselect=itemText;
        }
        else if (LOWORD(wParam) == 1 && (HWND)lParam == g_hButton_insert)
        {
            // 当按钮被点击时，显示 MessageBox 显示当前选择的 PID
            wchar_t pidText[512];
            GetWindowText(g_hEdit_userhook, pidText, _countof(pidText));
            auto hp = HookCode::Parse(pidText);
			if(hp)
				Host::InsertHook(g_pid,hp.value()); 
        }
        else if (HIWORD(wParam) == EN_CHANGE && (HWND)lParam == g_timeout)
        {
            // 当按钮被点击时，显示 MessageBox 显示当前选择的 PID
            wchar_t pidText[16];
            GetWindowText(g_timeout, pidText, _countof(pidText));
            TextThread::flushDelay=std::stoi(pidText);
        }
        else if (HIWORD(wParam) == EN_CHANGE && (HWND)lParam == g_codepage)
        {
            // 当按钮被点击时，显示 MessageBox 显示当前选择的 PID
            wchar_t pidText[16];
            GetWindowText(g_codepage, pidText, _countof(pidText));
            Host::defaultCodepage= std::stoi(pidText);
        }
        break;
    }

    case WM_DESTROY:
        if(attached)    
            Host::DetachProcess(g_pid);
        PostQuitMessage(0);
        break;

    default:
        return DefWindowProc(hWnd, message, wParam, lParam);
    }
    return 0;
}
 
int WINAPI WinMain_host(int pid)
{ 
    g_pid=pid;  
    const wchar_t CLASS_NAME[] = L"HOSTCLASS";
    auto hInstance = g_instance;
    WNDCLASS wc = {};
    wc.lpfnWndProc = WndProc_host;
    wc.hInstance = hInstance;
    wc.lpszClassName = CLASS_NAME;
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW );
    RegisterClass(&wc);

    HWND hWnd = CreateWindowEx(
        WS_EX_CLIENTEDGE,                          // Optional window styles
        CLASS_NAME,                 // Window class
        L"HOST",            // Window title
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
