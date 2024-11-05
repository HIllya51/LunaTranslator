

class Ryujinx : public ENGINE
{
public:
    Ryujinx()
    {

        check_by = CHECK_BY::FILE;
        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return wcscmp(processName_lower, L"ryujinx.exe") == 0;
        };
    };
    bool attach_function();
};
