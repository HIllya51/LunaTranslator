#include "EntisGLS.h"
namespace
{
    bool h2()
    {
        // 神学校 DL
        const uint8_t bytes1[] = {
            0x55,
            0x8b, 0xec,
            0x83, 0xec, 0x0c,
            0x8b, 0xc8,
            0x0f, 0xb7, 0x00,
            0x57,
            0x8b, 0x7d, 0x0c,
            0x89, 0x55, 0xfc,
            0x66, 0x85, 0xc0,
            0x74, XX,
            0xeb, 0x07,
            0x8d, 0xa4, 0x24, 0x00, 0x00, 0x00, 0x00,
            0x83, 0xc1, 0x02,
            0x89, 0x4d, 0xf4,
            0x66, 0x83, 0xf8, 0x0d};
        auto addr = MemDbg::findBytes(bytes1, sizeof(bytes1), processStartAddress, processStopAddress);

        if (!addr)
            return false;
        HookParam hp;
        hp.address = addr;
        hp.offset = regoffset(eax);
        hp.type = USING_STRING | CODEC_UTF16;
        return NewHook(hp, "EntisGLS");
    }
    bool h1()
    {

        // それは舞い散る桜のように-完全版-
        // int __thiscall sub_4BB5D0(_BYTE *this, LPCWCH lpWideCharStr)
        const uint8_t bytes1[] = {
            0x66, 0x83, 0xF9, 0x41,
            0x72, 0x06,
            0x66, 0x83, 0xF9, 0x5a,
            0x76, 0x0C,
            0x66, 0x83, 0xF9, 0x61,
            0x72, 0x12,
            0x66, 0x83, 0xF9, 0x7a,
            0x77, 0x0c

        };
        auto addr = MemDbg::findBytes(bytes1, sizeof(bytes1), processStartAddress, processStopAddress);

        if (!addr)
            return false;
        addr = MemDbg::findEnclosingAlignedFunction(addr);
        if (!addr)
            return false;
        HookParam hp;
        hp.address = addr;
        hp.offset = stackoffset(1);
        hp.embed_hook_font = F_GetGlyphOutlineW;
        hp.type = USING_STRING | CODEC_UTF16 | EMBED_ABLE | EMBED_AFTER_NEW;

        return NewHook(hp, "EntisGLS");
    }

}
bool EntisGLS::attach_function()
{
    return h1() || h2();
}