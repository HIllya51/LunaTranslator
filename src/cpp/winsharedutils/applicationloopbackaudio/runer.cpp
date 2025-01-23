
#ifndef WINXP
#include "LoopbackCapture.h"
#endif
DECLARE_API HANDLE StartCaptureAsync(void (*datacb)(void *ptr, size_t size))
{
#ifndef WINXP
    auto mutex = CreateSemaphoreW(NULL, 0, 1, NULL);
    std::thread([=]()
                {
        CLoopbackCapture loopbackCapture;
    loopbackCapture.StartCaptureAsync(GetCurrentProcessId(), false);
    WaitForSingleObject(mutex, INFINITE);
    CloseHandle(mutex);
    loopbackCapture.StopCaptureAsync();
    datacb(loopbackCapture.buffer.data(), loopbackCapture.buffer.size()); })
        .detach();
    return mutex;
#else
    return NULL;
#endif
}

DECLARE_API void StopCaptureAsync(HANDLE m)
{
    if (m)
        ReleaseSemaphore(m, 1, NULL);
}