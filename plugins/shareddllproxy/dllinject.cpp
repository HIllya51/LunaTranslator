// dllinject32.cpp : ���ļ����� "main" ����������ִ�н��ڴ˴���ʼ��������
// 
#include <iostream>
#include<Windows.h>
int dllinjectwmain(int argc, wchar_t* argv[])
{


    
    for (int i = 1; i < argc-1; i += 1) {
        auto PROCESS_INJECT_ACCESS = (
            PROCESS_CREATE_THREAD |
            PROCESS_QUERY_INFORMATION |
            PROCESS_VM_OPERATION |
            PROCESS_VM_WRITE |
            PROCESS_VM_READ);
        auto pid = _wtoi(argv[i]);
        auto hProcess = OpenProcess(PROCESS_INJECT_ACCESS, 0, pid);
        if (hProcess == 0)return 0;
        auto size = (wcslen(argv[argc-1]) + 1) * sizeof(wchar_t);
        auto remoteData = VirtualAllocEx(hProcess,
            nullptr,
            size,
            MEM_RESERVE | MEM_COMMIT,
            PAGE_READWRITE
        );
        if (remoteData == 0)return 0;
        WriteProcessMemory(hProcess, remoteData, argv[argc-1], size, 0);
        auto hThread = CreateRemoteThread(hProcess, 0, 0, (LPTHREAD_START_ROUTINE)LoadLibraryW, remoteData, 0, 0);
        if (hThread == 0) return 0;
        WaitForSingleObject(hThread, 10000);
        CloseHandle(hThread);
        VirtualFreeEx(hProcess, remoteData, size, MEM_RELEASE);
        CloseHandle(hProcess);
    } 
    return 1;
}

// ���г���: Ctrl + F5 ����� >����ʼִ��(������)���˵�
// ���Գ���: F5 ����� >����ʼ���ԡ��˵�

// ����ʹ�ü���: 
//   1. ʹ�ý��������Դ��������������/�����ļ�
//   2. ʹ���Ŷ���Դ�������������ӵ�Դ�������
//   3. ʹ��������ڲ鿴���������������Ϣ
//   4. ʹ�ô����б����ڲ鿴����
//   5. ת������Ŀ��>����������Դ����µĴ����ļ�����ת������Ŀ��>������������Խ����д����ļ����ӵ���Ŀ
//   6. ��������Ҫ�ٴδ򿪴���Ŀ����ת�����ļ���>���򿪡�>����Ŀ����ѡ�� .sln �ļ�
