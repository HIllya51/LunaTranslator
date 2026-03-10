
class PinkQuestion : public ENGINE
{
public:
  PinkQuestion()
  {
    check_by = CHECK_BY::CUSTOM;
    check_by_target = []()
    {
      auto _ = {L"nayuta.exe", L"data.0*"};
      return std::all_of(_.begin(), _.end(), Util::CheckFile);
    };
  };
  bool attach_function();
};