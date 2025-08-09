

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
            //"++UE5+Release-5.0-CL-20979098"
            return Util::SearchResourceString(L"Copyright Epic Games") || Util::SearchResourceString(L"UnrealEngine") || Util::SearchResourceString(L"++UE5+Release") || Util::SearchResourceString(L"++UE4+Release") || Util::SearchResourceString(L"UE5-CL-0");
        };
    };
    bool attach_function();
};
