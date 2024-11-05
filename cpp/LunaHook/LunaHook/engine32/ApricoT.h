

class ApricoT : public ENGINE
{
public:
    ApricoT()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"arc.a*";
    };
    bool attach_function();
};

class ApricoTlast : public ApricoT
{
public:
    ApricoTlast()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"arc.dat";
        is_engine_certain = false;
    };
};