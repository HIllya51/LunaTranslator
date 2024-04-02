#include <iostream>
#include <windows.h>
#include <thread>
#include <detours.h>
#include <string>
#include <assert.h>
#include "veh_hook.h"
namespace Win32Utils
{
    static HANDLE SafeHandle(HANDLE h) noexcept { return (h == INVALID_HANDLE_VALUE) ? nullptr : h; }
    struct HandleCloser
    {
        void operator()(HANDLE h) noexcept
        {
            assert(h != INVALID_HANDLE_VALUE);
            if (h)
                CloseHandle(h);
        }
    };

    using ScopedHandle = std::unique_ptr<std::remove_pointer<HANDLE>::type, HandleCloser>;
    std::wstring GetPathOfWnd(HWND hWnd)
    {
        ScopedHandle hProc;

        DWORD dwProcId = 0;
        if (GetWindowThreadProcessId(hWnd, &dwProcId))
        {
            hProc.reset(SafeHandle(OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, dwProcId)));
            if (!hProc)
            {
            }
        }
        else
        {
        }

        if (!hProc)
        {
            static const auto getProcessHandleFromHwnd = (HANDLE(WINAPI *)(HWND))GetProcAddress(
                LoadLibraryEx(L"Oleacc.dll", NULL, 0), "GetProcessHandleFromHwnd");
            if (getProcessHandleFromHwnd)
            {
                hProc.reset(getProcessHandleFromHwnd(hWnd));
                if (!hProc)
                {
                }
            }

            if (!hProc)
            {
                return {};
            }
        }

        std::wstring fileName(MAX_PATH, 0);
        DWORD size = MAX_PATH;
        if (!QueryFullProcessImageName(hProc.get(), 0, fileName.data(), &size))
        {
            return {};
        }

        fileName.resize(size);
        return fileName;
    }
}
namespace StrUtils
{
    template <typename CHAR_T>
    static void ToLowerCase(std::basic_string<CHAR_T> &str) noexcept
    {
        for (CHAR_T &c : str)
        {
            c = tolower(c);
        }
    }
}
static std::wstring GetExeName(HWND hWnd) noexcept
{
    std::wstring exeName = Win32Utils::GetPathOfWnd(hWnd);
    exeName = exeName.substr(exeName.find_last_of(L'\\') + 1);
    StrUtils::ToLowerCase(exeName);
    return exeName;
}
bool (*IsValidSrcWindow)(HWND);

struct hook_stack
{

#ifndef _WIN64
    uintptr_t _eflags; // pushfd
    uintptr_t edi,     // pushad
        esi,
        ebp,
        esp,
        ebx,
        edx,
        ecx, // this
        eax; // 0x28

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
    uintptr_t eflags; // pushaf
    union
    {
        uintptr_t stack[1]; // beginning of the runtime stack
        uintptr_t retaddr;
        BYTE base[1];
    };
};

uintptr_t findEnclosingAlignedFunction_strict(uintptr_t start, uintptr_t back_range)
{
    start &= ~0xf;
    for (uintptr_t i = start, j = start - back_range; i > j; i -= 0x10)
    {
        DWORD k = *(DWORD *)(i - 4);
        if (k == 0xcccccccc || k == 0x90909090 || k == 0xccccccc3 || k == 0x909090c3)
            return i;
    }
    return 0;
}
bool checkislunawindow(HWND hwndSrc)
{
    wchar_t title[100];
    GetWindowText(hwndSrc, title, 100);
    if (wcscmp(title, L"LunaTranslator") == 0 || GetExeName(hwndSrc) == L"lunatranslator_main.exe" || GetExeName(hwndSrc) == L"lunatranslator.exe")
        return true;
    else
        return false;
}
void hookedisvalidwindow(PCONTEXT context)
{
    auto hwndSrc = (HWND)(context->Rcx);
    if (checkislunawindow(hwndSrc))
    {
        // MessageBoxW(0,GetExeName(hwndSrc).c_str(),L"",0);
        context->Rcx = (uintptr_t)FindWindow(L"Shell_TrayWnd", nullptr);
    }
}
void starthookmagpie()
{
    uintptr_t IsValidSrcWindow = 0;

    wchar_t target[] = L"Shell_TrayWnd";
    auto base = (uintptr_t)GetModuleHandle(L"Magpie.App.dll");
    BYTE lea[] = {0x48, 0x8D, 0x05};
    //.text:0000000180146AD0 48 8D 05 91 87 10 00          lea     rax, aShellTraywnd              ; "Shell_TrayWnd"
    //.rdata:000000018024F268 53 00 68 00 65 00 6C 00 6C 00+text "UTF-16LE", 'Shell_TrayWnd',0

    __try
    {
        for (int i = 0; i < 0x1000000; i++)
        {
            if (memcmp(lea, (LPVOID)(i + base), 3) == 0)
            {
                auto addr = base + i;
                auto leastr = (*(int *)(addr + 3)) + 7 + addr;
                if (IsBadReadPtr((LPVOID)leastr, sizeof(target)) == 0)
                    if (wcscmp((wchar_t *)leastr, target) == 0)
                    {
                        IsValidSrcWindow = findEnclosingAlignedFunction_strict(addr, 0x1000);
                        break;
                    }
            }
        }
    }
    __except (EXCEPTION_EXECUTE_HANDLER)
    {
        return;
    }

    if (IsValidSrcWindow == 0)
        return;

    // IsValidSrcWindow=(decltype(IsValidSrcWindow))((uintptr_t)GetModuleHandle(L"Magpie.App.dll")+0x180146860-0x180000000);
    add_veh_hook((LPVOID)IsValidSrcWindow, hookedisvalidwindow, 0);
    // DetourTransactionBegin();
    // DetourUpdateThread(GetCurrentThread());
    // DetourAttach(&(PVOID&)IsValidSrcWindow,IsValidSrcWindow_hooked);
    // DetourTransactionCommit();
}

auto GetClassNameWs = GetClassNameW;
int
    WINAPI
    GetClassNameWH(
        _In_ HWND hWnd,
        _Out_writes_to_(nMaxCount, return) LPWSTR lpClassName,
        _In_ int nMaxCount)
{
    if (checkislunawindow(hWnd))
    {
        wcscpy(lpClassName, L"ApplicationManager_ImmersiveShellWindow");
        return TRUE;
    }
    else
        return GetClassNameWs(hWnd, lpClassName, nMaxCount);
}
void starthooklossless()
{
    DetourTransactionBegin();
    DetourUpdateThread(GetCurrentThread());
    DetourAttach(&(PVOID &)GetClassNameWs, GetClassNameWH);
    DetourTransactionCommit();
}
void starthook()
{
    if (GetModuleHandle(L"Magpie.App.dll"))
        starthookmagpie();
    else if (GetModuleHandle(L"Lossless.dll"))
        starthooklossless();
}
BOOL APIENTRY DllMain(HMODULE hModule,
                      DWORD ul_reason_for_call,
                      LPVOID lpReserved)
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
