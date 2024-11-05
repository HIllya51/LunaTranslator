

class FocasLens:public ENGINE{
    public:
    FocasLens(){
        
        check_by=CHECK_BY::FILE;
        check_by_target=L"dat\\*.arc"; 
    };
     bool attach_function();
};