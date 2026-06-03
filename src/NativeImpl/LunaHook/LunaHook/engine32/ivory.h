

class ivory : public ENGINE
{
public:
    ivory()
    {

        is_engine_certain = false;
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"BG/*.sg", L"CHR/*.sg", L"MAP/*.sg", L"PARTS/*.sg", L"MUSIC/*.px", L"SE/*.px"};
    };
    bool attach_function();
};
