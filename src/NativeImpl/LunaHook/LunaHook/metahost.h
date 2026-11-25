// Minimal subset of the .NET Framework 4 hosting declarations from
// metahost.h/mscoree.h. Modern Windows SDKs no longer ship those headers
// (they moved to the NETFXSDK component, which is not always installed), so
// the pieces needed for ICLRRuntimeHost::ExecuteInDefaultAppDomain are
// vendored here under their original names.
//
// The interface GUIDs and the vtable order (exactly 9 methods after
// IUnknown - the extra unnamed entry mscoree.tlb shows is an import
// artifact, a 10-method layout segfaults) were verified against
// C:\Windows\Microsoft.NET\Framework\v4.0.30319\mscoree.tlb and by an
// end-to-end test against the real CLR. Parameter names of the methods we
// never call are approximate; the ABI layout is what is verified.
#ifndef __LUNA_METAHOST_H_90F1A06C_7712_4762_86B5_7A5EBA6BDB02__
#define __LUNA_METAHOST_H_90F1A06C_7712_4762_86B5_7A5EBA6BDB02__

#include <Windows.h>
#include <objbase.h>

#ifndef EXTERN_GUID
#define EXTERN_GUID(itf, l, w1, w2, b1, b2, b3, b4, b5, b6, b7, b8) \
    EXTERN_C const GUID DECLSPEC_SELECTANY itf = {l, w1, w2, {b1, b2, b3, b4, b5, b6, b7, b8}}
#endif

interface IHostControl;
interface ICLRControl;

typedef HRESULT(STDAPICALLTYPE *FExecuteInAppDomainCallback)(LPVOID Cookie);

// {90F1A06E-7712-4762-86B5-7A5EBA6BDB02}
EXTERN_GUID(CLSID_CLRRuntimeHost, 0x90F1A06E, 0x7712, 0x4762, 0x86, 0xB5, 0x7A, 0x5E, 0xBA, 0x6B, 0xDB, 0x02);

// {90F1A06C-7712-4762-86B5-7A5EBA6BDB02}
EXTERN_GUID(IID_ICLRRuntimeHost, 0x90F1A06C, 0x7712, 0x4762, 0x86, 0xB5, 0x7A, 0x5E, 0xBA, 0x6B, 0xDB, 0x02);

MIDL_INTERFACE("90F1A06C-7712-4762-86B5-7A5EBA6BDB02")
ICLRRuntimeHost : public IUnknown
{
public:
    virtual HRESULT STDMETHODCALLTYPE Start(void) = 0;
    virtual HRESULT STDMETHODCALLTYPE Stop(void) = 0;
    virtual HRESULT STDMETHODCALLTYPE SetHostControl(IHostControl *pHostControl) = 0;
    virtual HRESULT STDMETHODCALLTYPE GetCLRControl(ICLRControl **pCLRControl) = 0;
    virtual HRESULT STDMETHODCALLTYPE UnloadAppDomain(DWORD dwAppDomainId, BOOL fWaitUntilDone) = 0;
    virtual HRESULT STDMETHODCALLTYPE ExecuteInAppDomain(DWORD dwAppDomainId,
                                                        FExecuteInAppDomainCallback pCallback,
                                                        LPVOID Cookie) = 0;
    virtual HRESULT STDMETHODCALLTYPE GetCurrentAppDomainId(DWORD *pdwAppDomainId) = 0;
    virtual HRESULT STDMETHODCALLTYPE ExecuteApplication(LPCWSTR pwzAppFullName, DWORD dwManifestFlags,
                                                        LPCWSTR pwzAppArg, DWORD dwRemainingArgs,
                                                        LPCWSTR *ppwzArgValues, LPVOID pReserved) = 0;
    virtual HRESULT STDMETHODCALLTYPE ExecuteInDefaultAppDomain(LPCWSTR pwzAssemblyPath, LPCWSTR pwzTypeName,
                                                                LPCWSTR pwzMethodName, LPCWSTR pwzArgument,
                                                                DWORD *pReturnValue) = 0;
};

// The real CorBindToRuntimeEx is an mscoree.dll export; this inline shim
// resolves it at runtime so callers can use the standard signature without
// touching GetProcAddress (and without linking mscoree.lib). Returns E_FAIL
// when the export is unavailable.
typedef HRESULT(WINAPI *PFN_CorBindToRuntimeEx)(LPCWSTR pwszVersion, LPCWSTR pwszBuildFlavor,
                                                DWORD startupFlags, REFCLSID rclsid, REFIID riid,
                                                LPVOID *ppInterface);

inline HRESULT WINAPI CorBindToRuntimeEx(LPCWSTR pwszVersion, LPCWSTR pwszBuildFlavor, DWORD startupFlags,
                                         REFCLSID rclsid, REFIID riid, LPVOID *ppInterface)
{
    static PFN_CorBindToRuntimeEx pfn;
    if (!pfn)
    {
        auto mscoree = GetModuleHandleW(L"mscoree.dll");
        if (!mscoree)
            mscoree = LoadLibraryW(L"mscoree.dll");
        if (mscoree)
            pfn = (PFN_CorBindToRuntimeEx)GetProcAddress(mscoree, "CorBindToRuntimeEx");
    }
    if (!pfn)
        return E_FAIL;
    return pfn(pwszVersion, pwszBuildFlavor, startupFlags, rclsid, riid, ppInterface);
}

#endif
