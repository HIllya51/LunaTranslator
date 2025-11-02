

class Broccoli : public ENGINE
{
public:
    Broccoli()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto _ = {L"voice*.pak", L"voice.pak", L"data.pak", L"data*.pak"};
            return std::all_of(_.begin(), _.end(), Util::CheckFile);
        };
    }
    bool attach_function();
};
