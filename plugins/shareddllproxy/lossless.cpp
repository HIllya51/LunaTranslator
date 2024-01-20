
#include <iostream>
#include<windows.h> 
#include<thread>
#include<detours.h>  
#include<string>
typedef BSTR( *GetAdapterNames_t)();
typedef BSTR(*GetDisplayNames_t)();

typedef bool (*SetDriverSettings_t)();
typedef void (*StatusListenerDelegate_t)(int status, HWND hwnd, int inputWidth, int inputHeight, int outputWidth, int outputHeight,  bool resized, float scaleFactor, int errorCode);
typedef bool (*Init_t)(StatusListenerDelegate_t callback);
typedef void (*UnInit_t)();
typedef bool (*Activate_t)(HWND hwnd);
typedef void(*ApplySettings_t1)(int scalingMode, int scalingFitMode, int scalingType, int scalingSubtype, float scaleFactor, bool resizeBeforeScale, bool windowedMode, int sharpness, bool VRS, bool clipCursor, bool cursorSensitivity, bool hideCursor, bool scaleCursor, bool doubleBuffering, bool vrrSupport, bool hdrSupport, bool allowTearing, bool legacyCaptureApi, bool drawFps, int gpuId, int displayId, int captureOffsetLeft, int captureOffsetTop, int captureOffsetRight, int captureOffsetBottom, bool multiDisplayMode);
typedef void(*ApplySettings_t2)(int scalingMode, int scalingFitMode, int scalingType, int scalingSubtype, float scaleFactor, bool resizeBeforeScale, bool windowedMode, int sharpness, bool VRS,int frameGeneration, bool clipCursor, bool cursorSensitivity, bool hideCursor, bool scaleCursor, bool doubleBuffering, bool vrrSupport, bool hdrSupport, bool allowTearing, bool legacyCaptureApi, bool drawFps, int gpuId, int displayId, int captureOffsetLeft, int captureOffsetTop, int captureOffsetRight, int captureOffsetBottom, bool multiDisplayMode);
typedef void(*ApplySettings_t3)(int scalingMode, int scalingFitMode, int scalingType, int scalingSubtype, float scaleFactor, bool resizeBeforeScale, bool windowedMode, int sharpness, bool VRS,int frameGeneration, bool clipCursor, bool cursorSensitivity, bool hideCursor, bool scaleCursor,int syncInterval, bool doubleBuffering, bool vrrSupport, bool hdrSupport, bool allowTearing, bool legacyCaptureApi, bool drawFps, int gpuId, int displayId, int captureOffsetLeft, int captureOffsetTop, int captureOffsetRight, int captureOffsetBottom, bool multiDisplayMode);
enum ErrorCode
{
    NO_CODE,
    RESIZE_FAILED,
    LARGE_OFFSET,
    FULLSCREEN_DETECTED
};
void  StatusListenerDelegate(int status, HWND hwnd, int inputWidth, int inputHeight, int outputWidth, int outputHeight, bool resized, float scaleFactor, int errorCode) {
    wprintf(L"%d %d %d %d %d %d %d %f %d\n", status, hwnd, inputWidth, inputHeight, outputWidth, outputHeight, resized, scaleFactor, errorCode);
} 
auto GetClassNameWs=GetClassNameW;
DWORD lunapid=0;
int
WINAPI
GetClassNameWH(
    _In_ HWND hWnd,
    _Out_writes_to_(nMaxCount, return) LPWSTR lpClassName,
    _In_ int nMaxCount
    ){
    DWORD dwProcessId;
    GetWindowThreadProcessId(hWnd, &dwProcessId);
    if(lunapid==dwProcessId){
        wcscpy(lpClassName,L"ApplicationManager_ImmersiveShellWindow");
        return TRUE;
    }
    else
        return GetClassNameWs(hWnd,lpClassName,nMaxCount);
}
// bool sub_18000A880() //不知道为什么，在控制台里面，这个会返回false
// {
//   ULONGLONG v0; // rax
//   ULONGLONG v1; // rax
//   DWORDLONG v2; // rax
//   struct _OSVERSIONINFOEXW VersionInformation; // [rsp+20h] [rbp-138h] BYREF

//   VersionInformation.dwOSVersionInfoSize = 284;
//   memset(&VersionInformation.dwBuildNumber, 0, 264);
//   VersionInformation.wServicePackMinor = 0;
//   *(_DWORD *)&VersionInformation.wSuiteMask = 0;
//   v0 = VerSetConditionMask(0i64, 2u, 3u);
//   v1 = VerSetConditionMask(v0, 1u, 3u);
//   v2 = VerSetConditionMask(v1, 0x20u, 3u);
//   *(_QWORD *)&VersionInformation.dwMajorVersion = 10i64;
//   VersionInformation.wServicePackMajor = 0;
//   return VerifyVersionInfoW(&VersionInformation, 0x23u, v2);
// }  
BOOL
WINAPI
VerifyVersionInfoWH(
    _Inout_ LPOSVERSIONINFOEXW lpVersionInformation,
    _In_    DWORD dwTypeMask,
    _In_    DWORDLONG dwlConditionMask
    ){
        return TRUE;
}
int checkversion(uintptr_t ApplySettings_ptr) {
    uintptr_t retptr = 0;
    for (int i = 0; i < 0x200; i++) {
        if ((*(DWORD*)(i + ApplySettings_ptr)) == 0xCCCCCCC3) {
            retptr = i + ApplySettings_ptr;
            break;
        }
    }
    if (retptr == 0)return 0;
    //2.5.1.0
    /*
    .text:0000000180016E93 0F B6 84 24 E0 00 00 00       movzx   eax, [rsp+arg_D8]
    .text:0000000180016E9B 88 05 05 4D 01 00             mov     cs:byte_18002BBA6, al
    .text:0000000180016EA1 44 89 0D 1C 4D 01 00          mov     cs:dword_18002BBC4, r9d
    .text:0000000180016EA8 C3                            retn
    */
    //2.5.0.1.b2
       /* .text:0000000180016DCE 0F B6 84 24 D8 00 00 00       movzx   eax, [rsp + arg_D0]
        .text:0000000180016DD6 88 05 CA 4D 01 00             mov     cs : byte_18002BBA6, al
        .text : 0000000180016DDC 44 89 0D DD 4D 01 00          mov     cs : dword_18002BBC0, r9d
        .text : 0000000180016DE3 C3                            retn*/
        
    //2.2.6
        /*.text:00000001800145D1 0F B6 84 24 D0 00 00 00       movzx   eax, [rsp + arg_C8]
        .text:00000001800145D9 88 05 C3 55 01 00             mov     cs : byte_180029BA2, al
        .text : 00000001800145DF 44 89 0D DA 55 01 00          mov     cs : dword_180029BC0, r9d
        .text : 00000001800145E6 C3                            retn*/
    retptr -= 7;
    if ((*(WORD*)retptr) != 0x8944)return 0;
    retptr -= 6;
    if ((*(WORD*)retptr) != 0x0588)return 0;
    retptr -= 8;
    if ((*(WORD*)retptr) != 0xb60f)return 0;
    retptr += 4;
    auto argnum = *(int*)retptr;
    wprintf(L"%x\n", argnum);
    if (argnum == 0xd0)return 1;
    else if (argnum == 0xd8)return 2;
    else if (argnum == 0xE0)return 3;
    return 0;
}
void enable_log(LPVOID Initptr) {
    
    __try {
        uintptr_t cmp = 0x180014690-0x1800145F0+(uintptr_t) Initptr; //这个基本是固定的
// .text:0000000180014690 80 3D 82 55 01 00 00          cmp     cs:byte_180029C19, 0
// .text:0000000180014697 48 8D 05 42 BE 00 00          lea     rax, aLogTxt                    ; "log.txt"
// .text:000000018001469E 48 8D 0D C3 BD 00 00          lea     rcx, aInit_0                    ; "Init\n"
// .text:00000001800146A5 48 0F 44 05 EB 54 01 00       cmovz   rax, cs:FileName
// .text:00000001800146AD 48 89 05 E4 54 01 00          mov     cs:FileName, rax
// .text:00000001800146B4 E8 87 E1 FF FF                call    sub_180012840
        if ((*(WORD*)cmp) != 0x3d80)return ;
        cmp+=7;
        if ((*(WORD*)cmp) != 0x8d48)return ;
        cmp+=7;
        if ((*(WORD*)cmp) != 0x8d48)return ;
        cmp+=7;
        if ((*(WORD*)cmp) != 0x0f48)return ;
        cmp+=8;
        if ((*(WORD*)cmp) != 0x8948)return ;
        cmp-=8;
        DWORD _;
        VirtualProtect((LPVOID)cmp, 8, PAGE_EXECUTE_READWRITE, &_); 
        memcpy((LPVOID)cmp, "\x90\x90\x90\x90\x90\x90\x90\x90", 8);
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        wprintf(L"unknow version\n");
    } 
    
} 
int losslesswmain(int argc, wchar_t* wargv[])
{
	SetProcessDPIAware(); 
    SetCurrentDirectoryW(wargv[1]);
    SetDllDirectoryW(wargv[1]);
	// for(int i=0;i<argc;i++){
	// 	wprintf(L"%d %s\n",i,wargv[i]);
	// }
	auto hwnd=(HWND)std::stoi(wargv[2]);
	auto scalingMode=std::stoi(wargv[3]);
	auto scalingFitMode=std::stoi(wargv[4]);
	auto scalingType=std::stoi(wargv[5]);
	auto scalingSubtype=std::stoi(wargv[6]);
	auto scaleFactor=std::stof(wargv[7]);
	auto resizeBeforeScale=wcscmp(wargv[8],L"True")==0;
	auto windowedMode=wcscmp(wargv[9],L"True")==0;
	auto sharpness=std::stoi(wargv[10]);
	auto VRS=wcscmp(wargv[11],L"True")==0;
	auto clipCursor=wcscmp(wargv[12],L"True")==0;
	auto cursorSensitivity=wcscmp(wargv[13],L"True")==0;
	auto hideCursor=wcscmp(wargv[14],L"True")==0;
	auto scaleCursor=wcscmp(wargv[15],L"True")==0;
	auto doubleBuffering=wcscmp(wargv[16],L"True")==0;
	auto vrrSupport=wcscmp(wargv[17],L"True")==0;
	auto hdrSupport=wcscmp(wargv[18],L"True")==0;
	auto allowTearing=wcscmp(wargv[19],L"True")==0;
	auto legacyCaptureApi=wcscmp(wargv[20],L"True")==0;
	auto drawFps=wcscmp(wargv[21],L"True")==0;
	auto gpuId=std::stoi(wargv[22]);
	auto displayId=std::stoi(wargv[23]);
	auto captureOffsetLeft=std::stoi(wargv[24]);
	auto captureOffsetTop=std::stoi(wargv[25]);
	auto captureOffsetRight=std::stoi(wargv[26]);
	auto captureOffsetBottom=std::stoi(wargv[27]);
	auto multiDisplayMode=wcscmp(wargv[28],L"True")==0;
    lunapid=std::stoi(wargv[29]);
    auto frameGeneration=std::stoi(wargv[30]);
    auto syncInterval=std::stoi(wargv[31]);

    auto Lossless = LoadLibraryW(LR"(.\Lossless.dll)");
    if (Lossless == 0)return 0;
     
    
    DetourTransactionBegin();
    DetourUpdateThread(GetCurrentThread()); 
    DetourAttach(&(PVOID&)GetClassNameWs, GetClassNameWH);  
    auto VerifyVersionInfoWs=VerifyVersionInfoW;
    DetourAttach(&(PVOID&)VerifyVersionInfoWs,VerifyVersionInfoWH);
    DetourTransactionCommit();

    auto Activate = (Activate_t)GetProcAddress(Lossless, "Activate");
    auto ApplySettings = GetProcAddress(Lossless, "ApplySettings");
    auto GetAdapterNames = (GetAdapterNames_t)GetProcAddress(Lossless, "GetAdapterNames");
    auto GetDisplayNames = (GetDisplayNames_t)GetProcAddress(Lossless, "GetDisplayNames");
    auto SetDriverSettings = (SetDriverSettings_t)GetProcAddress(Lossless, "SetDriverSettings");
    auto Init = (Init_t)GetProcAddress(Lossless, "Init");
    auto UnInit = (UnInit_t)GetProcAddress(Lossless, "UnInit");
    if (!(Activate && ApplySettings && GetAdapterNames && GetDisplayNames && SetDriverSettings && Init && UnInit))
        return 0;
    auto version=checkversion((uintptr_t)ApplySettings);
    
    if(version==0){
        MessageBoxA(0,"unsupported version","",0);
        ExitProcess(0);
    }
    enable_log(Init);

    Init(StatusListenerDelegate);
    
    SetDriverSettings(); 
	
    if(version==1)
        ((ApplySettings_t1)ApplySettings)(scalingMode-1, scalingFitMode, scalingType, scalingSubtype, scaleFactor, resizeBeforeScale, windowedMode, sharpness, VRS, clipCursor, cursorSensitivity, hideCursor, scaleCursor, doubleBuffering, vrrSupport, hdrSupport, allowTearing, legacyCaptureApi, drawFps, gpuId, displayId, captureOffsetLeft, captureOffsetTop, captureOffsetRight, captureOffsetBottom, multiDisplayMode);
    else if(version==2)
        ((ApplySettings_t2)ApplySettings)(scalingMode-1, scalingFitMode, scalingType, scalingSubtype, scaleFactor, resizeBeforeScale, windowedMode, sharpness, VRS,frameGeneration, clipCursor, cursorSensitivity, hideCursor, scaleCursor, doubleBuffering, vrrSupport, hdrSupport, allowTearing, legacyCaptureApi, drawFps, gpuId, displayId, captureOffsetLeft, captureOffsetTop, captureOffsetRight, captureOffsetBottom, multiDisplayMode);
    else if(version==3)
        ((ApplySettings_t3)ApplySettings)(scalingMode, scalingFitMode, scalingType, scalingSubtype, scaleFactor, resizeBeforeScale, windowedMode, sharpness, VRS,frameGeneration, clipCursor, cursorSensitivity, hideCursor, scaleCursor,syncInterval, doubleBuffering, vrrSupport, hdrSupport, allowTearing, legacyCaptureApi, drawFps, gpuId, displayId, captureOffsetLeft, captureOffsetTop, captureOffsetRight, captureOffsetBottom, multiDisplayMode);
	SetForegroundWindow(hwnd);
    Activate(hwnd); 
    std::thread([=]() {
        while (1) {
            DWORD pid;
            if (GetWindowThreadProcessId(hwnd, &pid) == 0)
                ExitProcess(0);
            Sleep(1000);
        }
        }).detach();
    std::thread([=]() {
		{
			SECURITY_ATTRIBUTES allAccess = std::invoke([] {
				static SECURITY_DESCRIPTOR sd = {};
				InitializeSecurityDescriptor(&sd, SECURITY_DESCRIPTOR_REVISION);
				SetSecurityDescriptorDacl(&sd, TRUE, NULL, FALSE);
				return SECURITY_ATTRIBUTES{ sizeof(SECURITY_ATTRIBUTES), &sd, FALSE };
			});
			auto ev = CreateEventW(&allAccess, FALSE, FALSE, (std::wstring(L"LOSSLESS_WAITFOR_STOP_SIGNAL") + std::to_wstring(GetCurrentProcessId())).c_str());
			WaitForSingleObject(ev, INFINITE);
			CloseHandle(ev);
		}
        
        Activate(0);
        UnInit();
        Sleep(1000);
        ExitProcess(0);
        }).detach();

    MSG msg;
    while (GetMessage(&msg, nullptr, 0, 0))
    {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    return 0;
}
 