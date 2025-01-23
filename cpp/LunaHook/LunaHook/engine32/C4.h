

class C4 : public ENGINE
{
public:
    C4()
    {

        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"C4.EXE", L"XEX.EXE"};
    };
    bool attach_function();
};