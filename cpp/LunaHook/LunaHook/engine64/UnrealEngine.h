

class UnrealEngine : public ENGINE
{
public:
    UnrealEngine()
    {

        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = false;
        check_by_target = []()
        {
            // Copyright Epic Games, Inc. All Rights Reserved.
            //++UE4+Release-4.27-CL-0
            return Util::SearchResourceString(L"Copyright Epic Games") || Util::SearchResourceString(L"UnrealEngine") || GetProcAddress(GetModuleHandleA(0), "agsCheckDriverVersion");
        };
    };
    bool attach_function();
};
