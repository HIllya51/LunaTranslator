

class AdobeAir : public ENGINE
{
public:
    AdobeAir()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFile(L"Adobe AIR\\Versions\\1.0\\Adobe AIR.dll") || GetModuleHandle(L"Adobe AIR.dll") || Util::CheckFileAny({L"*.swf", L"bg/*.swf"});
        };
    };
    bool attach_function();
};