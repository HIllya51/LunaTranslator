

class Rejet : public ENGINE
{
public:
    Rejet()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = [&]()
        {
            if (Util::CheckFileAll({L"gd.dat", L"pf.dat", L"sd.dat"}))
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