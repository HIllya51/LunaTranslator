

class For : public ENGINE
{
public:
    For()
    {
        // とらぶるウィッチーズ！！
        // https://vndb.org/v14659
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"se", L"info", L"Grphic", L"Data0*", L"mid/M*.MID"};
        is_engine_certain = false;
    };
    bool attach_function();
};