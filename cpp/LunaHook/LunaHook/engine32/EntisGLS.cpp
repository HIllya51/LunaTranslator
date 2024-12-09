#include"EntisGLS.h"

bool EntisGLS::attach_function() {  
    
    
//それは舞い散る桜のように-完全版-
//int __thiscall sub_4BB5D0(_BYTE *this, LPCWCH lpWideCharStr)
    const uint8_t bytes1[]={
       0x66,0x83,0xF9,0x41 ,
       0x72,0x06,
       0x66,0x83,0xF9,0x5a ,
       0x76,0x0C,
       0x66,0x83,0xF9,0x61 ,
       0x72,0x12,
       0x66,0x83,0xF9,0x7a ,
       0x77,0x0c

    };
    auto addr=MemDbg::findBytes(bytes1, sizeof(bytes1), processStartAddress, processStopAddress);
     
    if (!addr) return false;
    addr=MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr) return false;
    HookParam hp;
    hp.address = addr ;
    hp.offset=stackoffset(1);
    hp.embed_hook_font=F_GetGlyphOutlineW;
    hp.type = USING_STRING|CODEC_UTF16|EMBED_ABLE|EMBED_AFTER_NEW; 
    
    return NewHook(hp, "EntisGLS");
   
} 