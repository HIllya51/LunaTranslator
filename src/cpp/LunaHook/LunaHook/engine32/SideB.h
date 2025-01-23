

class SideB : public ENGINE
{
public:
  SideB()
  {

    check_by = CHECK_BY::RESOURCE_STR;
    check_by_target = L"side-B";
    // // 8/2/2014 jichi: Copyright is side-B, a conf.dat will be generated after the game is launched
    // It also contains lua5.1.dll and lua5.dll
  };
  bool attach_function();
};
