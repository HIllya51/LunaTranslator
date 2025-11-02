

class Live : public ENGINE
{
public:
    Live()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"live.dll";
    };
    bool attach_function();
};