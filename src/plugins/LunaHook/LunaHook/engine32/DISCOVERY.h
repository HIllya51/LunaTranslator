

class DISCOVERY : public ENGINE
{
public:
    DISCOVERY()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"BG.PD", L"CG.PD", L"CHIP.PD", L"SE.PB", L"STAND.PD", L"VOICE.PB", L"*.ID"};
        is_engine_certain = false;
    };
    bool attach_function();
};