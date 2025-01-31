
#include "LoopbackCapture.h"
DECLARE_API CLoopbackCapture *StartCaptureAsync()
{
    auto _ = new CLoopbackCapture;
    _->AddRef();
    _->StartCaptureAsync(GetCurrentProcessId(), false);
    return _;
}
DECLARE_API void StopCaptureAsync(CLoopbackCapture *ptr, void (*datacb)(void *ptr, size_t size))
{
    if (!ptr)
        return;
    ptr->StopCaptureAsync();
    datacb(ptr->buffer.data(), ptr->buffer.size());
    ptr->Release();
}