

class AGES7 : public ENGINE
{
public:
    AGES7()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"obb\\pack.bin", L"erc_nospfx.dll"};
    };
    bool attach_function();
};