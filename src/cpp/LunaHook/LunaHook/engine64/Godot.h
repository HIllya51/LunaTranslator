

class Godot : public ENGINE
{
public:
    Godot()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.pck";
    };
    bool attach_function();
};
