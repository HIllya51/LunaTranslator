

class GASTRO : public ENGINE
{
public:
    GASTRO()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"BMPDATA.ARC", L"MIDDATA.ARC", L"SCRDATA.ARC", L"SYSDATA.ARC"};
        is_engine_certain = false;
    };
    bool attach_function();
};