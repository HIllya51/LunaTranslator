

class LightVN : public ENGINE
{
public:
    LightVN()
    {

        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = false;
        check_by_target = []()
        {
            return Util::CheckFileAny({L"Data/Scripts/title.txt", L"Data/data*.vndat", L"Scripts/000_title.txt"}) ||
                   Util::CheckFileAll({L"LightTests.exe", L"BugTrap.dll", L"libGLESv2.dll", L"libEGL.dll"});
        };
    };
    bool attach_function();
};
