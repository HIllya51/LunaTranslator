

class GameMaker : public ENGINE
{
public:
  GameMaker()
  {

    check_by = CHECK_BY::CUSTOM;
    check_by_target = []() -> bool
    {
      // 仅用来鉴别
      return GetModuleHandle(L"gm_bench.dll");
    };
  };
  bool attach_function();
};