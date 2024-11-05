

class Wolf : public ENGINE
{
public:
    Wolf()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"data.wolf", L"data\\*.wolf", L"data\\basicdata\\cdatabase.dat"};
    };
    bool attach_function();
};