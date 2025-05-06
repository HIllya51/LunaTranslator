

class Syuntada : public ENGINE
{
public:
  Syuntada()
  {

    check_by = CHECK_BY::FILE;
    check_by_target = L"dSch.dat";
    // jichi 2/6/2015 平安亭
    // dPi.dat, dPih.dat, dSc.dat, dSch.dat, dSo.dat, dSoh.dat, dSy.dat
    // if (Util::CheckFile(L"dSoh.dat")) { // no idea why this file does not work
  };
  bool attach_function();
};