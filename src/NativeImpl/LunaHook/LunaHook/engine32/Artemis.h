

class Artemis : public ENGINE
{
public:
    Artemis()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFile(L"*.pfs") ||
                   Util::CheckFileAll({L"scenario/asbmacro.asb", L"scenario/main.iet", L"scenario/main/*.asb",
                                       L"system/*.asb", L"system/*.iet"});
        };
    };
    bool attach_function();
};