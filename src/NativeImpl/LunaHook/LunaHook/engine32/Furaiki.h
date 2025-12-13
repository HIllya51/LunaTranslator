
// 風雨来記3

class Furaiki : public ENGINE
{
public:
    Furaiki()
    {
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"bin/Grp_*.dat", L"bin/Snd_*.dat", L"ap/*.dat"};
    };
    bool attach_function();
};