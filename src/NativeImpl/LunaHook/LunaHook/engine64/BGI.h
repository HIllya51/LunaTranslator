

class BGI : public ENGINE
{
public:
    BGI()
    {

        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"bgi.*", L"sysgrp.arc"};
    };
    bool attach_function();
};
