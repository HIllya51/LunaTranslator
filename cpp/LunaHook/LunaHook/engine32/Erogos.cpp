#include"Erogos.h"
//らぶフェチ ～マゾ編～
//らぶフェチ～千聡編～
 
bool Erogos::attach_function() {    
   
  HookParam hp;
  hp.address = (DWORD)TextOutA;
  hp.type=USING_STRING|USING_SPLIT;
  hp.split=get_stack(4);
  hp.offset=get_stack(4);
  hp.length_offset=5;
  return NewHook(hp, "Erogos");
} 