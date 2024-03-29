/**
veh_hook Vectored Exception Handler hooking library
Version: 24-March-2008
**/
// #define WINVER 0x0501
// #define _WIN32_WINNT 0x0501
#include <windows.h>
#include "veh_hook.h"
#include<mutex>
static veh_list_t* list = NULL;
char int3bp[] = "\xCC";
std::mutex  vehlistlock;
bool add_veh_hook(void* origFunc, newFuncType newFunc, DWORD hook_type)
{
    std::lock_guard _(vehlistlock);
    //static veh_list_t* list = NULL;
    DWORD oldProtect;
    if (list == NULL) list = new_veh_list();
    if (list == NULL) return false;
    void* handle = AddVectoredExceptionHandler(1, (PVECTORED_EXCEPTION_HANDLER)veh_dispatch);
    veh_node_t* newnode = insert_veh_node(list, origFunc, newFunc, handle, hook_type);

    // For memory hooks especially, we need to know the address of the start of the relevant page.
    MEMORY_BASIC_INFORMATION mem_info;
    VirtualQuery(origFunc, &mem_info, sizeof(MEMORY_BASIC_INFORMATION));
    newnode->baseAddr = mem_info.BaseAddress;

    VirtualProtect(origFunc, sizeof(int), PAGE_EXECUTE_READWRITE, &newnode->OldProtect);
    memcpy((void*)(&newnode->origBaseByte), (const void*)origFunc, sizeof (BYTE));
    memcpy((void*)origFunc, (const void*)&int3bp, sizeof (BYTE));
    VirtualProtect(origFunc, sizeof(int), newnode->OldProtect, &oldProtect);
    return true;
}

bool remove_veh_hook(void* origFunc)
{
    std::lock_guard _(vehlistlock);
    if (list == NULL) return false;
    veh_node_t* node = get_veh_node(list, origFunc);
    if (node == NULL) return false;
    DWORD _p;
    VirtualProtect(node->origFunc, sizeof(int), PAGE_EXECUTE_READWRITE, &_p);
    memcpy((void*)node->origFunc, (const void*)(&node->origBaseByte), sizeof(char));
    VirtualProtect(node->origFunc, sizeof(int), node->OldProtect, &_p);
    RemoveVectoredExceptionHandler(node->handle);
    return remove_veh_node(list, origFunc);
}

bool remove_veh_node(veh_list_t* list, void* origFunc)
{
    veh_node_t* searchnode;
    veh_node_t* lastsearchnode = NULL;
    searchnode = list->head;

    while (searchnode != NULL)
    {
        if (searchnode->origFunc == origFunc)
        {
            if (lastsearchnode == NULL)
            {
                list->head = searchnode->next;
                if (list->tail == searchnode) list->tail = searchnode->next;
            }
            else
            {
                lastsearchnode->next = searchnode->next;
            }
            delete (searchnode);
            return true;
        }
        lastsearchnode = searchnode;
        searchnode = searchnode->next;
    }
    return false;
}
LONG CALLBACK veh_dispatch(PEXCEPTION_POINTERS ExceptionInfo)
{
    
    DWORD oldProtect;
    void* Addr = ExceptionInfo->ExceptionRecord->ExceptionAddress;
    ULONG Code = ExceptionInfo->ExceptionRecord->ExceptionCode;

    if (Code != STATUS_BREAKPOINT && Code != STATUS_SINGLE_STEP) return EXCEPTION_CONTINUE_SEARCH;
    // Try to find the node associated with the address of the current exception, continue searching for handlers if not found;
    std::lock_guard _(vehlistlock);
    if (Code == STATUS_BREAKPOINT )//&& hooktype == VEH_HK_INT3)
    {
        veh_node_t* currnode  = get_veh_node(list, Addr); 
        if (currnode == NULL) return EXCEPTION_CONTINUE_SEARCH;
    
        VirtualProtect(Addr, sizeof(int), PAGE_EXECUTE_READWRITE, &currnode->OldProtect);
        memcpy((void*)Addr, (const void*)(&currnode->origBaseByte), sizeof (char));
        currnode->newFunc(ExceptionInfo->ContextRecord);
        VirtualProtect(Addr, sizeof(int), currnode->OldProtect, &oldProtect);
        ExceptionInfo->ContextRecord->EFlags |= 0x100;
        
    }
    else if (Code == STATUS_SINGLE_STEP )//&& hooktype == VEH_HK_INT3)
    {
        veh_node_t* currnode  = get_veh_node(list, Addr, 0x10); 
        if (currnode == NULL) return EXCEPTION_CONTINUE_SEARCH;
        
        VirtualProtect(Addr, sizeof(int), PAGE_EXECUTE_READWRITE, &currnode->OldProtect);
        memcpy((void*)currnode->origFunc, (const void*)&int3bp, sizeof (BYTE));
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

veh_list_t* new_veh_list()
{
    veh_list_t* newlist = (veh_list_t*)malloc(sizeof(veh_list_t));
    if (newlist == NULL) return NULL;
    newlist->head = NULL;
    newlist->tail = NULL;
    return newlist;
}
veh_node_t* insert_veh_node(veh_list_t* list, void* origFunc, newFuncType newFunc, void* handle, DWORD hook_type)
{
    if (list == NULL) return NULL;
    /* create a new node and fill in the blanks */
    veh_node_t* newnode = new veh_node_t;
    if (newnode == NULL) return NULL;
    newnode->origFunc = origFunc;
    newnode->newFunc = newFunc;
    newnode->handle = handle;
    newnode->OldProtect = PAGE_EXECUTE_READWRITE;
    newnode->next = NULL;
    newnode->hooktype=hook_type;
    if (list->head == NULL)
    {
        list->head = newnode;
        list->tail = newnode;
    }
    else
    {
        list->tail->next = newnode;
        list->tail = newnode;
    }
    return newnode;
}

veh_node_t* get_veh_node(veh_list_t* list, void* origFunc, int range)
{
    veh_node_t* newnode;
    veh_node_t* closestnode = NULL;
    if (list == NULL) return NULL;
    newnode = list->head;
    while (newnode != NULL)
    {
        if(((uintptr_t)origFunc-(uintptr_t)newnode->origFunc)<=range)
        {
            closestnode=newnode;
            if(range==0)break;
            range=((uintptr_t)origFunc-(uintptr_t)newnode->origFunc);
        }
        newnode = newnode->next;
    }
    return closestnode;
}
