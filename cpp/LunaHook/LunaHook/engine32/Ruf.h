

class Ruf:public ENGINE{
    public:
    Ruf(){
        is_engine_certain=false;
        check_by=CHECK_BY::FILE_ALL;
        check_by_target=check_by_list{L"*.arc",L"*.wsm",L"*.scb",L"*.bmx"};
    };
     bool attach_function();
};