

class T2U : public ENGINE
{
public:
    T2U()
    {
        //(18禁ゲーム)[000128][BLUE GALE] Treating2U (bin+cue)
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto _ = {L"*.zbm", L"scene00.bdt", L"*.dat", L"*.Snn"};
            return std::all_of(_.begin(), _.end(), Util::CheckFile);
        };
    };
    bool attach_function();
};