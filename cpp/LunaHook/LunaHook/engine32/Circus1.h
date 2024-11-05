

class Circus1:public ENGINE{
    public:
    Circus1(){
        
        check_by=CHECK_BY::FILE;
        check_by_target=L"AdvData\\DAT\\NAMES.DAT";
    };
     bool attach_function();
};