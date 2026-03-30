
class PinkQuestion : public ENGINE
{
public:
  PinkQuestion()
  {
    check_by = CHECK_BY::FILE_ALL;
    check_by_target = check_by_list{L"nayuta.exe", L"data.0*"};
  };
  bool attach_function();
};