
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
            auto _ = {L"font.dat", L"graph.dat", L"sound.dat", L"music.dat", L"text.dat"};
            auto checkfile = std::all_of(_.begin(), _.end(), Util::CheckFile);
            return checkfile && Util::SearchResourceString(L"PiAS");
        };
    };
    bool attach_function();
};