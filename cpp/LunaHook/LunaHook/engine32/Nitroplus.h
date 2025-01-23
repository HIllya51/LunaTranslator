

class Nitroplus : public ENGINE
{
public:
    Nitroplus()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.npa";
    };
    bool attach_function();
};

class Nitroplusplus : public ENGINE
{
public:
    Nitroplusplus()
    {
        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = false;
        check_by_target = []()
        {
            return Util::SearchResourceString(L"Nitro+") && Util::CheckFile(L"system.dll");
        };
    };
    bool attach_function();
};