#include"pchooks.h"
 
bool pchooks::attach_function() {
    for (std::wstring DXVersion : { L"d3dx9", L"d3dx10" })
    if (HMODULE module = GetModuleHandleW(DXVersion.c_str())) PcHooks::hookD3DXFunctions(module);
    else for (int i = 0; i < 50; ++i)
        if (HMODULE module = GetModuleHandleW((DXVersion + L"_" + std::to_wstring(i)).c_str())) PcHooks::hookD3DXFunctions(module);
    PcHooks::hookGDIFunctions();
    PcHooks::hookGDIPlusFunctions();
    return true;
}  