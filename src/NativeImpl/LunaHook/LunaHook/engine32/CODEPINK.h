

class CODEPINK : public ENGINE
{
public:
    CODEPINK()
    {
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"CG/*.gpc", L"DATA/*.gpc", L"SCENARIO/*.gpc"};
        is_engine_certain = false;
    };
    bool attach_function();
};