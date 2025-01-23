#pragma once

// pchooks.h
// 8/1/2014 jichi

#include <Windows.h>

namespace PcHooks
{
    void hookGDIFunctions(void *ptr = 0);
    void hookGDIPlusFunctions();
    void hookD3DXFunctions(HMODULE d3dxModule);
    void hookOtherPcFunctions(void *ptr = 0);
    void hookGdiGdiplusD3dxFunctions();
} // namespace PcHooks

// EOF
