

class TAKUYO : public ENGINE
{
public:
    TAKUYO()
    {
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{
            L"voicedata*.arc",
            L"voicedata*.bin",
            L"sedata.arc",
            L"sedata.bin",
            L"BGMDATA.ARC",
            L"BGMDATA.BIN",
            L"bmpdata.arc",
            L"bmpdata.bin",
            L"sysdata.arc",
            L"sysdata.bin",
            L"scrdata.arc",
            L"scrdata.bin",
        };
    };
    bool attach_function();
};
