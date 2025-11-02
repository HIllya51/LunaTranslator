

class RUNE : public ENGINE
{
public:
    RUNE()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"vorbis.acm", L"*d*.g*"};
        is_engine_certain = false;
    };
    bool attach_function();
};
