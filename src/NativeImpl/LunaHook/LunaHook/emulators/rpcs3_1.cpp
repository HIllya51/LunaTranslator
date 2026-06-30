#include "rpcs3_1.h"

struct emfuncinfoX
{
    DWORD addr;
    emfuncinfo info;
};
namespace
{
    void BLJM61018(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        auto s = buffer->strA();
        if (all_ascii(s))
            return buffer->clear();
        if (endWith(last, s))
            return buffer->clear();
        last = s;
        s = re::sub(s, R"(\\n(\x81\x40)*)");
        buffer->from(s);
    }
    void BLJM60322(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        auto s = buffer->strA();
        if (all_ascii(s))
            return buffer->clear();
        if (s.size() <= 2)
            return buffer->clear();
        if (endWith(last, s))
            return buffer->clear();
        last = s;
    }
    void BLJM60444(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        auto s = buffer->strA();
        if (s == last)
            return buffer->clear();
        last = s;
        s = re::sub(s, R"(\n+)");
        s = re::sub(s, R"(\r+)");
        buffer->from(s);
    }
    void BLJM61131(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        auto s = buffer->strA();
        if (s == last)
            return buffer->clear();
        last = s;
        s = re::sub(s, R"(\[[^\]]+.)");
        s = re::sub(s, R"(\\k|\\x|%C|%B)");
        s = re::sub(s, R"(\%\d+\#[0-9a-fA-F]*\;)");
        s = re::sub(s, R"(\n+)");
        buffer->from(s);
    }
    void BLJM61067(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, '\x01');
        CharFilter(buffer, '\x02');
        CharFilter(buffer, '\x03');
        CharFilter(buffer, '\x04');
        CharFilter(buffer, '\x05');
        CharFilter(buffer, '\x06');
        CharFilter(buffer, '\x07');
        CharFilter(buffer, '\x08');
        CharFilter(buffer, '\x09');
    }
    void BLJS10133(TextBuffer *buffer, HookParam *hp)
    {
        auto sx = buffer->strA();
        if (sx.size() <= 4)
            return buffer->clear();
        auto s = (char *)RPCS3::emu_addr(hp->emu_addr);
        std::string ss;
        while (*s)
        {
            std::string _s = s;
            if (!isStringUtf8(_s))
                break;
            ss += _s + "\n";
            s += _s.size() + 1;
            if (startWith(sx, u8"「") && endWith(_s, u8"」"))
                break;
            if (startWith(sx, u8"（") && endWith(_s, u8"）"))
                break;
        }
        buffer->from(ss);
    }
    void BLJM61120(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        auto s = buffer->strA();
        if (endWith(last, s))
            return buffer->clear();
        last = s;
        NewLineCharFilterA(buffer, hp);
    }
}

static const emfuncinfoX emfunctionhooks_1[] = {
    // Rozen Maiden -Wechseln sie welt ab-
    {0xe08d90, {FULL_STRING, 0, 0, 0, BLJM61120, "BLJM61120"}},
    // 第２次スーパーロボット大戦ＯＧ
    {0x300d0ee0, {DIRECT_READ | CODEC_UTF8, 0, 0, 0, BLJS10133, "BLJS10133"}},
    // 俺たちに翼はない
    {0x185EC8, {FULL_STRING, 1, 0, 0, BLJM61018, "BLJM61018"}},
    // L@ve once -mermaid's tears-
    {0x19CF60, {FULL_STRING, 1, 0, 0, BLJM60322, "BLJM60322"}},
    // DISORDER6
    {0x1bc188, {FULL_STRING, 2, 0, 0, BLJM61067, "BLJM61067"}},
    // Dunamis15
    {0x42c90, {CODEC_UTF8 | FULL_STRING, 1, 0, 0, BLJM61131, "BLJM60347"}},
    // たっち、しよっ！ ～Love Application～
    {0x2F2DCC, {FULL_STRING, 1, 0, 0, BLJM60444, "BLJM60444"}},
    // ‘＆’ - 空の向こうで咲きますように -
    {0x46328, {CODEC_UTF8 | FULL_STRING, 1, 0, 0, BLJM61131, "BLJM61131"}},
    // 解放少女 SIN
    {0x3300C2480, {DIRECT_READ, 0, 0, 0, BLJM61067, "BLJM61118"}},

};

void rpcs3_load_functions(std::unordered_map<DWORD, emfuncinfo> &m)
{
    for (auto i = 0; i < ARRAYSIZE(emfunctionhooks_1); i++)
    {
        m.emplace(emfunctionhooks_1[i].addr, emfunctionhooks_1[i].info);
    }
}