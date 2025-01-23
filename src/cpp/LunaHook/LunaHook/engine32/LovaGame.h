
class LovaGame : public ENGINE
{
public:
    LovaGame()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"UE3ShaderCompileWorker.exe", L"awesomium_process.exe"};
    }
    bool attach_function();
};