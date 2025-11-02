

class Wolf : public ENGINE
{

public:
    Wolf()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = [&]() -> bool
        {
            auto s = check_by_list{L"data.wolf", L"data\\*.wolf", L"data\\basicdata\\cdatabase.dat"};
            return std::any_of(s.begin(), s.end(), Util::CheckFile) || GetModuleHandle(L"GuruGuruSMF4.dll") || Util::SearchResourceString(L"Game / WOLF RPG Editor");
        };
    };
    bool attach_function();
};