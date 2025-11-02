

class Suika2 : public ENGINE
{
public:
    Suika2()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            if (wcscmp(processName_lower, L"suika.exe") == 0)
                return true;
            char suika2copyright[] = "Suika2: Copyright";
            return 0 != MemDbg::findBytes(suika2copyright, sizeof(suika2copyright) - 1, processStartAddress, min(processStopAddress, processStartAddress + 0x200000));
        };
    };
    bool attach_function();
};