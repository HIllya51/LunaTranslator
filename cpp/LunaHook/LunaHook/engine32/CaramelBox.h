

class CaramelBox : public ENGINE
{
public:
    CaramelBox()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto str = std::wstring(processName_lower);
            DWORD len = str.size();

            // jichi 8/10/2013: Since *.bin is common, move CaramelBox to the end
            str[len - 3] = L'b';
            str[len - 2] = L'i';
            str[len - 1] = L'n';
            str[len] = 0;
            return (Util::CheckFile(str.c_str()) || Util::CheckFile(L"trial.bin"));
        };
        is_engine_certain = false;
    };
    bool attach_function();
};

class CaramelBoxMilkAji : public ENGINE
{
public:
    CaramelBoxMilkAji()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"SdActiRc.dll";
        is_engine_certain = false;
    };
    bool attach_function();
};

class CaramelBox2 : public ENGINE
{
public:
    CaramelBox2()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            if (!Util::CheckFile(L"*.mpg"))
                return false;
            char copyright[] = "OTOBOKU-CaramelBox"; // OTOBOKU-CaramelBox  //Software\Caramel-Box\OTOMEHABOKUNIKOISHITERU
            return 0 != MemDbg::findBytes(copyright, sizeof(copyright), processStartAddress, min(processStopAddress, processStartAddress + 0x200000));
        };
    };
    bool attach_function();
};