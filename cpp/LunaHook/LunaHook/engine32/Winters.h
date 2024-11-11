

class Winters : public ENGINE
{
public:
    Winters()
    {
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"MSG.dat", L"SCR.ifx", L"VFN.dat", L"GRP.ifx"};
    };
    bool attach_function();
};