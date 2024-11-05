

class Sprite : public ENGINE
{
public:
    Sprite()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE;
        check_by_target = L"*.cct";
    };
    bool attach_function();
};
class TextXtra_x32 : public ENGINE
{

public:
    TextXtra_x32()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return GetModuleHandle(L"TextXtra.x32");
        };
    };
    bool attach_function();
};