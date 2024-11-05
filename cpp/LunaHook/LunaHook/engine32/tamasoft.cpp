#include"tamasoft.h"
bool tamasoft::attach_function() { 
    HookParam hp;
    hp.address=(DWORD)TextOutA;
    hp.offset=get_stack(4);
    hp.split=get_stack(4);
    hp.type=USING_STRING|USING_SPLIT;
    return NewHook(hp,"tamasoft");
} 