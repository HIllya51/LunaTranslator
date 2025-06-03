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
    void FSLPM55195(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("%n\x81\x40"));
        StringFilter(buffer, TEXTANDLEN("%n"));
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
}
struct emfuncinfoX
{
    DWORD addr;
    emfuncinfo info;
};
static const emfuncinfoX emfunctionhooks_1[] = {
    // 夏夢夜話
    {0x7689BC, {DIRECT_READ, 0, 0, 0, SLPS25276, "SLPS-25276"}},
    // マイネリーベ 優美なる記憶
    {0x19BF230, {DIRECT_READ, 0, 0, 0, SLPM65684, "SLPM-65684"}},
    // マイネリーベⅡ ～誇りと正義と愛～
    {0x1FFD0DC, {DIRECT_READ, 0, 0, 0, SLPM66247, "SLPM-66247"}},
    // セパレイトハーツ (Separate Hearts)
    {0x1F63320, {DIRECT_READ, 0, 0, 0, SLPM66298, "SLPM-66298"}},
    // アカイイト
    {0x136800, {0, PCSX2_REG_OFFSET(t0), 0, 0, FSLPM66136, "SLPM-65732"}},
    // Nana
    {0x15036C, {0, PCSX2_REG_OFFSET(a3), 0, 0, FSLPM65914, "SLPM-65914"}},
    // My Merry May with be
    {0x1DB7DC, {0, PCSX2_REG_OFFSET(a3), 0, 0, FSLPM66045, "SLPM-66045"}},
    // CLANNAD - ゲオオンラインストア
    {0x1DB7DC, {0, PCSX2_REG_OFFSET(s4), 0, 0, FSLPM66302, "SLPM-66302"}},
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
    // 風雨来記
    {0x1FFACA0, {DIRECT_READ, 0, 0, 0, SLPM66458, "SLPM-66458"}},
    // うたわれるもの 散りゆく者への子守唄
    {0x50574C, {DIRECT_READ, 0, 0, 0, SLPS25679, "SLPS-25679"}},
    // Only you リベルクルス ドラマCD付き
    {0x461F38, {DIRECT_READ, 0, 0, SLPS25150, 0, "SLPS-25150"}},
    // D.C. ～ダ・カーポ～ the Origin
    {0x517688, {DIRECT_READ, 0, 0, 0, SLPM66905, "SLPM-66905"}},
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