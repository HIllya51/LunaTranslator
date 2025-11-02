

class Malie : public ENGINE
{
public:
    Malie()
    {

        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"Malie.ini", L"Malie.exe"};
    };
    bool attach_function();
};