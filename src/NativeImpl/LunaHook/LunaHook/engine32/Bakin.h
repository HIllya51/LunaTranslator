// RPG Developer Bakin (SmileBoom) / SGB engine runtime
// sgb_rpgplayer exe (C#, Yukar.Engine) + SharpKmyCore.dll (C++/CLI) + kmyCore.dll (native) + data.sgbpack
class Bakin : public ENGINE
{
public:
  Bakin()
  {
    check_by = CHECK_BY::FILE_ALL;
    check_by_target = check_by_list{L"kmyCore.dll", L"data.sgbpack"};
    is_engine_certain = true;
  };
  bool attach_function();
};
