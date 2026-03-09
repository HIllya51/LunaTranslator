

class Rejet : public ENGINE
{
public:
    Rejet()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = [&]()
        {
            auto _ = {L"gd.dat", L"pf.dat", L"sd.dat"};
            auto checkfile = std::all_of(_.begin(), _.end(), Util::CheckFile);
            if (checkfile)
                return true;
            tokyo = Util::SearchResourceString(L"Rejet株式会社");
            return tokyo;
        };
    };
    bool attach_function();
    // https://vndb.org/v7675
    // TOKYOヤマノテBOYS DARK CHERRY DISC
    bool tokyo = false;
};