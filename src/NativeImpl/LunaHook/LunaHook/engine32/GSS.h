#ifndef __LUNA_ENGINE_GSS_H_
#define __LUNA_ENGINE_GSS_H_

class GSS : public ENGINE
{
public:
    GSS()
    {
        // 雪語り [リニューアル版 おまけディスク]
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{
            L"Gss.exe",
            L"scrdata.arc",
            L"scrdata.bin",
            L"OMDATA.arc",
            L"OMBGM.arc",
        };
        is_engine_certain = false;
    };
    bool attach_function();
};

#endif
