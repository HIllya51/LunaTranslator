

class Mink:public ENGINE{
    public:
    Mink(){
        
        check_by=CHECK_BY::FILE;
        check_by_target=L"*.at2";//Mink, sample files: voice.at2, voice.det, voice.nme
    };
     bool attach_function();
};

class Mink2:public ENGINE{
    public:
    Mink2(){
        
        check_by=CHECK_BY::FILE;
        check_by_target=L"Scr\\*.sc";
        is_engine_certain=false;
    };
     bool attach_function();
};