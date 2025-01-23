

class Erogos : public ENGINE
{
public:
    Erogos()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"ags.exe", L"bg.dat", L"bgm.dat", L"mov.dat", L"script.dat", L"voice.dat"};
        is_engine_certain = false;
    };
    bool attach_function();
};