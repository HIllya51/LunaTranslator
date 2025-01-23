

class Speed : public ENGINE
{
public:
    Speed()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto hcb = std::wstring(processName);
            hcb = hcb.substr(0, hcb.size() - 4) + L".hcb";
            return (Util::CheckFile(hcb.c_str()) && Util::CheckFile(L"bgm.bin") && Util::CheckFile(L"cg.bin") && Util::CheckFile(L"se.bin") && Util::CheckFile(L"vo.bin"));
        };
    };
    bool attach_function();
};