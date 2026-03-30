

class AbogadoPowers : public ENGINE
{
public:
    AbogadoPowers()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFileAll({L"*.dsk", L"*.pal", L"*.pft", L"*.fnt"}) &&
                   Util::SearchResourceString(L"AbogadoPowers / Scarecrow");
        };
    };
    bool attach_function();
};