

class LightVN : public ENGINE
{
public:
    LightVN()
    {

        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = false;
        check_by_target = []()
        {
            auto s = check_by_list{L"Data/Scripts/title.txt", L"Data/data*.vndat", L"Scripts/000_title.txt"};
            auto s2 = check_by_list{L"LightTests.exe", L"BugTrap.dll", L"libGLESv2.dll", L"libEGL.dll"};
            return std::any_of(s.begin(), s.end(), Util::CheckFile) || std::all_of(s2.begin(), s2.end(), Util::CheckFile);
        };
    };
    bool attach_function();
};
