

class Sprite : public ENGINE
{
    HMODULE TextXtra;

public:
    Sprite()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = [&]()
        {
            return (TextXtra = GetModuleHandle(L"TextXtra.x32")) || Util::CheckFile(L"*.cct");
        };
    };
    bool attach_function();
};