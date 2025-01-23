

class Rejet : public ENGINE
{
public:
    Rejet()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"gd.dat", L"pf.dat", L"sd.dat"};
    };
    bool attach_function();
};