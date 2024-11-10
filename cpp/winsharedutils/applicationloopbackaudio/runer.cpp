
#include "LoopbackCapture.h"

DECLARE_API HANDLE StartCaptureAsync(void (*datacb)(void *ptr, size_t size))
{
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
}

DECLARE_API void StopCaptureAsync(HANDLE m)
{
    ReleaseSemaphore(m, 1, NULL);
}