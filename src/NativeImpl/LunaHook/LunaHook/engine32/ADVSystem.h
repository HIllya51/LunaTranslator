

class ADVSystem : public ENGINE
{
public:
    ADVSystem()
    {
        enginename = "ADV System";
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFileAll({L"*.PK", L"*.PK0", L"*.PKA", L"*.PKB", L"*.PKC"}) &&
                   Util::SearchResourceString(L"U-Me SOFT") &&
                   Util::SearchResourceString(L"ADV System 1.75.romance");
        };
    };
    bool attach_function();
};