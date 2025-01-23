

class AIL : public ENGINE
{
public:
    AIL()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto _ = {L"*.wa", L"Gall*.da", L"Pall*.da", L"vall*.da", L"sall.sn", L"help/*.ht"};
            auto old = std::all_of(_.begin(), _.end(), Util::CheckFile);
            auto _2 = Util::CheckFile(L"Gall*.dat");
            return old | _2;
        };
    };
    bool attach_function();
};