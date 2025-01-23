

class sakusesu : public ENGINE
{
public:
    sakusesu()
    {
        // サクセス

        check_by = CHECK_BY::FILE;
        check_by_target = L"SCRIPT/*.AFS";
        is_engine_certain = false;
    };
    bool attach_function();
};