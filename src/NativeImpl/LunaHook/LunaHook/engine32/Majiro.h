

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
                    (Util::CheckFile(L"scenario*.arc") && Util::CheckFile(L"fastdata*.arc") && Util::CheckFile(L"data*.arc") && Util::CheckFile(L"voice*.arc")));
        };
    };
    bool attach_function();
};
