

class OVERDRIVE : public ENGINE
{
public:
    OVERDRIVE()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"DATA\\bgm.vfa", L"DATA\\grp.vfa", L"DATA\\SCR.arc", L"DATA\\snd.vfa"};
    };
    bool attach_function();
};