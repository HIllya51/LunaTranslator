

class Majiro : public ENGINE
{
public:
    Majiro()
    {
        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = false;
        check_by_target = []()
        {
            return Util::CheckFile(L"data*.arc") &&
                   (Util::CheckFile(L"stream*.arc") ||
                    Util::CheckFileAll({L"scenario*.arc", L"fastdata*.arc", L"data*.arc", L"voice*.arc"}));
        };
    };
    bool attach_function();
};
