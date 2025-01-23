

class Diskdream : public ENGINE
{
public:
    Diskdream()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"system.har", L"Graphic.har", L"wave*.har"};
    };
    bool attach_function();
};