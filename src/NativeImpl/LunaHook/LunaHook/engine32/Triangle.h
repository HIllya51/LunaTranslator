

class Triangle : public ENGINE
{
public:
    Triangle()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"Execle.exe";
    };
    bool attach_function();
};

class Triangle2 : public ENGINE
{
public:
    Triangle2()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"pix.bin", L"pix.xml"};
    };
    bool attach_function();
};

class TriangleM : public ENGINE
{
public:
    TriangleM()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []
        {
            wchar_t _[] = L"fsroot_\\common\\app_info.rson";

            for (int i = 0; i < 10; i++)
            {
                _[6] = L'0' + i;
                if (Util::CheckFile(_))
                    return 1;
            }
            return 0;
        };
    };
    bool attach_function();
};