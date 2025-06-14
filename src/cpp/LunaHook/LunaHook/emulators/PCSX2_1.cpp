#include "PCSX2_1.h"

namespace
{
    void FSLPM66136(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        strReplace(s, "#cr0");
        s = re::sub(s, R"((\\n)+)", " ");
        s = re::sub(s, R"(\\d$|^\@[a-z]+|#.*?#|\$)");
        s = re::sub(s, R"(@w|\\c)");
        buffer->from(s);
    }
    void FSLPM65914(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        strReplace(s, L"①ｎ");
        if (startWith(s, L"Ｖ＿") || std::all_of(s.begin(), s.end(), [](wchar_t c)
                                                 { return (c == L'±') || (c == L'-') || (c == L'\\') || (c == L'．') || (c == L'，') || (c == L'－') || (c == L'　') || (c == L' ') || ((c >= L'０') && (c <= L'９')) || ((c >= L'0') && (c <= L'9')); }))
            return buffer->clear();
        s = re::sub(s, LR"(^([±\s]+[０-９０-９，．\-]+|[０-９0-9，．\-]+)$)");
        buffer->fromWA(s);
    }
    void SLPM55227(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        s = re::sub(s, LR"(@(.*?)@)", L"$1");
        strReplace(s, L"%n");
        buffer->fromWA(s);
    }
    void FSLPM66045(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(%\w+\d*\w*)", " ");
        s = re::sub(s, R"(%N+)");
        buffer->from(s);
    }
    void FSLPM66302(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        s = strSplit(s, L"\");")[0];
        s = re::sub(s, LR"((\\n)+)", L" ");
        s = re::sub(s, LR"(\\d$|^\@[a-z]+|#.*?#|\$)");
        s = re::sub(s, LR"(@w|\\c)");
        strReplace(s, L"＊Ａ", L"岡崎");
        strReplace(s, L"＊Ｂ", L"朋也");
        buffer->fromWA(s);
    }
    void FSLPS25677(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        s = re::sub(s, LR"(^\[.*$)");
        s = re::sub(s, LR"(\_0C|\_1_5C|\_1C)");
        s = re::sub(s, LR"(^([a-zA-Z]+)|([a-zA-Z]+)$)");
        buffer->fromWA(s);
    }
    void SLPM66272(TextBuffer *buffer, HookParam *hp)
    {
        auto ss = buffer->strA();
        auto s = buffer->strAW();
        if (WideStringToString(s, 932) != ss)
            return buffer->clear();
        strReplace(s, L"#");
        strReplace(s, L"ﾞ");
        strReplace(s, L"!");
        buffer->fromWA(s);
        if (buffer->strAW().size() <= 4)
            buffer->clear();
    }
    void SLPM65396(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, '\n');
    }
    void SLPS25604(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("CR"));
    }
    void SLPM55014(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("%FS"));
        StringFilter(buffer, TEXTANDLEN("%FE"));
        StringFilter(buffer, TEXTANDLEN("%LC"));
        StringFilter(buffer, TEXTANDLEN("%N"));
    }
    void SLPM55170(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("%P"));
        StringFilter(buffer, TEXTANDLEN("%K"));
    }
    void SLPM55159(TextBuffer *buffer, HookParam *hp)
    {
        SLPM55170(buffer, hp);
        StringReplacer(buffer, TEXTANDLEN("\x81\xe1\x81\x5c\x81\x5c\x81\xe2"), TEXTANDLEN("\x81\x5c\x81\x5c\x81\x5c\x81\x5c"));
        auto s = buffer->strA();
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
    }
    void SLPM62343(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, '\n');
        StringFilter(buffer, TEXTANDLEN("/K"));
        StringFilter(buffer, TEXTANDLEN("/L"));
        StringFilter(buffer, TEXTANDLEN("\x81\x40"));
    }
    void SLPL25871(TextBuffer *buffer, HookParam *hp)
    {
        if (buffer->size <= 4)
            return buffer->clear();
        CharFilter(buffer, '\n');
        StringFilter(buffer, TEXTANDLEN("\x81\x40"));
    }
    void FSLPS25547(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, '\n');
        FSLPS25677(buffer, hp);
    }
    void SLPS25809(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("/K"));
        CharFilter(buffer, '\n');
        auto s = buffer->strA();
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
    }
    template <int i>
    void SLPS25897(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, '\n');
        auto s = buffer->strA();
        static std::string last;
        if (startWith(s, last))
        {
            buffer->from(s.substr(last.size()));
        }
        last = s;
    }
    void SLPS25276(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        strReplace(s, "\\k");
        strReplace(s, "\\P");
        auto __ = [](std::string ss)
        {
            if (startWith(ss, " "))
                ss = ss.substr(1);
            if (endWith(ss, "\n"))
                ss = ss.substr(0, ss.size() - 1);
            return ss;
        };
        if (startWith(s, last))
        {
            buffer->from(__(s.substr(last.size())));
        }
        else
        {
            buffer->from(__(s));
        }
        last = s;
    }
    void SLPS25662(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, '\n');
        auto s = buffer->strA();
        static std::string last;
        if (last.size() && startWith(s, last))
        {
            buffer->from(s.substr(last.size()));
        }
        else
        {
            std::string name = (char *)emu_addr(0x1869C60);
            if (name.size())
                name = "\x81\x79" + name + "\x81\x7a";
            buffer->from(name + buffer->strA());
        }
        last = s;
    }
    void SLPS25801(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, '\n');
        auto s = buffer->strA();
        static std::string last;
        if (last.size() && startWith(s, last))
        {
            buffer->from(s.substr(last.size()));
        }
        else
        {
            std::string name = (char *)emu_addr(0x342B0F);
            if (name.size())
                name = u8"【" + name + u8"】";
            buffer->from(name + buffer->strA());
        }
        last = s;
    }
    void SLPS25902(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, '\n');
        StringFilter(buffer, TEXTANDLEN("/K"));
        auto s = buffer->strA();
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
    }
    void FSLPM66332(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, '\x01');
        SLPS25897<3>(buffer, hp);
    }
    void SLPS25897_1(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, '\n');
        auto s = buffer->strA();
        static std::string last;
        if (last.size() && startWith(s, last))
        {
            buffer->from(s.substr(last.size()));
        }
        else
        {
            std::string name = (char *)emu_addr(0x1869C60);
            if (name.size())
                name = "\x81\x79" + name + "\x81\x7a";
            buffer->from(name + buffer->strA());
        }
        last = s;
    }
    void SLPM55240(TextBuffer *buffer, HookParam *hp)
    {
        StringReplacer(buffer, TEXTANDLEN("%x02―%x01"), TEXTANDLEN("――"));
    }
    void FSLPM55195(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("%n\x81\x40"));
        StringFilter(buffer, TEXTANDLEN("%n"));
    }
    void SLPM55154(TextBuffer *buffer, HookParam *hp)
    {
        static lru_cache<std::string> cache(4);
        static std::string last;
        static std::string last2;
        auto s = buffer->strA();
        strReplace(s, "\n");
        strReplace(s, "\r");
        if (startWith(s, "cdrom0"))
            return buffer->clear();
        if (endWith(last, s))
        {
            return buffer->clear();
        }
        if (s.size())
        {
            last = s;
            if (cache.touch(s))
            {
                return buffer->clear();
            }
            if (last2 == s)
            {
                return buffer->clear();
            }
            last2 = s;
        }
    }
    void SLPM55185(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("%n"));
        static std::string last;
        auto s = buffer->strA();
        if (last == s)
            return buffer->clear();
        last = s;
    }
    void FSLPM66293(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("#cr0"));
        CharFilter(buffer, '\n');
        std::string name = (char *)emu_addr(0x712260);
        buffer->from(name + buffer->strA());
    }
    void FSLPM65997(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(#\w+?\[\d\])");
        strReplace(s, "#n");
        buffer->from(s);
    }
    void SLPM66437(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        strReplace(s, L"d");
        buffer->fromWA(s);
    }
    void SLPM66905(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(\x81\x6f(.*?)\x81\x5e(.*?)\x81\x70)", "$2");
        strReplace(s, "\n");
        strReplace(s, "\x81\x40");
        buffer->from(s);
    }
    void SLPS25414(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        static std::string last;
        auto len = *(int *)emu_addr(0x20AB10);
        if (!len)
            return;
        auto strx = std::string((char *)emu_addr(0x20AB14), len);
        std::string str;
        for (auto i = 0; i < strx.size(); i++)
        {
            if (strx[i])
            {
                str += strx[i];
            }
            else
            {
                while (i % 4 != 3)
                    i++;
            }
        }
        auto parse = [](std::string str2)
        {
            strReplace(str2, "\\k\\n");
            str2 = re::sub(str2, R"(\\p\d{4})");
            return str2;
        };
        if (startWith(str, last))
        {
            buffer->from(parse(str.substr(last.size())));
        }
        else
        {
            buffer->from(parse(str));
        }
        last = str;
    }
    void SLPS25379(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        static std::string last;
        static std::string lasts[2];
        std::string collect;
        auto addrs = {0xFA7436, 0xFA7480};
        for (auto str : addrs)
            collect += (char *)emu_addr(str);
        if (last == collect)
            return;
        last = collect;
        int i = -1;
        collect = "";
        for (auto str : addrs)
        {
            i++;
            std::string x = (char *)emu_addr(str);
            if (i && (lasts[i] == x))
                break;
            lasts[i] = x;
            collect += x;
        }
        static std::string last1;
        if (last1.size() && startWith(collect, last1))
        {
            buffer->from(collect.substr(last1.size()));
        }
        else
        {
            buffer->from((char *)emu_addr(0xFA73EC) + collect);
        }
        last1 = collect;
    }
    void SLPM66344(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        auto addrs = {0x1FFE9D8, 0x1FFE9F4, 0x1FFEA10};
        std::string collect;
        for (auto str : addrs)
        {
            std::string __ = (char *)emu_addr(str);
            if (startWith(__, "\x81\x40"))
            {
                __ = __.substr(2);
            }
            collect += __;
        }
        static std::string last;
        if (last == collect)
            return;
        last = collect;
        buffer->from(collect);
    }
    void SLPM66817(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        static std::string last;
        static std::string lasts[3];
        std::string collect;
        auto addrs = {0xB9DDE4, 0xB9DE64, 0xB9DEE4};
        for (auto str : addrs)
            collect += (char *)emu_addr(str);
        if (last == collect)
            return;
        last = collect;
        int i = -1;
        collect = "";
        for (auto str : addrs)
        {
            i++;
            std::string x = (char *)emu_addr(str);
            if (i && (lasts[i] == x))
                break;
            lasts[i] = x;
            collect += x;
        }
        static std::string last1;
        if (last1.size() && startWith(collect, last1))
        {
            buffer->from(collect.substr(last1.size()));
        }
        else
        {
            buffer->from(std::string("\x81\x79") + (char *)emu_addr(0xB9DDC4) + "\x81\x7a" + collect);
        }
        last1 = collect;
    }
    void SLPS25220(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        static std::string last;
        static std::string lasts[3];
        std::string collect;
        auto addrs = {0x312FDC, 0x31230E, 0x312340};
        for (auto str : addrs)
            collect += (char *)emu_addr(str);
        if (last == collect)
            return;
        last = collect;
        int i = -1;
        collect = "";
        for (auto str : addrs)
        {
            i++;
            std::string x = (char *)emu_addr(str);
            if (i && (lasts[i] == x))
                break;
            lasts[i] = x;
            collect += x;
        }
        static std::string last1;
        auto parse = [](std::string str2)
        {
            return strReplace(str2, "\x99\xa2", "\x81\x45");
        };
        if (startWith(collect, last1))
        {
            buffer->from(parse(collect.substr(last1.size())));
        }
        else
        {
            buffer->from(parse(collect));
        }
        last1 = collect;
    }
    void SLPM66892(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        std::string s = (char *)PCSX2_REG(t0) + 0x15010;
        s += (char *)PCSX2_REG(t0);
        strReplace(s, "%n");
        buffer->from(s);
    }
    void SLPM66892_1(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        auto s = (char *)PCSX2_REG(t0);
        while (*s)
            s -= 1;
        s += 1;
        buffer->from(s);
    }
    void SLPS25150(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        static std::string last;
        static std::string lasts[4];
        std::string collect;
        auto addrs = {0x461F38, 0x462000, 0x4620CA, 0x462192};
        for (auto str : addrs)
            collect += (char *)emu_addr(str);
        if (last == collect)
            return;
        last = collect;
        int i = -1;
        collect = "";
        for (auto str : addrs)
        {
            i++;
            std::string x = (char *)emu_addr(str);
            if (i && (lasts[i] == x))
                break;
            lasts[i] = x;
            collect += x;
        }
        static std::string last1;
        if (startWith(collect, last1))
        {
            buffer->from(collect.substr(last1.size()));
        }
        else
        {
            buffer->from(collect);
        }
        last1 = collect;
    }
    template <int a, int b, int c, int d>
    void SLPS20394(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        static std::string last;
        static std::string lasts[4];
        std::string collect;
        auto addrs = {a, b, c, d};
        for (auto str : addrs)
            collect += (char *)emu_addr(str);
        if (last == collect)
            return;
        last = collect;
        int i = -1;
        collect = "";
        for (auto str : addrs)
        {
            i++;
            std::string x = (char *)emu_addr(str);
            if ((x[0] == 'y') || (x[0] == 'u'))
            {
                x = '\x81' + x;
            }
            if (i && (lasts[i] == x))
                break;
            lasts[i] = x;
            if (endWith(x, "\r"))
                x = x.substr(0, x.size() - 1);
            collect += x;
        }
        strReplace(collect, "\x99\xea", "\x98\xa3");
        strReplace(collect, "\x81\x40");
        buffer->from(collect);
    }
    void SLPM66458(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("\\n"));
        CharFilter(buffer, '\n');
        CharFilter(buffer, '\x01');
    }
    void SLPM65843(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("\\n"));
    }
    void SLPS25679(TextBuffer *buffer, HookParam *hp)
    {
        StringReplacer(buffer, TEXTANDLEN("\x87\x4e"), TEXTANDLEN("\x81\x60"));
        StringReplacer(buffer, TEXTANDLEN("\x87\x4f"), TEXTANDLEN("\x81\x60"));
        StringReplacer(buffer, TEXTANDLEN("\x87\x50"), TEXTANDLEN("\x81\x60"));
        StringReplacer(buffer, TEXTANDLEN("\x87\x51"), TEXTANDLEN("\x81\x60"));
        StringReplacer(buffer, TEXTANDLEN("\x87\x52"), TEXTANDLEN("\x81\x60"));
        StringReplacer(buffer, TEXTANDLEN("\x87\x5b"), TEXTANDLEN("\x81\x5b"));

        auto s = buffer->strAW();
        s = re::sub(s, LR"(\[(.*?)\*(.*?)\])", L"$1");
        buffer->fromWA(s);
    }
    void SLPM66298(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, "%[A-Z]+[0-9]*");
        buffer->from(s);
    }
    void SLPM65684(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        strReplace(s, L".");
        strReplace(s, L"T0");
        buffer->fromWA(s);
    }
    void SLPM66247(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        strReplace(s, "\x81\x40");
        strReplace(s, "\n");
        std::string name = (char *)emu_addr(0x19EB073);
        if (name.size())
        {
            strReplace(name, "#r");
            s = name + s;
        }

        buffer->from(s);
    }
    void SLPS25081(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        const uintptr_t val = PCSX2_REG(a0);
        const uintptr_t val2 = val & 0xFFFF;
        buffer->from_t(val2);
    }
    void SLPM55006(TextBuffer *buffer, HookParam *hp)
    {
        auto __ = buffer->strA();
        if (__.size() % 2)
            return buffer->clear();
        for (int i = 0; i < __.size() / 2; i++)
        {
            if (!IsShiftjisWord(*(WORD *)(__.data() + 2 * i)))
                return buffer->clear();
        }
        static std::string last;
        if (last == __)
            return buffer->clear();
        last = __;
    }
    void SLPS20196(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        const uintptr_t val = PCSX2_REG(a0);
        const uintptr_t val2 = val & 0xFFFF;
        const uintptr_t val3 = ((val2 & 0xFF) << 8) | ((val2 >> 8) & 0xFF);
        buffer->from_t(val3);
    }
    void SLPS25581(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        const uintptr_t p1 = PCSX2_REG(s1);
        const uintptr_t p2 = p1 & 0x0FFFFFFF;
        uint8_t *ptr = (uint8_t *)emu_addr(p2);
        if (!ptr || ptr == nullptr)
        {
            return;
        }
        uint8_t b0 = ptr[0];
        uint8_t b1 = ptr[1];
        const uintptr_t sjis = ((uintptr_t)b1 << 8) | b0;
        buffer->from_t(sjis);
    }
    void SLPM65355(TextBuffer *buffer, HookParam *hp)
    {
        static std::string lastoutput;
        static std::string last;
        auto s = buffer->strA();
        if (last == s)
            return buffer->clear();
        if (last.empty())
            last = s;
        if (last.size() == s.size())
        {
            bool good = false;
            for (int i = last.size() - 1; i >= 0; i--)
            {
                if (s[i] != last[i])
                {
                    good = true;
                    buffer->from(s.substr(0, i + 1));
                    break;
                }
            }
            if (!good)
                buffer->clear();
        }
        last = s;
        auto sw = buffer->strAW();
        strReplace(sw, L"@");
        sw = re::sub(sw, L"#\\d+");
        buffer->fromWA(sw);
    }
    void SLPS25941(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        auto s = buffer->strA();
        if (last == s)
        {
            return buffer->clear();
        }
        last = s;
        strReplace(s, "$n");
        strReplace(s, "$k");
        s = re::sub(s, R"(\$s\d+)");
        buffer->from(s);
    }
    void SLPM62207(TextBuffer *buffer, HookParam *hp)
    {
        SLPM55006(buffer, hp);
        static std::string last;
        auto s = buffer->strA();
        if (endWith(last, s))
        {
            return buffer->clear();
        }
        last = s;
    }
    void SLPS25941_2(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        auto s = buffer->strA();
        if (endWith(last, s))
        {
            return buffer->clear();
        }
        last = s;
        SLPS25941(buffer, hp);
        auto s1 = buffer->strA();
        s1 = re::sub(s1, R"(^\d+)");
        buffer->from(s1);
    }
    WORD SLPM66163ReadChar()
    {
        const uintptr_t val_a0 = PCSX2_REG(a0);
        const uintptr_t val_s0 = PCSX2_REG(s0);
        uint8_t *bytes = (uint8_t *)&val_a0;
        uint8_t b1 = bytes[3];
        uint8_t b2 = bytes[2];
        uint8_t b3 = bytes[1];
        uint8_t b4 = bytes[0];
        //  ConsoleOutput("b1=0x%x b2=0x%x b3=0x%x b4=0x%x", b1, b2, b3, b4);

        // 0x00 被输出
        if (!b2 && !b3 && !b4)
        {
            return 0;
        }

        const uint8_t byteval = b4;

        const bool is_normal_sjis = ((byteval >= 0x81 && byteval <= 0x9F) || (byteval >= 0xE0 && byteval <= 0xEF));

        if (is_normal_sjis)
        {
            // it's a normal 2-byte Shift-JIS character
            const uintptr_t p1 = val_s0 & 0x0FFFFFFF;
            uint8_t *storageptr = (uint8_t *)emu_addr(p1);
            if (!storageptr || storageptr == nullptr)
            {
                return 0;
            }
            uint8_t b0 = storageptr[0];
            uint8_t b1 = storageptr[1];
            const uintptr_t sjis = ((uintptr_t)b1 << 8) | b0;
            //    ConsoleOutput("2sjis: 0x%x", sjis);
            return sjis;
        }
        else
        {
            // it's the game's custom 1-byte encoding
            uintptr_t sjis = 0x0;
            switch (byteval)
            {
                // clang-format off
                case 0xd7:sjis=0xE782;break;
                case 0xd8:sjis=0xE882;break;
                case 0xd9:sjis=0xE982;break;
                case 0xda:sjis=0xEA82;break;
                case 0xdb:sjis=0xEB82;break;
                case 0xdc:sjis=0xED82;break;
                case 0xdd:sjis=0xF182;break;
                case 0xde:sjis=0x4A81;break;
                case 0xdf:sjis=0x4B81;break;
                case 0x22:sjis=0x6881;break;
                case 0x23:sjis=0x23;break;
                case 0x24:sjis=0x24;break;
                case 0x25:sjis=0x25;break;
                case 0x26:sjis=0x26;break;
                case 0x27:sjis=0x27;break;
                case 0x28:sjis=0x28;break;
                case 0x29:sjis=0x29;break;
                case 0x2a:sjis=0x2A;break;
                case 0x2b:sjis=0x2B;break;
                case 0x2c:sjis=0x2C;break;
                case 0x2d:sjis=0x2D;break;
                case 0x2e:sjis=0x2E;break;
                case 0x2f:sjis=0x2F;break;
                case 0x30:sjis=0x30;break;
                case 0x31:sjis=0x31;break;
                case 0x32:sjis=0x32;break;
                case 0x33:sjis=0x33;break;
                case 0x34:sjis=0x34;break;
                case 0x35:sjis=0x35;break;
                case 0x36:sjis=0x36;break;
                case 0x37:sjis=0x37;break;
                case 0x38:sjis=0x38;break;
                case 0x39:sjis=0x39;break;
                case 0x3a:sjis=0x3A;break;
                case 0x3b:sjis=0x3B;break;
                case 0x3d:sjis=0x3D;break;
                case 0x3e:sjis=0x3E;break;
                case 0x3f:sjis=0x3F;break;
                case 0x40:sjis=0x40;break;
                case 0x41:sjis=0x41;break;
                case 0x42:sjis=0x42;break;
                case 0x43:sjis=0x43;break;
                case 0x44:sjis=0x44;break;
                case 0x45:sjis=0x45;break;
                case 0x46:sjis=0x46;break;
                case 0x47:sjis=0x47;break;
                case 0x48:sjis=0x48;break;
                case 0x49:sjis=0x49;break;
                case 0x4a:sjis=0x4A;break;
                case 0x4b:sjis=0x4B;break;
                case 0x4c:sjis=0x4C;break;
                case 0x4d:sjis=0x4D;break;
                case 0x4e:sjis=0x4E;break;
                case 0x4f:sjis=0x4F;break;
                case 0x50:sjis=0x50;break;
                case 0x51:sjis=0x51;break;
                case 0x52:sjis=0x52;break;
                case 0x53:sjis=0x53;break;
                case 0x54:sjis=0x54;break;
                case 0x55:sjis=0x55;break;
                case 0x56:sjis=0x56;break;
                case 0x57:sjis=0x57;break;
                case 0x58:sjis=0x58;break;
                case 0x59:sjis=0x59;break;
                case 0x5a:sjis=0x5A;break;
                case 0x5b:sjis=0x5B;break;
                case 0x5c:sjis=0x5C;break;
                case 0x5d:sjis=0x5D;break;
                case 0x5e:sjis=0x5E;break;
                case 0x5f:sjis=0x5F;break;
                case 0x60:sjis=0x6581;break;
                case 0x61:sjis=0x61;break;
                case 0x62:sjis=0x62;break;
                case 0x63:sjis=0x63;break;
                case 0x64:sjis=0x64;break;
                case 0x65:sjis=0x65;break;
                case 0x66:sjis=0x66;break;
                case 0x67:sjis=0x67;break;
                case 0x68:sjis=0x68;break;
                case 0x69:sjis=0x69;break;
                case 0x6a:sjis=0x6A;break;
                case 0x6b:sjis=0x6B;break;
                case 0x6c:sjis=0x6C;break;
                case 0x6d:sjis=0x6D;break;
                case 0x6e:sjis=0x6E;break;
                case 0x6f:sjis=0x6F;break;
                case 0x70:sjis=0x70;break;
                case 0x71:sjis=0x71;break;
                case 0x72:sjis=0x72;break;
                case 0x73:sjis=0x73;break;
                case 0x74:sjis=0x74;break;
                case 0x75:sjis=0x75;break;
                case 0x76:sjis=0x76;break;
                case 0x77:sjis=0x77;break;
                case 0x78:sjis=0x78;break;
                case 0x79:sjis=0x79;break;
                case 0x7a:sjis=0x7A;break;
                case 0x7c:sjis=0x7C;break;
                case 0x7d:sjis=0x7D;break;
                case 0xa1:sjis=0x4281;break;
                case 0xa2:sjis=0x7581;break;
                case 0xa3:sjis=0x7681;break;
                case 0xa4:sjis=0x4181;break;
                case 0xa5:sjis=0x4581;break;
                case 0xa6:sjis=0xF082;break;
                case 0xa7:sjis=0x9F82;break;
                case 0xa8:sjis=0xA282;break;
                case 0xa9:sjis=0xA482;break;
                case 0xaa:sjis=0xA582;break;
                case 0xab:sjis=0xA882;break;
                case 0xac:sjis=0xE282;break;
                case 0xad:sjis=0xE382;break;
                case 0xae:sjis=0xE582;break;
                case 0xaf:sjis=0xC182;break;
                case 0xb0:sjis=0xEA88;break;
                case 0xb1:sjis=0xA082;break;
                case 0xb2:sjis=0xA282;break;
                case 0xb3:sjis=0xA482;break;
                case 0xb4:sjis=0xA682;break;
                case 0xb5:sjis=0xA882;break;
                case 0xb6:sjis=0xA982;break;
                case 0xb7:sjis=0xAB82;break;
                case 0xb8:sjis=0xAD82;break;
                case 0xb9:sjis=0xAF82;break;
                case 0xba:sjis=0xB182;break;
                case 0xbb:sjis=0xB382;break;
                case 0xbc:sjis=0xB582;break;
                case 0xbd:sjis=0xB782;break;
                case 0xbe:sjis=0xB982;break;
                case 0xbf:sjis=0xBB82;break;
                case 0xc0:sjis=0xBD82;break;
                case 0xc1:sjis=0xBF82;break;
                case 0xc2:sjis=0xC282;break;
                case 0xc3:sjis=0xC482;break;
                case 0xc4:sjis=0xC682;break;
                case 0xc5:sjis=0xC882;break;
                case 0xc6:sjis=0xC982;break;
                case 0xc7:sjis=0xCA82;break;
                case 0xc8:sjis=0xCB82;break;
                case 0xc9:sjis=0xCC82;break;
                case 0xca:sjis=0xCD82;break;
                case 0xcb:sjis=0xD082;break;
                case 0xcc:sjis=0xD382;break;
                case 0xcd:sjis=0xD682;break;
                case 0xce:sjis=0xD982;break;
                case 0xcf:sjis=0xDC82;break;
                case 0xd0:sjis=0xDD82;break;
                case 0xd1:sjis=0xDE82;break;
                case 0xd2:sjis=0xDF82;break;
                case 0xd3:sjis=0xE082;break;
                case 0xd4:sjis=0xE282;break;
                case 0xd5:sjis=0xE482;break;
                case 0xd6:sjis=0xE682;break;
                // clang-format on
            }
            if (!sjis)
            {
                return 0;
            }
            //   ConsoleOutput("1sjis: 0x%x", sjis);
            return sjis;
        }
    }
    void SLPM66163(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        static std::string collect;
        static lru_cache<std::string> last(4);
        auto c = SLPM66163ReadChar();
        if (c)
        {
            char bs[3] = {0};
            *(WORD *)bs = c;
            collect += bs;
        }
        else
        {
            if (collect.size() == 2 || !last.touch(collect))
            {
                buffer->from(collect);
            }
            collect.clear();
        }
    }
    void SLPM55184(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("\x81\xa1"));
    }
    void SLPM65786(TextBuffer *buffer, HookParam *hp)
    {
        auto w = *(WORD *)buffer->buff;
        if (w == 0x4081 || !(IsShiftjisWord(w)))
        {
            buffer->clear();
        }
    }
    void SLPM55156(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        if (endWith(last, s))
            return buffer->clear();
        last = s;
        strReplace(s, "\n");
        buffer->from(s);
    }
    void SLPM55052(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = s.substr(0, s.find("\\\r"));
        static std::string last;
        if (endWith(last, s))
            return buffer->clear();
        last = s;
        s = re::sub(s, "<[A-Z].*?[\\dA-Z]>");
        strReplace(s, "\n");
        strReplace(s, "\r");
        buffer->from(s);
    }
    void SLPM55197(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        auto s = buffer->strA();
        if (endWith(last, s))
            return buffer->clear();
        last = s;
        buffer->from(strReplace(strReplace(s, "%P"), "%K"));
    }
    void SLPM55102(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        strReplace(s, L",");
        strReplace(s, L"^");
        strReplace(s, L"\ue09c", L"?");
        buffer->fromWA(s);
    }
    void SLPS25135(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        const uintptr_t val1 = PCSX2_REG(a1);
        const uintptr_t val2 = (val1 & 0x0000FFFF);
        const uintptr_t sjis = ((val2 & 0xFF) << 8) | ((val2 >> 8) & 0xFF);
        buffer->from_t(sjis);
    }
    void SLPS25759(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        const uintptr_t val_v0 = PCSX2_REG(v0);
        const uintptr_t val_a0 = PCSX2_REG(a0);
        const uintptr_t p1 = val_v0 & 0x0FFFFFFF;
        uint8_t *storageptr = (uint8_t *)emu_addr(p1);
        if (storageptr == nullptr || !storageptr)
        {
            return;
        }
        const uint8_t b0 = *(storageptr - 1);
        const uint8_t b1 = (uint8_t)(val_a0 & 0x000000FF);

        const uintptr_t sjis = ((uintptr_t)b1 << 8) | b0;

        buffer->from_t(sjis);
    }
    void SLPS25051(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        static bool send = false;
        static uint8_t store = 0x00;
        const uintptr_t val1 = PCSX2_REG(v0);
        const uintptr_t val2 = (val1 & 0x000000FF);
        const uint8_t byteval = (uint8_t)val2;

        if (byteval == 0x00)
        {
            return;
        }

        if (!send)
        {
            store = byteval;
        }
        else
        {
            uint8_t b0 = store;
            uint8_t b1 = byteval;

            // game uses ・ (81 45) at newlines and sentence ends
            // i'm replacing these with ASCII space ' ' (00 20)
            // probably should be fixed in a filter func instead, but whatever
            if (b0 == 0x81 && b1 == 0x45)
            {
                b0 = 0x00;
                b1 = 0x20;
            }

            const uintptr_t sjis = ((uintptr_t)b1 << 8) | b0;

            buffer->from_t(sjis);
            store = 0x00;
        }

        send = !send;
    }
    void SLPM66452(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        const uintptr_t val1 = PCSX2_REG(v0);
        const uintptr_t val2 = (val1 & 0x0000FFFF);

        if (!val2)
        {
            return;
        }

        const uintptr_t sjis = ((val2 & 0xFF) << 8) | ((val2 >> 8) & 0xFF);
        buffer->from_t(sjis);
    }
    void SLPM55225(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        buffer->from_t(*(char *)PCSX2_REG(a0));
    }
}
struct emfuncinfoX
{
    DWORD addr;
    emfuncinfo info;
};
static const emfuncinfoX emfunctionhooks_1[] = {
    // Piaキャロットへようこそ！！G.P. ～学園プリンセス～
    {0x23AF40, {DIRECT_READ, 0, 0, 0, SLPM55102, "SLPM-55102"}},
    // Clear ～新しい風の吹く丘で～
    {0x1D0C580, {DIRECT_READ, 0, 0, 0, 0, "SLPM-55136"}},
    // ヒャッコ よろずや事件簿！
    {0x17B6D4, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM55159, "SLPM-55159"}},
    // トリガーハート エグゼリカ エンハンスド
    {0x324694, {0, PCSX2_REG_OFFSET(s0), 0, 0, SLPM55052, "SLPM-55052"}},
    // Memories Off 6 Next Relation
    {0x17F334, {0, PCSX2_REG_OFFSET(v1), 0, 0, SLPM55197, "SLPM-55197"}},
    // メルティブラッド アクトレスアゲイン [通常版]
    {0x853710, {DIRECT_READ, 0, 0, 0, SLPM55184, "SLPM-55184"}},
    // つよきす2学期 ～Swift Love～ [通常版]
    {0x19E41C, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM55154, "SLPM-55154"}},
    // Sweet Honey Coming [DXパック]
    {0x1DDB4D0, {DIRECT_READ, 0, 0, 0, SLPM55185, "SLPM-55185"}},
    // お掃除戦隊くりーんきーぱー H [通常版]
    {0x14658A4, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-55220"}},
    // 顔のない月 Select story
    {0xB3FCDC, {DIRECT_READ, 0, 0, 0, 0, "SLPM-62784"}},
    // ef - A Fairy Tale of the Two. [初回限定特別同梱版]
    {0xA10588, {DIRECT_READ, 0, 0, 0, SLPM55240, "SLPM-55240"}},
    // スズノネセブン！～Rebirth Knot～
    {0x1FF9A70, {DIRECT_READ, 0, 0, 0, FSLPM55195, "SLPM-55243"}},
    // 萌え萌え2次大戦(略)2[chu～♪] [通常版]
    {0x1A2690, {0, PCSX2_REG_OFFSET(t4), 0, 0, SLPM65396, "SLPS-25956"}},
    // ストライクウィッチーズ あなたとできること [通常版]
    {0x10A948, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(a0), 0, 0, 0, "SLPM-55174"}},
    // 真・恋姫†夢想 ～乙女繚乱☆三国志演義～ [通常版]
    {0xBC9740, {DIRECT_READ, 0, 0, 0, SLPM65843, "SLPM-55288"}},
    // 神曲奏界ポリフォニカ THE BLACK -EPSODE 1 & 2 BOX EDITION-
    {0x309570, {DIRECT_READ, 0, 0, 0, 0, "SLPM-55095"}},
    // 神曲奏界ポリフォニカ アフタースクール
    {0x32A3F0, {DIRECT_READ, 0, 0, 0, 0, "SLPM-55270"}},
    // 戦極姫 ～戦乱に舞う乙女達～
    {0x13C16C, {0, 0, 0, SLPM55225, 0, "SLPM-55225"}},
    // 戦極姫2・炎 ～百華、戦乱辰風の如く～
    {0x1C5D7C, {0, PCSX2_REG_OFFSET(v0), 0, 0, 0, "SLPM-55278"}},
    // 花と乙女に祝福を ～春風の贈り物～
    {0x109C5C, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(a1), 0, 0, SLPM65786, "SLPM-55263"}},
    // Monochrome (モノクローム)
    {0x4B7A60, {DIRECT_READ, 0, 0, 0, SLPM55170, "SLPM-65682"}},
    // Missing Blue [通常版]
    {0x12A80C, {0, 0, 0, SLPS25051, 0, "SLPS-25051"}}, //@mills
    // 四八 （仮）
    {0x17529C, {0, 0, 0, SLPS25759, 0, "SLPS-25759"}}, //@mills
    // かまいたちの夜2 ～監獄島のわらべ唄～ [通常版]
    {0x111C78, {0, 0, 0, SLPS25135, 0, "SLPS-25135"}}, //@mills
    // かまいたちの夜x3 三日月島事件の真相
    {0x112830, {0, 0, 0, SLPM66452, 0, "SLPM-66452"}}, //@mills
    // 桃華月憚 ～光風の陵王～
    {0x29AB3C, {0, 0, 0, 0, 0, "SLPM-55200"}},
    // 夏色の砂時計
    {0x205554, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(v1), 0, 0, 0, "SLPS-25026"}},
    // なついろ ～星屑のメモリー～
    {0x16D230, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(s0), 0, 0, SLPM65786, "SLPM-65786"}},
    // 夏色小町【一日千夏】
    {0x2AB318, {DIRECT_READ, 0, 0, 0, SLPM65355, "SLPM-65355"}},
    // SDガンダム - G GENERATION WARS
    {0x4BF474, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPS25941, "SLPS-25941"}},
    {0x51B59C, {0, PCSX2_REG_OFFSET(v1), 0, 0, SLPS25941_2, "SLPS-25941"}},
    // 風雨来記
    {0x1FFACA0, {DIRECT_READ, 0, 0, 0, SLPM66458, "SLPM-66458"}},
    // 風雨来記2
    {0x2AC77C, {0, 0, 0, SLPM66163, 0, "SLPM-66163"}}, //@mills
    // SIMPLE2000シリーズ Vol.9 THE 恋愛アドベンチャー ～BITTERSWEET FOOLS～
    {0x16C798, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM62207, "SLPM-62207"}},
    // あかね色に染まる坂 ぱられる
    {0x126660, {0, PCSX2_REG_OFFSET(v1), 0, 0, SLPM55006, "SLPM-55006"}},
    // SIMPLE 2000シリーズ Vol.92 THE 呪いのゲーム
    {0x128D58, {0, 0, 0, SLPS25581, 0, "SLPS-25581"}}, //@mills
    // 赤川次郎ミステリー月の光　 ～沈める鐘の殺人～
    {0x118150, {0, 0, 0, SLPS20196, 0, "SLPS-20196"}}, //@mills
    // 最終電車
    {0x1264EC, {0, 0, 0, SLPS25081, 0, "SLPS-25081"}}, //@mills
    // 夏夢夜話
    {0x7689BC, {DIRECT_READ, 0, 0, 0, SLPS25276, "SLPS-25276"}},
    // マイネリーベ 優美なる記憶
    {0x19BF230, {DIRECT_READ, 0, 0, 0, SLPM65684, "SLPM-65684"}},
    // マイネリーベⅡ ～誇りと正義と愛～
    {0x1FFD0DC, {DIRECT_READ, 0, 0, 0, SLPM66247, "SLPM-66247"}},
    // セパレイトハーツ (Separate Hearts)
    {0x1F63320, {DIRECT_READ, 0, 0, 0, SLPM66298, "SLPM-66298"}}, //@mills
    // アカイイト
    {0x136800, {0, PCSX2_REG_OFFSET(t0), 0, 0, FSLPM66136, "SLPM-65732"}},
    // Nana
    {0x15036C, {0, PCSX2_REG_OFFSET(a3), 0, 0, FSLPM65914, "SLPM-65914"}},
    // My Merry May with be
    {0x1DB7DC, {0, PCSX2_REG_OFFSET(a3), 0, 0, FSLPM66045, "SLPM-66045"}},
    // CLANNAD - ゲオオンラインストア
    {0x14AC38, {0, PCSX2_REG_OFFSET(s4), 0, 0, FSLPM66302, "SLPM-66302"}},
    // 苺ましまろ
    {0x1439F4, {0, PCSX2_REG_OFFSET(s1), 0, 0, FSLPS25547, "SLPS-25547"}},
    // ブラッドプラス ワン ナイト キス
    {0x267B58, {0, PCSX2_REG_OFFSET(a3), 0, 0, FSLPS25677, "SLPS-25677"}},
    {0x268260, {0, PCSX2_REG_OFFSET(a3), 0, 0, FSLPS25677, "SLPS-25677"}},
    // プリンセスラバー！ Eternal Love For My Lady
    {0x92748C, {DIRECT_READ, 0, 0, 0, FSLPM55195, "SLPM-55195"}},
    // 破滅のマルス
    {0x308460, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-65997"}},
    // フレンズ ～青春の輝き～
    {0x456048, {DIRECT_READ, 0, 0, 0, 0, "SLPS-25385"}},
    // SAMURAI 7
    {0x190FDac, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-66399"}},
    // 高円寺女子サッカー
    {0x53FA10, {DIRECT_READ | CODEC_UTF8, 0, 0, 0, FSLPM66332, "SLPM-66332"}},
    // 銀魂 銀さんと一緒！ボクのかぶき町日記
    {0x8DA13A, {DIRECT_READ, 0, 0, 0, SLPS25809, "SLPS-25809"}},
    // THE 恋愛ホラーアドベンチャー～漂流少女～
    {0x1A1640, {DIRECT_READ, 0, 0, 0, SLPM62343, "SLPM-62343"}},
    // 好きなものは好きだからしょうがない！！ -FIRST LIMIT & TARGET†NIGHTS- Sukisho！ Episode ＃01+＃02
    {0x268CE9, {DIRECT_READ, 0, 0, SLPS20394<0x268CE9, 0x268D2A, 0x268D6B, 0x268DAC>, 0, "SLPS-20352"}}, //[ディスク 1]
    {0x2690EA, {DIRECT_READ, 0, 0, SLPS20394<0x2690EA, 0x26912A, 0x26916B, 0x2691AC>, 0, "SLPS-20353"}}, //[ディスク 2]
    // 好きなものは好きだからしょうがない！！ -RAIN- Sukisyo！ Episode #03
    {0x2AF161, {DIRECT_READ, 0, 0, SLPS20394<0x2AF161, 0x2AFAA8, 0x2AEFA4, 0x2AEFE5>, 0, "SLPS-20394"}},
    // ドラスティックキラー
    {0x1AC5D40, {DIRECT_READ, 0, 0, 0, SLPL25871, "SLPS-25871"}},
    {0x1AC6970, {DIRECT_READ, 0, 0, 0, SLPL25871, "SLPS-25871"}},
    // うたわれるもの 散りゆく者への子守唄
    {0x50574C, {DIRECT_READ, 0, 0, 0, SLPS25679, "SLPS-25679"}},
    // Only you リベルクルス ドラマCD付き
    {0x461F38, {DIRECT_READ, 0, 0, SLPS25150, 0, "SLPS-25150"}},
    // D.C. ～ダ・カーポ～ the Origin
    {0x517688, {DIRECT_READ, 0, 0, 0, SLPM66905, "SLPM-66905"}},
    // D.C.I.F. ～ダ・カーポ～イノセント・フィナーレ～ [通常版]
    {0x114068, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPM55156, "SLPM-55156"}},
    // Soul Link EXTENSION
    {0x1E14A3C, {DIRECT_READ, 0, 0, 0, SLPM66437, "SLPM-66437"}},
    // デ・ジ・キャラット ファンタジー エクセレント
    {0x10E2C80, {DIRECT_READ, 0, 0, 0, SLPM65396, "SLPM-65396"}},
    // I/O
    {0xF0BF80, {DIRECT_READ, 0, 0, 0, SLPM66272, "SLPM-66272"}},
    // シークレット・オブ・エヴァンゲリオン
    {0x842E48, {DIRECT_READ, 0, 0, 0, SLPS25897<2>, "SLPM-66569"}},
    // PANDORA ～君の名前を僕は知る～
    {0x1690C50, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-55269"}},
    // 学園アリス ～きらきら★メモリーキッス～
    {0x711FC0, {DIRECT_READ, 0, 0, 0, FSLPM66293, "SLPM-66293"}},
    // After...～忘れえぬ絆～
    {0x15DA4c, {DIRECT_READ, 0, 0, 0, SLPS25897<1>, "SLPM-65481"}},
    // ゼロの使い魔 迷子の終止符と幾千の交響曲
    {0x1FFD934, {DIRECT_READ, 0, 0, 0, SLPS25897_1, "SLPS-25897"}},
    // スキップ・ビート
    {0x1CF70F0, {DIRECT_READ, 0, 0, 0, SLPM55170, "SLPM-55170"}},
    // Myself;Yourself
    {0x1443e8, {0, 0, 0, SLPM66892, 0, std::vector<const char *>{"SLPM-66891", "SLPM-66892"}}},   // [通常版] && [初回限定版]
    {0x13F1F8, {0, 0, 0, SLPM66892_1, 0, std::vector<const char *>{"SLPM-66891", "SLPM-66892"}}}, // [通常版] && [初回限定版]
    // Myself; Yourself それぞれのfinale
    {0x1C785A8, {DIRECT_READ, 0, 0, 0, 0, "SLPM-55163"}},
    // ARIA The ORIGINATION ～蒼い惑星のエルシエロ～
    {0x10F8488, {DIRECT_READ, 0, 0, 0, SLPM55014, "SLPM-55014"}},
    // ARIA The NATURAL ～遠い記憶のミラージュ～
    {0x1137428, {DIRECT_READ, 0, 0, 0, 0, "SLPM-66536"}},
    // 猛獣使いと王子様
    {0x16681E0, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-55264"}},
    // 120円の春
    {0x1CEAF56, {DIRECT_READ, 0, 0, 0, SLPM65843, "SLPM-65843"}},
    // ゲームになったよ！ドクロちゃん～健康診断大作戦～
    {0x1B9Bbec, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-66186"}},
    // 地獄少女 澪縁
    {0x2A078F, {DIRECT_READ, 0, 0, 0, SLPM65396, "SLPM-55213"}},
    // エーデルブルーメ
    {0x46631C, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-66975"}},
    // セキレイ ～未来からのおくりもの～
    {0x4639C5, {DIRECT_READ, 0, 0, 0, SLPM55227, "SLPM-55227"}},
    // Fate/stay night[Realta Nua]
    {0x2C0DD5, {DIRECT_READ, 0, 0, 0, 0, "SLPM-66513"}},
    // アルトネリコ 世界の終わりで詩い続ける少女
    {0xC3FC8C, {DIRECT_READ, 0, 0, 0, SLPS25604, "SLPS-25604"}},
    // アルトネリコ 世界の終わりで詩い続ける少女 [PlayStation2 the Best]
    {0xC3F6CC, {DIRECT_READ, 0, 0, 0, SLPS25604, "SLPS-73249"}},
    // アルトネリコ2 世界に響く少女たちの創造詩
    {0xAF15BC, {DIRECT_READ, 0, 0, 0, SLPS25604, "SLPS-25819"}},
    // アルトネリコ2 世界に響く少女たちの創造詩 [PlayStation2 the Best]
    {0xAF1B3C, {DIRECT_READ, 0, 0, 0, SLPS25604, "SLPS-73263"}},
    // CLOCK ZERO ～終焉の一秒～
    {0x1A07855, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-55281"}},
    // ToHeart2
    {0x20AB10, {DIRECT_READ, 0, 0, SLPS25414, 0, "SLPS-25414"}},
    // 仔羊捕獲ケーカク！ スイートボーイズライフ
    {0x911CA2, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-66582"}},
    // Palais de Reine
    {0xB9DDC4, {DIRECT_READ, 0, 0, SLPM66817, 0, "SLPM-66817"}},
    // 東京魔人學園外法帖血風録
    {0xFA73EC, {DIRECT_READ, 0, 0, SLPS25379, 0, std::vector<const char *>{"SLPS-25378", "SLPS-25379"}}},
    // エリュシオン～永遠のサンクチュアリ～
    {0x312FDC, {DIRECT_READ, 0, 0, SLPS25220, 0, "SLPS-25220"}},
    // 純情ロマンチカ ～恋のドキドキ大作戦
    {0x83907A, {DIRECT_READ, 0, 0, 0, SLPS25902, "SLPS-25902"}},
    // 今日からマ王！はじマりの旅 [プレミアムBOX]
    {0x356FB0, {DIRECT_READ | CODEC_UTF8, 0, 0, 0, SLPS25662, "SLPS-25662"}},
    // 今日からマ王！ 眞マ国の休日
    {0x3428D0, {DIRECT_READ | CODEC_UTF8, 0, 0, 0, SLPS25801, "SLPS-25801"}},
    // 遙かなる時空の中で3 運命の迷宮 [Triple Pack]
    {0x1FFE9D8, {DIRECT_READ, 0, 0, SLPM66344, 0, "SLPM-66344"}},
    // Angel's Feather
    {0x31B880, {DIRECT_READ, 0, 0, SLPS20394<0x31B480, 0x31B880, 0x31BC80, 0x31C080>, 0, std::vector<const char *>{"SLPM-65512", "SLPM-65513"}}},
    // 空色の風琴 ～Remix～
    {0x1A9238, {DIRECT_READ, 0, 0, 0, SLPM65843, "SLPM-65848"}},
};

extern void pcsx2_load_functions(std::unordered_map<DWORD, emfuncinfo> &m)
{
    for (auto i = 0; i < ARRAYSIZE(emfunctionhooks_1); i++)
    {
        m.emplace(emfunctionhooks_1[i].addr, emfunctionhooks_1[i].info);
    }
}