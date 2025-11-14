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
    void SLPM66726(TextBuffer *buffer, HookParam *)
    {
        static lru_cache<std::wstring> cache(5);
        static std::wstring last;
        auto s = buffer->strAW();
        if (cache.touch(s))
            return buffer->clear();
        if (endWith(last, s))
            return buffer->clear();
        last = s;
        s = re::sub(s, LR"(<(.*?)>\[(.*?)\])", L"$1");
        strReplace(s, L"\n");
        buffer->fromWA(s);
    }
    void SLPM66491(TextBuffer *buffer, HookParam *)
    {
        auto s = buffer->strAW();
        strReplace(s, L"^");
        s = re::sub(s, L"<(.*?),(.*?)>", L"$1");
        buffer->fromWA(s);
    }
    void SLPM66919(TextBuffer *buffer, HookParam *)
    {
        auto s = buffer->strAW();
        strReplace(s, L"^");
        buffer->fromWA(s);
    }
    void SLPS25468(TextBuffer *buffer, HookParam *)
    {
        auto s = buffer->strAW();
        strReplace(s, L"#");
        buffer->fromWA(s);
    }
    void SLPM66958(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        s = re::sub(s, L"#[a-zA-Z0-9]+");
        buffer->fromWA(s);
    }
    void SLPM65589(TextBuffer *buffer, HookParam *hp)
    {
        if (buffer->size <= 1)
            return buffer->clear();
        SLPM66958(buffer, hp);
    }
    void SLPM66408(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        strReplace(s, "%n");
        s = re::sub(s, "%w\\d+");
        buffer->from(s);
    }
    void SLPM66357(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = s.substr(0, s.find("\n\n"));
        if (startWith(s, "<") || startWith(s, ";"))
        {
            if (startWith(s, "<WINDOW NAME"))
                return buffer->from(re::sub(s.substr(0, s.find("\n") - 1), "<WINDOW NAME=\"(.*?)\".*", "$1"));
            return buffer->clear();
        }
        buffer->from(strReplace(strReplace(s, "<KEYWAIT>"), "\n"));
    }
    void SLPM55016(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        if (startWith(s, "<"))
        {
            if (startWith(s, "<WINDOW NAME"))
                return buffer->from(re::sub(s.substr(0, s.find("\n") - 1), "<WINDOW NAME=\"(.*?)\".*", "\x81\x79$1\x81\x7a"));
            else if (startWith(s, "<SELECT TEXT"))
            {
                std::string collect;
                for (auto &&ss : strSplit(s, "\n"))
                {
                    if (startWith(ss, "<SELECT TEXT"))
                    {
                        if (collect.size())
                            collect += '\n';
                        collect += re::sub(ss, "<SELECT TEXT=\"(.*?)\".*", "$1");
                    }
                }
                return buffer->from(collect);
            }
            else
                return buffer->clear();
        }
        if (!IsShiftjisWord(*(WORD *)s.data()))
            return buffer->clear();
        buffer->from(s.substr(0, 2));
    }
    void SLPM55047(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, "#v\\w+#");
        strReplace(s, "#r\x81\x40");
        strReplace(s, "#r");
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
        s = re::sub(s, R"(%K)");
        buffer->from(s);
    }
    void FSLPM66302(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        s = strSplit(s, L");")[0];
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
    void SLPM66499(TextBuffer *buffer, HookParam *hp)
    {
        static int idx = 0;
        if (buffer->size != 2)
        {
            return buffer->clear();
        }
        auto w = *(WORD *)buffer->buff;
        if (!(IsShiftjisWord(w)))
        {
            return buffer->clear();
        }
        if (idx++ % 3)
            return buffer->clear();
        StringFilter(buffer, TEXTANDLEN("\x81\x40"));
    }
    void SLPM66239(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, '\r');
    }
    void SLPS25612(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, L'\r');
        CharFilter(buffer, L'\n');
    }
    void SLPS25395(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(\\n(\x81\x40)*)");
        buffer->from(s);
    }
    void SLPM66543(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("fc"));
        StringFilter(buffer, TEXTANDLEN("\\c(say)"));
    }
    void SLPS25483(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("@y"));
        StringFilter(buffer, TEXTANDLEN("@w"));
    }
    void SLPM66861(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("||"));
    }
    void SLPM65964(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("||"));
        auto s = buffer->strA();
        if (endWith(s, "\xab"))
        {
            s = s.substr(0, s.size() - 1);
        }
        strReplace(s, "\x81\x40");
        buffer->from(s);
    }
    void SLPS25604(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("CR"));
    }
    void SLPM55170(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        s = re::sub(s, LR"(\{(.*?)\}\[(.*?)\])", L"$1");
        s = re::sub(s, L"%CG(.*?)%CE");
        s = re::sub(s, L"%[A-Z]+");
        buffer->fromWA(s);
        StringFilter(buffer, TEXTANDLEN("\x81\xe8"));
        StringReplacer(buffer, TEXTANDLEN("\x84\xa5\x84\xa7"), TEXTANDLEN("\x81\x5c\x81\x5c"));
        StringReplacer(buffer, TEXTANDLEN("\x81\xe1\x81\x5c\x81\x5c\x81\xe2"), TEXTANDLEN("\x81\x5c\x81\x5c\x81\x5c\x81\x5c"));
    }
    void SLPM66245(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->fromWA(strReplace(s, L"/"));
    }
    void FSLPM65971(TextBuffer *buffer, HookParam *hp)
    {
        static lru_cache<std::string> cache(4);
        auto s = buffer->strA();
        if (cache.touch(s))
            return buffer->clear();
        if (startWith(s, "\x81\x40"))
            s = s.substr(2);
        buffer->from(strReplace(s, "\r"));
    }
    void SLPM65943(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
        s = re::sub(s, "\x02(.*?)\x03(.*?)\x04", "$2");
        s = re::sub(s, "\x01");
        s = re::sub(s, "\xff");
        buffer->from(s);
    }
    void SLPS25689(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        strReplace(s, "@w0");
        s = re::sub(s, "@v\\d+");
        if (last == s)
            return buffer->clear();
        last = s;
        s = re::sub(s, "[\r\n]+(\x81\x40)*");
        buffer->from(s);
    }
    void SLPM55159(TextBuffer *buffer, HookParam *hp)
    {
        SLPM55170(buffer, hp);
        auto s = buffer->strA();
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
    }
    void SLPS25870(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("\n\x81\x40"));
        CharFilter(buffer, '\n');
    }
    void SLPM66935(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("\n\x81\x40"));
    }
    void SLPM65937(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        auto s = buffer->strA();
        if (startWith(s, last))
        {
            buffer->from(s.substr(last.size()));
            last = s;
            return;
        }
        last = s;
        std::string name = (char *)emu_addr(0x601C54);
        if (name.size() && name != "\x81\x40")
            name = "\x81\x79" + name + "\x81\x7a";
        else
            name = "";
        buffer->from(name + buffer->strA());
    }
    void SLPM66112(TextBuffer *buffer, HookParam *hp)
    {
        std::string name = (char *)emu_addr(0x330D92);
        if (name.size())
            name = "\x81\x79" + name + "\x81\x7a";
        buffer->from(name + buffer->strA());
        SLPM66935(buffer, hp);
    }
    void SLPM62343(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, '\n');
        StringFilter(buffer, TEXTANDLEN("/K"));
        StringFilter(buffer, TEXTANDLEN("/L"));
        StringFilter(buffer, TEXTANDLEN("\x81\x40"));
    }
    void SLPS25766(TextBuffer *buffer, HookParam *hp)
    {
        SLPM62343(buffer, hp);
        static std::string last;
        auto s = buffer->strA();
        if (last == s)
            return buffer->clear();
        last = s;
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
        StringFilter(buffer, TEXTANDLEN("\n\x81\x40"));
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
    void SLPM66997(TextBuffer *buffer, HookParam *hp)
    {
        SLPS25897<4>(buffer, hp);
        auto s = buffer->strAW();
        s = re::sub(s, L"\\[(.*?)\\]");
        buffer->fromWA(s);
    }
    void SLPM66858(TextBuffer *buffer, HookParam *hp)
    {
        if (strcmp(hp->name, "SLPM-66858") == 0)
        {
            auto s = buffer->strAW();
            s = re::sub(s, L"\\[(.*?)\\]");
            s = re::sub(s, L"\n(\u3000)+");
            buffer->fromWA(s);
        }
        else if (strcmp(hp->name, "SLPS-25830") == 0)
        {
        }
        SLPS25897<6>(buffer, hp);
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
    void FSLPM66127(TextBuffer *buffer, HookParam *hp)
    {
        StringReplacer(buffer, TEXTANDLEN("\x81\x91"), TEXTANDLEN("!!")); //"――"
        StringReplacer(buffer, TEXTANDLEN("\x81\x90"), TEXTANDLEN("!?")); //"――"
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
        StringReplacer(buffer, TEXTANDLEN("%x02―%x01"), TEXTANDLEN("\x81\x5c\x81\x5c")); //"――"
    }
    void FSLPM55195(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("%n\x81\x40"));
        StringFilter(buffer, TEXTANDLEN("%n"));
    }
    void SLPM55079(TextBuffer *buffer, HookParam *hp)
    {
        FSLPM55195(buffer, hp);
        auto s = buffer->strAW();
        s = re::sub(s, L"@(.*?)@", L"$1");
        buffer->fromWA(s);
    }
    void SLPS25749(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(%h\(\d+\))");
        buffer->from(s);
    }
    void SLPS25719(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        auto s = buffer->strA();
        strReplace(s, "\\@");
        strReplace(s, "\\n");
        s = re::sub(s, "\\f\\d+");
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void SLPM66620(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        if (endWith(s, "p"))
            buffer->from(s.substr(0, s.size() - 1));
    }
    void SLPM66398(TextBuffer *buffer, HookParam *hp)
    {
        SLPM66620(buffer, hp);
        auto s = buffer->strAW();
        strReplace(s, L".");
        strReplace(s, L"r");
        s = re::sub(s, L"v\\d+");
        buffer->fromWA(s);
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
    void SLPM65535(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("#cr0\x81\x40"));
        StringFilter(buffer, TEXTANDLEN("#cr0"));
    }
    void SLPM65634(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("#cr0"));
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
        s = re::sub(s, R"(#\w+?\[[\.\d]*\])");
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
    void SLPM66150(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        if (startWith(s, last))
        {
            buffer->from(strReplace(s.substr(last.size()), "\x01"));
            last = s;
            return;
        }
        last = s;
        buffer->from(strReplace(s, "\x01"));
    }
    void SLPS25193(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        if (endWith(last, s))
        {
            buffer->clear();
        }
        else
        {
            buffer->from(re::sub(s, R"(\\[a-zA-Z0-9]+)"));
        }
        last = s;
    }
    void SLPM66225(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        if (endWith(last, s))
        {
            buffer->clear();
        }
        last = s;
        SLPM66905(buffer, hp);
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
    void SLPM66127X(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        auto str = (char *)PCSX2_REG(a1);
        std::string collect;
        while (*str)
        {
            std::string __ = str;
            str += __.size() + 1;
            if (startWith(__, "\x81\x40"))
            {
                __ = __.substr(2);
            }
            collect += __;
        }
        buffer->from(strReplace(collect, "\n"));
    }
    template <int a, int b, int c>
    void SLPM66344(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        auto addrs = {a, b, c};
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
    void SLPM65971(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        if ((WORD)PCSX2_REG(v1) != 1)
            return;
        buffer->from((char *)PCSX2_REG(s0));
    }
    void SLPM65710(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        if ((WORD)PCSX2_REG(s4) != 0x2f3c)
            return;
        buffer->from((char *)PCSX2_REG(a0));
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
    void SLPM65607(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        const int val = PCSX2_REG(v1);
        if (val != 0x80000000)
            return;
        buffer->from((char *)PCSX2_REG(t0));
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
    void SLPM66470(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, "\n(\x81\x40)*");
        buffer->from(s);
        SLPM55006(buffer, hp);
        s = buffer->strA();
        static std::set<std::string> last;
        if (last.find(s) != last.end())
            return buffer->clear();
        last.emplace(s);
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
    void SLPM66755(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        strReplace(s, "\xf0\x43");
        if (endWith(s, ","))
            s = s.substr(0, s.size() - 1);
        buffer->from(s);
    }
    void SLPM65887(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        if (startWith(s, last))
        {
            buffer->from(s.substr(last.size()));
        }
        last = s;
    }
    void SLPM66757(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        strReplace(s, "%n");
        s = re::sub(s, R"(%s\d{2})");
        buffer->from(s);
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
    void SLPM66460(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        auto s = buffer->strA();
        if (endWith(last, s))
        {
            return buffer->clear();
        }
        last = s;
        s = re::sub(s, R"(@r\(\d,(.*?)\))");
        buffer->from(s);
    }
    void SLPS25668(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        auto s = buffer->strA();
        if (endWith(last, s))
        {
            return buffer->clear();
        }
        last = s;
        if (s.size() == 1)
            return buffer->clear();
        for (int i = 0; i < s.size() / 2; i++)
        {
            if (!IsShiftjisWord(*(WORD *)(s.data() + 2 * i)))
                return buffer->clear();
        }
    }
    void SLPM66605(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        auto s = buffer->strA();
        if (endWith(last, s))
        {
            return buffer->clear();
        }
        last = s;
        if (startWith(s, "*"))
            buffer->from(s.substr(1));
        NewLineCharFilterA(buffer, hp);
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
    void SLPM55098(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        auto s = buffer->strA();
        if (endWith(last, s))
        {
            return buffer->clear();
        }
        last = s;
        StringFilter(buffer, TEXTANDLEN("cr"));
        StringFilter(buffer, TEXTANDLEN("\x81\x40"));
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
    void SLPM66734(TextBuffer *buffer, HookParam *hp)
    {
        auto w = *(WORD *)buffer->buff;
        if (!(IsShiftjisWord(w)))
        {
            return buffer->clear();
        }
        buffer->size = strstr((char *)buffer->buff, "O$") - (char *)buffer->buff;
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
    void SLPM66918(TextBuffer *buffer, HookParam *hp)
    {
        SLPM55156(buffer, hp);
        auto s = buffer->strA();
        static lru_cache<std::string> last(5);
        if (last.touch(s))
            return buffer->clear();
    }
    void SLPM66743(TextBuffer *buffer, HookParam *hp)
    {
        SLPM66918(buffer, hp);
        StringReplacer(buffer, TEXTANDLEN("\x98\xe6"), TEXTANDLEN("\x9f\x54"));
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
    void SLPM66406(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        auto s = buffer->strA();
        if (endWith(last, s))
            return buffer->clear();
        last = s;
        s = s.substr(1);
        if (!IsShiftjisWord(*(WORD *)s.data()))
        {
            last.clear();
            return buffer->clear();
        }
        buffer->from(s);
    }
    void SLPS25278(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(%[A-Z]+\d*)");
        s = re::sub(s, R"((\x81\x40)*\x87\x53)");
        buffer->from(s);
    }
    void SLPM55197(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        auto s = buffer->strA();
        if (endWith(last, s))
            return buffer->clear();
        last = s;
        SLPM55170(buffer, hp);
    }
    void SLPM66791(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        buffer->from(re::sub(s, "%B\\d\\w"));
        SLPM55170(buffer, hp);
    }
    void SLPM55102(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        strReplace(s, L",");
        strReplace(s, L"^");
        strReplace(s, L"\ue09c", L"?");
        buffer->fromWA(s);
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
    void SLPM55225(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        buffer->from_t(*(char *)PCSX2_REG(a0));
    }
    void SLPS25709(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        buffer->from_t(*(char *)PCSX2_REG(a1));
    }
    void SLPM66641(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        auto s = (char *)PCSX2_REG(a1);
        while (strstr(s, "\n") != s)
            s -= 1;
        s += 1;
        static std::string last;
        std::string ss = s;
        ss = ss.substr(0, ss.find("\n"));
        ss = re::sub(ss, "<WINDOW(.*?)>");
        if (ss.size() <= 1)
            return;
        if (last == ss)
            return;
        last = ss;
        buffer->from(ss);
    }
    void SLPM66441(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        std::string s = (char *)PCSX2_REG(a3);
        static std::unordered_map<uintptr_t, std::string> last;
        auto found = last.find(PCSX2_REG(a3));
        if (found != last.end() && found->second == s)
            return;
        if (!IsShiftjisWord(*(WORD *)s.data()))
            return;
        last[PCSX2_REG(a3)] = s;
        buffer->from(s);
    }
    void SLPM66285(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        static char *last = nullptr;
        auto ptr = (char *)PCSX2_REG(a0);
        while (strstr(ptr, "\r\n\r\n") != ptr)
            ptr -= 1;
        ptr += 4;
        if (last == ptr)
            return;
        last = ptr;
        std::string s = ptr;
        if (startWith(s, "<") || startWith(s, "//") || startWith(s, "["))
            return;
        buffer->from(strReplace(re::sub(s.substr(0, s.find("\r\n\r\n")), "<v \\w+>"), "\r\n"));
    }
    void SLPM66329(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = s.substr(0, s.find("KEYWAIT"));
        std::string ss;
        for (auto _ : strSplit(s, "\n"))
        {
            if (all_ascii(_))
                continue;
            ss += _;
        }
        static std::string last;
        if (endWith(last, ss))
            return buffer->clear();
        last = ss;
        buffer->from(strReplace(ss, "\n"));
    }
    void SLPM25257(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->viewA();
        if (s.size() < 2)
        {
            return;
        }
        // prevent junk strings during game boot
        if (!IsShiftjisWord(*(WORD *)s.data()))
        {
            buffer->clear();
            return;
        }
    }
    void SLPS25617(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("\\c"));
    }
    void SLPM66331(TextBuffer *buffer, HookParam *hp)
    {
        SLPS25897<5>(buffer, hp);
        CharFilter(buffer, '\x01');
    }
    void SLPM66352(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        s = re::sub(s, L"%[a-zA-Z0-9]+");
        strReplace(s, L"⑳", L"　");
        buffer->fromWA(s);
    }
    void SLPM66146(TextBuffer *buffer, HookParam *hp)
    {
        SLPM66352(buffer, hp);
        auto s = buffer->strA();
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
    }
    void SLPM65552(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        if (s.find(L"<8") != s.npos)
            return buffer->clear();
        s = s.substr(0, s.find(L"fﾓ"));
        buffer->fromWA(strReplace(s, L"@"));
    }
    void SLPM66254(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        if (s == L"ﾕ" || s == L"ﾐ" || buffer->size == 1)
            return buffer->clear();
    }
    void SLPM66157(TextBuffer *buffer, HookParam *hp)
    {
        if (buffer->size == 1)
            return buffer->clear();
    }
    void SLPM66052(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        if (s[2] == '"')
        {
            return buffer->fromWA(L"【" + re::search(s, L"\"(.*?)\"").value()[1].str() + L"】");
        }
        if (!startWith(s, L"ﾕ"))
            return buffer->clear();
        buffer->fromWA(s.substr(1));
    }
    void SLPS25540(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        if (buffer->buff[0] <= 0x7f)
            return buffer->clear();
        static std::set<std::string> cache;
        if (cache.find(s) != cache.end())
            return buffer->clear();
        cache.insert(s);
        buffer->from(strReplace(strReplace(strReplace(s, "\x84\x71\x84\x72", "\x81\x5b\x81\x5b"), "\n"), "\n\x81\x40"));
    }
    void SLPM66026(TextBuffer *buffer, HookParam *hp)
    {
        if (buffer->size <= 8)
            return buffer->clear();
        buffer->size -= 7;
        auto s = buffer->strAW();
        buffer->fromWA(strReplace(strReplace(s, L"@　"), L"@"));
    }
    void SLPM65867(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        if (!startWith(s, "print"))
            return buffer->clear();
        s = re::sub(s, R"(@\[(.*?)@\])", "\x81\x79$1\x81\x7a");
        strReplace(s, "@n");
        strReplace(s, "@c");
        buffer->from(s.substr(6, s.size() - 7));
    }
    void SLPM65771(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        if (endWith(last, s))
            return buffer->clear();
        last = s;
        static lru_cache<std::string> cache(3);
        if (cache.touch(s))
            return buffer->clear();
        buffer->from(s.substr(2));
    }
    void SLPM65832(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        if (endWith(last, s))
            return buffer->clear();
        last = s;
        auto sw = buffer->strAW();
        std::wstring ss;
        for (auto c : sw)
        {
            if (c <= 0x7f)
                continue;
            ss += c;
        }
        buffer->fromWA(ss);
    }
    void SLPM65866(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        if (endWith(last, s))
            return buffer->clear();
        last = s;
        static std::set<std::string> cache;
        if (cache.find(s) != cache.end())
            return buffer->clear();
        cache.insert(s);
        auto sw = buffer->strAW();
        strReplace(sw, L"@");
        strReplace(sw, L"&");
        strReplace(sw, L"\n");
        strReplace(sw, L"　");
        strReplace(sw, L"\xff");
        buffer->fromWA(sw);
    }
    void SLPM65585(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        auto _ = *(WORD *)PCSX2_REG(a1);
        if (_ <= 0xff || _ == 0x815b)
            return;
        buffer->from_t(_);
        *split = PCSX2_REG(v0);
    }
    void SLPM65785(TextBuffer *buffer, HookParam *hp)
    {
        if (*(WORD *)buffer->buff < 0x100)
            buffer->clear();
    }
    void SLPM62375(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        buffer->from((char *)PCSX2_REG(v1), 1);
    }
    void SLPS25409(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        WORD _ = PCSX2_REG(v0) | (PCSX2_REG(a0) << 8);
        buffer->from_t(_);
    }
    void SLPM65762(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        if (endWith(s, L"p"))
            s = s.substr(0, s.size() - 1);
        strReplace(s, L"kn", L"\n");
        buffer->fromWA(s);
    }
    void SLPM65736(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("#n\x81\x40"));
        FSLPM65997(buffer, hp);
        auto s = buffer->strA();
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
    }
    void SLPM65717(TextBuffer *buffer, HookParam *hp)
    {
        static int idx = 0;
        if ((idx++) % 2 == 0)
            return buffer->clear();
        auto s = buffer->strAW();
        strReplace(s, L"s");
        strReplace(s, L"n");
        buffer->fromWA(s);
    }
    void SLPM65641(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        auto s = buffer->strA();
        if (all_ascii(s.substr(0, 3)))
            return buffer->clear();
        if (s.size() == 3)
            return buffer->clear();
        if (last == s)
            return buffer->clear();
        last = s;
        StringFilter(buffer, TEXTANDLEN("\x81\xa1"));
    }
    void SLPM67009(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        s = re::sub(s, L"<.*?>");
        strReplace(s, L"//　");
        strReplace(s, L"//");
        buffer->fromWA(s);
    }
    void SLPM65555(TextBuffer *buffer, HookParam *hp)
    {
        static lru_cache<std::string> last(4);
        auto s = buffer->strA();
        auto spls = strSplit(s, "\n");
        s.clear();
        for (auto &&_ : spls)
        {
            if (last.touch(_))
                continue;
            if (!s.empty())
                s += '\n';
            s += _;
        }
        buffer->from(s);
    }
    void SLPS25433(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, "%", 2);
    }
    void SLPM67003(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        if (s.size() == 1)
            return buffer->clear();
        if (all_ascii(s))
            return buffer->clear();
        if (s[0] == L'"')
            return buffer->clear();
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->fromWA(strReplace(s, L"//"));
    }
    void SLPM62122(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(strReplace(s, "CR"));
    }
    void SLPM65639(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        if (all_ascii(s))
            return buffer->clear();
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
        StringFilter(buffer, TEXTANDLEN("\\n"));
    }
    void SLPM65448(TextBuffer *buffer, HookParam *hp)
    {
        static lru_cache<std::string> cache(4);
        auto s = buffer->strA();
        if (cache.touch(s))
            return buffer->clear();
        CharFilter(buffer, '\n');
    }
    void SLPM65764(TextBuffer *buffer, HookParam *hp)
    {
        if (buffer->size == 1)
            return buffer->clear();
    }
    void SLPM62509(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        std::string name = (char *)emu_addr(0x22BE80);
        if (name.size())
        {
            s = "\x81\x79" + name + "\x81\x7a" + s;
        }
        buffer->from(s);
    }
    void SLPM65671(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        strReplace(s, L"ｫ");
        strReplace(s, L"ｩ");
        buffer->fromWA(s);
    }
    void SLPS25392(TextBuffer *buffer, HookParam *hp)
    {
        static INT IDX;
        if (IDX++ % 2)
            return buffer->clear();
        StringReplacer(buffer, TEXTANDLEN("\xe9\x85"), TEXTANDLEN("\x81\x79"));
        StringReplacer(buffer, TEXTANDLEN("\xe9\x86"), TEXTANDLEN("\x81\x7a"));
    }
    void SLPS025221(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        if ((DWORD)PCSX2_REG(at) != 0x50210000)
            return;
        std::string s = (char *)PCSX2_REG(a1);
        if (all_ascii(s))
            return;
        static std::string last;
        if (s == last)
            return;
        last = s;
        buffer->from(strReplace(s, "\x81\x40") + "\n");
    }
    void SLPS25219(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        auto s = (char *)PCSX2_REG(a0);
        if ((WORD)PCSX2_REG(v1) == 0x91fc || (WORD)PCSX2_REG(v1) == 0x8f10)
            buffer->from(s);
    }
    void SLPM65559(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        static unsigned char last;
        unsigned char c = PCSX2_REG(a0);
        if (last)
        {
            WORD x = c << 8 | last;
            if (x != 0x4081)
                buffer->from_t(x);
            last = 0;
        }
        else
        {
            if (IsShiftjisLeadByte(c))
                last = c;
        }
    }
    void SLPM66847(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        buffer->from(re::sub(s, "\\$\\w"));
    }
    void SLPM65676(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        if (s == "\xff" || s == "\x03" || s == "\x01" || s == "&" || s == "@")
            return buffer->clear();
    }
    void SLPS25294(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        if (all_ascii(s))
            return buffer->clear();
        if (startWith(s, "["))
            return buffer->clear();
        NewLineCharFilterA(buffer, hp);
    }
    void SLPM65282(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        auto ss = strSplit(s, "#cr0");
        if (ss.size() > 1 && ss[0].size() < 10)
        {
            ss[0] = "\x81\x79" + ss[0] + "\x81\x7a";
        }
        s.clear();
        for (auto &&_ : ss)
        {
            s += _;
        }
        buffer->from(s);
    }
    void SLPS25248(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        if (all_ascii(s) || s == "\x81\x40")
            buffer->clear();
    }
    void SLPM65306(TextBuffer *buffer, HookParam *hp)
    {
        buffer->size -= 7;
        auto s = buffer->strAW();
        strReplace(s, L"@");
        buffer->fromWA(s);
    }
    void SLPS25245(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        strReplace(s, L"／");
        s = re::sub(s, LR"(%?[ A-Z]+\d+)");
        buffer->fromWA(s);
    }
    void SLPM65255(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        s = re::sub(s, LR"([・\u0001-\u007f\uf8f3])");
        buffer->fromWA(s);
    }
    void SLPM65275(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(\n(\x81\x40)*)");
        if ((s[0] == 'B' && s[s.size() - 1] == 'B') || (s[0] == 'W' && s[s.size() - 1] == 'W'))
        {
            s = s.substr(1, s.size() - 2);
        }
        buffer->from(s);
    }
    void SLPS25235(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        strReplace(s, L"@");
        buffer->fromWA(s);
    }
    void SLPM65400(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"([\n\r]+(\x81\x40)*)");
        s = re::sub(s, R"(\x81\x6f(.*?)\x81\x5e(.*?)\x81\x70)", "$2");
        buffer->from(s);
    }
    void SLPM65301(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(#cr0(\x81\x40)*)");
        buffer->from(s);
    }
    void SLPM65295(TextBuffer *buffer, HookParam *hp)
    {
        static bool last = false;
        if (IsShiftjisLeadByte(*(BYTE *)buffer->buff))
        {
            last = true;
        }
        else
        {
            if (!last)
            {
                buffer->clear();
            }
            last = false;
        }
    }
    void SLPS25238(TextBuffer *buffer, HookParam *hp)
    {
        static int i = 0;
        i++;
        if (i % 2 == 1)
            return buffer->clear();
        auto s = buffer->strA();
        s = re::sub(s, R"(%[A-Z])");
        buffer->from(s);
    }
    void SLPM65154(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(\\[a-z])");
        buffer->from(s);
    }
    void SLPS25256(TextBuffer *buffer, HookParam *hp)
    {
        static int i = 0;
        i++;
        if (i % 2 == 1)
            return buffer->clear();
        SLPM65154(buffer, hp);
    }
    void SLPS25223(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("$n"));
        auto s = buffer->strA();
        if (all_ascii(s))
            buffer->clear();
    }
    void SLPM65239(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, "^(.*?)#cr0", "\x81\x79$1\x81\x7a");
        strReplace(s, "#cr0");
        strReplace(s, "\x81\x79\x81\x40\x81\x40\x81\x40\x81\x40\x81\x7a");
        buffer->from(s);
    }
    void SLPM65910(TextBuffer *buffer, HookParam *hp)
    {
        if (buffer->buff[0] == '&')
            return buffer->clear();
        auto s = buffer->strAW();
        s = s.substr(0, s.rfind(L"fV"));
        s = re::sub(s, L"@　*");
        buffer->fromWA(s);
    }
    void SLPM66980(TextBuffer *buffer, HookParam *hp)
    {
        if (buffer->buff[0] == '&')
            return buffer->clear();
        auto s = buffer->strAW();
        s = s.substr(0, s.rfind(L"E\""));
        s = re::sub(s, L"@　*");
        buffer->fromWA(s);
    }
    void SLPS25494(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->viewA();
        if (all_ascii(s))
            return buffer->clear();
        if (s == "\x95\xb6\x8e\x9a\x94\xc5")
            return buffer->clear();
        SLPS25395(buffer, hp);
    }
}
struct emfuncinfoX
{
    DWORD addr;
    emfuncinfo info;
};
static const emfuncinfoX emfunctionhooks_1[] = {
    // Fragrance Tale ～フレグランス テイル～
    {0x128B78, {FULL_STRING, PCSX2_REG_OFFSET(a1), 0, 0, SLPS25494, "SLPS-25494"}},
    {0x4A47A0, {DIRECT_READ, 0, 0, 0, SLPS25395, "SLPS-25494"}},
    // そして僕らは、・・・and he said
    {0x134A6C, {0, 0, 0, SLPM65971, FSLPM65971, "SLPM-65971"}},
    // Apocripha/0
    {0x1222c8, {FULL_STRING, PCSX2_REG_OFFSET(a0), 0, SLPM65710, 0, "SLPM-65710"}},
    // Angel's Feather −黒の残影−
    {0x12D940, {0, PCSX2_REG_OFFSET(t7), 0, 0, SLPM65943, "SLPM-65943"}},
    // 銀のエクリプス
    {0x112858, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPM66980, "SLPM-66980"}},
    // カフェ・リンドバーグ -summer season-
    {0x211e08, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPM65910, "SLPM-65910"}},
    // 裏切りは僕の名前を知っている ～黄昏に堕ちた祈り～
    {0xB424B6, {DIRECT_READ, 0, 0, 0, SLPS25809, "SLPM-55274"}},
    // きみスタ ～きみとスタディ～
    {0x1A37A4, {DIRECT_READ, 0, 0, 0, 0, "SLPM-66376"}},
    // オレンジハニー 僕はキミに恋してる
    {0x6FC7FA, {DIRECT_READ, 0, 0, 0, SLPS25766, "SLPS-25766"}},
    // 紫の焔
    {0xD68412, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-55053"}},
    // ヘルミーナとクルス
    {0x12E374, {0, PCSX2_REG_OFFSET(s1), 0, 0, SLPM62122, "SLPM-62122"}},
    // 君が望む永遠 ～Rumbling hearts～
    {0x230d00, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPM65154, "SLPM-65154"}},
    // エンジェリック・コンサート
    {0xA2B038, {DIRECT_READ, 0, 0, 0, SLPM65239, "SLPM-65239"}},
    // Canvas～セピア色のモチーフ～
    {0x1940c8, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPS25223, "SLPS-25223"}},
    // Never7 ～the end of infinity～
    {0x1a0dd0, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPS25256, "SLPS-25256"}},
    // カナリア～この想いを歌に乗せて～
    {0x1c6be4, {0, PCSX2_REG_OFFSET(a0), 0, SLPS25219, 0, "SLPS-25219"}},
    // 探偵学園Q ～奇翁館の殺意～
    {0x158040, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM67003, "SLPM-65450"}},
    // トライアングルアゲイン2
    {0x16598c, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM65255, "SLPM-65273"}},
    // EVE burst error PLUS
    {0x49B590, {DIRECT_READ, 0, 0, 0, 0, "SLPM-65320"}},
    // あいかぎ ～ぬくもりとひだまりの中で～
    {0x4F263C, {DIRECT_READ, 0, 0, 0, 0, "SLPS-25274"}},
    // My Merry May
    {0x1293C0, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPS25193, std::vector<const char *>{"SLPS-25192", "SLPS-25193"}}},
    // My Merry Maybe
    {0x1598b0, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPS25238, "SLPS-25238"}},
    // My Merry May with be
    {0x1DB7DC, {0, PCSX2_REG_OFFSET(a3), 0, 0, FSLPM66045, "SLPM-66045"}},
    // とらかぷっ！だーっしゅ！！でらっくすぱっく
    {0xA5E964, {DIRECT_READ, 0, 0, 0, SLPM65301, "SLPM-65301"}},
    // カフェ・リトルウィッシュ ～魔法のレシピ～
    {0x11a9b8, {0, PCSX2_REG_OFFSET(v0), 0, 0, SLPM65295, "SLPM-65295"}},
    // ゆめりあ
    {0x227374, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPS25235, "SLPS-25235"}},
    // 最終兵器彼女
    {0xAF4351, {DIRECT_READ, 0, 0, 0, SLPM65275, "SLPM-65275"}},
    // D→A:BLACK [通常版]
    {0x177298, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(v0), 0, 0, 0, "SLPS-25292"}},
    // ビストロ・きゅーぴっと2 特別版
    {0x14A3FC, {0, PCSX2_REG_OFFSET(v1), 0, 0, SLPM65255, "SLPM-65255"}},
    // ファンタスティックフォーチュン2 ☆☆☆
    {0x36DA10, {DIRECT_READ, 0, 0, 0, SLPM66458, "SLPS-25396"}},
    // ビストロ・きゅーぴっと2 特別版
    {0xF61D20, {DIRECT_READ, 0, 0, 0, SLPM65535, "SLPM-65347"}},
    // トゥルーラブストーリー サマーデイズ アンド イエット...
    {0x168B1C, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPS25245, "SLPS-25245"}},
    // SAKURA～雪月華～ [初回限定版]
    {0x25B5C0, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM65306, "SLPM-65306"}},
    // キノの旅 -the Beautiful World-
    {0x12920c, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(s1), 0, 0, SLPS25248, "SLPS-25248"}},
    // グリーングリーン ～鐘の音ロマンティック～
    {0x94B318, {DIRECT_READ, 0, 0, 0, SLPM65282, std::vector<const char *>{"SLPM-65281", "SLPM-65282"}}},
    // カンブリアンQTS ～化石になっても～
    {0x159e10, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPM65448, "SLPM-65448"}},
    // アラビアンズ・ロスト ～The engagement on desert～
    {0x3A2F70, {DIRECT_READ, 0, 0, 0, SLPM66847, "SLPM-66847"}},
    // INTERLUDE
    {0x572040, {DIRECT_READ, 0, 0, 0, SLPS25395, "SLPS-25283"}},
    // てんたま -1st Sunny Side-
    {0x1DFD630, {DIRECT_READ, 0, 0, 0, SLPM66352, "SLPS-25298"}},
    // てんたま2wins [限定版]
    {0x4A3A60, {DIRECT_READ, 0, 0, 0, SLPM66352, "SLPM-65520"}},
    // Remember11 ～the age of infinity～ [通常版]
    {0xAFCF80, {DIRECT_READ, 0, 0, 0, 0, "SLPM-65550"}},
    // 宇宙のステルヴィア
    {0x4CDE54, {0, PCSX2_REG_OFFSET(s1), 0, 0, SLPS25294, "SLPS-25294"}},
    // ステディ×スタディ [限定版]
    {0x194EA40, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-65557"}},
    // ロスト・アヤ・ソフィア
    {0x1992960, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-65592"}},
    // ふぁいなる・アプローチ [通常版]
    {0x21298C, {USING_CHAR | CODEC_ANSI_BE, PCSX2_REG_OFFSET(a0), 0, 0, SLPM65676, "SLPM-65676"}},
    // W ～ウィッシュ～ [初回限定版]
    {0x1107C0, {0, PCSX2_REG_OFFSET(s4), 0, 0, SLPM65671, "SLPM-65671"}},
    // D→A:WHITE [通常版]
    {0x1769bc, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(v0), 0, 0, 0, "SLPS-25438"}},
    // Princess Holiday～転がるりんご亭千夜一夜～
    {0x13c208, {0, PCSX2_REG_OFFSET(a1), 0, SLPM65585, 0, "SLPM-65585"}},
    // おしえて！ ぽぽたん
    {0xB116A4, {DIRECT_READ, 0, 0, 0, SLPM65535, "SLPM-65535"}},
    // メンアットワーク！3 愛と青春のハンター学園 [初回限定版]
    {0x16fd1c, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(s0), 0, 0, SLPM65764, "SLPM-65764"}},
    // DESIRE
    {0x1072D0, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPS25392, "SLPS-25392"}},
    // セイント・ビースト ～螺旋の章～ [限定版]
    {0x1056DC, {0, PCSX2_REG_OFFSET(s0), 0, 0, 0, "SLPS-25807"}},
    // てのひらをたいように ～永久の絆～ [初回限定版]
    {0x211590, {0, 0, 0, SLPM65559, 0, "SLPM-65559"}},
    // パティシエなにゃんこ ～初恋はいちご味～ [限定版]
    {0x147A70, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM65639, "SLPM-65639"}},
    // 水月 ～迷心～
    {0x1e6a20, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM55170, "SLPM-65751"}},
    // 夏少女 Promised Summer
    {0xBBBA70, {DIRECT_READ, 0, 0, 0, SLPM65634, "SLPM-65634"}},
    // 十六夜れんか ～かみふるさと～
    {0x112F2C, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(v1), 0, 0, 0, "SLPM-65545"}},
    // オレンジポケット -リュート- [初回限定版]
    {0x12AF28, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(v0), 0, 0, 0, "SLPM-65524"}},
    // 3LDK ～幸せになろうよ～ [初回限定版]
    {0x15562C, {0, 0, 0, SLPM65607, SLPM66861, "SLPM-65607"}},
    // 帝国千戦記 [初回限定版]
    {0x1DB228, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPS25433, "SLPS-25433"}},
    // サクラ大戦 ～熱き血潮に～
    {0x1f1420, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM67003, "SLPM-67003"}},
    // サクラ大戦Ⅴ ～さらば愛しき人よ～
    {0x1F6E550, {DIRECT_READ, 0, 0, 0, SLPM67009, "SLPM-67009"}},
    // 月は東に日は西に -Operation Sanctuary-
    {0x131890, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM65717, "SLPM-65717"}},
    // うたう♪タンブリング・ダイス ～私たち3人、あ・げ・る～
    {0x122A60, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM65641, "SLPM-65641"}},
    // CROSS+CHANNEL ～To all people～ [限定版]
    {0x198500, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM55170, "SLPM-65546"}},
    // THE 恋愛ホラーアドベンチャー～漂流少女～
    {0x1A1640, {DIRECT_READ, 0, 0, 0, SLPM62343, "SLPM-62343"}},
    // THE 外科医
    {0x22BF40, {DIRECT_READ, 0, 0, SLPM66344<0x22BF40, 0x22BF6F, 0x22BF9E>, SLPM62509, "SLPM-62509"}},
    // THE 娘育成シミュレーション
    {0x132234, {0, 0, 0, SLPM62375, 0, "SLPM-62375"}},
    // THE 恋愛アドベンチャー ～BITTERSWEET FOOLS～
    {0x16C798, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM62207, "SLPM-62207"}},
    // THE 呪いのゲーム
    {0x128D58, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(s1), 0, 0, 0, "SLPS-25581"}}, //@mills
    // ドラゴンクエストⅤ 天空の花嫁
    {0x745A7C, {DIRECT_READ, 0, 0, 0, SLPM65555, "SLPM-65555"}},
    // プリンセスナイトメア
    {0x3E1960, {DIRECT_READ, 0, 0, 0, NewLineCharFilterA, "SLPM-66973"}},
    // Routes PE
    {0x175D48, {USING_CHAR, PCSX2_REG_OFFSET(a1), 0, 0, 0, "SLPS-25727"}},
    // Drastic Killer
    {0x1AC6040, {DIRECT_READ, 0, 0, 0, SLPS25870, std::vector<const char *>{"SLPS-25870", "SLPS-25871"}}},
    // カラフルBOX ～to LOVE～ [通常版]
    {0xD1A970, {DIRECT_READ, 0, 0, 0, SLPM65589, "SLPM-65589"}},
    // PIZZICATO POLKA ～縁鎖現夜～
    {0x4DD7C6, {DIRECT_READ, 0, 0, 0, SLPM55170, "SLPM-65611"}},
    // なついろ ～星屑のメモリー～ [初回限定版]
    {0x16D22C, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(s0), 0, 0, SLPM65785, "SLPM-65785"}},
    // こころの扉 初回限定版 [コレクターズエディション]
    {0x12A508, {0, PCSX2_REG_OFFSET(a1), 0, 0, 0, "SLPS-25348"}},
    // センチメンタルプレリュード
    {0x1653680, {DIRECT_READ, 0, 0, 0, SLPS25395, "SLPS-25395"}},
    // 蒼のままで・・・・・・
    {0x2DB2B0, {DIRECT_READ, 0, 0, 0, SLPM65736, "SLPM-65736"}},
    // 片神名 ～喪われた因果律～
    {0x1CF65c, {DIRECT_READ, 0, 0, 0, SLPM65762, "SLPM-65762"}},
    // 双恋—フタコイ— [初回限定版]
    {0x18A4F8, {USING_CHAR, 0, 0, SLPS25409, 0, "SLPS-25409"}},
    // ラブルートゼロ KissKiss☆ラビリンス [通常版]
    {0x2E8368, {DIRECT_READ, 0, 0, 0, SLPS25604, "SLPM-55149"}},
    // ふしぎ遊戯 朱雀異聞
    {0xF7294C, {DIRECT_READ, 0, 0, 0, FSLPM65997, std::vector<const char *>{"SLPM-66998", "SLPM-66999"}}},
    // ふしぎ遊戯 玄武開伝 外伝 鏡の巫女
    {0x17975E5, {DIRECT_READ, 0, 0, 0, FSLPM65997, std::vector<const char *>{"SLPM-66023", "SLPM-66024"}}}, // [限定版] && [通常版]
    // きまぐれストロベリーカフェ
    {0x2151f0, {DIRECT_READ, 0, 0, SLPM66344<0x2151f0, 0x215215, 0x21523a>, 0, "SLPM-65381"}},
    // Yo-Jin-Bo ～運命のフロイデ～
    {0x20ee28, {0, PCSX2_REG_OFFSET(t4), 0, 0, SLPM66543, "SLPM-66543"}},
    // 永遠のアセリア −この大地の果てで−
    {0x141A80, {0, PCSX2_REG_OFFSET(t7), 0, 0, SLPS25468, "SLPS-25468"}},
    // IZUMO コンプリート
    {0x12DD1C, {0, PCSX2_REG_OFFSET(v1), 0, 0, SLPM65832, "SLPM-65832"}},
    // 新世紀エヴァンゲリオン 綾波育成計画 with アスカ補完計画
    {0xF2AA20, {DIRECT_READ, 0, 0, 0, 0, "SLPM-65334"}},
    // 新世紀エヴァンゲリオン 鋼鉄のガールフレンド2nd
    {0x126BC4, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPM65867, "SLPM-65867"}},
    // 何処へ行くの、あの日 ～光る明日へ…～
    {0x219A2C, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPM65866, "SLPM-65866"}},
    // 月は切り裂く ～探偵 相楽恭一郎～ [限定版]
    {0x19722F5, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-65895"}},
    // すい～とし～ずん
    {0x20B810, {DIRECT_READ, 0, 0, 0, SLPS25483, "SLPS-25483"}},
    // ナチュラル2 -DUO- 桜色の季節 DXパック
    {0x132150, {0, PCSX2_REG_OFFSET(s3), 0, 0, SLPM65771, "SLPM-65771"}},
    // マビノ×スタイル
    {0x4DC238, {DIRECT_READ, 0, 0, 0, SLPM55170, "SLPM-65941"}},
    // Dear My Friend ～Love like powdery snow～
    {0x16EA9C, {0, PCSX2_REG_OFFSET(s0), 0, 0, SLPM66052, "SLPM-65918"}},
    // 初恋-first kiss- 初回限定版
    {0x2133F8, {0, PCSX2_REG_OFFSET(s4), 0, 0, SLPM66026, "SLPM-66026"}},
    // for Symphony ～with all one's heart～
    {0x2AFEF0, {DIRECT_READ, 0, 0, 0, SLPS25395, "SLPS-25506"}},
    // ホームメイド ～終の館～ [初回限定版]
    {0x16CBB4, {0, PCSX2_REG_OFFSET(s0), 0, 0, SLPM66052, "SLPM-65962"}},
    // まじかる☆ている ～ちっちゃな魔法使い～ [初回限定版]
    {0x17F3A8, {DIRECT_READ, 0, 0, 0, SLPM66861, "SLPM-65964"}},
    {0x110DA0, {0, PCSX2_REG_OFFSET(s4), 0, 0, SLPM65964, "SLPM-65964"}},
    // Like Life an hour [通常版]
    {0x1AE51C, {0, PCSX2_REG_OFFSET(t0), 0, 0, SLPM65887, "SLPM-65887"}},
    // らぶドル ～Lovely Idol～ [初回限定版]
    {0x190888, {DIRECT_READ, 0, 0, 0, 0, "SLPM-65968"}},
    // スクールランブル ねる娘は育つ。
    {0x18C0A0, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPS25540, "SLPS-25540"}},
    // 巫女舞 ～永遠の想い～
    {0x165E38, {0, PCSX2_REG_OFFSET(s2), 0, 0, SLPM66052, "SLPM-66052"}},
    // 雪語り リニューアル版
    {0x4152C0, {DIRECT_READ, 0, 0, 0, SLPM66458, "SLPS-25482"}},
    // ラムネ ～ガラスびんに映る海～ 初回限定版
    {0x256070, {DIRECT_READ, 0, 0, 0, SLPM66458, "SLPM-66083"}},
    // 双恋島 恋と水着のサバイバル！
    {0x15C5E8, {0, PCSX2_REG_OFFSET(s4), 0, 0, 0, "SLPS-25543"}},
    // 極上生徒会
    {0x1DB1A60, {DIRECT_READ, 0, 0, 0, SLPM66352, "SLPM-66086"}},
    // しろがねの鳥籠 [通常版]
    {0x424710, {DIRECT_READ | CODEC_UTF8, 0, 0, 0, SLPM66150, "SLPM-66150"}},
    // 星界の戦旗
    {0x60300C, {DIRECT_READ, 0, 0, SLPM66344<0x60300C, 0x6030EC, 0x6031CC>, SLPM65937, "SLPM-65937"}},
    // ふしぎの海のナディア [通常版]
    {0x330D08, {DIRECT_READ, 0, 0, SLPM66344<0x330D08, 0x330D36, 0x330D64>, SLPM66112, "SLPM-66112"}},
    // ルーンプリンセス 初回限定版
    {0x11AA2C, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(t5), 0, 0, SLPM66157, "SLPM-66157"}},
    // 式神の城 七夜月幻想曲
    {0x1722E8, {0, PCSX2_REG_OFFSET(s4), 0, 0, NewLineCharFilterA, "SLPM-66069"}},
    // ふぁいなりすと [通常版]
    {0x167428, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(s2), 0, 0, SLPM66254, "SLPM-66254"}},
    // メタルウルフREV [初回限定版]
    {0x125830, {0, PCSX2_REG_OFFSET(s4), 0, 0, SLPM65552, "SLPM-65552"}},
    // ジュエルスオーシャン Star of Sierra Leone
    {0x115CB8, {0, PCSX2_REG_OFFSET(s2), 0, 0, SLPM66245, "SLPM-66245"}},
    // 闇夜にささやく ～探偵 相楽恭一郎～ [通常版]
    {0x186AB6C, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-66296"}},
    // 魔法先生ネギま！ 課外授業 乙女のドキドキ・ビーチサイド
    {0x2A1CF8, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPM66329, "SLPM-66329"}},
    // e'tude prologue ～揺れ動く心のかたち～
    {0x2EF2C0, {DIRECT_READ, 0, 0, 0, SLPS25617, "SLPS-25617"}},
    // 高円寺女子サッカー 1st stage限定版
    {0x53FA10, {CODEC_UTF8 | DIRECT_READ, 0, 0, 0, SLPM66331, "SLPM-66331"}},
    // つよきす ～Mighty Heart～ [通常版]
    {0x99A124, {DIRECT_READ, 0, 0, 0, SLPM66408, "SLPM-66408"}},
    // ローゼンメイデン ドゥエルヴァルツァ [通常版]
    {0x2178C4, {0, PCSX2_REG_OFFSET(t0), 0, 0, SLPM66357, "SLPM-66357"}},
    // F～ファナティック～ [初回限定版]
    {0x102748, {USING_CHAR | CODEC_ANSI_BE, PCSX2_REG_OFFSET(t2), 0, 0, 0, std::vector<const char *>{"SLPM-65296", "SLPM-65297"}}}, //@mills
    // 想いのかけら ～Close to ～
    {0xC28066, {DIRECT_READ, 0, 0, 0, SLPM25257, "SLPS-25257"}}, //@mills
    // 舞-HiME 運命の系統樹
    {0x4AEE40, {DIRECT_READ, 0, 0, 0, 0, "SLPS-25508"}}, //@mills
    // 桜華 ～心輝かせる桜～
    {0x16AABC, {0, PCSX2_REG_OFFSET(s1), 0, 0, SLPM66406, "SLPM-66406"}},
    // ギャラクシーエンジェルⅡ ～絶対領域の扉～ [通常版]
    {0x1529DC3, {DIRECT_READ, 0, 0, 0, NewLineCharFilterA, "SLPM-66243"}},
    // 魂響 ～御霊送りの詩～ [通常版]
    {0x1D344D0, {DIRECT_READ, 0, 0, 0, SLPM66757, "SLPM-66433"}},
    // あそびにいくヨ！ ～ちきゅうぴんちのこんやくせんげん～
    {0x1A80F42, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-66457"}},
    // スクールランブル二学期 恐怖の(?)夏合宿！ 洋館に幽霊現る！？ お宝を巡って真っ向勝負!!!の巻 [初回限定版]
    {0x19C8D4, {DIRECT_READ, 0, 0, 0, 0, "SLPS-25669"}},
    // あやかしびと -幻妖異聞録- [通常版]
    {0x23F138, {DIRECT_READ, 0, 0, 0, SLPM66491, "SLPM-66491"}},
    // Strawberry Panic！ [通常版]
    {0x1E53908, {DIRECT_READ | CODEC_UTF16, 0, 0, 0, SLPS25612, "SLPS-25612"}},
    // パルフェ Chocolat Second Style
    {0x1E0C7Fb, {DIRECT_READ, 0, 0, 0, SLPM66398, "SLPM-66398"}},
    // レッスルエンジェルス SURVIVOR
    {0x7EA530, {DIRECT_READ, 0, 0, 0, SLPM66239, "SLPM-66239"}},
    // _summer##
    {0x15EDDC, {0, PCSX2_REG_OFFSET(s4), 0, 0, SLPM66460, "SLPM-66460"}},
    // 鳥篭の向こうがわ
    {0x12B96C, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPS25668, "SLPS-25668"}},
    // 龍刻 Ryu-Koku [限定版]
    {0x1E15280, {DIRECT_READ, 0, 0, 0, FSLPM66045, "SLPM-66534"}},
    // 夢見師 [初回限定版]
    {0x1AD96C, {DIRECT_READ, 0, 0, 0, SLPM66861, "SLPM-66618"}},
    // 乙女の事情 [初回限定版]
    {0x1B090C, {DIRECT_READ, 0, 0, 0, SLPM66861, "SLPM-66507"}},
    // 神様家族 応援願望
    {0x1293AC, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM66499, "SLPM-66499"}},
    // Gift -prism- [通常版]
    {0x4B5A50, {DIRECT_READ, 0, 0, 0, NewLineCharFilterA, "SLPM-66530"}},
    // 女子高生 GAME'S-HIGH！
    {0x12A5445, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-66495"}},
    // 世界ノ全テ ～two of us～
    {0x1C0F98, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM55156, "SLPM-66544"}},
    // ホワイトブレス～絆～ [通常版]
    {0x1EC6018, {DIRECT_READ, 0, 0, 0, SLPM55170, "SLPM-66607"}},
    // 保健室へようこそ [通常版]
    {0x1A0510, {DIRECT_READ, 0, 0, 0, 0, "SLPM-66440"}},
    // I”s Pure
    {0xDADAF8, {DIRECT_READ, 0, 0, 0, 0, "SLPM-66570"}},
    // REC☆ドキドキ声優パラダイス☆ [通常版]
    {0x16BA7B2, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-66565"}},
    // すくぅ～る らぶっ！～恋と希望のメトロノーム～
    {0x14FE48, {0, 0, 0, SLPM66641, 0, "SLPM-66641"}},
    // 「ラブ★コン ～パンチDEコント～」[通常版]
    {0x18B810, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPM66470, "SLPM-66470"}},
    // 蒼い空のネオスフィア ～ナノカ・フランカ発明工房記2～ [通常版]
    {0x1AEEB4B, {DIRECT_READ, 0, 0, 0, SLPS25749, "SLPS-25749"}},
    // 智代アフター ～It's a Wonderful Life～ CS Edition
    {0x58E7C5, {DIRECT_READ, 0, 0, 0, 0, "SLPM-66611"}},
    // はぴねす！でらっくす [初回限定版]
    {0x1A13B4, {DIRECT_READ, 0, 0, 0, SLPS25719, "SLPS-25719"}},
    // ひぐらしのなく頃に祭
    {0x1E0697C, {DIRECT_READ, 0, 0, 0, SLPM66620, "SLPM-66620"}},
    // きると ～貴方と紡ぐ夢と恋のドレス～ [初回限定版]
    {0x113470, {0, PCSX2_REG_OFFSET(s4), 0, 0, SLPM66734, "SLPM-66734"}},
    // シムーン 異薔薇戦争 封印のリ・マージョン [通常版]
    {0x1D3D178, {DIRECT_READ, 0, 0, 0, SLPS25689, "SLPS-25689"}},
    // お嬢様組曲 -Sweet Concert- [通常版]
    {0x116E34, {0, PCSX2_REG_OFFSET(t5), 0, 0, SLPM66726, "SLPM-66726"}},
    // まじしゃんず・あかでみい
    {0x2DB307, {DIRECT_READ, 0, 0, 0, NewLineCharFilterA, "SLPS-25775"}},
    // 許嫁 [初回限定版]
    {0x1B22E4, {DIRECT_READ, 0, 0, 0, SLPM66861, "SLPM-66732"}},
    // 魔女っ娘ア・ラ・モードⅡ ～魔法と剣のストラグル～ [通常版]
    {0x549F50, {DIRECT_READ, 0, 0, 0, SLPM66755, "SLPM-66755"}},
    // Que ～エンシェントリーフの妖精～ [通常版]
    {0x8A2488, {DIRECT_READ, 0, 0, 0, SLPM66757, "SLPM-66757"}},
    // IZUMO零 ～横濱あやかし絵巻～
    {0x657790, {DIRECT_READ, 0, 0, 0, 0, "SLPM-66764"}},
    // 夜刀姫斬鬼行 -剣の巻-
    {0x10BC0C, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(t0), 0, 0, SLPM65786, "SLPM-66598"}},
    // キャッスルファンタジア アリハト戦記
    {0x127184, {0, PCSX2_REG_OFFSET(v1), 0, 0, SLPM66605, "SLPM-66605"}},
    // 月面兎兵器ミーナ -ふたつのPROJECT M- [通常版]
    {0x394E3C, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-66754"}},
    // プリンセスコンチェルト [通常版]
    {0x389920, {0, 0, 0, SLPM66285, 0, "SLPM-66285"}},
    // 妖鬼姫伝 ～あやかし幻灯話～ [限定版]
    {0xD103A2, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-66826"}},
    // StarTRain -your past makes your future- [初回限定版]
    {0x18E980, {DIRECT_READ, 0, 0, 0, 0, "SLPM-66879"}},
    // カラフルアクアリウム～My Little Mermaid～ [通常版]
    {0x9D9804, {DIRECT_READ, 0, 0, 0, 0, "SLPM-66805"}},
    // 熱帯低気圧少女 [通常版]
    {0x1B4044, {DIRECT_READ, 0, 0, 0, SLPM66861, "SLPM-66861"}},
    // ぷりサガ～プリンセスをさがせ～
    {0x114128, {0, PCSX2_REG_OFFSET(s2), 0, 0, SLPM55016, "SLPM-66890"}},
    // 最終試験くじら−Alive− //SLPM-66809
    // 水夏A.S+ Eternal Name [通常版] //SLPM-66787
    {0x1FFE8C0, {DIRECT_READ, 0, 0, 0, NewLineCharFilterA, std::vector<const char *>{"SLPM-66809", "SLPM-66787"}}},
    // プリンセスメーカー5
    {0x19B5D4, {0, PCSX2_REG_OFFSET(v0), 0, 0, SLPM66918, "SLPM-66918"}},
    // School Days L×H
    {0x1421AC, {0, PCSX2_REG_OFFSET(v1), 0, 0, 0, "SLPM-67015"}},
    // IZUMO2 学園狂想曲 ダブルタクト
    {0xDDC80E, {DIRECT_READ, 0, 0, 0, 0, "SLPM-66908"}},
    // 君が主で執事が俺で～お仕え日記～ [初回限定版]
    {0x1EF66E0, {DIRECT_READ, 0, 0, 0, FSLPM55195, "SLPM-66933"}},
    // Φなる・あぷろーち 2 ～1st priority～ [初回限定版]
    {0x1B64F4, {DIRECT_READ, 0, 0, 0, 0, "SLPM-66942"}},
    // 12RIVEN - the Ψcliminal of integral -
    {0x1D3DDB0, {DIRECT_READ, 0, 0, 0, SLPM55170, "SLPM-66901"}},
    // 吸血奇譚 ムーンタイズ
    {0x2B1780, {DIRECT_READ, 0, 0, 0, SLPM66919, "SLPM-66919"}},
    // true tears～トゥルーティアーズ～
    {0x564568, {DIRECT_READ, 0, 0, 0, SLPM66935, "SLPM-66935"}},
    // プリズム・アーク -AWAKE-
    {0x173F94, {0, PCSX2_REG_OFFSET(s1), 0, 0, 0, "SLPM-66846"}},
    // 終末少女幻想アリスマチック Apocalypse [通常版]
    {0x1BCA7D0, {DIRECT_READ, 0, 0, 0, SLPM66997, "SLPM-66997"}},
    // ほしがりエンプーサ
    {0x3649D0, {DIRECT_READ, 0, 0, 0, SLPS25395, "SLPM-66969"}},
    // ほしフル～星の降る街～
    {0x6F0B28, {DIRECT_READ, 0, 0, SLPM66344<0x6F0B28, 0x6F0B5D, 0x6F0B92>, 0, "SLPM-66920"}},
    // H2Oプラス
    {0xD88890, {DIRECT_READ, 0, 0, 0, 0, "SLPM-66921"}},
    // Lの季節2 ～Invisible Memories～ [通常版]
    {0x1D43970, {DIRECT_READ, 0, 0, 0, SLPM55170, "SLPM-55009"}},
    // アオイシロ [初回限定版]
    {0xB2F560, {DIRECT_READ, 0, 0, 0, SLPM66958, "SLPM-66958"}},
    // よつのは ～a journey of sincerity～ [通常版]
    {0x114218, {0, PCSX2_REG_OFFSET(s2), 0, 0, SLPM55016, "SLPM-55016"}},
    // 白銀のソレイユ Contract to the future 未来への契約 [通常版]
    {0x1FFD934, {DIRECT_READ, 0, 0, 0, SLPS25897<3>, "SLPM-55026"}},
    // Sugar+Spice！ ～あの子のステキな何もかも～
    {0x64508E, {DIRECT_READ, 0, 0, 0, SLPM55047, "SLPM-55047"}},
    // シークレットゲーム -KILLER QUEEN-
    {0x1BC90C0, {DIRECT_READ, 0, 0, 0, 0, "SLPM-55028"}},
    // レッスルエンジェルス サバイバー2
    {0xEAC080, {DIRECT_READ, 0, 0, 0, NewLineCharFilterA, "SLPM-55058"}},
    // 夢見白書 ～Second Dream～ [通常版]
    {0x1B3EC4, {DIRECT_READ, 0, 0, 0, 0, "SLPM-55071"}},
    // Scarlett ～日常の境界線～ [通常版]
    {0x4906D9, {DIRECT_READ, 0, 0, 0, SLPM55079, "SLPM-55079"}},
    // 恋する乙女と守護の楯 [通常版]
    {0x13294C, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM55098, "SLPM-55098"}},
    // 大奥記
    {0x1BF050, {0, 0, 0, SLPM66441, 0, "SLPM-66441"}},
    // Piaキャロットへようこそ！！G.P. ～学園プリンセス～
    {0x23AF40, {DIRECT_READ, 0, 0, 0, SLPM55102, "SLPM-55102"}},
    // Piaキャロットへようこそ！！3 ～round summer～
    {0x11f960, {0, 0, 0, SLPS025221, 0, "SLPS-25221"}},
    // Clear ～新しい風の吹く丘で～
    {0x1D0C580, {DIRECT_READ, 0, 0, 0, 0, "SLPM-55136"}},
    // ヒャッコ よろずや事件簿！
    {0x17B6D4, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM55159, "SLPM-55159"}},
    // トリガーハート エグゼリカ エンハンスド
    {0x324694, {0, PCSX2_REG_OFFSET(s0), 0, 0, SLPM55052, "SLPM-55052"}},
    // Memories Off Duet ～1st & 2nd Stories～
    {0xA929BC, {DIRECT_READ, 0, 0, 0, SLPM66352, "SLPS-25226"}},
    // Memories Off ～それから～ [通常版]
    {0xB9B400, {DIRECT_READ, 0, 0, 0, SLPM66352, "SLPM-65610"}},
    // Memories Off ～それから again～ [限定版]
    {0x1E03CF0, {DIRECT_READ, 0, 0, 0, SLPM66352, "SLPM-66352"}},
    // Memories Off AfterRain vol.1 折鶴 [SPECIAL EDITION]
    {0xC49B80, {DIRECT_READ, 0, 0, 0, SLPM66352, "SLPM-65857"}},
    // Memories Off AfterRain Vol.2 想演
    {0xC49D00, {DIRECT_READ, 0, 0, 0, SLPM66352, "SLPM-65903"}},
    // Memories Off #5 とぎれたフィルム
    {0x1F34FE0, {DIRECT_READ, 0, 0, 0, SLPM66146, std::vector<const char *>{"SLPM-66146", "SLPM-66147"}}},
    // Memories Off #5 encore [通常版]
    {0x1D4E270, {DIRECT_READ, 0, 0, 0, SLPM66791, "SLPM-66791"}},
    // Memories Off 6 ～T-Wave～ [通常版]
    {0x1A1528, {0, PCSX2_REG_OFFSET(s3), 0, 0, SLPM55197, "SLPM-66988"}},
    // Memories Off 6 Next Relation
    {0x17F334, {0, PCSX2_REG_OFFSET(v1), 0, 0, SLPM55197, "SLPM-55197"}},
    // メモオフみっくす
    {0x1943860, {DIRECT_READ, 0, 0, 0, SLPS25278, "SLPS-25278"}},
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
    // 萌え萌え2次大戦（略）☆デラックス
    {0x1ACF30, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPM55156, "SLPS-25896"}},
    // 萌え萌え2次大戦(略)2[chu～♪] [通常版]
    {0x1A2690, {0, PCSX2_REG_OFFSET(t4), 0, 0, NewLineCharFilterA, "SLPS-25956"}},
    // ストライクウィッチーズ あなたとできること [通常版]
    {0x10A948, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(a0), 0, 0, 0, "SLPM-55174"}},
    // 恋姫†夢想 ～ドキッ☆乙女だらけの三国志演義～ [通常版]
    {0x66C5C0, {DIRECT_READ, 0, 0, 0, SLPS25395, "SLPM-55068"}},
    // 真・恋姫†夢想 ～乙女繚乱☆三国志演義～ [通常版]
    {0xBC9740, {DIRECT_READ, 0, 0, 0, SLPS25395, "SLPM-55288"}},
    // 神曲奏界ポリフォニカ
    {0x1239C8, {0, PCSX2_REG_OFFSET(s0), 0, 0, SLPM66743, "SLPM-66743"}},
    // 神曲奏界ポリフォニカ 0～4話フルパック
    {0x3B56F0, {DIRECT_READ, 0, 0, 0, 0, "SLPM-66977"}},
    // 神曲奏界ポリフォニカ THE BLACK -EPSODE 1 & 2 BOX EDITION-
    {0x309570, {DIRECT_READ, 0, 0, 0, 0, "SLPM-55095"}},
    // 神曲奏界ポリフォニカ ３&４話完結編
    {0x38A8B0, {DIRECT_READ, 0, 0, 0, 0, "SLPM-66909"}},
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
    // Missing Blue
    {0x12A80C, {0, 0, 0, SLPS25051, 0, std::vector<const char *>{"SLPS-25039", "SLPS-25051"}}}, //@mills
    // 四八 （仮）
    {0x17529C, {0, 0, 0, SLPS25759, 0, "SLPS-25759"}}, //@mills
    // かまいたちの夜2 ～監獄島のわらべ唄～ [通常版]
    {0x111C78, {USING_CHAR | CODEC_ANSI_BE, PCSX2_REG_OFFSET(a1), 0, 0, 0, "SLPS-25135"}}, //@mills
    // かまいたちの夜x3 三日月島事件の真相
    {0x112830, {USING_CHAR | CODEC_ANSI_BE, PCSX2_REG_OFFSET(v0), 0, 0, 0, "SLPM-66452"}}, //@mills
    // 桃華月憚 ～光風の陵王～
    {0x29AB3C, {0, 0, 0, 0, 0, "SLPM-55200"}},
    // 夏色の砂時計
    {0x205554, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(v1), 0, 0, 0, std::vector<const char *>{"SLPM-65136", "SLPM-65125", "SLPS-25026"}}},
    // なついろ ～星屑のメモリー～
    {0x16D230, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(s0), 0, 0, SLPM65786, "SLPM-65786"}},
    // 夏色小町【一日千夏】
    {0x2AB318, {DIRECT_READ, 0, 0, 0, SLPM65355, std::vector<const char *>{"SLPM-65355", "SLPM-65356"}}},
    // SDガンダム - G GENERATION WARS
    {0x4BF474, {0, PCSX2_REG_OFFSET(a1), 0, 0, SLPS25941, "SLPS-25941"}},
    {0x51B59C, {0, PCSX2_REG_OFFSET(v1), 0, 0, SLPS25941_2, "SLPS-25941"}},
    // 風雨来記
    {0x1FFACA0, {DIRECT_READ, 0, 0, 0, SLPM66458, "SLPM-66458"}},
    // 風雨来記2
    {0x2AC77C, {0, 0, 0, SLPM66163, 0, "SLPM-66163"}}, //@mills
    // あかね色に染まる坂 ぱられる
    {0x126660, {0, PCSX2_REG_OFFSET(v1), 0, 0, SLPM55006, "SLPM-55006"}},
    // 赤川次郎ミステリー月の光　 ～沈める鐘の殺人～
    {0x118150, {USING_CHAR | CODEC_ANSI_BE, PCSX2_REG_OFFSET(a0), 0, 0, 0, "SLPS-20196"}}, //@mills
    // 最終電車
    {0x1264EC, {0, 0, 0, SLPS25081, 0, "SLPS-25081"}}, //@mills
    // 夏夢夜話
    {0x7689BC, {DIRECT_READ, 0, 0, 0, SLPS25276, "SLPS-25276"}},
    // マイネリーベ 優美なる記憶
    {0x19BF230, {DIRECT_READ, 0, 0, 0, SLPM65684, "SLPM-65684"}},
    // マイネリーベⅡ ～誇りと正義と愛～
    {0x1FFD0DC, {DIRECT_READ, 0, 0, 0, SLPM66247, "SLPM-66247"}},
    // セパレイトハーツ (Separate Hearts)
    {0x1F63320, {DIRECT_READ, 0, 0, 0, SLPM66352, "SLPM-66298"}}, //@mills
    // アカイイト
    {0x136800, {0, PCSX2_REG_OFFSET(t0), 0, 0, FSLPM66136, "SLPM-65732"}},
    // Nana
    {0x15036C, {0, PCSX2_REG_OFFSET(a3), 0, 0, FSLPM65914, "SLPM-65914"}},
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
    // 好きなものは好きだからしょうがない！！ -FIRST LIMIT & TARGET†NIGHTS- Sukisho！ Episode ＃01+＃02
    {0x268CE9, {DIRECT_READ, 0, 0, SLPS20394<0x268CE9, 0x268D2A, 0x268D6B, 0x268DAC>, 0, "SLPS-20352"}}, //[ディスク 1]
    {0x2690EA, {DIRECT_READ, 0, 0, SLPS20394<0x2690EA, 0x26912A, 0x26916B, 0x2691AC>, 0, "SLPS-20353"}}, //[ディスク 2]
    // 好きなものは好きだからしょうがない！！ -RAIN- Sukisyo！ Episode #03
    {0x2AF161, {DIRECT_READ, 0, 0, SLPS20394<0x2AF161, 0x2AFAA8, 0x2AEFA4, 0x2AEFE5>, 0, "SLPS-20394"}},
    // ドラスティックキラー
    {0x1AC5D40, {DIRECT_READ, 0, 0, 0, SLPL25871, "SLPS-25871"}},
    {0x1AC6970, {DIRECT_READ, 0, 0, 0, SLPL25871, "SLPS-25871"}},
    // うたわれるもの 散りゆく者への子守唄
    {0x50574C, {DIRECT_READ, 0, 0, 0, SLPS25679, std::vector<const char *>{"SLPS-25678", "SLPS-25679"}}},
    // Only you リベルクルス ドラマCD付き
    {0x461F38, {DIRECT_READ, 0, 0, SLPS25150, 0, "SLPS-25150"}},
    // D.C.P.S. ～ダ・カーポ～ プラスシチュエーション
    {0x114384, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPM65400, "SLPM-65400"}},
    // D.C. ～ダ・カーポ～ the Origin
    {0x517688, {DIRECT_READ, 0, 0, 0, SLPM66905, "SLPM-66905"}},
    // D.C.I.F. ～ダ・カーポ～イノセント・フィナーレ～ [通常版]
    {0x114068, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPM55156, "SLPM-55156"}},
    // D.C.F.S. ～ダ・カーポ～ フォーシーズンズ DXパック
    {0x112A98, {0, PCSX2_REG_OFFSET(a0), 0, 0, SLPM66225, "SLPM-66225"}},
    // Soul Link EXTENSION
    {0x1E14A3C, {DIRECT_READ, 0, 0, 0, SLPM66437, "SLPM-66437"}},
    // デ・ジ・キャラット ファンタジー エクセレント
    {0x10E2C80, {DIRECT_READ, 0, 0, 0, NewLineCharFilterA, "SLPM-65396"}},
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
    // いつか、届く、あの空に。 ～陽の道と緋の昏と～ [通常版] //SLPM-66858
    // ゼロの使い魔 夢魔が紡ぐ夜風の幻想曲 [限定版] //SLPS-25830
    {0x1FFD900, {DIRECT_READ, 0, 0, 0, SLPM66858, std::vector<const char *>{"SLPM-66858", "SLPS-25830"}}},
    // ゼロの使い魔 迷子の終止符と幾千の交響曲
    {0x1FFD934, {DIRECT_READ, 0, 0, 0, SLPS25897_1, "SLPS-25897"}},
    // ゼロの使い魔 小悪魔と春風の協奏曲 [通常版]
    {0x1C0E38, {0, 0, 0, SLPS25709, NewLineCharFilterA, "SLPS-25709"}},
    // スキップ・ビート
    {0x1CF70F0, {DIRECT_READ, 0, 0, 0, SLPM55170, "SLPM-55170"}},
    // Myself;Yourself
    {0x1443e8, {0, 0, 0, SLPM66892, 0, std::vector<const char *>{"SLPM-66891", "SLPM-66892"}}},   // [通常版] && [初回限定版]
    {0x13F1F8, {0, 0, 0, SLPM66892_1, 0, std::vector<const char *>{"SLPM-66891", "SLPM-66892"}}}, // [通常版] && [初回限定版]
    // Myself; Yourself それぞれのfinale
    {0x1C785A8, {DIRECT_READ, 0, 0, 0, 0, "SLPM-55163"}},
    // ARIA The ORIGINATION ～蒼い惑星のエルシエロ～
    {0x10F8488, {DIRECT_READ, 0, 0, 0, SLPM66352, "SLPM-55014"}},
    // ARIA The NATURAL ～遠い記憶のミラージュ～
    {0x1137428, {DIRECT_READ, 0, 0, 0, 0, "SLPM-66536"}},
    // 猛獣使いと王子様
    {0x16681E0, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-55264"}},
    // 120円の春
    {0x1CEAF56, {DIRECT_READ, 0, 0, 0, SLPS25395, "SLPM-65843"}},
    // ゲームになったよ！ドクロちゃん～健康診断大作戦～
    {0x1B9Bbec, {DIRECT_READ, 0, 0, 0, FSLPM65997, "SLPM-66186"}},
    // 地獄少女 澪縁
    {0x2A078F, {DIRECT_READ, 0, 0, 0, NewLineCharFilterA, "SLPM-55213"}},
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
    {0x83907A, {DIRECT_READ, 0, 0, 0, SLPS25809, "SLPS-25902"}},
    // 今日からマ王！はじマりの旅 [プレミアムBOX]
    {0x356FB0, {DIRECT_READ | CODEC_UTF8, 0, 0, 0, SLPS25662, "SLPS-25662"}},
    // 今日からマ王！ 眞マ国の休日
    {0x3428D0, {DIRECT_READ | CODEC_UTF8, 0, 0, 0, SLPS25801, "SLPS-25801"}},
    // 遙かなる時空の中で3 運命の迷宮
    {0x1FD73C, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(t7), 0, 0, FSLPM66127, std::vector<const char *>{"SLPM-66344", "SLPM-66347", "SLPM-66348"}}}, // 开场
    {0x1FD6A0, {0, PCSX2_REG_OFFSET(a1), 0, SLPM66127X, FSLPM66127, std::vector<const char *>{"SLPM-66344", "SLPM-66347", "SLPM-66348"}}},
    // 遙かなる時空の中で3 十六夜記 Harukanaru Toki no Naka de 3 - Izayoiki
    {0x25882C, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(t7), 0, 0, FSLPM66127, "SLPM-66127"}},
    {0x258790, {0, PCSX2_REG_OFFSET(a1), 0, SLPM66127X, FSLPM66127, "SLPM-66127"}},
    // 遙かなる時空の中で4
    {0x1B043C, {USING_CHAR | DATA_INDIRECT, PCSX2_REG_OFFSET(s1), 0, 0, FSLPM66127, "SLPM-66952"}},
    {0x1B0360, {0, PCSX2_REG_OFFSET(a1), 0, SLPM66127X, FSLPM66127, "SLPM-66952"}},
    // Angel's Feather
    {0x31B880, {DIRECT_READ, 0, 0, SLPS20394<0x31B480, 0x31B880, 0x31BC80, 0x31C080>, 0, std::vector<const char *>{"SLPM-65512", "SLPM-65513"}}},
    // 空色の風琴 ～Remix～
    {0x1A9238, {DIRECT_READ, 0, 0, 0, SLPS25395, "SLPM-65848"}},
    {0x10c324, {FULL_STRING, PCSX2_REG_OFFSET(a0), 0, 0, SLPS25395, "SLPM-65848"}},
};

extern void pcsx2_load_functions(std::unordered_map<DWORD, emfuncinfo> &m)
{
    for (auto i = 0; i < ARRAYSIZE(emfunctionhooks_1); i++)
    {
        m.emplace(emfunctionhooks_1[i].addr, emfunctionhooks_1[i].info);
    }
}