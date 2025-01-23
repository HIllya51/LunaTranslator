

class godot : public ENGINE
{
public:
    godot()
    {

        check_by = CHECK_BY::RESOURCE_STR;
        check_by_target = L"Godot Engine";
    };
    bool attach_function();
};