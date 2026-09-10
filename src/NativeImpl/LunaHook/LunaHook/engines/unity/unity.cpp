#include "unity.h"

#include "mono.def.hpp"
#include "monoil2cpp.h"
#include <memory>
namespace
{

  void mscorlib_system_string_InternalSubString_hook_fun(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    uintptr_t offset = context->argof(1, hp);
    uintptr_t startIndex = context->argof(2, hp);
    uintptr_t length = context->argof(3, hp);

    MonoString *string = (MonoString *)offset;
    if (string == 0)
      return;
    auto data = (uintptr_t)(startIndex + string->chars);
    if (wcslen((wchar_t *)data) < length)
      return;
    buffer->from(data, length * 2);
  }

  void tmpfilter(TextBuffer *buffer, HookParam *)
  {
    auto s = buffer->strW();
    s = re::sub(s, LR"(<line-height=[^>]*?>)");
    s = re::sub(s, LR"(<sprite anim=[^>]*?>)");
    buffer->from(s);
  }
  void tmpembed(hook_context *context, TextBuffer buffer, HookParam *hp)
  {
    unity_ui_string_embed_fun(context->argof(hp->offset, hp), buffer);
    g_monoil2cpp->apply_font((void *)context->argof_thiscall());
  }

#ifdef _WIN64
  void Naninovel_UI_RevealableText_SetTextValue_Filter(TextBuffer *buffer, HookParam *hp)
  {
    auto s = buffer->strW();
    strReplace(s, L"<br>");
    s = re::sub(s, L"<ruby.*?>(.*?)</ruby>", L"$1");
    buffer->from(s);
  }
#endif
  struct functioninfo
  {
    const char *assemblyName;
    const char *namespaze;
    const char *klassName;
    const char *name;
    int argsCount;
    int offset;
    decltype(HookParam::text_fun) text_fun = nullptr;
    bool Embed = false;
    bool isstring = true;
    const wchar_t *lineSeparator = nullptr;
    decltype(HookParam::filter_fun) filter_fun = nullptr;
    decltype(HookParam::embed_fun) embed_fun = nullptr;

    bool createhook(bool strict)
    {
      auto addr = (uintptr_t)g_monoil2cpp->get_method_pointer(assemblyName, namespaze, klassName, name, argsCount, strict);
      if (!addr)
        return false;

      HookParam hp;
      hp.address = addr;
      hp.offset = offset;
      hp.lineSeparator = lineSeparator;
      hp.text_fun = text_fun;
      hp.filter_fun = filter_fun;
      hp.embed_fun = embed_fun;
      if (isstring)
      {
        hp.type = USING_STRING | CODEC_UTF16 | FULL_STRING;
        if (!hp.text_fun)
          hp.type |= CSHARP_STRING;
        if (Embed)
          hp.type |= EMBED_ABLE;
      }
      else
      {
        hp.type = USING_CHAR | CODEC_UTF16;
      }
      hp.jittype = JITTYPE::UNITY;
      sprintf(hp.function, "%s:%s:%s:%s:%d", assemblyName, namespaze, klassName, name, argsCount);
      char name[1024];
      sprintf(name, "%s:%s", klassName, name);
      return NewHook(hp, name);
    }
  };
  functioninfo commonhooks[] = {
      {"mscorlib", "System", "String", "ToCharArray", 0, 1},
      {"mscorlib", "System", "String", "Replace", 2, 1},
      //{"mscorlib","System","String","ToString",0,1},
      // 虽然可能会有少量误伤，但这个乱码太多了，而且不知道原因，为了大多数更好，还是删了吧。
      // 一定要用的话，用特殊码：HMF1@mscorlib:System:String:ToString:0:JIT:UNITY
      {"mscorlib", "System", "String", "IndexOf", 1, 1},
      {"mscorlib", "System", "String", "Substring", 2, 1, mscorlib_system_string_InternalSubString_hook_fun}, // 这个如果不加截断，对于部分游戏，会导致host.output内存占用爆炸多，直接爆内存。可能会影响部分游戏，待测试。
      {"mscorlib", "System", "String", "op_Inequality", 2, 1},
      {"mscorlib", "System", "String", "InternalSubString", 2, 1, mscorlib_system_string_InternalSubString_hook_fun},

      {"Unity.TextMeshPro", "TMPro", "TMP_Text", "set_text", 1, 2, nullptr, true, true, nullptr, tmpfilter, tmpembed},
      {"Unity.TextMeshPro", "TMPro", "TextMeshPro", "set_text", 1, 2, nullptr, true, true, nullptr, tmpfilter, tmpembed},
      {"Unity.TextMeshPro", "TMPro", "TextMeshProUGUI", "SetText", 2, 2, nullptr, true, true, nullptr, tmpfilter, tmpembed},
      {"UnityEngine.UI", "UnityEngine.UI", "Text", "set_text", 1, 2, nullptr, true},
      {"UnityEngine.UIElementsModule", "UnityEngine.UIElements", "TextElement", "set_text", 1, 2, nullptr, true},
      {"UnityEngine.UIElementsModule", "UnityEngine.UIElements", "TextField", "set_value", 1, 2, nullptr, true},
      {"UnityEngine.TextRenderingModule", "UnityEngine", "GUIText", "set_text", 1, 2, nullptr, true},
      {"UnityEngine.TextRenderingModule", "UnityEngine", "TextMesh", "set_text", 1, 2, nullptr, true},
      {"UGUI", "", "UILabel", "set_text", 1, 2, nullptr, true},
  };
  functioninfo extrahooks[] = {
      // https://vndb.org/r37234 && https://vndb.org/r37235
      // Higurashi When They Cry Hou - Ch.2 Watanagashi && Higurashi When They Cry Hou - Ch.3 Tatarigoroshi
      {"Assembly-CSharp", "Assets.Scripts.Core.TextWindow", "TextController", "SetText", 4, 3, nullptr, true},
      // Higurashi When They Cry Hou - Rei ひぐらしのなく頃に礼
      {"Assembly-CSharp", "Assets.Scripts.Core.TextWindow", "TextController", "SetText", 5, 3, nullptr, true},
      // 逆転裁判123 成歩堂セレクション
      {"Assembly-CSharp", "", "MessageText", "Append", 1, 2, nullptr, false, false},
#ifdef _WIN64
      // 神託の使徒×終焉の女神
      {"Assembly-CSharp", "", "TextManager", "SetText", 1, 2, nullptr, true, true, LR"(\n)"},
      // 魔法少女ノ魔女裁判
      {"Elringus.Naninovel.Runtime", "Naninovel.UI", "RevealableText", "SetTextValue", 1, 2, nullptr, true, true, nullptr, Naninovel_UI_RevealableText_SetTextValue_Filter},
#endif
  };
  bool hook_mono_il2cpp()
  {
    for (const wchar_t *monoName : {L"mono.dll", L"mono-2.0-bdwgc.dll", L"GameAssembly.dll"})
    {
      HMODULE module = GetModuleHandleW(monoName);
      if (!module)
        continue;
      bool il2cpp = wcscmp(monoName, L"GameAssembly.dll") == 0;
      std::unique_ptr<monoil2cpp> runtime(il2cpp ? create_il2cpp_runtime(module) : create_mono_runtime(module));
      g_monoil2cpp = runtime.get();
      bool succ = false;
      using infos = std::tuple<functioninfo *, size_t, bool>;
      for (auto &&[hooks, size, strict] : {infos{commonhooks, ARRAYSIZE(commonhooks), false}, infos{extrahooks, ARRAYSIZE(extrahooks), true}})
      {
        for (auto i = 0; i < size; i++)
        {
          auto &hook = hooks[i];
          succ |= hook.createhook(strict);
        }
      }
      if (succ)
      {
        patch_fun = []()
        { g_monoil2cpp->ensure_tmp_font_loaded(); };
        runtime.release();
        return true;
      }
      g_monoil2cpp = nullptr;
    }
    return false;
  }
}

bool Unity::attach_function_()
{
  return hook_mono_il2cpp();
}