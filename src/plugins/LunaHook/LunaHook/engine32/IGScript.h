

class IGScript:public ENGINE{
    public:
    IGScript(){
        
        check_by=CHECK_BY::CUSTOM;
        check_by_target=[](){
            return GetModuleHandle(L"Script.dll")&&Util::CheckFile(L"*.iga");
        };
        is_engine_certain=false;
    };
     bool attach_function();
};