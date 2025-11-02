

class Godot : public ENGINE
{
public:
    Godot()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFile(L"*.pck") || Util::SearchResourceString(L"Godot Engine");
        };
    };
    bool attach_function();
};
