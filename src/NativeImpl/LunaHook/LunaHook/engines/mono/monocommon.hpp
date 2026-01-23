#include "def_mono.hpp"
#include "def_il2cpp.hpp"
#include "monostringapis.h"
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

    /** jichi 12/26/2014 Mono
     *  Sample game: [141226] ハ�レ�めいと
     */
    void SpecialHookMonoString(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        if (auto sw = commonsolvemonostring(context->argof(1, hp)))
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
    std::atomic<bool> usefonthook = false;

    void hook_GetTextElement()
    {
        // internal TMP_TextElement GetTextElement(uint unicode, TMP_FontAsset fontAsset, FontStyles fontStyle, FontWeight fontWeight, out bool isUsingAlternativeTypeface)
        auto addr = tryfindmonoil2cpp("Unity.TextMeshPro", "TMPro", "TMP_Text", "GetTextElement", -1);
        // public static AssetBundle LoadFromFile(string path)
        static auto LoadFromFile = tryfindmonoil2cppMethod("UnityEngine.AssetBundleModule", "UnityEngine", "AssetBundle", "LoadFromFile", 1);
        // public Object[] LoadAllAssets(Type type)
        static auto LoadAllAssets = tryfindmonoil2cpp("UnityEngine.AssetBundleModule", "UnityEngine", "AssetBundle", "LoadAllAssets", 0);
        static auto TMP_FontAsset = tryfindmonoil2cppClass("Unity.TextMeshPro", "TMPro", "TMP_FontAsset");

        // auto thread = AutoThread();
        static auto asset = LR"(.\arialuni_sdf_u2021)";
        auto assetpath = create_string_csharp(asset);
        static auto AssetBundle = mono_runtime_invoke((MonoMethod *)LoadFromFile, nullptr, &assetpath, nullptr);
        static auto assets = mono_runtime_invoke((MonoMethod *)LoadAllAssets, AssetBundle, nullptr, nullptr);
        // 先存一下。不知道为什么，调用LoadAllAssets就会崩溃。
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
        auto s = buffer.strW();
        if (auto sw = commonsolvemonostring(context->argof(hp->offset, hp)))
        {
            auto origin = std::wstring(sw.value());
            std::wstring pre = re::match(origin, LR"(((<line-height=[^>]*?>|<sprite anim=[^>]*?>)*)(.*?))").value()[1];
            std::wstring app = re::match(origin, LR"((.*?)((<line-height=[^>]*?>|<sprite anim=[^>]*?>)*))").value()[2];
            s = pre + s + app;
        }
        buffer.from(s);
    }
}
namespace
{
#ifdef _WIN64
    void Naninovel_UI_RevealableText_SetTextValue_Filter(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        strReplace(s, L"<br>");
        s = re::sub(s, L"<ruby.*?>(.*?)</ruby>", L"$1");
        buffer->from(s);
    }
#endif
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
        decltype(HookParam::filter_fun) filter_fun = nullptr;
        decltype(HookParam::embed_fun) embed_fun = nullptr;
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
        uintptr_t getaddr(bool _ = false)
        {
            return tryfindmonoil2cpp(assemblyName, namespaze, klassName, name, argsCount, _);
        }
    };
    bool NewHook_check(uintptr_t addr, functioninfo &hook)
    {
        HookParam hp;
        hp.address = addr;
        hp.offset = hook.offset;
        hp.lineSeparator = hook.lineSeparator;
        hp.text_fun = hook.text_fun;
        hp.filter_fun = hook.filter_fun;
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
        return NewHookRetry(hp, hook.hookname().c_str());
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
    std::vector<functioninfo> extrahooks{
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
            if (HMODULE module = GetModuleHandleW(monoName))
            {
                // bool b2=monodllhook(module);
                il2cppfunctions::init(module);
                monofunctions::init(module);
                bool succ = false;
                for (auto hook : commonhooks)
                {
                    auto addr = hook.getaddr();
                    if (!addr)
                        continue;
                    succ |= NewHook_check(addr, hook);
                }
                for (auto hook : extrahooks)
                {
                    auto addr = hook.getaddr(true);
                    if (!addr)
                        continue;
                    succ |= NewHook_check(addr, hook);
                }
                if (succ)
                {
                    if (0)
                    {
                        hook_GetTextElement();
                        patch_fun = []()
                        {
                            usefonthook = true;
                        };
                    }
                    return true;
                }
            }
        return false;
    }
}