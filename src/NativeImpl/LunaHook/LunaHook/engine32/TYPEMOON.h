

class TYPEMOON : public ENGINE
{
public:
    TYPEMOON()
    {
        // https://vndb.org/v165
        check_by = CHECK_BY::FILE_ALL;
        is_engine_certain = false;
        check_by_target = check_by_list{L"data0*.p", L"0*.p"};
    };
    bool attach_function();
};
