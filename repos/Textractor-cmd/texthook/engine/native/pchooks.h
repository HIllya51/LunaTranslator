#pragma once

// pchooks.h
// 8/1/2014 jichi

#include <Windows.h>

namespace PcHooks {

void hookGDIFunctions();
void hookGDIPlusFunctions();
void hookD3DXFunctions(HMODULE d3dxModule);
void hookOtherPcFunctions();

} // namespace PcHooks

// EOF
