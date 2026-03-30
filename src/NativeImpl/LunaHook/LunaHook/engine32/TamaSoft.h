

class TamaSoft : public ENGINE
{
public:
    TamaSoft()
    {
        // LOST CHILD
        // https://vndb.org/v1183
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFileAll({L"data.epk", L"data.e01"}) && Util::SearchResourceString(L"Programmed by sgt (based by mic-o24)");
        };
    };
    bool attach_function();
};