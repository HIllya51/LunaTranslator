

class sakanagl:public ENGINE{
    public:
    sakanagl(){
        
        check_by=CHECK_BY::CUSTOM; 
        is_engine_certain=false;
        check_by_target=[](){
            return GetModuleHandleW(L"sakanagl.dll");
        };
    }; 
    bool attach_function(); 
};
