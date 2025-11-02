

class Jellyfish : public ENGINE
{
public:
    HMODULE ism;
    DWORD minaddr, maxaddr;
    Jellyfish()
    {

        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = [this]()
        {
            ism = GetModuleHandle(L"ism.dll");
            return ism;
        };
        // check_by_list{L"ism.dll"};//,L"data.isa"};
    };
    bool attach_function();
    bool Jellyfish_attach_function();
    bool Jellyfish_attach_function2();
    bool Jellyfish_attach_function3();
};
