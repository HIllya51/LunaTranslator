

class MerRouge : public ENGINE
{
public:
  MerRouge()
  {

    check_by = CHECK_BY::FILE_ALL;
    check_by_target = check_by_list{L"bmp/*.pak", L"cv/*.pcv", L"scenario/*.txt", L"SE/*.wav"};
  };
  bool attach_function();
};