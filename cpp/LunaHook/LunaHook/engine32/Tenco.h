

class Tenco:public ENGINE{
    public:
    Tenco(){
        
        check_by=CHECK_BY::FILE;
        check_by_target=L"Check.mdx";
    };
     bool attach_function();
};