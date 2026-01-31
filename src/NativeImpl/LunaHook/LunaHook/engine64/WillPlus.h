

class WillPlus : public ENGINE
{
public:
    WillPlus()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"Rio.arc", L"Chip*.arc"};
    };
    bool attach_function();
};
