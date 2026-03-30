
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
            return Util::CheckFileAll({L"font.dat", L"graph.dat", L"sound.dat", L"music.dat", L"text.dat"}) &&
                   Util::SearchResourceString(L"PiAS");
        };
    };
    bool attach_function();
};