

class Broccoli : public ENGINE
{
public:
    Broccoli()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"voice*.pak", L"voice.pak", L"data.pak", L"data*.pak"};
    }
    bool attach_function();
};
