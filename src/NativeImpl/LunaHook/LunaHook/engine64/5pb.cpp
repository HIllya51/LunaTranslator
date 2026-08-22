#include "5pb.h"
#include "mages/mages.h"
namespace
{
    // https://vndb.org/v46553
    // 新宿葬命
    bool _strncat()
    {
        HookParam hp;
        hp.address = (uintptr_t)GetProcAddress(GetModuleHandleA("ucrtbase.dll"), "strncat");
        hp.type = USING_STRING | CODEC_UTF8 | NO_CONTEXT | USING_SPLIT;
        hp.offset = stackoffset(2);
        hp.split = stackoffset(1);
        hp.length_offset = 3;
        hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
        {
            auto s = buffer->strA();
            strReplace(s, "%N", "\n");
            // sub_140096E80
            //%I %B %C %R( %Z %%
            buffer->from(s);
        };
        return NewHook(hp, "strncat");
    }
}
bool _5pb::attach_function()
{
    // CHAOS;HEAD_NOAH
    bool b3 = hookmages::MAGES();
    return b3 || _strncat();
}
bool _5pb_2::attach_function()
{
    // STEINS;GATE RE:BOOT
    // https://vndb.org/r128730
    /*
.text:000000014003E0FD 48 8D 15 28 08 58 00                          lea     rdx, aRender    ; "render"
.text:000000014003E104 48 8B 4D 27                                   mov     rcx, [rbp+57h+var_30]
.text:000000014003E108 E8 C3 60 1E 00                                call    sub_1402241D0
.text:000000014003E10D BA 08 00 00 00                                mov     edx, 8
.text:000000014003E112 48 8B 4D 27                                   mov     rcx, [rbp+57h+var_30]
.text:000000014003E116 E8 95 5B 1E 00                                call    sub_140223CB0
.text:000000014003E11B 48 8D 0D DE 0D 00 00                          lea     rcx, sub_14003EF00
    */
    char aRender[] = "render";
    auto addr = MemDbg::findBytes(aRender, sizeof(aRender), processStartAddress, processStopAddress);
    if (!addr)
        return false;
    addr = MemDbg::find_leaorpush_addr(addr, processStartAddress, processStopAddress);
    if (!addr)
        return false;
    BYTE check[] = {0x48, 0x8d, 0x15, XX4,
                    0x48, 0x8b, XX, XX,
                    0xe8, XX4,
                    0xba, 0x08, 0x00, 0x00, 0x00,
                    0x48, 0x8b, XX, XX,
                    0xe8, XX4,
                    0x48, 0x8d, 0x0d, XX4};
    if (!MatchPattern(addr, check, sizeof(check)))
        return false;
    addr = addr + sizeof(check) - 7;
    addr = addr + 7 + *(int *)(addr + 3);
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | CODEC_UTF8 | FULL_STRING | USING_SPLIT;
    hp.offset = regoffset(rdx);
    hp.split = regoffset(r9);
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(\[.*?\])");          // 注音
        s = re::sub(s, R"(#[a-fA-F0-9]{6};)"); // 颜色
        s = re::sub(s, R"(%r)");
        s = re::sub(s, R"(%C)");
        s = re::sub(s, R"(%p(.*?);)");
        s = re::sub(s, u8R"((　)*\\n(　)*)");
        s = re::sub(s, u8R"(\n\n+)", "\n");
        buffer->from(s);
    };
    return NewHook(hp, "render");
}