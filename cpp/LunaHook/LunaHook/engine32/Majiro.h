

class Majiro : public ENGINE
{
public:
    Majiro()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"data*.arc", L"stream*.arc"};
    };
    bool attach_function();
};
