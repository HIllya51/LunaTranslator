#ifdef WINXP
#include <mfapi.h>
#include "xpdef.hpp"
static void *loadproc(LPCWSTR lib, LPCSTR func)
{
    auto plib = (LoadLibraryW(lib));
    if (!plib)
        return nullptr;
    return GetProcAddress(plib, func);
}

STDAPI ActivateAudioInterfaceAsync(
    _In_ LPCWSTR deviceInterfacePath,
    _In_ REFIID riid,
    _In_opt_ PROPVARIANT *activationParams,
    _In_ IActivateAudioInterfaceCompletionHandler *completionHandler,
    _COM_Outptr_ IActivateAudioInterfaceAsyncOperation **activationOperation)
{
    auto func = loadproc(L"Mmdevapi.dll", "ActivateAudioInterfaceAsync");
    if (!func)
        return E_NOTIMPL;
    return ((decltype(&ActivateAudioInterfaceAsync))(func))(deviceInterfacePath, riid, activationParams, completionHandler, activationOperation);
}

STDAPI MFCancelWorkItem(MFWORKITEM_KEY Key)
{
    auto func = loadproc(L"Mfplat.dll", "MFCancelWorkItem");
    if (!func)
        return E_NOTIMPL;
    return ((decltype(&MFCancelWorkItem))(func))(Key);
}
STDAPI MFUnlockWorkQueue(_In_ DWORD dwWorkQueue)
{
    auto func = loadproc(L"Mfplat.dll", "MFUnlockWorkQueue");
    if (!func)
        return E_NOTIMPL;
    return ((decltype(&MFUnlockWorkQueue))(func))(dwWorkQueue);
}

STDAPI MFPutWorkItem2(
    DWORD dwQueue,
    LONG Priority,
    _In_ IMFAsyncCallback *pCallback,
    _In_opt_ IUnknown *pState)
{
    auto func = loadproc(L"Mfplat.dll", "MFPutWorkItem2");
    if (!func)
        return E_NOTIMPL;
    return ((decltype(&MFPutWorkItem2))(func))(dwQueue, Priority, pCallback, pState);
}
STDAPI MFPutWaitingWorkItem(
    HANDLE hEvent,
    LONG Priority,
    void *pResult,
    void *pKey)
{
    auto func = loadproc(L"Mfplat.dll", "MFPutWaitingWorkItem");
    if (!func)
        return E_NOTIMPL;
    return ((decltype(&MFPutWaitingWorkItem))(func))(hEvent, Priority, pResult, pKey);
}
STDAPI MFLockSharedWorkQueue(
    _In_ PCWSTR wszClass,
    _In_ LONG BasePriority,
    _Inout_ DWORD *pdwTaskId,
    _Out_ DWORD *pID)
{
    auto func = loadproc(L"Mfplat.dll", "MFLockSharedWorkQueue");
    if (!func)
        return E_NOTIMPL;
    return ((decltype(&MFLockSharedWorkQueue))(func))(wszClass, BasePriority, pdwTaskId, pID);
}
#endif