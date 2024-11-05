

class PPSSPPengine : public ENGINE
{
public:
    PPSSPPengine()
    {

        check_by = CHECK_BY::FILE;
        is_engine_certain = false;
        check_by_target = L"PPSSPP*.exe";
    };
    bool attach_function();
};
