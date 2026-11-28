#include "Bakin.h"
#include "metahost.h"
#include <atlbase.h>

/**
 * RPG Developer Bakin (スマイルツール) games run on the SGB engine runtime:
 *
 *   sgb_rpgplayer (renamed per game, C# / Yukar.Engine, 32-bit, CLR 4)
 *     -> SharpKmyCore.dll (C++/CLI) -> kmyCore.dll (native) + data.sgbpack
 *
 * Only the managed layer is hookable - the kmyCore draw calls re-submit
 * sliced partial strings every frame. Since the player exe is renamed per
 * game, types are located by searching every loaded assembly: a tiny managed
 * helper (BakinClrHelper.dll, built from engine32/BakinClrHelper.cs by the
 * LunaBakinClrHelperDll target and shipped next to LunaHook32.dll, like
 * LunaTmpFontLoader) runs inside the game's CLR via
 * ICLRRuntimeHost::ExecuteInDefaultAppDomain (mscoree CorBindToRuntimeEx;
 * the ICLRRuntimeHost declarations live in the vendored metahost.h, which
 * the Windows SDK no longer ships).
 *
 * Managed x86 calling convention, verified against the JITted code: this in
 * ecx, the FIRST parameter in edx, parameters 2..n on the stack (stack[0] is
 * the return address, so argN lives at stack[N-1]), callee cleanup of the
 * stack part only. System.String on x86:
 * [MethodTable*][int Length][UTF-16LE chars].
 */

namespace
{
  // executes the managed helper inside the game's CLR: calls LunaCLRH.M.<entry>
  // with arg and puts its DWORD return value into *ret
  bool bakin_clr_execute(const wchar_t *helperPath, const wchar_t *entry, const char *arg, DWORD *ret)
  {
    CComPtr<ICLRRuntimeHost> host;
    if (FAILED(CorBindToRuntimeEx(L"v4.0.30319", nullptr, 0, CLSID_CLRRuntimeHost, IID_ICLRRuntimeHost,
                                  (void **)&host)) ||
        !host)
      return false;
    host->Start(); // no-op / S_FALSE when the game CLR is already running
    wchar_t warg[256];
    MultiByteToWideChar(CP_ACP, 0, arg, -1, warg, 256);
    DWORD val = 0;
    HRESULT hr = host->ExecuteInDefaultAppDomain(helperPath, L"LunaCLRH.M", entry, warg, &val);
    if (SUCCEEDED(hr) && val)
    {
      *ret = val;
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
    int strArg;         // 1-based index of the argument carrying the text
  };
  // enqueue-time: MapScene::PushMessage is called once per dialogue BLOCK
  // (verified against Bubblydoll Wildmachine, common 1.12.7.4), so these see
  // whole blocks; the per-line display-time source is the typewriter hook
  // below
  const BakinClrTarget bakin_clr_targets[] = {
      {"Yukar.Engine.MapScene", "PushMessage", 3, 1},
      {"Yukar.Engine.MessageWindow", "PushMessage", 3, 1},
  };

  bool bakin_insert_clr_hooks(const std::wstring &helperPath)
  {
    bool ok = false;
    for (auto &t : bakin_clr_targets)
    {
      char arg[256];
      sprintf_s(arg, "%s|%s|%d", t.type, t.method, t.params);
      DWORD addr = 0;
      if (!bakin_clr_execute(helperPath.c_str(), L"GetAddr", arg, &addr))
        continue;
      HookParam hp;
      hp.address = addr;
      hp.offset = t.strArg == 1 ? regoffset(edx) : 4 * (t.strArg - 1);
      hp.type = USING_STRING | CODEC_UTF16 | NO_CONTEXT | FULL_STRING;
      hp.text_fun = bakin_clr_text_fun;
      std::string name = std::string(t.type) + "." + t.method;
      ok |= NewHook(hp, name.c_str());
    }
    return ok;
  }

  // ---------------------------------------------------------------------
  // typewriter hook: MessageEntry.drawStringWithCommands(
  //                      TextDrawer, Vector2, int, float, float)
  //
  // MessageWindow::Draw() calls it every visible frame with this = the
  // displayed MessageEntry (one page = several sentences). The entry's
  // parts (List<MessageParts>) hold per-fragment text, line number and
  // endTime, and entry.time is the reveal clock - a line is fully typed
  // exactly when every part of it has endTime <= time, so each newly
  // completed line is emitted (concatenated part texts; ruby is a separate
  // field). SpriteManager+TextSprite::Draw calls this too with its own
  // entries, interleaved with the message window - hence the per-page slot
  // cache in the text_fun.
  // ---------------------------------------------------------------------

  // resolved by the helper at insertion time: managed auto layout reorders
  // fields, so no offset can be hardcoded
  static int bakin_off_entry_time;   // MessageEntry::time        (float)
  static int bakin_off_entry_parts;  // MessageEntry::parts       (List<MessageParts>)
  static int bakin_off_list_items;   // List<MessageParts>::_items (array)
  static int bakin_off_list_size;    // List<MessageParts>::_size  (int)
  static int bakin_off_part_endtime; // MessageParts::endTime     (float)
  static int bakin_off_part_line;    // MessageParts::line        (int)
  static int bakin_off_part_text;    // MessageParts::text        (String)

  struct BakinPageState
  {
    std::wstring first; // first part's text = page identity
    int watermark;      // last emitted line index of that page
  };

  void bakin_clr_typewriter_text_fun(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto entry = (uintptr_t)context->offset(hp->offset, *hp); // this = MessageEntry
    if (entry <= 0x10000 || (entry & 3))
      return;
    auto list = *(const uintptr_t *)(entry + bakin_off_entry_parts);
    if (list <= 0x10000 || (list & 3))
      return;
    auto items = *(const uintptr_t *)(list + bakin_off_list_items);
    auto count = *(const int *)(list + bakin_off_list_size);
    if (items <= 0x10000 || count <= 0 || count > 512)
      return;
    if (*(const int *)(items + 4) < count) // array: [MT][length][elements]
      return;
    auto time = *(const float *)(entry + bakin_off_entry_time);

    // page identity = content of the first part carrying text: a pointer
    // would not survive GC compaction between frames
    const ClrString *first = nullptr;
    for (int i = 0; i < count && !first; i++)
    {
      auto part = *(const uintptr_t *)(items + 8 + 4 * i);
      if (part <= 0x10000 || (part & 3))
        return;
      auto t = (const ClrString *)(*(const uintptr_t *)(part + bakin_off_part_text));
      if ((uintptr_t)t > 0x10000 && t->length > 0 && t->length < 4096)
        first = t;
    }
    if (!first)
      return;

    // per-page watermark slot cache (see the section comment above)
    static BakinPageState pages[4];
    static int victim = 0;
    BakinPageState *slot = nullptr;
    for (auto &p : pages)
      if (p.first.size() == (size_t)first->length &&
          memcmp(p.first.data(), first->chars, first->length * sizeof(wchar_t)) == 0)
      {
        slot = &p;
        break;
      }
    if (!slot)
    {
      for (auto &p : pages)
        if (p.first.empty())
        {
          slot = &p;
          break;
        }
      if (!slot)
        slot = &pages[victim], victim = (victim + 1) % 4;
      slot->first.assign(first->chars, first->length);
      slot->watermark = -1;
    }
    int watermark = slot->watermark;

    // walk the parts in order, grouped by line number
    int curLine = -1;
    bool curComplete = true;
    bool emitted = false;
    std::wstring lineText;
    for (int i = 0; i < count; i++)
    {
      auto part = *(const uintptr_t *)(items + 8 + 4 * i);
      if (part <= 0x10000 || (part & 3))
        return;
      auto text = (const ClrString *)(*(const uintptr_t *)(part + bakin_off_part_text));
      int line = *(const int *)(part + bakin_off_part_line);
      bool complete = *(const float *)(part + bakin_off_part_endtime) <= time;

      if (line != curLine)
      {
        // emit the first newly completed line; one per call, the per-frame
        // calls pace out the rest
        if (!emitted && curLine >= 0 && curComplete && curLine > watermark)
        {
          buffer->from(lineText.data(), lineText.size() * sizeof(wchar_t));
          watermark = curLine;
          emitted = true;
        }
        curLine = line;
        curComplete = complete;
        lineText.clear();
      }
      else if (!complete)
        curComplete = false;

      if ((uintptr_t)text > 0x10000 && text->length > 0 && text->length < 4096)
        lineText.append(text->chars, text->length);
    }
    if (!emitted && curLine >= 0 && curComplete && curLine > watermark)
    {
      buffer->from(lineText.data(), lineText.size() * sizeof(wchar_t));
      watermark = curLine;
      emitted = true;
    }
    slot->watermark = watermark;
  }

  bool bakin_insert_typewriter_hook(const std::wstring &helperPath)
  {
    // ばぶりーどーる/わいるどましーん
    const char *type = "Yukar.Engine.MessageWindow+MessageEntry";
    const char *method = "drawStringWithCommands";
    const struct
    {
      const char *arg;
      int *out;
    } probes[] = {
        {"Yukar.Engine.MessageWindow+MessageEntry|time", &bakin_off_entry_time},
        {"Yukar.Engine.MessageWindow+MessageEntry|parts", &bakin_off_entry_parts},
        {"Yukar.Engine.MessageWindow+MessageEntry|parts|_items", &bakin_off_list_items},
        {"Yukar.Engine.MessageWindow+MessageEntry|parts|_size", &bakin_off_list_size},
        {"Yukar.Engine.MessageWindow+MessageEntry+MessageParts|endTime", &bakin_off_part_endtime},
        {"Yukar.Engine.MessageWindow+MessageEntry+MessageParts|line", &bakin_off_part_line},
        {"Yukar.Engine.MessageWindow+MessageEntry+MessageParts|text", &bakin_off_part_text},
    };
    for (auto &pr : probes)
    {
      DWORD off = 0;
      if (!bakin_clr_execute(helperPath.c_str(), L"GetTypeFieldOffset", pr.arg, &off))
        return false;
      *pr.out = (int)off;
    }
    char arg[256];
    sprintf_s(arg, "%s|%s|5", type, method);
    DWORD addr = 0;
    if (!bakin_clr_execute(helperPath.c_str(), L"GetAddr", arg, &addr))
      return false;
    HookParam hp;
    hp.address = addr;
    // managed x86 calling convention: this in ecx
    hp.offset = regoffset(ecx);
    hp.type = USING_STRING | CODEC_UTF16 | NO_CONTEXT; // | FULL_STRING;
    hp.text_fun = bakin_clr_typewriter_text_fun;
    std::string name = std::string(type) + "." + method;
    return NewHook(hp, name.c_str());
  }

}

bool Bakin::attach_function()
{
  auto helperPath = bakin_helper_path();
  if (GetFileAttributesW(helperPath.c_str()) == INVALID_FILE_ATTRIBUTES)
    return false;
  return bakin_insert_clr_hooks(helperPath) | bakin_insert_typewriter_hook(helperPath);
}
