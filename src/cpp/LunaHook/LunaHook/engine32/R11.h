

class R11 : public ENGINE
{
public:
    R11()
    {

        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"FILE/bg.afs", L"FILE/bgm.afs", L"FILE/bgmpc.afs", L"FILE/chr.afs", L"FILE/etc.afs", L"FILE/ev.afs", L"FILE/file.afs", L"FILE/mac.afs", L"FILE/se.afs", L"FILE/voice.afs"};
    };
    bool attach_function();
};