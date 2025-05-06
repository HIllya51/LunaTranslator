

class e_Erekiteru : public ENGINE
{
public:
    e_Erekiteru()
    {
        // https://vndb.org/v15578
        // 水素～1/2の奇蹟～
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"hmc.dll", L"*.pkk"};
    };
    bool attach_function();
};