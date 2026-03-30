

class Atelier : public ENGINE
{
public:
    Atelier()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"message.dat";
    };
    bool attach_function();
};

class Atelier2 : public ENGINE
{
public:
    Atelier2()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFileAll({L"*.ARC", L"*.ARI"}) ||
                   Util::CheckFileAll({L"ARC\\*.ARC", L"ARC\\*.ARI"});
        };
    };
    bool attach_function();
};