#include "Bakin.h"
#include "metahost.h"
#include <atlbase.h>

/**
 * RPG Developer Bakin (スマイルツール) games run on the SGB engine runtime:
 *
 *   sgb_rpgplayer (shinobim_s.exe, C# / Yukar.Engine, 32-bit, CLR 4)
 *     -> SharpKmyCore.dll (C++/CLI) -> kmyCore.dll (native) + data.sgbpack
 *
 * The managed layer is the only hook source needed (the kmyCore.dll draw calls
 * re-submit sliced partial strings every frame and produce garbage). The game
 * event system pushes complete message strings to
 * Yukar.Engine.MapScene::PushMessage(str, winAlign, winType), which forwards
 * to Yukar.Engine.MessageWindow::PushMessage - one call per message, whole
 * sentence, before the TextDrawer typewriter slices the string. Only after
 * that does the sliced partial reach the native layer.
 *
 * Because the player exe is renamed per game, types are located by searching
 * every loaded assembly; a tiny managed helper (BakinClrHelper.dll, compiled
 * from engine32/BakinClrHelper.cs by the LunaBakinClrHelperDll CMake target and
 * shipped next to LunaHook32.dll, like LunaTmpFontLoader) runs inside the
 * game's own CLR through ICLRRuntimeHost::ExecuteInDefaultAppDomain and
 * resolves the JIT-compiled method entry point via reflection
 * (RuntimeHelpers.PrepareMethod + MethodHandle.GetFunctionPointer).
 *
 * metahost.h is no longer shipped with the Windows SDK (the pieces moved to
 * the NETFXSDK component), so the needed ICLRRuntimeHost declarations live in
 * the vendored LunaHook/metahost.h, and the interface is obtained through the
 * mscoree export CorBindToRuntimeEx.
 *
 * Managed x86 calling convention (verified against the JITted code in the
 * live game): this in ecx, the FIRST parameter in edx, parameters 2..n on the
 * stack, callee cleanup of the stack part only. System.String on x86:
 * [MethodTable*][int Length][UTF-16LE chars].
 */

namespace
{
  // executes the managed helper inside the game's CLR and returns
  // the JIT-compiled entry point of "type|method|paramCount"
  bool bakin_clr_method_addr(const wchar_t *helperPath, const char *type, const char *method, int params, DWORD *addr)
  {
    CComPtr<ICLRRuntimeHost> host;
    if (FAILED(CorBindToRuntimeEx(L"v4.0.30319", nullptr, 0, CLSID_CLRRuntimeHost, IID_ICLRRuntimeHost,
                                  (void **)&host)) ||
        !host)
      return false;
    host->Start(); // no-op / S_FALSE when the game CLR is already running
    char arg[256];
    sprintf_s(arg, "%s|%s|%d", type, method, params);
    wchar_t warg[256];
    MultiByteToWideChar(CP_ACP, 0, arg, -1, warg, 256);
    DWORD ret = 0;
    HRESULT hr = host->ExecuteInDefaultAppDomain(helperPath, L"LunaCLRH.M", L"GetAddr", warg, &ret);
    if (SUCCEEDED(hr) && ret)
    {
      *addr = ret;
      return true;
    }
    return false;
  }

  // BakinClrHelper.dll is built into the same directory as this dll (see the
  // LunaBakinClrHelperDll CMake target), exactly like LunaTmpFontLoader.dll
  std::wstring bakin_helper_path()
  {
    wchar_t dllpath[MAX_PATH];
    GetModuleFileNameW((HMODULE)&__ImageBase, dllpath, MAX_PATH);
    std::wstring p(dllpath);
    return p.substr(0, p.find_last_of(L"\\/") + 1) + L"BakinClrHelper.dll";
  }

  // managed System.String on x86: [MethodTable*][int Length][UTF-16LE chars]
  struct ClrString
  {
    const void *methodTable;
    int length;
    const wchar_t chars[1];
  };

  void bakin_clr_text_fun(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto str = (const ClrString *)(uintptr_t)context->offset(hp->offset, *hp);
    if ((uintptr_t)str <= 0x10000 || ((uintptr_t)str & 3))
      return;
    if (str->length <= 0 || str->length > 4096)
      return;
    buffer->from(str->chars, str->length * sizeof(wchar_t));
  }

  struct BakinClrTarget
  {
    const char *type;   // namespace-qualified managed type name
    const char *method; // method name
    int params;         // parameter count, to disambiguate overloads
    const char *name;   // hook name
  };
  // the string is the first parameter of every entry below
  const BakinClrTarget bakin_clr_targets[] = {
      {"Yukar.Engine.MapScene", "PushMessage", 3, "Bakin_PushMessage"},
      {"Yukar.Engine.MessageWindow", "PushMessage", 3, "Bakin_WinPushMessage"},
      {"Yukar.Engine.MessageWindow", "SetMessageText", 1, "Bakin_SetMessageText"},
      {"Yukar.Engine.BattleViewer", "SetDisplayMessage", 2, "Bakin_BattleMessage"},
      {"Yukar.Engine.ToastWindow", "show", 1, "Bakin_Toast"},
      {"Yukar.Engine.ScriptRunner", "FuncTelopImpl", 2, "Bakin_Telop"},
  };

  bool bakin_insert_clr_hooks()
  {
    auto helperPath = bakin_helper_path();
    if (GetFileAttributesW(helperPath.c_str()) == INVALID_FILE_ATTRIBUTES)
      return false; // helper not shipped alongside this dll
    bool ok = false;
    for (auto &t : bakin_clr_targets)
    {
      DWORD addr = 0;
      if (!bakin_clr_method_addr(helperPath.c_str(), t.type, t.method, t.params, &addr))
        continue;
      HookParam hp;
      hp.address = addr;
      // managed x86 calling convention (verified against the JITted code in the
      // live game): this in ecx, the FIRST parameter in edx, parameters 2..n
      // on the stack, callee cleanup of the stack part only
      hp.offset = regoffset(edx);
      hp.type = USING_STRING | CODEC_UTF16 | NO_CONTEXT | FULL_STRING;
      hp.text_fun = bakin_clr_text_fun;
      ok |= NewHook(hp, t.name);
    }
    return ok;
  }

}

bool Bakin::attach_function()
{
  return bakin_insert_clr_hooks();
}
