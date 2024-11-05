

class PCSX2:public ENGINE{
    public:
    PCSX2(){
        
        check_by=CHECK_BY::FILE;
        check_by_target=L"pcsx2*.exe";    //PCSX2.exe or PCSX2WX.exe
    };
    bool attach_function();
     
};