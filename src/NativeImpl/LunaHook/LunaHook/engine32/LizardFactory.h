

class LizardFactory : public ENGINE
{
public:
    LizardFactory()
    {
        // Monster Brothel Ver1.15a
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFile(L"archive") && GetModuleHandle(L"glew32.dll") && GetModuleHandle(L"Vox.dll");
        };
        is_engine_certain = false;
    };
    bool attach_function();
};