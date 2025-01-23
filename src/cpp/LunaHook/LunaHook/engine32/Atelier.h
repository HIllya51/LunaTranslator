

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
            return (Util::CheckFile(L"*.ARC") && Util::CheckFile(L"*.ARI")) ||
                   (Util::CheckFile(L"ARC\\*.ARC") && Util::CheckFile(L"ARC\\*.ARI"));
        };
    };
    bool attach_function();
};