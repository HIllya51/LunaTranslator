

class Footy2:public ENGINE{
    public:
    Footy2(){
        
        check_by=CHECK_BY::FILE;
        check_by_target=L"Footy2.dll"; 
        dontstop=true;
    };
     bool attach_function();
};