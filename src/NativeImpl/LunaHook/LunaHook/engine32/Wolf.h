

class Wolf : public ENGINE
{

public:
    Wolf()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = [&]() -> bool
        {
            return Util::CheckFileAny({L"data.wolf", L"data\\*.wolf", L"data\\basicdata\\cdatabase.dat"}) ||
                   GetModuleHandle(L"GuruGuruSMF4.dll") ||
                   Util::SearchResourceString(L"Game / WOLF RPG Editor");
        };
    };
    bool attach_function();
};