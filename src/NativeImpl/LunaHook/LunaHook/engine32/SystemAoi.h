

class SystemAoi : public ENGINE
{
public:
    SystemAoi()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.vfs";
        // jichi 7/6/2014: Better to test AoiLib.dll? ja.wikipedia.org/wiki/ソフトハウスキャラ
    };
    bool attach_function();
};