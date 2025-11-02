

class Ages3ResT : public ENGINE
{
public:
    Ages3ResT()
    {
        // Muv-Luv_Alternative16_20th
        // マブラヴ オルタネイティヴ age20th Edition
        check_by = CHECK_BY::FILE;
        check_by_target = L"Ages3ResT.dll";
    };
    bool attach_function();
};