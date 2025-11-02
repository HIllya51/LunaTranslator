

class AniSeed : public ENGINE
{
public:
    AniSeed()
    {
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"bg/*.sg", L"chr/*.sg", L"event/*.sg", L"music/*.px", L"oneshot/*.px", L"script/*.kaf", L"system/*.sg"};
    };
    bool attach_function();
};