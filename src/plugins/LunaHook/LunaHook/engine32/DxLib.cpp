#include"DxLib.h"
bool DxLibFilter(LPVOID data, size_t* size, HookParam*)
{
    auto text = reinterpret_cast<LPSTR>(data);
    auto len = reinterpret_cast<size_t*>(size);

    StringCharReplacer(text, len, "%N", 2, ' ');
    StringFilter(text, len, "%K", 2);
    StringFilter(text, len, "%P", 2);

    return true;
}
bool InsertDxLibHook()
{
    
      /*
      * Sample games:
      * https://vndb.org/v7849
      * https://vndb.org/v10231
      */
    const BYTE bytes[] = {
      0xF7, 0xC6, XX4,            // test esi,00000003      << hook here
      0x75, XX,                   // jne BookofShadows.exe+15FE54
      0x8B, 0xD9,                 // mov ebx,ecx
      0xC1, 0xE9, 0x02,           // shr ecx,02
      0x75, XX,                   // jne BookofShadows.exe+15FEAE
      0xEB, XX                    // jmp BookofShadows.exe+15FE76
    };

    ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
    if (!addr) {
        ConsoleOutput("DxLib: pattern not found");
        return false;
    }

    HookParam hp;
    hp.address = addr;
    hp.offset =get_reg(regs::esi);
    hp.type = USING_STRING;
    hp.filter_fun = DxLibFilter;
    ConsoleOutput(" INSERT DxLib");
    
    return NewHook(hp, "DxLib");
}


bool DxLib::attach_function() { 
    return InsertDxLibHook();
} 