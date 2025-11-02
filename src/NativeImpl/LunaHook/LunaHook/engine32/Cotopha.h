

class Cotopha : public ENGINE
{
public:
    Cotopha()
    {

        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"*.noa", L"data\\*.noa"};
    };
    bool attach_function();
};