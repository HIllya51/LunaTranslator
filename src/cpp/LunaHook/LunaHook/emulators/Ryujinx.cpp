#include "Ryujinx.h"

namespace
{
  /*
  UnsafeJitFunction->
    invokeCompileMethodHelper->
      jitMgr->m_jit->compileMethod

  FlushInstructionCache
  */
  /*
 unsigned __int8 *__fastcall UnsafeJitFunction(
        PrepareCodeConfig *config,
        COR_ILMETHOD_DECODER *ILHeader,
        CORJIT_FLAGS *pJitFlags,
        unsigned int *a4)
  */
  /*
  CorJitResult invokeCompileMethodHelper(EEJitManager *jitMgr,
                                   CEEInfo *comp,
                                   struct CORINFO_METHOD_INFO *info,
                                   CORJIT_FLAGS jitFlags,
                                   BYTE **nativeEntry,
                                   uint32_t *nativeSizeOfCode)
  */
  /*
  CorJitResult CILJit::compileMethod(ICorJitInfo*         compHnd,
                                     CORINFO_METHOD_INFO* methodInfo,
                                     unsigned             flags,
                                     uint8_t**            entryAddress,
                                     uint32_t*            nativeSizeOfCode)
  */

  /*
  const char* CEEInfo::getMethodNameFromMetadata(CORINFO_METHOD_HANDLE ftnHnd,
                                                  const char** className,
                                                  const char** namespaceName,
                                                  const char** enclosingClassNames,
                                                  size_t maxEnclosingClassNames)
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
struct passinfo
{
  void **nativeEntry;
  std::string methodname;
  std::string className;
  std::string namespaceName;
  std::string enclosingClassName;
};
bool Ryujinx::attach_function()
{
  HostInfo(HOSTINFO::EmuWarning, TR[RYUJINXUNSUPPORT]);
  return true;
  /*
  UnsafeJitFunction

  if ( !EEJitManager::LoadJIT(ExecutionManager::m_pEEJitManager) )
  {
    if ( !v10->m_jit )
    {
      CurrentIP = GetCurrentIP();
      EEPolicy::HandleFatalError(0x80131506, CurrentIP, L"Failed to load JIT compiler", 0i64, 0i64, 0i64);
      __debugbreak();
    }
    if ( !v10->m_alternateJit )
    {
      v46 = GetCurrentIP();
      EEPolicy::HandleFatalError(0x80131506, v46, L"Failed to load alternative JIT compiler", 0i64, 0i64, 0i64);
LABEL_89:
      RealCOMPlusThrow(kInvalidProgramException);
    }
  }
  */
  wchar_t aFailedToLoadJi[] = L"Failed to load JIT compiler";
  auto paFailedToLoadJi = MemDbg::findBytes(aFailedToLoadJi, sizeof(aFailedToLoadJi), processStartAddress, processStopAddress);
  if (!paFailedToLoadJi)
    return false;
  auto lea_aFailedToLoadJi = MemDbg::find_leaorpush_addr(paFailedToLoadJi, processStartAddress, processStopAddress);
  if (!lea_aFailedToLoadJi)
    return false;
  ConsoleOutput("lea_aFailedToLoadJi %p", lea_aFailedToLoadJi - processStartAddress);
  BYTE funcstart[] = {0x48, 0x89, 0x5c, 0x24, 0x10, 0x55, 0x56, 0x57, 0x41, 0x54, 0x41, 0x55, 0x41, 0x56, 0x41, 0x57};
  auto UnsafeJitFunction = reverseFindBytes(funcstart, sizeof(funcstart), lea_aFailedToLoadJi - 0x1000, lea_aFailedToLoadJi);
  if (!UnsafeJitFunction)
    return false;
  ConsoleOutput("UnsafeJitFunction %p", UnsafeJitFunction - processStartAddress);
  BYTE sig_call_invokeCompileMethodHelper[] = {
      0x48, 0x8D, 0x44, 0x24, XX,   // lea rax,[rbp+xx]
      0x48, 0x89, 0x44, 0x24, 0x28, // mov [rsp+28],rax
      0x48, 0x8d, 0x45, XX,         // lea rax,[rbp-xx]
      0x48, 0x89, 0x44, 0x24, 0x20, // mov [rsp+20],rax
      0x4c, 0x8d, 0x8d, XX4,        // lea r9,[rbp+xx]
      0x4c, 0x8d, 0x85, XX4,        // lea r8,[rbp+xx]
      0x48, 0x8d, 0x95, XX4,        // lea rdx,[rbp+xx]
      0x49, 0x8b, 0xcc,             // mov rcx,r12
      0xe8, XX4};
  auto call_invokeCompileMethodHelper = MemDbg::findBytes(sig_call_invokeCompileMethodHelper, sizeof(sig_call_invokeCompileMethodHelper), UnsafeJitFunction, UnsafeJitFunction + 0x1000);
  if (!call_invokeCompileMethodHelper)
    return call_invokeCompileMethodHelper;
  BYTE sig_getMethodNameFromMetadata[] = {
      0x41, 0xb8, 0xff, 0x0f, 0x00, 0x00,
      0x66, 0x41, 0x23, 0xc8,
      0x0f, 0xb7, 0x02,
      0x66, 0x41, 0x23, 0xc0,
      0x44, 0x0f, 0xb7, 0xc9,
      0x41, 0x81, 0xc9, 0x00, 0x60, 0x00, 0x00,
      0x41, 0xc1, 0xe1, 0x0c};
  auto ptr_sig_getMethodNameFromMetadata = MemDbg::findBytes(sig_getMethodNameFromMetadata, sizeof(sig_getMethodNameFromMetadata), processStartAddress, processStopAddress);
  if (!ptr_sig_getMethodNameFromMetadata)
    return false;
  BYTE start_getMethodNameFromMetadata[] = {0x48, 0x89, XX, XX};
  getMethodNameFromMetadata = (decltype(getMethodNameFromMetadata))reverseFindBytes(start_getMethodNameFromMetadata, sizeof(start_getMethodNameFromMetadata), ptr_sig_getMethodNameFromMetadata - 0x100, ptr_sig_getMethodNameFromMetadata, 0, true);
  if (!getMethodNameFromMetadata)
    return false;
  ConsoleOutput("getMethodNameFromMetadata %p", (uintptr_t)getMethodNameFromMetadata - processStartAddress);
  HookParam hp_invokeCompileMethodHelper;
  hp_invokeCompileMethodHelper.address = *(int *)(call_invokeCompileMethodHelper + sizeof(sig_call_invokeCompileMethodHelper) - 4) + call_invokeCompileMethodHelper + sizeof(sig_call_invokeCompileMethodHelper);
  hp_invokeCompileMethodHelper.user_value = (uintptr_t) new passinfo{};
  hp_invokeCompileMethodHelper.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto methodInfo = (CORINFO_METHOD_INFO *)context->r8;

    const char *className;
    const char *namespaceName;
    const char *enclosingClassName;
    auto methodname = getMethodNameFromMetadata((CEEInfo *)context->rdx, methodInfo->ftn, &className, &namespaceName, &enclosingClassName);
    if (!methodname)
    {
      ((passinfo *)hp->user_value)->nativeEntry = 0;
    }
    else
    {
      ((passinfo *)hp->user_value)->nativeEntry = (void **)context->stack[5];
      ((passinfo *)hp->user_value)->methodname = methodname;
      ((passinfo *)hp->user_value)->className = className;
      ((passinfo *)hp->user_value)->namespaceName = namespaceName;
      // ((passinfo *)hp->user_value)->enclosingClassName = enclosingClassName;
    }
  };
  bool succ = NewHook(hp_invokeCompileMethodHelper, "invokeCompileMethodHelper");
  BYTE sig_call_FlushInstructionCache[] = {
      /*
      .text:0000000140086454                 call    cs:__imp_GetCurrentProcess
  .text:000000014008645A                 mov     config, rax     ; hProcess
  .text:000000014008645D                 mov     r8d, ebx        ; dwSize
  .text:0000000140086460                 mov     ILHeader, rsi   ; lpBaseAddress
  .text:0000000140086463                 call    cs:__imp_FlushInstructionCache
      */
      0xFF, 0x15, XX4,
      0x48, 0x8B, XX,
      0x44, 0x8B, XX,
      0x48, 0x8B, XX,
      0xFF, 0x15, XX4};
  auto ptr_sig_call_FlushInstructionCache = MemDbg::findBytes(sig_call_FlushInstructionCache, sizeof(sig_call_FlushInstructionCache), hp_invokeCompileMethodHelper.address, hp_invokeCompileMethodHelper.address + 0x1000);
  if (!ptr_sig_call_FlushInstructionCache)
    return false;
  HookParam hp_call_FlushInstructionCache;
  hp_call_FlushInstructionCache.address = ptr_sig_call_FlushInstructionCache + sizeof(sig_call_FlushInstructionCache) - 6;
  hp_call_FlushInstructionCache.user_value = hp_invokeCompileMethodHelper.user_value;
  hp_call_FlushInstructionCache.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto info = (passinfo *)hp->user_value;
    if (!info->nativeEntry)
      return;
    if (info->methodname != "RegisterFunction")
      return;
    if (info->className != "Translator")
      return;
    // Ryujinx.HLE.HOS:ArmProcessContext`1:Initialize
    // Ryujinx.Cpu.Jit:JitCpuContext:Execute
    HookParam hp_cs_function;
    hp_cs_function.address = *(uintptr_t *)info->nativeEntry;
    hp_cs_function.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      ConsoleOutput("%s\n%p %p %p %p %p %p", hp->name, context->rcx, context->rdx, context->r8, context->r9, context->r10, context->r11);
    };
    NewHook(hp_cs_function, (info->namespaceName + ":" + info->className + ":" + info->methodname).c_str());
  };
  succ |= NewHook(hp_call_FlushInstructionCache, "FlushInstructionCache");
  return succ;
}