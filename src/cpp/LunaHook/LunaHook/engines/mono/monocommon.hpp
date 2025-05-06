#include "def_mono.hpp"
#include "def_il2cpp.hpp"
#include "monostringapis.h"
namespace
{

    void mscorlib_system_string_InternalSubString_hook_fun(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        uintptr_t offset = context->argof(1);
        uintptr_t startIndex = context->argof(2);
        uintptr_t length = context->argof(3);

        MonoString *string = (MonoString *)offset;
        if (string == 0)
            return;
        auto data = (uintptr_t)(startIndex + string->chars);
        if (wcslen((wchar_t *)data) < length)
            return;
        buffer->from(data, length * 2);
    }

    /** jichi 12/26/2014 Mono
     *  Sample game: [141226] ハ�レ�めいと
     */
    void SpecialHookMonoString(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        if (auto sw = commonsolvemonostring(context->argof(1)))
            buffer->from(sw.value());

#ifndef _WIN64
        auto s = context->ecx;
        for (int i = 0; i < 0x10; i++) // traverse pointers until a non-readable address is met
            if (s && !::IsBadReadPtr((LPCVOID)s, sizeof(DWORD)))
                s = *(DWORD *)s;
            else
                break;
        if (!s)
            s = hp->address;
        if (hp->type & USING_SPLIT)
            *split = s;
#endif
    }

}

namespace monocommon
{

    bool monodllhook(HMODULE module)
    {
        HookParam hp;
        const MonoFunction funcs[] = {MONO_FUNCTIONS_INITIALIZER};
        for (auto func : funcs)
        {
            if (FARPROC addr = GetProcAddress(module, func.functionName))
            {
                hp.address = (uintptr_t)addr;
                hp.type = USING_STRING | func.hookType;
                hp.filter_fun = all_ascii_Filter;
                hp.offset = stackoffset(func.textIndex);
                hp.text_fun = (decltype(hp.text_fun))func.text_fun;
                ConsoleOutput("Mono: INSERT");
                NewHook(hp, func.functionName);
            }
        }
        return true;
    }
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
        std::string hookname()
        {
            char tmp[1024];
            sprintf(tmp, "%s:%s", klassName, name);
            return tmp;
        }
        std::string info()
        {
            char tmp[1024];
            sprintf(tmp, "%s:%s:%s:%s:%d", assemblyName, namespaze, klassName, name, argsCount);
            return tmp;
        }
    };
    bool NewHook_check(uintptr_t addr, functioninfo &hook)
    {

        HookParam hp;
        hp.address = addr;
        hp.offset = hook.offset;
        hp.lineSeparator = hook.lineSeparator;
        hp.text_fun = (decltype(hp.text_fun))hook.text_fun;
        if (hook.isstring)
        {
            hp.type = USING_STRING | CODEC_UTF16 | FULL_STRING;
            if (!hp.text_fun)
                hp.type |= CSHARP_STRING;
            if (hook.Embed)
                hp.type |= EMBED_ABLE;
        }
        else
        {
            hp.type = USING_CHAR | CODEC_UTF16;
        }
        hp.jittype = JITTYPE::UNITY;
        strcpy(hp.function, hook.info().c_str());
        auto succ = NewHook(hp, hook.hookname().c_str());
#ifdef _WIN64
        if (!succ)
        {
            hp.type |= BREAK_POINT;
            succ |= NewHook(hp, hook.hookname().c_str());
        }
#endif
        return succ;
    }
    std::vector<functioninfo> commonhooks{
        {"mscorlib", "System", "String", "ToCharArray", 0, 1},
        {"mscorlib", "System", "String", "Replace", 2, 1},
        //{"mscorlib","System","String","ToString",0,1},
        // 虽然可能会有少量误伤，但这个乱码太多了，而且不知道原因，为了大多数更好，还是删了吧。
        // 一定要用的话，用特殊码：HMF1@mscorlib:System:String:ToString:0:JIT:UNITY
        {"mscorlib", "System", "String", "IndexOf", 1, 1},
        {"mscorlib", "System", "String", "Substring", 2, 1, mscorlib_system_string_InternalSubString_hook_fun}, // 这个如果不加截断，对于部分游戏，会导致host.output内存占用爆炸多，直接爆内存。可能会影响部分游戏，待测试。
        {"mscorlib", "System", "String", "op_Inequality", 2, 1},
        {"mscorlib", "System", "String", "InternalSubString", 2, 1, mscorlib_system_string_InternalSubString_hook_fun},

        {"Unity.TextMeshPro", "TMPro", "TMP_Text", "set_text", 1, 2, nullptr, true},
        {"Unity.TextMeshPro", "TMPro", "TextMeshPro", "set_text", 1, 2, nullptr, true},
        {"Unity.TextMeshPro", "TMPro", "TextMeshProUGUI", "SetText", 2, 2, nullptr, true},
        {"UnityEngine.UI", "UnityEngine.UI", "Text", "set_text", 1, 2, nullptr, true},
        {"UnityEngine.UIElementsModule", "UnityEngine.UIElements", "TextElement", "set_text", 1, 2, nullptr, true},
        {"UnityEngine.UIElementsModule", "UnityEngine.UIElements", "TextField", "set_value", 1, 2, nullptr, true},
        {"UnityEngine.TextRenderingModule", "UnityEngine", "GUIText", "set_text", 1, 2, nullptr, true},
        {"UnityEngine.TextRenderingModule", "UnityEngine", "TextMesh", "set_text", 1, 2, nullptr, true},
        {"UGUI", "", "UILabel", "set_text", 1, 2, nullptr, true},
    };
    std::vector<functioninfo> extrahooks{
        // https://vndb.org/r37234 && https://vndb.org/r37235
        // Higurashi When They Cry Hou - Ch.2 Watanagashi && Higurashi When They Cry Hou - Ch.3 Tatarigoroshi
        {"Assembly-CSharp", "Assets.Scripts.Core.TextWindow", "TextController", "SetText", 4, 3, nullptr, true},
        // 逆転裁判123 成歩堂セレクション
        {"Assembly-CSharp", "", "MessageText", "Append", 1, 2, nullptr, false, false},
#ifdef _WIN64
        // 神託の使徒×終焉の女神
        {"Assembly-CSharp", "", "TextManager", "SetText", 1, 2, nullptr, true, true, LR"(\n)"},
#endif
    };
    bool hook_mono_il2cpp()
    {
        for (const wchar_t *monoName : {L"mono.dll", L"mono-2.0-bdwgc.dll", L"GameAssembly.dll"})
            if (HMODULE module = GetModuleHandleW(monoName))
            {
                // bool b2=monodllhook(module);
                il2cppfunctions::init(module);
                monofunctions::init(module);
                bool succ = false;
                for (auto hook : commonhooks)
                {
                    auto addr = tryfindmonoil2cpp(hook.assemblyName, hook.namespaze, hook.klassName, hook.name, hook.argsCount);
                    if (!addr)
                        continue;
                    succ |= NewHook_check(addr, hook);
                }
                for (auto hook : extrahooks)
                {
                    auto addr = tryfindmonoil2cpp(hook.assemblyName, hook.namespaze, hook.klassName, hook.name, hook.argsCount, true);
                    if (!addr)
                        continue;
                    succ |= NewHook_check(addr, hook);
                }
                if (succ)
                {
                    return true;
                }
            }
        return false;
    }
}