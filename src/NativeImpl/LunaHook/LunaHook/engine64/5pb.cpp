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