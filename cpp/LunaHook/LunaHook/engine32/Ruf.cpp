#include"Ruf.h"
 
bool Ruf::attach_function() {
    const BYTE bytes[] = {
    //奴隷市場Renaissance
        0x81,XX,0x00,0x01,0x00,0x00,
        0x8B,0xF0,
        0x76,0x07,
        0x81,0x6D,0xF4,0x00,0x80,0x00,0x00, 
    }; 
    const BYTE bytes2[] = {
    //セイレムの魔女たち
        0x81,XX,0x00,0x01,0x00,0x00, 
        0x76,0x07,
        0x81,0x6D,0xF4,0x00,0x80,0x00,0x00, 
    }; 
    auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (addr == 0) 
        addr = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
    if (addr == 0)return false; 
    addr = findfuncstart(addr);
    if (addr == 0)return false; 
    HookParam hp;
    hp.address = addr;  
    hp.offset=get_reg(regs::edx); 
    hp.type |= CODEC_ANSI_BE;
    return NewHook(hp, "Ruf");
} 