
// Labyrinth of Touhou Tri
class THLabyrinth3 : public ENGINE
{
public:
    THLabyrinth3()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{
            L"Content/bgm1.dxa",
            L"Content/img1.dxa",
            L"Content/se1.dxa",
        };
    };
    bool attach_function();
};
