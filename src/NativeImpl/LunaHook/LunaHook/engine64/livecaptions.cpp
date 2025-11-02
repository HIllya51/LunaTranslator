#include "livecaptions.h"

bool livecaptions::attach_function()
{
    auto srdll = GetModuleHandle(L"Microsoft.CognitiveServices.Speech.extension.embedded.sr.dll");
    if (!srdll)
        return false;
    auto [s, e] = Util::QueryModuleLimits(srdll);
    bool succ = false;
    // std::_Char_traits<char,int>::copy(void *, const void *, size_t)
    // std::_Char_traits<char,int>::move(void *, const void *, size_t)
    BYTE sig[] = {
        0x40, 0x53,             // push    rbx
        0x48, 0x83, 0xec, 0x20, // sub    rsp,0x20
        0x48, 0x8b, 0xd9,       // mov    rbx,rcx
        0xe8, XX4,              // call    memmove_0 ，新版本改成call    memcpy_0了
        0x48, 0x8b, 0xc3,       // mov    rax,rbx
        0x48, 0x83, 0xc4, 0x20, // add    rsp,0x20
        0x5b,                   // pop    rbx
        0xc3                    // ret
    };
    for (auto addr : Util::SearchMemory(sig, sizeof(sig), PAGE_EXECUTE, s, e))
    {
        auto target = addr + 2 + 4 + 3 + 5 + *(int *)(addr + 2 + 4 + 3 + 1);
        if (*(WORD *)target != 0x25ff)
            continue;
        HookParam hp;
        hp.address = addr;
        hp.type = USING_STRING | CODEC_UTF8 | FULL_STRING;
        hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
        {
            auto ptr = context->rdx;
            auto size = context->r8;
            buffer->from(ptr, size);
        };
        succ |= NewHook(hp, "LiveCaptions");
    }
    return succ;
}