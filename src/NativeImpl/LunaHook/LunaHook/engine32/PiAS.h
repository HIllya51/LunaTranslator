
// https://vndb.org/v10757
// 堕ちた天使が詩う歌

class PiAS : public ENGINE
{
public:
    PiAS()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = [&]()
        {
            if (Util::CheckFileAll({L"font.dat", L"graph.dat", L"sound.dat", L"music.dat", L"text.dat"}) &&
                Util::SearchResourceString(L"PiAS"))
                return true;
            is_engine_certain = false;
            return Util::CheckFileAll({L"FONT0.dat", L"graph.dat", L"sound.dat", L"text.dat"});
        };
    };
    bool attach_function();
};