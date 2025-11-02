#include "rpcs3_1.h"

struct emfuncinfoX
{
    DWORD addr;
    emfuncinfo info;
};
namespace
{

    void FBLJM61131(TextBuffer *buffer, HookParam *hp)
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
}

static const emfuncinfoX emfunctionhooks_1[] = {
    // ‘＆’ - 空の向こうで咲きますように -
    {0x46328, {CODEC_UTF8, 1, 0, 0, FBLJM61131, "BLJM61131"}},
    // Dunamis15
    {0x42c90, {CODEC_UTF8, 1, 0, 0, FBLJM61131, "BLJM60347"}},

};

void rpcs3_load_functions(std::unordered_map<DWORD, emfuncinfo> &m)
{
    for (auto i = 0; i < ARRAYSIZE(emfunctionhooks_1); i++)
    {
        m.emplace(emfunctionhooks_1[i].addr, emfunctionhooks_1[i].info);
    }
}