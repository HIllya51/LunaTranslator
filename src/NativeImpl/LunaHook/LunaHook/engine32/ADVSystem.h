

class ADVSystem : public ENGINE
{
public:
    ADVSystem()
    {
        enginename = "ADV System";
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto _ = {L"*.PK", L"*.PK0", L"*.PKA", L"*.PKB", L"*.PKC"};
            auto checkfile = std::all_of(_.begin(), _.end(), Util::CheckFile);
            return checkfile && Util::SearchResourceString(L"U-Me SOFT") && Util::SearchResourceString(L"ADV System 1.75.romance");
        };
    };
    bool attach_function();
};