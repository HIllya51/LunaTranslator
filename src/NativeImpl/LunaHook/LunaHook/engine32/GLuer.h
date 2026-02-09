
// 桜雪

class GLuer : public ENGINE
{
public:
    GLuer()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"bg", L"bgm", L"ev", L"obj", L"se", L"system", L"text", L"voice"};
        is_engine_certain = false;
    };
    bool attach_function();
};