

class System4x : public ENGINE
{
public:
    System4x()
    {

        check_by = CHECK_BY::FILE;
        // jichi 12/26/2013: Add this after alicehook
        check_by_target = L"AliceStart.ini";
    };
    bool attach_function();
};