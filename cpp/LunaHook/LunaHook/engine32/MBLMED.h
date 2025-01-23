

class MBLMED : public ENGINE
{
public:
    MBLMED()
    {

        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"*.mbl", L"*.med"};
    };
    bool attach_function();
};