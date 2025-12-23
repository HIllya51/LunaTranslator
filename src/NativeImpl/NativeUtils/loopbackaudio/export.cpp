
#include "LoopbackCapture.h"
DECLARE_API HRESULT StartCaptureAsync(SupperRecord **ptr)
{
    // 在win10及以前，不能同时启动多个(必须MFUnlockWorkQueue后才能下一个，否则m_AudioClient->Initialize会E_UNEXPECTED)，win11可以同时启动多个
    *ptr = nullptr;
    auto _ = std::make_unique<SupperRecord>();
    if (!_)
        return E_POINTER;
    CHECK_FAILURE(_->StartCaptureAsync(GetCurrentProcessId(), false));
    *ptr = _.get();
    _.release();
    return S_OK;
}
DECLARE_API void StopCapture(SupperRecord *ptr, void (*datacb)(void *ptr, size_t size))
{
    if (!ptr)
        return;
    ptr->StopCapture();
    datacb(ptr->buffer.data(), ptr->buffer.size());
    delete ptr;
}
