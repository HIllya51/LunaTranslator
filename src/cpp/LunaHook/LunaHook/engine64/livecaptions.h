

class livecaptions : public ENGINE
{
public:
    livecaptions()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return GetModuleHandle(L"vcruntime140_app.dll") && GetModuleHandle(L"Microsoft.CognitiveServices.Speech.extension.embedded.sr.dll");
        };
    };
    bool attach_function();
};
