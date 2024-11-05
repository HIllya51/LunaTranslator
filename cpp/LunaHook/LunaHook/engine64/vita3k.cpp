﻿#include "vita3k.h"
namespace
{
    auto isVirtual = true;
    auto idxDescriptor = isVirtual == true ? 2 : 1;
    auto idxEntrypoint = idxDescriptor + 1;
    uintptr_t getDoJitAddress()
    {
        auto RegisterBlockSig1 = "40 55 53 56 57 41 54 41 56 41 57 48 8D 6C 24 E9 48 81 EC 90 00 00 00 48 8B ?? ?? ?? ?? ?? 48 33 C4 48 89 45 07 4D 8B F1 49 8B F0 48 8B FA 48 8B D9 4C 8B 7D 77 48 8B 01 48 8D 55 C7 FF 50 10";
        auto first = find_pattern(RegisterBlockSig1, processStartAddress, processStopAddress);
        if (first)
            return first;
        /*
        // DebugSymbol: RegisterBlock
        // ?RegisterBlock@EmitX64@X64@Backend@Dynarmic@@IEAA?AUBlockDescriptor@1234@AEBVLocationDescriptor@IR@4@PEBX_K@Z <- new
        // ?RegisterBlock@EmitX64@X64@Backend@Dynarmic@@IEAA?AUBlockDescriptor@1234@AEBVLocationDescriptor@IR@4@PEBX1_K@Z
        const symbols = DebugSymbol.findFunctionsMatching(
            'Dynarmic::Backend::X64::EmitX64::RegisterBlock'
        );
        if (symbols.length !== 0) {
            console.warn('Sym RegisterBlock');
            return symbols[0];
        }
        */
        auto PatchBlockSig1 = "4C 8B DC 49 89 5B 10 49 89 6B 18 56 57 41 54 41 56 41 57"; // "4C 8B DC 49 89 5B ?? 49 89 6B ?? 56 57 41 54 41 56 41 57";
        first = find_pattern(PatchBlockSig1, processStartAddress, processStopAddress);
        if (first)
        {
            idxDescriptor = 1;
            idxEntrypoint = 2;
            return first;
        }
        return 0;
    }
    struct emfuncinfo
    {
        uint64_t type;
        int argidx;
        int padding;
        decltype(HookParam::text_fun) hookfunc;
        decltype(HookParam::filter_fun) filterfun;
        const char *_id;
    };
    std::unordered_map<uintptr_t, emfuncinfo> emfunctionhooks;

    bool checkiscurrentgame(const emfuncinfo &em)
    {
        auto wininfos = get_proc_windows();
        for (auto &&info : wininfos)
        {
            if (info.title.find(acastw(em._id)) != info.title.npos)
                return true;
        }
        return false;
    }
}

bool vita3k::attach_function()
{
    ConsoleOutput("[Compatibility] Vita3k 0.1.9 3520+");
    auto DoJitPtr = getDoJitAddress();
    if (DoJitPtr == 0)
        return false;
    ConsoleOutput("DoJitPtr %p", DoJitPtr);
    spDefault.jittype = JITTYPE::VITA3K;
    spDefault.minAddress = 0;
    spDefault.maxAddress = -1;
    HookParam hp;
    hp.address = DoJitPtr;
    hp.text_fun = [](hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto descriptor = *argidx(stack, idxDescriptor + 1); // r8
        auto entrypoint = *argidx(stack, idxEntrypoint + 1); // r9
        auto em_address = *(uint32_t *)descriptor;
        if (!entrypoint)
            return;
        // ConsoleOutput("%p",em_address);
        jitaddraddr(em_address, entrypoint, JITTYPE::VITA3K);
        [&]()
        {
            if (emfunctionhooks.find(em_address) == emfunctionhooks.end())
                return;
            auto op = emfunctionhooks.at(em_address);
            if (!(checkiscurrentgame(op)))
                return;

            HookParam hpinternal;
            hpinternal.address = entrypoint;
            hpinternal.emu_addr = em_address; // 用于生成hcode
            hpinternal.type = USING_STRING | NO_CONTEXT | BREAK_POINT | op.type;
            hpinternal.text_fun = op.hookfunc;
            hpinternal.filter_fun = op.filterfun;
            hpinternal.argidx = op.argidx;
            hpinternal.padding = op.padding;
            hpinternal.jittype = JITTYPE::VITA3K;
            NewHook(hpinternal, op._id);
        }();
        delayinsertNewHook(em_address);
    };
    return NewHook(hp, "vita3kjit");
}

namespace
{
    bool FPCSG01023(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex("<br>"), "");
        s = std::regex_replace(s, std::regex("%CF11F"), "");
        s = std::regex_replace(s, std::regex("%CFFFF"), "");
        s = std::regex_replace(s, std::regex("%K%P"), "");
        s = std::regex_replace(s, std::regex("%K%N"), "");
        s = std::regex_replace(s, std::regex("\n"), "");
        return write_string_overwrite(data, len, s);
    }
    template <int idx>
    bool FPCSG01282(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex("(\\n)+"), " ");
        s = std::regex_replace(s, std::regex("\\d$|^@[a-z]+|#.*?#|\\$"), "");
        static std::string last;
        if (last == s)
            return false;
        last = s;
        return write_string_overwrite(data, len, s);
    }

    template <int index>
    void ReadU16TextAndLenDW(hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = VITA3K::emu_arg(stack)[index];
        buffer->from(address + 0xC, (*(DWORD *)(address + 0x8)) * 2);
    }

    bool FPCSG00410(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex("#[A-Za-z]+\\[(\\d*[.])?\\d+\\]"), "");
        s = std::regex_replace(s, std::regex("#Pos\\[[\\s\\S]*?\\]"), "");
        s = std::regex_replace(s, std::regex("#n"), " ");
        // .replaceAll("④", "!?").replaceAll("②", "!!").replaceAll("⑥", "。").replaceAll("⑪", "【")
        // 	.replaceAll("⑫", "】").replaceAll("⑤", "、").replaceAll("①", "・・・")
        strReplace(s, "\x87\x43", "!?");
        strReplace(s, "\x87\x41", "!!");
        strReplace(s, "\x87\x45", "\x81\x42");
        strReplace(s, "\x87\x4a", "\x81\x79");
        strReplace(s, "\x87\x4b", "\x81\x7a");
        strReplace(s, "\x87\x44", "\x81\x41");
        strReplace(s, "\x87\x40", "\x81\x45\x81\x45\x81\x45");
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG00448(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex("[\\s]"), "");
        s = std::regex_replace(s, std::regex("(#n)+"), "");
        s = std::regex_replace(s, std::regex("#[A-Za-z]+\\[(\\d*[.])?\\d+\\]"), "");
        s = std::regex_replace(s, std::regex("#Pos[\\s\\S]*?\\]"), "");
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG01008(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex("#Ruby\\[([^,]+)\\.([^\\]]+)\\]."), "$1");
        s = std::regex_replace(s, std::regex("(#n)+"), " ");
        s = std::regex_replace(s, std::regex("#[A-Za-z]+\\[(\\d*[.])?\\d+\\]"), "");
        return write_string_overwrite(data, len, s);
    }
    void TPCSG00903(hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = VITA3K::emu_arg(stack)[0];
        buffer->from(address + 0x1C, (*(DWORD *)(address + 0x14)));
    }
    bool FPCSG00903(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex("\\\\n"), " ");
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG01180(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex(R"(\\n)"), " ");
        s = std::regex_replace(s, std::regex(R"(,.*$)"), " ");
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG00839(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::wstring((wchar_t *)data, *len / 2);
        s = std::regex_replace(s, std::wregex(L"\\[[^\\]]+."), L"");
        s = std::regex_replace(s, std::wregex(L"\\\\k|\\\\x|%C|%B|%p-1;"), L"");
        s = std::regex_replace(s, std::wregex(L"#[0-9a-fA-F]+;([^%#]+)(%r)?"), L"$1");
        s = std::regex_replace(s, std::wregex(L"\\\\n"), L"");
        static std::wstring last;
        if (last.find(s) != last.npos)
            return false;
        last = s;
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG00751(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex("[\\s]"), "");
        s = std::regex_replace(s, std::regex("@[a-z]"), "");
        // s = std::regex_replace(s, std::regex("＄"), "");
        strReplace(s, "\x81\x90", "");
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG00401(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex(R"([\s])"), "");
        s = std::regex_replace(s, std::regex(R"(\c)"), "");
        s = std::regex_replace(s, std::regex(R"(\\n)"), "");
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG00912(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex("%N"), "");
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG00706(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::wstring((wchar_t *)data, *len / 2);
        s = std::regex_replace(s, std::wregex(L"<br>"), L"");
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG00696(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        //.replace(/㌔/g, '⁉')
        //.replace(/㍉/g, '!!')
        strReplace(s, "\x87\x60", "");
        strReplace(s, "\x87\x5f", "");
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG00389(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex("[\\s]"), "");
        s = std::regex_replace(s, std::regex("(#n)+"), "");
        s = std::regex_replace(s, std::regex("#[A-Za-z]+\\[(\\d*[.])?\\d+\\]"), "");
        s = std::regex_replace(s, std::regex("#Pos\\[[\\s\\S]*?\\]"), "");
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG00216(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex("[\\s]"), "");
        s = std::regex_replace(s, std::regex("(#n)+"), "");
        s = std::regex_replace(s, std::regex("#[A-Za-z]+\\[(\\d*[.])?\\d+\\]"), "");
        s = std::regex_replace(s, std::regex("#Pos\\[[\\s\\S]*?\\]"), "");
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG00405(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex("[\\s]"), "");
        return write_string_overwrite(data, len, s);
    }
    bool PCSG00776(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        auto ws = StringToWideString(s, 932).value();
        strReplace(ws, L"\x02", L"");
        Trim(ws);
        return write_string_overwrite(data, len, WideStringToString(ws));
    }
    void PCSG00912(hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = VITA3K::emu_arg(stack)[1];
        std::string final_string = "";
        BYTE pattern[] = {0x47, 0xff, 0xff};
        auto results = MemDbg::findBytes(pattern, sizeof(pattern), address, address + 0x50);
        if (!results)
            return;

        address = results + 5;

        while (true)
        {
            std::string text = (char *)address;
            final_string += text;
            address = address + (text.size() + 1);

            auto bytes = (BYTE *)address;

            if (!(bytes[0] == 0x48 && bytes[1] == 0xFF && bytes[2] == 0xFF))
                break;
            address = address + (3);
            bytes = (BYTE *)address;
            if (!(bytes[0] == 0x47 && bytes[1] == 0xFF && bytes[2] == 0xFF))
                break;

            address = address + (5);
        }
        buffer->from(final_string);
    }
    void TPCSG00291(hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto a2 = VITA3K::emu_arg(stack)[0];

        auto vm = *(DWORD *)(a2 + (0x28));
        vm = *(DWORD *)VITA3K::emu_addr(stack, vm);
        vm = *(DWORD *)VITA3K::emu_addr(stack, vm + 8);
        uintptr_t address = VITA3K::emu_addr(stack, vm);
        auto len1 = *(DWORD *)(address + 4);
        auto p = address + 0x20;
        if (len1 > 4 && *(WORD *)(p + 2) == 0)
        {
            auto p1 = *(DWORD *)(address + 8);
            vm = *(DWORD *)VITA3K::emu_addr(stack, vm);
            vm = *(DWORD *)VITA3K::emu_addr(stack, vm + 0xC);
            p = VITA3K::emu_addr(stack, vm);
        }
        static int fm = 0;
        static std::string pre;
        auto b = fm;
        auto s = [](uintptr_t address)
        {
            auto frist = *(WORD *)address;
            auto lo = frist & 0xFF; // uppercase: 41->5A
            auto hi = frist >> 8;
            if (hi == 0 && (lo > 0x5a || lo < 0x41) /* T,W,? */)
            {
                return std::string();
            }
            std::string s;
            int i = 0;
            WORD c;
            char buf[3] = {0};
            while ((c = *(WORD *)(address + i)) != 0)
            {
                // reverse endian: ShiftJIS BE => LE
                buf[0] = c >> 8;
                buf[1] = c & 0xFF;

                if (c == 0x815e /* ／ */)
                {
                    s += ' '; // single line
                }
                else if (buf[0] == 0)
                {
                    //// UTF16 LE turned BE: 5700=>0057, 3100, 3500
                    //// 4e00 6d00=>PLAYER
                    // do nothing
                    if (buf[1] == 0x4e)
                    {
                        s += "PLAYER";
                        fm++;
                    }
                }
                else
                {
                    s += buf;
                }
                i += 2;
            }
            return s;
        }(p);
        if (b > 0)
        {
            fm--;
            return;
        }
        if (s == pre)
            return;
        pre = std::move(s);
        buffer->from(pre);
    }

    bool FPCSG00468(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex(u8R"(\\n(　)*|\\k)"), "");
        s = std::regex_replace(s, std::regex(R"(\[|\*[^\]]+])"), "");
        s = std::regex_replace(s, std::regex(u8"×"), "");
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG00808(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex(R"(^\s+|\s+$)"), "");
        s = std::regex_replace(s, std::regex(R"(\s*(#n)*\s*)"), "");
        s = std::regex_replace(s, std::regex(R"(#\w+(\[.+?\])?)"), "");
        return write_string_overwrite(data, len, s);
    }
    bool F010088B01A8FC000(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        static std::string last;
        s = std::regex_replace(s, std::regex(R"(#\w+(\[.+?\])?)"), "");
        s = std::regex_replace(s, std::regex(u8"　"), "");
        if (last == s)
            return false;
        last = s;
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG00815(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex(R"(\s*(#n)*\s*)"), "");
        s = std::regex_replace(s, std::regex(R"(#\w+(\[.+?\])?)"), "");
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG00855(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex(u8R"(#n(　)*)"), "");
        s = std::regex_replace(s, std::regex(R"(#\w.+?])"), "");
        return write_string_overwrite(data, len, s);
    }
    template <int idx>
    bool FPCSG00855_2(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        static std::string last;
        if (last == s)
            return false;
        last = s;
        strReplace(s, u8"Χ", u8"、");
        strReplace(s, u8"Δ", u8"。");
        strReplace(s, u8"Λ", u8"っ");
        strReplace(s, u8"《", u8"（");
        strReplace(s, u8"》", u8"）");
        strReplace(s, u8"∫", u8"「");
        strReplace(s, u8"∨", u8"」");
        strReplace(s, u8"∴", u8"『");
        strReplace(s, u8"∵", u8"』");
        strReplace(s, u8"П", u8"【");
        strReplace(s, u8"Ц", u8"】");
        if (write_string_overwrite(data, len, s))
            return FPCSG00855(data, len, hp);
        else
            return false;
    }
    bool FPCSG00477(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        auto ws = StringToWideString(s, 932).value();
        ws = std::regex_replace(ws, std::wregex(LR"(#n\u3000*)"), L"");
        ws = std::regex_replace(ws, std::wregex(LR"(#\w.+?])"), L"");
        s = WideStringToString(ws, 932);
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG00852(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        auto ws = StringToWideString(s, 932).value();
        ws = std::regex_replace(ws, std::wregex(LR"(\^)"), L"");
        s = WideStringToString(ws, 932);
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG01066(void *data, size_t *len, HookParam *hp)
    {
        auto s = std::string((char *)data, *len);
        s = std::regex_replace(s, std::regex(u8R"(\n(　)*)"), "");
        return write_string_overwrite(data, len, s);
    }
    bool FPCSG01075(void *data, size_t *len, HookParam *hp)
    {
        if (!FPCSG00808(data, len, hp))
            return false;
        auto s = std::string((char *)data, *len);
        static std::string last;
        if (last == s)
            return false;
        last = s;
        return true;
    }
    auto _ = []()
    {
        emfunctionhooks = {
            // Tsuihou Senkyo
            {0x8002e176, {0, 0, 0, 0, FPCSG01023, "PCSG01023"}}, // dialogue+name,sjis
            // 死神と少女 Shinigami to Shoujo
            {0x800204ba, {0, 2, 0, 0, FPCSG01282<0>, "PCSG01282"}}, // dialogueNVL,sjis
            {0x8000f00e, {0, 1, 0, 0, FPCSG01282<1>, "PCSG01282"}}, // dialogue main
            {0x80011f1a, {0, 0, 0, 0, FPCSG01282<2>, "PCSG01282"}}, // Name
            {0x8001ebac, {0, 1, 0, 0, FPCSG01282<3>, "PCSG01282"}}, // choices
            // 神凪ノ杜 Kannagi no Mori Satsukiame Tsuzuri
            {0x828bb50c, {CODEC_UTF16, 0, 0, ReadU16TextAndLenDW<0>, 0, "PCSG01268"}}, // dialogue
            {0x828ba9b6, {CODEC_UTF16, 0, 0, ReadU16TextAndLenDW<0>, 0, "PCSG01268"}}, // name
            {0x8060D376, {CODEC_UTF8, 0, 0, 0, 0, "PCSG01268"}},                       // vita3k v0.2.0 can't find 0x828bb50c && 0x828ba9b6, unknown reason.
            // Sanzen Sekai Yuugi ~MultiUniverse Myself~
            {0x8005ae24, {0, 0, 0, 0, 0, "PCSG01194"}}, // dialouge+name,sjis,need remap jis char,to complex
            // Marginal #4 Road to Galaxy
            {0x8002ff90, {CODEC_UTF8, 0, 0, 0, FPCSG01008, "PCSG01008"}}, // text
            // BLACK WOLVES SAGA  -Weiβ und Schwarz-
            {0x800581a2, {CODEC_UTF8, 0, 0, 0, FPCSG01008, "PCSG00935"}}, // text
            // New Game! The Challenge Stage!
            {0x8012674c, {CODEC_UTF8, 0, 0, TPCSG00903, FPCSG00903, "PCSG00903"}},
            // Kenka Banchou Otome
            {0x80009722, {CODEC_UTF16, 0, 0, 0, FPCSG00839, "PCSG00839"}},
            // Arcana famiglia -La storia della Arcana Famiglia-
            {0x80070e30, {0, 2, 0, 0, FPCSG00751, "PCSG00751"}}, // all,sjis
            {0x80070cdc, {0, 1, 0, 0, FPCSG00751, "PCSG00751"}}, // text
            // もし、この世界に神様がいるとするならば。 Moshi, Kono Sekai ni Kami-sama ga Iru to Suru Naraba.
            {0x80c1f270, {CODEC_UTF16, 0, 0, ReadU16TextAndLenDW<0>, FPCSG00706, "PCSG00706"}}, // dialogue
            {0x80d48bfc, {CODEC_UTF16, 0, 0, ReadU16TextAndLenDW<1>, FPCSG00706, "PCSG00706"}}, // Dictionary1
            {0x80d48c20, {CODEC_UTF16, 0, 0, ReadU16TextAndLenDW<0>, FPCSG00706, "PCSG00706"}}, // Dictionary2
            // Angelique Retour
            {0x8008bd1a, {0, 1, 0, 0, FPCSG00696, "PCSG00696"}}, // text1,sjis
            {0x8008cd48, {0, 0, 0, 0, FPCSG00696, "PCSG00696"}}, // text2
            {0x8008f75a, {0, 0, 0, 0, FPCSG00696, "PCSG00696"}}, // choice
            // Tsuki ni Yorisou Otome no Sahou
            {0x8002aefa, {0, 2, 0, 0, 0, "PCSG00648"}}, // dialogue,sjis
            // MARGINAL#4 IDOL OF SUPERNOVA
            {0x800718f8, {0, 0, 0, 0, FPCSG00448, "PCSG00448"}}, // dialogue,sjis
            // Nekketsu Inou Bukatsu-tan Trigger Kiss
            {0x8004e44a, {0, 0, 0, 0, FPCSG00410, "PCSG00410"}}, // dialogue,sjis
            // バイナリースター Binary Star
            {0x80058606, {0, 1, 0xd, 0, FPCSG00389, "PCSG00389"}}, // dialogue,sjis
            // Amagami
            {0x80070658, {0, 0, 0, TPCSG00291, 0, "PCSG00291"}},
            // Rui wa Tomo o Yobu
            {0x81003db0, {CODEC_UTF8, 1, 0, 0, FPCSG00839, "PCSG00216"}}, // dialogue
            // Reine des Fleurs
            {0x8001bff2, {0, 0, 0, 0, FPCSG00405, "PCSG00405"}}, // dialogue,sjis
            // Muv-Luv
            {0x80118f10, {0, 5, 0, 0, PCSG00776, "PCSG00776"}}, // dialogue, choices
            {0x80126e7e, {0, 0, 0, 0, PCSG00776, "PCSG00776"}}, // dialogue
            // Re:Birthday Song ~Koi o Utau Shinigami~
            {0x80033af6, {0, 0, 2, 0, 0, "PCSG00911"}}, // dialogue
            // Un:Birthday Song ~Ai o Utau Shinigami~
            {0x80038538, {0, 0, 0, PCSG00912, 0, "PCSG00912"}},
            {0x80033d66, {0, 3, 4, 0, FPCSG00912, "PCSG00912"}},
            // Sora*yume
            {0x8000bad4, {0, 1, 0, 0, FPCSG00401, "PCSG00401"}},
            // Tengai ni Mau, Iki na Hana

            {0x8006808e, {CODEC_UTF8, 0, 0, 0, FPCSG01180, "PCSG01180"}},
            {0x80089408, {CODEC_UTF8, 0, 0, 0, FPCSG01180, "PCSG01180"}},

            // Kokuchou no Psychedelica (黒蝶のサイケデリカ)
            {0x80043538, {CODEC_UTF8, 1, 0, 0, FPCSG00468, "PCSG00468"}},
            // Haitaka no Psychedelica (灰鷹のサイケデリカ)
            {0x80022c06, {CODEC_UTF8, 4, 0, 0, FPCSG00468, "PCSG00812"}},
            // Yuukyuu no Tierblade -Lost Chronicle- (悠久のティアブレイド -Lost Chronicle-)
            {0x8003542a, {CODEC_UTF8, 10, 0, 0, FPCSG00808, "PCSG00808"}},
            {0x8002a95a, {CODEC_UTF8, 6, 0, 0, FPCSG00808, "PCSG00808"}},
            {0x801a98aa, {CODEC_UTF8, 9, 0, 0, FPCSG00808, "PCSG00808"}},
            {0x801a42bc, {CODEC_UTF8, 9, 0, 0, FPCSG00808, "PCSG00808"}},
            {0x801a42d0, {CODEC_UTF8, 7, 0, 0, FPCSG00808, "PCSG00808"}},
            // Yuukyuu no Tierblade -Fragments of Memory- (悠久のティアブレイド -Fragments of Memory-)
            {0x80035f44, {CODEC_UTF8, 10, 0, 0, FPCSG01075, "PCSG01075"}},
            {0x8000d868, {CODEC_UTF8, 9, 0, 0, FPCSG01075, "PCSG01075"}},
            {0x8004598e, {CODEC_UTF8, 0, 0, 0, FPCSG01075, "PCSG01075"}},
            {0x801b1d16, {CODEC_UTF8, 9, 0, 0, FPCSG01075, "PCSG01075"}},
            {0x801ac31e, {CODEC_UTF8, 9, 0, 0, FPCSG01075, "PCSG01075"}},
            {0x801ac33a, {CODEC_UTF8, 7, 0, 0, FPCSG01075, "PCSG01075"}},
            {0x801b879a, {CODEC_UTF8, 5, 0, 0, FPCSG01075, "PCSG01075"}},
            {0x8009f570, {CODEC_UTF8, 5, 0, 0, FPCSG01075, "PCSG01075"}},
            // Magic Kyun! Renaissance (マジきゅんっ！ルネッサンス)
            {0x8008375a, {0, 1, 0, 0, FPCSG00852, "PCSG00852"}},
            {0x8001c194, {0, 1, 0, 0, FPCSG00852, "PCSG00852"}},
            // Chouchou Jiken Lovesodic / Chouchou Jiken Rhapsodic (蝶々事件ラブソディック)
            {0x8008dea2, {CODEC_UTF8, 4, 0, 0, FPCSG01066, "PCSG01066"}},
            {0x8008eb38, {CODEC_UTF8, 0, 0, 0, FPCSG01066, "PCSG01066"}},
            // Hyakka Yakou (百華夜光)
            {0x80032b30, {0, 8, 0, 0, 0, "PCSG00477"}},
            {0x80019c5a, {0, 5, 0, 0, 0, "PCSG00477"}},
            {0x80031a46, {0, 6, 0, 0, 0, "PCSG00477"}},
            {0x8003a49a, {0, 0, 0, 0, FPCSG00477, "PCSG00477"}},
            {0x80182532, {0, 7, 0, 0, FPCSG00477, "PCSG00477"}},
            {0x8017d1da, {0, 5, 0, 0, 0, "PCSG00477"}},
            {0x8017d478, {0, 4, 0, 0, 0, "PCSG00477"}},
            {0x8017a6aa, {0, 6, 0, 0, 0, "PCSG00477"}},
            // Hana Oboro ~Sengoku-den Ranki~ (花朧 ～戦国伝乱奇～)
            {0x80037600, {CODEC_UTF8, 6, 0, 0, FPCSG00855, "PCSG00855"}},
            {0x80036580, {CODEC_UTF8, 6, 0, 0, FPCSG00855, "PCSG00855"}},
            {0x801a2ada, {CODEC_UTF8, 0, 0, 0, FPCSG00855_2<0>, "PCSG00855"}},
            {0x801a2ba8, {CODEC_UTF8, 0, 0, 0, FPCSG00855_2<1>, "PCSG00855"}},
            {0x801a2d9e, {CODEC_UTF8, 0, 0, 0, FPCSG00855_2<2>, "PCSG00855"}},
            {0x801a2e68, {CODEC_UTF8, 0, 0, 0, FPCSG00855_2<3>, "PCSG00855"}},
            // PsychicEmotion6 (サイキックエモーション ムー)
            {0x80035948, {CODEC_UTF8, 9, 0, 0, FPCSG00815, "PCSG00815"}},
            {0x80034580, {CODEC_UTF8, 6, 0, 0, FPCSG00815, "PCSG00815"}},
            // Code: Realize ~Shirogane no Kiseki~ (Code:Realize ～白銀の奇跡～)
            {0x80015bcc, {CODEC_UTF8, 0, 0x1c, 0, F010088B01A8FC000, "PCSG01110"}},
            {0x80038e76, {CODEC_UTF8, 8, 0, 0, F010088B01A8FC000, "PCSG01110"}},
        };
        return 1;
    }();
}