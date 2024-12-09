#include"HXP.h"
 

bool HXP::attach_function() { 
    //https://vndb.org/v172
    //エクソダスギルティー・オルタナティブ
    auto addr=MemDbg::findCallerAddress((DWORD)TextOutA, 0x01003d66,processStartAddress, processStopAddress); 
    if(addr==0)return false;
    addr=MemDbg::findEnclosingAlignedFunction(addr);
    if(addr==0)return false;
    HookParam hp;
    hp.address = (DWORD)addr;
    hp.offset=stackoffset(2);
    hp.type = CODEC_ANSI_BE;
    
    return NewHook(hp, "HXP");
} 