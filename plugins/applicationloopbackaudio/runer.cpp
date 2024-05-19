
#include "LoopbackCapture.h"
int wmain(int argc, wchar_t *argv[])
{
    CLoopbackCapture loopbackCapture;
    loopbackCapture.StartCaptureAsync(GetCurrentProcessId(), false, argv[1]);
    WaitForSingleObject(
        CreateEventW(&allAccess, FALSE, FALSE, argv[2]),
        INFINITE);
    loopbackCapture.StopCaptureAsync();
    return 0;
}