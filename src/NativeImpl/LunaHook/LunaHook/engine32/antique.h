

class antique : public ENGINE
{
public:
    antique()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"*.VMC", L"vorbis.acm", L"SE.DAT", L"PACK.DAT"};
        is_engine_certain = false;
    };
    bool attach_function();
};