#include <iostream>
#include<windows.h> 
#include<thread>
#include<detours.h>  
#include<string>
#include<assert.h>
#include<MinHook.h>
namespace Win32Utils{
static HANDLE SafeHandle(HANDLE h) noexcept { return (h == INVALID_HANDLE_VALUE) ? nullptr : h; }
struct HandleCloser { void operator()(HANDLE h) noexcept { assert(h != INVALID_HANDLE_VALUE); if (h) CloseHandle(h); } };

using ScopedHandle = std::unique_ptr<std::remove_pointer<HANDLE>::type, HandleCloser>;
std::wstring GetPathOfWnd(HWND hWnd) {
	ScopedHandle hProc;

	DWORD dwProcId = 0;
	if (GetWindowThreadProcessId(hWnd, &dwProcId)) {
		hProc.reset(SafeHandle(OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, dwProcId)));
		if (!hProc) {
		}
	} else {
	}

	if (!hProc) {
		static const auto getProcessHandleFromHwnd = (HANDLE (WINAPI*)(HWND))GetProcAddress(
			LoadLibraryEx(L"Oleacc.dll", NULL, 0), "GetProcessHandleFromHwnd");
		if (getProcessHandleFromHwnd) {
			hProc.reset(getProcessHandleFromHwnd(hWnd));
			if (!hProc) {
			}
		}

		if (!hProc) {
			return {};
		}
	}

	std::wstring fileName(MAX_PATH, 0);
	DWORD size = MAX_PATH;
	if (!QueryFullProcessImageName(hProc.get(), 0, fileName.data(), &size)) {
		return {};
	}

	fileName.resize(size);
	return fileName;
}
}
namespace StrUtils{
template<typename CHAR_T>
static void ToLowerCase(std::basic_string<CHAR_T>& str) noexcept {
	for (CHAR_T& c : str) {
		c = tolower(c);
	}
}
}
static std::wstring GetExeName(HWND hWnd) noexcept {
	std::wstring exeName = Win32Utils::GetPathOfWnd(hWnd);
	exeName = exeName.substr(exeName.find_last_of(L'\\') + 1);
	StrUtils::ToLowerCase(exeName);
	return exeName;
}
bool(*IsValidSrcWindow)(HWND);

struct hook_stack
{

#ifndef _WIN64
	uintptr_t _eflags;		//pushfd
	uintptr_t edi,        // pushad
		esi,
		ebp,
		esp,
		ebx,
		edx,
		ecx,        // this
		eax;        // 0x28
	
#else
	uintptr_t r15,
		r14,
		r13,
		r12,
		r11,
		r10,
		r9,
		r8,
		rdi,
		rsi,
		rbp,
		rsp,
		rdx,
		rcx,
		rbx,
		rax;
#endif
	uintptr_t eflags;     // pushaf
	union
	{
		uintptr_t stack[1];   // beginning of the runtime stack
		uintptr_t retaddr;
		BYTE base[1];
	};

};


uintptr_t findEnclosingAlignedFunction_strict(uintptr_t start, uintptr_t back_range)
{
  start &= ~0xf;
  for (uintptr_t i = start, j = start - back_range; i > j; i-=0x10) {
    DWORD k = *(DWORD *)(i-4);
    if (k == 0xcccccccc
      || k == 0x90909090
      || k == 0xccccccc3
      || k == 0x909090c3
      )
      return i;
  }
  return 0;
}
bool checkislunawindow(HWND hwndSrc)
{
    wchar_t title[100];
    GetWindowText(hwndSrc,title,100);
    if (wcscmp(title,L"LunaTranslator")==0||GetExeName(hwndSrc) == L"lunatranslator_main.exe"||GetExeName(hwndSrc) == L"lunatranslator.exe")
		return true;
	else return false;
}
class hooks{
public:
void IsValidSrcWindow_hooked(uintptr_t lpDataBase)
{
    auto stack=(hook_stack*)(lpDataBase-sizeof(hook_stack)+sizeof(uintptr_t));
    auto hwndSrc=(HWND)(stack->rcx);
    if (checkislunawindow(hwndSrc))
    {
        //MessageBoxW(0,GetExeName(hwndSrc).c_str(),L"",0);
        stack->rcx=(uintptr_t)FindWindow(L"Shell_TrayWnd",nullptr);
    }
}
hooks(LPVOID location){
    BYTE common_hook[] = {
		0x9c, // push rflags
		0x50, // push rax
		0x53, // push rbx
		0x51, // push rcx
		0x52, // push rdx
		0x54, // push rsp
		0x55, // push rbp
		0x56, // push rsi
		0x57, // push rdi
		0x41, 0x50, // push r8
		0x41, 0x51, // push r9
		0x41, 0x52, // push r10
		0x41, 0x53, // push r11
		0x41, 0x54, // push r12
		0x41, 0x55, // push r13
		0x41, 0x56, // push r14
		0x41, 0x57, // push r15
		// https://docs.microsoft.com/en-us/cpp/build/x64-calling-convention
		// https://stackoverflow.com/questions/43358429/save-value-of-xmm-registers
		0x48, 0x83, 0xec, 0x20, // sub rsp,0x20
		0xf3, 0x0f, 0x7f, 0x24, 0x24, // movdqu [rsp],xmm4
		0xf3, 0x0f, 0x7f, 0x6c, 0x24, 0x10, // movdqu [rsp+0x10],xmm5
		0x48, 0x8d, 0x94, 0x24, 0xa8, 0x00, 0x00, 0x00, // lea rdx,[rsp+0xa8]
		0x48, 0xb9, 0,0,0,0,0,0,0,0, // mov rcx,@this
		0x48, 0xb8, 0,0,0,0,0,0,0,0, // mov rax,@TextHook::Send
		0x48, 0x89, 0xe3, // mov rbx,rsp
		0x48, 0x83, 0xe4, 0xf0, // and rsp,0xfffffffffffffff0 ; align stack
		0xff, 0xd0, // call rax
		0x48, 0x89, 0xdc, // mov rsp,rbx
		0xf3, 0x0f, 0x6f, 0x6c, 0x24, 0x10, // movdqu xmm5,XMMWORD PTR[rsp + 0x10]
		0xf3, 0x0f, 0x6f, 0x24, 0x24, // movdqu xmm4,XMMWORD PTR[rsp]
		0x48, 0x83, 0xc4, 0x20, // add rsp,0x20
		0x41, 0x5f, // pop r15
		0x41, 0x5e, // pop r14
		0x41, 0x5d, // pop r13
		0x41, 0x5c, // pop r12
		0x41, 0x5b, // pop r11
		0x41, 0x5a, // pop r10
		0x41, 0x59, // pop r9
		0x41, 0x58, // pop r8
		0x5f, // pop rdi
		0x5e, // pop rsi
		0x5d, // pop rbp
		0x5c, // pop rsp
		0x5a, // pop rdx
		0x59, // pop rcx
		0x5b, // pop rbx
		0x58, // pop rax
		0x9d, // pop rflags
		0xff, 0x25, 0x00, 0x00, 0x00, 0x00, // jmp qword ptr [rip]
		0,0,0,0,0,0,0,0 // @original
	};
	int this_offset = 50, send_offset = 60, original_offset = 126;
    DWORD _;
    VirtualProtect(location, 10, PAGE_EXECUTE_READWRITE, &_);
    auto trampoline=VirtualAlloc(0,sizeof(common_hook),MEM_COMMIT,PAGE_EXECUTE_READWRITE);
	void* original;
	MH_STATUS error;
	if ((error = MH_CreateHook(location, trampoline, &original)) != MH_OK)
		return;
 
	*(hooks**)(common_hook + this_offset) = this;
	*(void(hooks::**)(uintptr_t))(common_hook + send_offset) = &hooks::IsValidSrcWindow_hooked;
	*(void**)(common_hook + original_offset) = original;
	memcpy(trampoline, common_hook, sizeof(common_hook));
	MH_EnableHook(location);
}
};
void starthookmagpie()
{
    uintptr_t IsValidSrcWindow=0;
    
    
    wchar_t target[]=L"Shell_TrayWnd";
    auto base=(uintptr_t)GetModuleHandle(L"Magpie.App.dll");
    BYTE lea[]={0x48,0x8D,0x05};
    //.text:0000000180146AD0 48 8D 05 91 87 10 00          lea     rax, aShellTraywnd              ; "Shell_TrayWnd"
    //.rdata:000000018024F268 53 00 68 00 65 00 6C 00 6C 00+text "UTF-16LE", 'Shell_TrayWnd',0
    
    __try{
        for(int i=0;i<0x1000000;i++)
        {
            if(memcmp(lea,(LPVOID)(i+base),3)==0)
            {
                auto addr=base+i;
                auto leastr=(*(int*)(addr+3))+7+addr;
                if(IsBadReadPtr((LPVOID)leastr,sizeof(target))==0)
                if(wcscmp((wchar_t*)leastr,target)==0)
                {
                    IsValidSrcWindow=findEnclosingAlignedFunction_strict(addr,0x1000);
                    break;
                }
            }
        }  
    }__except(EXCEPTION_EXECUTE_HANDLER) { return; }
    
    if(IsValidSrcWindow==0)return;
    
    //IsValidSrcWindow=(decltype(IsValidSrcWindow))((uintptr_t)GetModuleHandle(L"Magpie.App.dll")+0x180146860-0x180000000);
    MH_Initialize(); 
    hooks _((LPVOID)IsValidSrcWindow);
    // DetourTransactionBegin();
    // DetourUpdateThread(GetCurrentThread()); 
    // DetourAttach(&(PVOID&)IsValidSrcWindow,IsValidSrcWindow_hooked);
    // DetourTransactionCommit();
}

auto GetClassNameWs=GetClassNameW;
int
WINAPI
GetClassNameWH(
    _In_ HWND hWnd,
    _Out_writes_to_(nMaxCount, return) LPWSTR lpClassName,
    _In_ int nMaxCount
    ){
    if(checkislunawindow(hWnd)){
        wcscpy(lpClassName,L"ApplicationManager_ImmersiveShellWindow");
        return TRUE;
    }
    else
        return GetClassNameWs(hWnd,lpClassName,nMaxCount);
}
void starthooklossless()
{
	DetourTransactionBegin();
    DetourUpdateThread(GetCurrentThread()); 
    DetourAttach(&(PVOID&)GetClassNameWs, GetClassNameWH);
    DetourTransactionCommit();
}
void starthook()
{
	if(GetModuleHandle(L"Magpie.App.dll"))
		starthookmagpie();
	else if(GetModuleHandle(L"Lossless.dll"))
		starthooklossless();
}
BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
        starthook();
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}

