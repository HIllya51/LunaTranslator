/**
veh_hook Vectored Exception Handler hooking library
Version: 24-March-2008
**/
// #define WINVER 0x0501
// #define _WIN32_WINNT 0x0501
#include <windows.h>
#include "veh_hook.h"
#include <mutex>
char int3bp[] = OPCODE_INT3;
std::mutex vehlistlock;

struct veh_node
{
    void *origFunc;
    newFuncType newFunc;
    void *handle;
    DWORD hooktype;
    void *baseAddr; // Address of the page in which origFunc resides.
    BYTE origBaseByte;
    DWORD OldProtect;
    veh_node(void *origFunc, newFuncType newFunc, void *handle, DWORD hooktype) : hooktype(hooktype), handle(handle), newFunc(newFunc), origFunc(origFunc), OldProtect(PAGE_EXECUTE_READWRITE)
    {
    }
};

static std::map<void *, veh_node> list;

veh_node *get_veh_node(void *origFunc, int range = 0)
{
    for (int i = 0; i <= range; i++)
    {
        auto ptr = (void *)((uintptr_t)origFunc - i);
        if (list.find(ptr) == list.end())
            continue;
        return &list.at(ptr);
    }
    return nullptr;
}

bool add_veh_hook(void *origFunc, newFuncType newFunc, DWORD hook_type)
{
    std::lock_guard _(vehlistlock);
    // static veh_list_t* list = NULL;
    DWORD oldProtect;
    if (get_veh_node(origFunc))
        return false;
    void *handle = AddVectoredExceptionHandler(1, (PVECTORED_EXCEPTION_HANDLER)veh_dispatch);
    veh_node newnode{origFunc, newFunc, handle, hook_type};

    // For memory hooks especially, we need to know the address of the start of the relevant page.
    MEMORY_BASIC_INFORMATION mem_info;
    VirtualQuery(origFunc, &mem_info, sizeof(MEMORY_BASIC_INFORMATION));
    newnode.baseAddr = mem_info.BaseAddress;
    if (!VirtualProtect(origFunc, sizeof(int), PAGE_EXECUTE_READWRITE, &newnode.OldProtect))
    {
        return false;
    }
    memcpy((void *)(&newnode.origBaseByte), (const void *)origFunc, sizeof(BYTE));
    memcpy((void *)origFunc, (const void *)&int3bp, sizeof(BYTE));
    VirtualProtect(origFunc, sizeof(int), newnode.OldProtect, &oldProtect);
    list.emplace(std::make_pair(origFunc, newnode));
    return true;
}
void repair_origin(veh_node *node)
{
    DWORD _p;
    if (!VirtualProtect(node->origFunc, sizeof(int), PAGE_EXECUTE_READWRITE, &_p))
        return;
    memcpy((void *)node->origFunc, (const void *)(&node->origBaseByte), sizeof(BYTE));
    VirtualProtect(node->origFunc, sizeof(int), node->OldProtect, &_p);
}
bool remove_veh_hook(void *origFunc)
{
    std::lock_guard _(vehlistlock);
    veh_node *node = get_veh_node(origFunc);
    if (node == NULL)
        return false;
    repair_origin(node);
    RemoveVectoredExceptionHandler(node->handle);
    return list.erase(origFunc), true;
}

LONG CALLBACK veh_dispatch(PEXCEPTION_POINTERS ExceptionInfo)
{

    DWORD oldProtect;
    void *Addr = ExceptionInfo->ExceptionRecord->ExceptionAddress;
    ULONG Code = ExceptionInfo->ExceptionRecord->ExceptionCode;

    if (Code != STATUS_BREAKPOINT && Code != STATUS_SINGLE_STEP)
        return EXCEPTION_CONTINUE_SEARCH;
    // Try to find the node associated with the address of the current exception, continue searching for handlers if not found;

    if (Code == STATUS_BREAKPOINT) //&& hooktype == VEH_HK_INT3)
    {
        veh_node *currnode;
        {
            std::lock_guard _(vehlistlock);
            currnode = get_veh_node(Addr);
        }
        if (currnode == NULL)
            return EXCEPTION_CONTINUE_SEARCH;

        if (currnode->newFunc(ExceptionInfo->ContextRecord))
        {
            repair_origin(currnode);
            ExceptionInfo->ContextRecord->EFlags |= 0x100;
        }
        else
        {
            remove_veh_hook(Addr);
        }
    }
    else if (Code == STATUS_SINGLE_STEP) //&& hooktype == VEH_HK_INT3)
    {
        std::lock_guard _(vehlistlock);
        veh_node *currnode = get_veh_node(Addr, 0x10);
        if (currnode == NULL)
            return EXCEPTION_CONTINUE_SEARCH;

        VirtualProtect(Addr, sizeof(int), PAGE_EXECUTE_READWRITE, &currnode->OldProtect);
        memcpy((void *)currnode->origFunc, (const void *)&int3bp, sizeof(BYTE));
        VirtualProtect(Addr, sizeof(int), currnode->OldProtect, &oldProtect);
        ExceptionInfo->ContextRecord->EFlags &= ~0x00000100; // Remove TRACE from EFLAGS
    }
    // else if (Code == STATUS_SINGLE_STEP && hooktype == VEH_HK_HW)
    // {
    //     currnode->newFunc(ExceptionInfo->ContextRecord);
    // }
    // else if (Code == STATUS_SINGLE_STEP && hooktype == VEH_HK_MEM)
    // {

    //     currnode->newFunc(ExceptionInfo->ContextRecord);
    // }
    return EXCEPTION_CONTINUE_EXECUTION;
}