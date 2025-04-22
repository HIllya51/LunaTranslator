/**
veh_hook Vectored Exception Handler hooking library
Version: 24-March-2008
**/
// #define WINVER 0x0501
// #define _WIN32_WINNT 0x0501
#include <windows.h>
#include "veh_hook.h"
#include <mutex>
struct veh_node
{
    void *origFunc;
    newFuncType newFunc;
    void *handle = nullptr;
    DWORD hooktype;
    void *baseAddr; // Address of the page in which origFunc resides.
    BYTE origBaseByte;
    DWORD OldProtect;
    int usecount;
    veh_node(void *origFunc, newFuncType newFunc, DWORD hooktype) : hooktype(hooktype), newFunc(newFunc), origFunc(origFunc), OldProtect(PAGE_EXECUTE_READWRITE), usecount(0)
    {
    }
};

static std::mutex vehlistlock;
static std::map<void *, veh_node> list;

static veh_node *get_veh_node(void *origFunc)
{
    if (list.find(origFunc) == list.end())
        return nullptr;
    return &list.at(origFunc);
}

LONG CALLBACK veh_dispatch(PEXCEPTION_POINTERS ExceptionInfo);
static bool __add_veh_hook(void *origFunc, newFuncType newFunc, DWORD hook_type)
{
    DWORD oldProtect;
    if (get_veh_node(origFunc))
    {
        return false;
    }
    veh_node newnode{origFunc, newFunc, hook_type};

    // For memory hooks especially, we need to know the address of the start of the relevant page.
    MEMORY_BASIC_INFORMATION mem_info;
    VirtualQuery(origFunc, &mem_info, sizeof(MEMORY_BASIC_INFORMATION));
    newnode.baseAddr = mem_info.BaseAddress;
    if (!VirtualProtect(origFunc, sizeof(int), PAGE_EXECUTE_READWRITE, &newnode.OldProtect))
    {
        return false;
    }
    newnode.origBaseByte = *(BYTE *)origFunc;
    *(BYTE *)origFunc = OPCODE_INT3;
    VirtualProtect(origFunc, sizeof(int), newnode.OldProtect, &oldProtect);
    newnode.handle = AddVectoredExceptionHandler(1, veh_dispatch);
    list.emplace(std::make_pair(origFunc, newnode));
    return true;
}

bool add_veh_hook(void *origFunc, newFuncType newFunc, DWORD hook_type)
{
    std::lock_guard _(vehlistlock);
    return __add_veh_hook(origFunc, newFunc, hook_type);
}
std::vector<void *> add_veh_hook(std::vector<void *> origFuncs, std::vector<newFuncType> newFuncs, DWORD hook_type)
{
    std::lock_guard _(vehlistlock);
    std::vector<void *> succ;
    for (auto i = 0; i < origFuncs.size(); i++)
    {
        if (__add_veh_hook(origFuncs[i], newFuncs[i], hook_type))
            succ.push_back(origFuncs[i]);
    }
    return succ;
}
static void repair_origin(veh_node *node)
{
    DWORD _p;
    if (!VirtualProtect(node->origFunc, sizeof(int), PAGE_EXECUTE_READWRITE, &_p))
        return;
    *(BYTE *)node->origFunc = node->origBaseByte;
    VirtualProtect(node->origFunc, sizeof(int), node->OldProtect, &_p);
}
static void RemoveNode(veh_node *node)
{
    repair_origin(node);
    if (node->handle)
        RemoveVectoredExceptionHandler(node->handle);
    list.erase(node->origFunc);
}
bool remove_veh_hook(void *origFunc)
{
    std::lock_guard _(vehlistlock);
    veh_node *node = get_veh_node(origFunc);
    if (!node)
        return true;
    if (node->usecount > 0)
    {
        node->usecount -= 1;
        return false;
    }
    RemoveNode(node);
    return true;
}
static thread_local veh_node *lastnode;
static LONG CALLBACK veh_dispatch(PEXCEPTION_POINTERS ExceptionInfo)
{

    DWORD oldProtect;
    void *Addr = ExceptionInfo->ExceptionRecord->ExceptionAddress;
    ULONG Code = ExceptionInfo->ExceptionRecord->ExceptionCode;

    if (Code != STATUS_BREAKPOINT && Code != STATUS_SINGLE_STEP)
        return EXCEPTION_CONTINUE_SEARCH;
    // Try to find the node associated with the address of the current exception, continue searching for handlers if not found;

    std::lock_guard _(vehlistlock);
    if (Code == STATUS_BREAKPOINT) //&& hooktype == VEH_HK_INT3)
    {
        veh_node *currnode = get_veh_node(Addr);
        if (!currnode)
            return EXCEPTION_CONTINUE_SEARCH;
        currnode->usecount += 1;
        lastnode = currnode;
        repair_origin(currnode);
        if (currnode->newFunc(ExceptionInfo->ContextRecord))
            ExceptionInfo->ContextRecord->EFlags |= 0x100;
        else
        {
            currnode->usecount -= 1;
            lastnode = nullptr;
        }
    }
    else if (Code == STATUS_SINGLE_STEP) //&& hooktype == VEH_HK_INT3)
    {
        if (!lastnode)
            return EXCEPTION_CONTINUE_EXECUTION;
        if (lastnode->usecount <= 0)
        {
            RemoveNode(lastnode);
            lastnode = nullptr;
            return EXCEPTION_CONTINUE_EXECUTION;
        }
        VirtualProtect(Addr, sizeof(int), PAGE_EXECUTE_READWRITE, &lastnode->OldProtect);
        *(BYTE *)lastnode->origFunc = OPCODE_INT3;
        VirtualProtect(Addr, sizeof(int), lastnode->OldProtect, &oldProtect);
        ExceptionInfo->ContextRecord->EFlags &= ~0x00000100; // Remove TRACE from EFLAGS
        lastnode->usecount -= 1;
        lastnode = nullptr;
    }
    return EXCEPTION_CONTINUE_EXECUTION;
}