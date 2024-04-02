/**
veh_hook Vectored Exception Handler hooking library
Version: 24-March-2008
**/

#ifndef LIST_T_H_INCLUDED
#define LIST_T_H_INCLUDED
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <functional>
// VEH Hooking types
#define VEH_HK_INT3 0
#define VEH_HK_MEM 1
#define VEH_HK_HW 2
// -

#define OPCODE_INT3 "\xCC"

// typedef void (*pfvoid)();
// typedef void (*newFuncType)(PCONTEXT);
using newFuncType = void (*)(PCONTEXT); // std::function<void(PCONTEXT)>;

typedef struct veh_node
{
	void *origFunc;
	newFuncType newFunc;
	void *handle;
	DWORD hooktype;
	void *baseAddr; // Address of the page in which origFunc resides.
	BYTE origBaseByte;
	DWORD OldProtect;
	struct veh_node *next;
} veh_node_t;

typedef struct
{
	veh_node_t *head;
	veh_node_t *tail;
} veh_list_t;

// VEH hook interface functions for creating and removing hooks.
bool add_veh_hook(void *origFunc, newFuncType newFunc, DWORD hook_type);
bool remove_veh_hook(void *origFunc);

// The VEH dispathing function is called by Windows every time an exception is encountered.
// the function dispatches calls to the correct inctercept function.
LONG CALLBACK veh_dispatch(PEXCEPTION_POINTERS ExceptionInfo);

// Functions used internally by the library.
veh_list_t *new_veh_list();
veh_node_t *insert_veh_node(veh_list_t *list, void *origFunc, newFuncType newFunc, void *handle, DWORD hook_type);
bool remove_veh_node(veh_list_t *list, void *origFunc);
veh_node_t *get_veh_node(veh_list_t *list, void *origFunc, int range = 0);

#endif // LIST_T_H_INCLUDED
