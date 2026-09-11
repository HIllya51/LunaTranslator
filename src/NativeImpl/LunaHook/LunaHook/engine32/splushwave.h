

class splushwave : public ENGINE
{
public:
    splushwave()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::SearchResourceString(L"splush wave") ||
                   Util::CheckFileAll({L"Syuusei.dat", L"*_ADD.DAT", L"*_BASE.DAT", L"*_CG.DAT", L"*_SE.DAT", L"*_VOI.DAT", L"*_BOOT.DAT"}) ||              // とある魔雀の禁書目録
                   Util::CheckFileAll({L"Syuusei.dat", L"*_BASE.DAT", L"*_BGM.DAT", L"*_SE.DAT", L"*_KOE.DAT", L"BOOT.DAT"}); // Unlimited Mahjongg Works
        };
        is_engine_certain = false;
    };
    bool attach_function();
};