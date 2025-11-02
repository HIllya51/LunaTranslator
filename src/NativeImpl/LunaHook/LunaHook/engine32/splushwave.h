

class splushwave : public ENGINE
{
public:
    splushwave()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::SearchResourceString(L"splush wave") ||
                   (Util::CheckFile(L"Syuusei.dat") && Util::CheckFile(L"*_ADD.DAT") && Util::CheckFile(L"*_BASE.DAT") && Util::CheckFile(L"*_CG.DAT") && Util::CheckFile(L"*_SE.DAT") && Util::CheckFile(L"*_VOI.DAT") && Util::CheckFile(L"*_BOOT.DAT")); // とある魔雀の禁書目録
        };
        is_engine_certain = false;
    };
    bool attach_function();
};