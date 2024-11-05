

class PONScripter:public ENGINE{
    public:
    PONScripter(){
        
        check_by=CHECK_BY::FILE_ANY;
        check_by_target=check_by_list{L"Proportional ONScripter",L"ponscr.exe"};
    }; 
     bool attach_function(); 
};
