

class Xbangbang : public ENGINE
{
public:
    Xbangbang()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"fastdata.arc";
        is_engine_certain = false;
    };
    bool attach_function();
};