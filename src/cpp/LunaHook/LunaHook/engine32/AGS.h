

class AGS : public ENGINE
{
public:
    AGS()
    {

        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"voice/*.pk", L"sound/*.pk", L"misc/*.pk"};
        is_engine_certain = false;
    };
    bool attach_function();
};