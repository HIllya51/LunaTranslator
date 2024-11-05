#include "Ryujinx.h"

namespace
{
  /*
  const char* CEEInfo::getMethodNameFromMetadata(CORINFO_METHOD_HANDLE ftnHnd,
                                                  const char** className,
                                                  const char** namespaceName,
                                                  const char** enclosingClassNames,
                                                  size_t maxEnclosingClassNames)
  */
  /*
  CorJitResult CILJit::compileMethod(ICorJitInfo*         compHnd,
                                     CORINFO_METHOD_INFO* methodInfo,
                                     unsigned             flags,
                                     uint8_t**            entryAddress,
                                     uint32_t*            nativeSizeOfCode)
  */
  /*
  CorJitResult invokeCompileMethodHelper(EEJitManager *jitMgr,
                                   CEEInfo *comp,
                                   struct CORINFO_METHOD_INFO *info,
                                   CORJIT_FLAGS jitFlags,
                                   BYTE **nativeEntry,
                                   uint32_t *nativeSizeOfCode)
  */
  struct CEEInfo;
  struct CORINFO_METHOD_HANDLE;
  struct CORINFO_METHOD_INFO
  {
    CORINFO_METHOD_HANDLE *ftn;
    // CORINFO_MODULE_HANDLE scope;
    // uint8_t *ILCode;
    // unsigned ILCodeSize;
    // unsigned maxStack;
    // unsigned EHcount;
    // CorInfoOptions options;
    // CorInfoRegionKind regionKind;
    // CORINFO_SIG_INFO args;
    // CORINFO_SIG_INFO locals;
  };
  const char *(*getMethodNameFromMetadata)(CEEInfo *, CORINFO_METHOD_HANDLE *, const char **, const char **, const char **) = 0;

}
bool Ryujinx::attach_function()
{
  WarningOutput("not support ryuujinx, please use yuzu/sudachi instead.");
  return true;
  auto invokeCompileMethodHelper = processStartAddress + 0x84CC0;
  getMethodNameFromMetadata = (decltype(getMethodNameFromMetadata))(processStartAddress + 0x7AED0);
  HookParam hp;
  hp.address = invokeCompileMethodHelper;
  hp.text_fun = [](hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto methodInfo = (CORINFO_METHOD_INFO *)stack->r8;

    const char *className;
    const char *namespaceName;
    const char *enclosingClassName;
    auto methodname = getMethodNameFromMetadata((CEEInfo *)stack->rdx, methodInfo->ftn, &className, &namespaceName, &enclosingClassName);
    if (!methodname)
      return;
    if (strcmp(methodname, "RegisterFunction") != 0)
      return;

    ConsoleOutput("%s %s %s %s", className, namespaceName, enclosingClassName, methodname);
    HookParam hpinternal;
    hpinternal.user_value = stack->stack[5]; // entryAddress->RegisterFunction
    hpinternal.address = stack->retaddr;
    hpinternal.text_fun = [](hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      HookParam hp_cs_function;
      hp_cs_function.address = *(uintptr_t *)hp->user_value;
      hp_cs_function.text_fun = [](hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        ConsoleOutput("%p %p %p %p %p %p", stack->rcx, stack->rdx, stack->r8, stack->r9, stack->r10, stack->r11);
      };
      NewHook(hp_cs_function, "RegisterFunction");

      hp->type = HOOK_EMPTY;
    };
    NewHook(hpinternal, "invokeCompileMethodHelper Return");
  };
  return NewHook(hp, "invokeCompileMethodHelper");
}