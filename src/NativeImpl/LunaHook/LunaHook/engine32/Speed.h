

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
            return Util::CheckFileAll({hcb.c_str(),L"bgm.bin",L"cg.bin",L"se.bin",L"vo.bin"});
        };
    };
    bool attach_function();
};