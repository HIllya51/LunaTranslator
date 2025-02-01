
#include "LoopbackCapture.h"
DECLARE_API HRESULT StartCaptureAsync(CLoopbackCapture **ptr)
{
    *ptr = nullptr;
    CComPtr<CLoopbackCapture> _ = new CLoopbackCapture;
    if (!_)
        return E_POINTER;
    CHECK_FAILURE(_->StartCaptureAsync(GetCurrentProcessId(), false));
    *ptr = _.Detach();
    return S_OK;
}
DECLARE_API void StopCaptureAsync(CLoopbackCapture *ptr, void (*datacb)(void *ptr, size_t size))
{
    if (!ptr)
        return;
    ptr->StopCaptureAsync();
    datacb(ptr->buffer.data(), ptr->buffer.size());
    ptr->Release();
}