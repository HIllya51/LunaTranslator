

class Retouch : public ENGINE
{
public:
    Retouch()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"resident.dll";
    };
    bool attach_function();
};