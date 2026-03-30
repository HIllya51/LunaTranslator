

class T2U : public ENGINE
{
public:
    T2U()
    {
        //(18禁ゲーム)[000128][BLUE GALE] Treating2U (bin+cue)
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"*.zbm", L"scene00.bdt", L"*.dat", L"*.Snn"};
    };
    bool attach_function();
};