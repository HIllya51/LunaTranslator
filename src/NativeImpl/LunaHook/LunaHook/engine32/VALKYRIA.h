

class VALKYRIA : public ENGINE
{
public:
    VALKYRIA()
    {

        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = true;
        check_by_target = []()
        {
            return Util::SearchResourceString(L"Copyright(C)VALKYRIA") && Util::CheckFile(L"data0*-00.dat");
        };
    }
    bool attach_function();
};