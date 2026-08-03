

class RibbonMagic : public ENGINE
{
public:
    RibbonMagic()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"setup", L"voice", L"se", L"scenario", L"cg", L"cg.dat", L"bgm", L"system"};
    };
    bool attach_function();
};