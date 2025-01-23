
#include "python/python.h"

class Renpy : public ENGINE
{
public:
    Renpy()
    {
        // 使用lunatranslator启动游戏，会把cwd修改成exe所在目录，其中没有.py
        //  check_by=CHECK_BY::CUSTOM;
        //  check_by_target=[](){
        //      //Renpy - sample game https://vndb.org/v19843
        //      return Util::CheckFile(L"*.py")|| GetModuleHandleW(L"librenpython.dll");
        //  };

        check_by = CHECK_BY::CUSTOM;
        check_by_target = [this]()
        { return attach_function_(); };
    };
    bool attach_function() { return true; }
    bool attach_function_()
    {
#ifndef _WIN64
        return InsertRenpyHook();
#else
        return InsertRenpyHook() || InsertRenpy3Hook();
#endif
    }
};
