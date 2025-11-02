

class ONScripterru : public ENGINE
{
public:
    ONScripterru()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        { return Util::SearchResourceString(L"ONScripter-RU") || Util::SearchResourceString(L"onscripter-ru.exe"); };
    };
    bool attach_function();
};