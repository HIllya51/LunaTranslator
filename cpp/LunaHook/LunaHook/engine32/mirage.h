

class mirage : public ENGINE
{
public:
    mirage()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"anim/anm.pk", L"misc/*.pk", // bg.pk,script.pk,chr.pk,thumb.pk,se.pk,grp.pk,system.px,eff.pk
                                        L"movie/*.mj",
                                        L"sound/*.pk", // env.pk,music.pk
                                        L"voice/voice.pk"};
    };
    bool attach_function();
};