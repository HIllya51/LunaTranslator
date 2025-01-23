

class Leaf : public ENGINE
{
public:
    Leaf()
    {

        check_by = CHECK_BY::FILE_ANY;
        // check_by_target=L"*.pak";
        check_by_target = check_by_list{L"*.pak", L"Data\\*.pck"};
        is_engine_certain = false;
    };
    bool attach_function();
};