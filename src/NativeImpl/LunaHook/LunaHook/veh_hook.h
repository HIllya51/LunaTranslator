/**
veh_hook Vectored Exception Handler hooking library
Version: 24-March-2008
**/

#ifndef LIST_T_H_INCLUDED_E8409B65_27B8_4880_99F3_C9F0FF1787F1
#define LIST_T_H_INCLUDED_E8409B65_27B8_4880_99F3_C9F0FF1787F1
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <functional>
// VEH Hooking types
#define VEH_HK_INT3 0
#define VEH_HK_MEM 1
#define VEH_HK_HW 2
// -

#define OPCODE_INT3 '\xCC'

// typedef void (*pfvoid)();
// typedef void (*newFuncType)(PCONTEXT);
using newFuncType = std::function<bool(PCONTEXT)>;

// VEH hook interface functions for creating and removing hooks.
bool add_veh_hook(void *origFunc, newFuncType newFunc, DWORD hook_type = VEH_HK_INT3);
std::vector<void *> add_veh_hook(std::vector<void *> origFuncs, std::vector<newFuncType> newFuncs, DWORD hook_type = VEH_HK_INT3);
bool remove_veh_hook(void *origFunc);


#endif // LIST_T_H_INCLUDED