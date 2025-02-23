

class Ruf : public ENGINE
{
public:
    Ruf()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto fs = {L"*.arc", L"*.scb", L"*.bmx"};
            return std::all_of(fs.begin(), fs.end(), Util::CheckFile) && (Util::CheckFile(L"*.wsm") || GetModuleHandle(L"Kagura.dll"));
        };
    };
    bool attach_function();
};