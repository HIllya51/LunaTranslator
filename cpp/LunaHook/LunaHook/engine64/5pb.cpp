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
        hp.offset = get_stack(2);
        hp.split = get_stack(1);
        hp.length_offset = 3;
        hp.filter_fun = [](void *data, size_t *len, HookParam *hp)
        {
            auto s = std::string((char *)data, *len);
            strReplace(s, "%N", "\n");
            // sub_140096E80
            //%I %B %C %R( %Z %%
            return write_string_overwrite(data, len, s);
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