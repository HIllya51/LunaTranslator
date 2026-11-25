
// MINS ADVSYS3 引擎 (ADVSYS3.EXE, 1996-1998)
// 已知游戏: いちょう (icho, 1998)
class AdvSys3 : public ENGINE
{
public:
    AdvSys3()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFile(L"arc.dat") && Util::SearchStringFileInfo(L"ADVSYS3");
        };
    };
    bool attach_function();
};
