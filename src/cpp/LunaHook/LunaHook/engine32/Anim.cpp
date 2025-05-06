#include "Anim.h"

bool InsertAnimHook()
{
    const BYTE bytes[] = {0xC7, 0x45, 0xFC, 0x01, 0x00, 0x00, 0x00, 0x8B, 0x4D, 0x10, 0x51, 0x8D, 0x8D, 0x40, 0x7E, 0xFF, 0xFF};
    ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
    if (!addr)
    {
        ConsoleOutput("Anim: pattern not found");
        return false;
    }
    HookParam myhp;
    myhp.address = addr + 10;

    myhp.type = USING_STRING | NO_CONTEXT | EMBED_ABLE | EMBED_AFTER_OVERWRITE | EMBED_DYNA_SJIS; // /HQ 不使用上下文区分 把所有线程的文本都提取
    myhp.embed_hook_font = F_GetGlyphOutlineA;
    // data_offset
    myhp.offset = regoffset(ecx);
    char nameForUser[HOOK_NAME_SIZE] = "Anim";

    return NewHook(myhp, nameForUser);
}

bool InsertAnim2Hook()
{
    const BYTE bytes[] = {0xC7, 0x45, 0xFC, 0x01, 0x00, 0x00, 0x00, 0x8B, 0x45, 0x10, 0x50, 0x8D, 0x8D, 0xAC, 0x7E, 0xFF, 0xFF};
    ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
    if (!addr)
    {
        ConsoleOutput("Anim2: pattern not found");
        return false;
    }
    HookParam myhp;
    myhp.address = addr + 10;
    myhp.embed_hook_font = F_GetGlyphOutlineA;
    // メスつまみ３
    // そんな俺に声をかけてきたのは、近所のスーパーで働いている主婦の、@n『@[赤羽:あかばね]@[千晶:ちあき]』さんだ。
    myhp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
        std::string result = buffer->strA();
        result = re::sub(result, "@\\[(.*?):(.*?)\\]", "$1");
        buffer->from(result);
    };
    myhp.lineSeparator = L"@n";
    myhp.type = USING_STRING | NO_CONTEXT | EMBED_ABLE | EMBED_AFTER_OVERWRITE | EMBED_DYNA_SJIS;
    // 僕がいない間に変貌えられた妻の秘肉 ～ラブラブ新婚妻は他の男に抱かれ淫らに喘ぐ夢を見るか～ 体験版

    // data_offset
    myhp.offset = regoffset(eax);

    return NewHook(myhp, "Anim2");
}
namespace
{
    void Anim3Filter(TextBuffer *buffer, HookParam *)
    {
        StringFilterBetween(buffer, TEXTANDLEN("\x81\x40"), TEXTANDLEN("@m")); // @r(2,はと)
        StringFilterBetween(buffer, TEXTANDLEN("\x81\x40"), TEXTANDLEN("@n")); // @r(2,はと)
        StringCharReplacer(buffer, TEXTANDLEN("@b"), ' ');
        StringCharReplacer(buffer, TEXTANDLEN("\x81\x42"), '.');
        StringCharReplacer(buffer, TEXTANDLEN("\x81\x48"), '?');
        StringCharReplacer(buffer, TEXTANDLEN("\x81\x49"), '!');
    }

    bool InsertAnim3Hook()
    {
        /*
         * Sample games:
         * https://vndb.org/v17427
         * https://vndb.org/v18837
         */
        const BYTE bytes[] = {
            0xCC,            // int 3
            0x55,            // push ebp      << hook here
            0x8B, 0xEC,      // mov ebp,esp
            0x81, 0xEC, XX4, // sub esp,00000830
            0xA1, XX4,       // mov eax,[musu_mama.exe+A91F0]
            0x33, 0xC5,      // xor eax,ebp
            0x89, 0x45, 0xE8 // mov [ebp-18],eax
        };
        ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
        ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
        if (!addr)
        {
            ConsoleOutput("Anim3: pattern not found");
            return false;
        }

        HookParam hp;
        hp.address = addr + 1;
        hp.offset = regoffset(edx);
        hp.type = USING_STRING;
        hp.filter_fun = Anim3Filter;
        ConsoleOutput("INSERT Anim3");

        return NewHook(hp, "Anim3");
    }
}
bool Anim::attach_function()
{
    PcHooks::hookGDIFunctions(GetGlyphOutlineA);
    auto b1 = InsertAnimHook() || InsertAnim2Hook();
    b1 = InsertAnim3Hook() || b1;
    return b1;
}