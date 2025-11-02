

class AbogadoPowers : public ENGINE
{
public:
    AbogadoPowers()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto _ = {L"*.dsk", L"*.pal", L"*.pft", L"*.fnt"};
            auto checkfile = std::all_of(_.begin(), _.end(), Util::CheckFile);
            return checkfile && Util::SearchResourceString(L"AbogadoPowers / Scarecrow");
        };
    };
    bool attach_function();
};