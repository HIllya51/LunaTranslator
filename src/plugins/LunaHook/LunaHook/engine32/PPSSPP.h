

class PPSSPPengine:public ENGINE{
    public:
    PPSSPPengine(){
        
        check_by=CHECK_BY::FILE;
        check_by_target=L"PPSSPP*.exe";
        is_engine_certain=false;
    };
    bool attach_function();
     
};