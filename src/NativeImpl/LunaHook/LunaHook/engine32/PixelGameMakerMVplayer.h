

class PixelGameMakerMVplayer : public ENGINE
{
public:
    PixelGameMakerMVplayer()
    {
        enginename = "Pixel Game Maker MV player";
        check_by = CHECK_BY::RESOURCE_STR;
        check_by_target = L"Pixel Game Maker MV player";
    };
    bool attach_function();
};