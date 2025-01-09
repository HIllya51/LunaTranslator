/**
veh_hook Vectored Exception Handler hooking library
Version: 24-March-2008
**/
// #define WINVER 0x0501
// #define _WIN32_WINNT 0x0501
#include <windows.h>
#include "veh_hook.h"
#include <mutex>
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
    int usecount;
    bool removed;
    veh_node(void *origFunc, newFuncType newFunc, void *handle, DWORD hooktype) : hooktype(hooktype), handle(handle), newFunc(newFunc), origFunc(origFunc), OldProtect(PAGE_EXECUTE_READWRITE), usecount(0), removed(false)
    {
    }
};

static std::map<void *, veh_node> list;

veh_node *get_veh_node(void *origFunc)
{
    if (list.find(origFunc) == list.end())
        return nullptr;
    return &list.at(origFunc);
}

bool __add_veh_hook(void *origFunc, newFuncType newFunc, DWORD hook_type)
{
    DWORD oldProtect;
    auto hasexitst = get_veh_node(origFunc); // hookfinder不删除钩子
    if (hasexitst)
    {
        if (!hasexitst->removed)
            return false;
        hasexitst->newFunc = newFunc;
        hasexitst->removed = false;
        return true;
    }
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
    newnode.origBaseByte = *(BYTE *)origFunc;
    *(BYTE *)origFunc = OPCODE_INT3;
    VirtualProtect(origFunc, sizeof(int), newnode.OldProtect, &oldProtect);
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
void repair_origin(veh_node *node)
{
    DWORD _p;
    if (!VirtualProtect(node->origFunc, sizeof(int), PAGE_EXECUTE_READWRITE, &_p))
        return;
    *(BYTE *)node->origFunc = node->origBaseByte;
    VirtualProtect(node->origFunc, sizeof(int), node->OldProtect, &_p);
}
bool __remove_veh_hook(void *origFunc)
{
    veh_node *node = get_veh_node(origFunc);
    if (!node)
        return true;
    if (node->usecount <= 0)
    {
        repair_origin(node);
        RemoveVectoredExceptionHandler(node->handle);
        list.erase(origFunc);
        return true;
    }
    else
    {
        node->removed = true;
        return false;
    }
}
void remove_veh_hook(void *origFunc)
{
    // 仅会在手动移除时被调用
    // while (true)
    // {
    //     std::lock_guard _(vehlistlock);
    if (__remove_veh_hook(origFunc))
        ;
    //    break;
    //}
}
void remove_veh_hook(std::vector<void *> origFuncs)
{
    std::lock_guard _(vehlistlock);
    for (auto origFunc : origFuncs)
    {
        // hookfinder时，usecount有时会无法归零（例如JIT重新写code），所以仅尝试一次即可
        __remove_veh_hook(origFunc);
    }
}
thread_local veh_node *lastnode;
LONG CALLBACK veh_dispatch(PEXCEPTION_POINTERS ExceptionInfo)
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
        lastnode = currnode;
        repair_origin(currnode);
        if (!currnode->removed)
        {
            currnode->usecount += 1;
            if (currnode->newFunc(ExceptionInfo->ContextRecord))
                ExceptionInfo->ContextRecord->EFlags |= 0x100;
        }
    }
    else if (Code == STATUS_SINGLE_STEP) //&& hooktype == VEH_HK_INT3)
    {
        if (!lastnode)
            return EXCEPTION_CONTINUE_SEARCH;
        if (!lastnode->removed)
        {
            VirtualProtect(Addr, sizeof(int), PAGE_EXECUTE_READWRITE, &lastnode->OldProtect);
            *(BYTE *)lastnode->origFunc = OPCODE_INT3;
            VirtualProtect(Addr, sizeof(int), lastnode->OldProtect, &oldProtect);
            ExceptionInfo->ContextRecord->EFlags &= ~0x00000100; // Remove TRACE from EFLAGS
        }
        lastnode->usecount -= 1;
        lastnode = nullptr;
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