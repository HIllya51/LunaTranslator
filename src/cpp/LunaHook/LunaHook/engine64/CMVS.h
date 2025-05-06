

class CMVS : public ENGINE
{
public:
  CMVS()
  {

    check_by = CHECK_BY::FILE;
    check_by_target = L"data\\pack\\*.cpz";

    // jichi 8/19/2013: DO NOT WORK for games like「ハピメア」
    // if (wcsstr(str,L"cmvs32") || wcsstr(str,L"cmvs64")) {
    //  InsertCMVSHook();
    //  return true;
    //}
  };
  bool attach_function();
};