// dllmain.cpp : Defines the entry point for the DLL application.
 
#include <stdio.h>
#include <windows.h> 
extern void SetFileMapping();
extern void DestroyFileMapping();
extern int testadd(int, int);
BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{

    switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH:
        SetFileMapping();
        break;
    case DLL_PROCESS_DETACH:
        DestroyFileMapping();
        break;
    case DLL_THREAD_ATTACH:
        break;
    case DLL_THREAD_DETACH:
        break;
    }

    return TRUE;
}