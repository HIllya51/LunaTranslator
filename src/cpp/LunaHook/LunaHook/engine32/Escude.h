

class Escude : public ENGINE
{
public:
    Escude()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"configure.cfg", L"gfx.bin"};
    }
    bool attach_function();
};