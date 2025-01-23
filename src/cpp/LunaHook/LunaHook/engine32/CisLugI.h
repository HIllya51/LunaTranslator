#include "engine.h"

class CisLugI : public ENGINE
{
public:
    CisLugI()
    {
        // CisLugI-シスラギ-
        // https://vndb.org/v23679
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"chara.rvk5", L"back.rvk5", L"bgm.rvk5", L"container*.rvk5", L"script/*.rvk5", L"Sgr/*.rvk5"};
    };
    bool attach_function();
};