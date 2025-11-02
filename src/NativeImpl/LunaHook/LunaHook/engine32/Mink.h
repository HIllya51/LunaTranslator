

class Mink : public ENGINE
{
public:
    Mink()
    {

        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"*.at2", L"*.atm"}; // Mink, sample files: voice.at2, voice.det, voice.nme
    };
    bool attach_function();
};

class Mink2 : public ENGINE
{
public:
    Mink2()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"Scr\\*.sc";
        is_engine_certain = false;
    };
    bool attach_function();
};
class Mink3 : public ENGINE
{
public:
    Mink3()
    {
        // 夜勤病棟 復刻版+
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"voice*.dat", L"tpd.dat", L"tms.dat", L"thm.dat", L"se.dat", L"scr.dat", L"rec.dat", L"bgm.dat", L"cgm.dat", L"gpd.dat", L"gpdtp.dat", L"mov.dat", L"msk.dat", L"msktp.dat", L"read.dat"};
        is_engine_certain = false;
    };
    bool attach_function();
};