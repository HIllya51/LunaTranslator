

class Troy : public ENGINE
{
public:
    Troy()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"*.mma", L"sfe.dll"};
        is_engine_certain = false;
    };
    bool attach_function();
};