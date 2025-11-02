

class NUGSystem : public ENGINE
{
public:
    NUGSystem()
    {
        // https://vndb.org/v1053
        // そらうた
        enginename = "NUG System";
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto _ = {L"bgm.dat", L"data.dat", L"image.dat", L"se.dat", L"story.dat", L"system.dat", L"voice.dat"};
            return std::all_of(_.begin(), _.end(), Util::CheckFile) && Util::SearchResourceString(L"NUG System");
        };
    };
    bool attach_function();
};