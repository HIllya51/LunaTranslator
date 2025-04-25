#include "AIL.h"
bool InsertAIL2Hook()
{
  auto findalign = [](uintptr_t addr1)
  {
    const BYTE pattern[] = {0x90, 0x90, 0x83, 0xec};
    return reverseFindBytes(pattern, sizeof(pattern), processStartAddress, addr1) + 2;
  };
  bool succ = false;
  BYTE bytes1[] = {
      //				.text:0042E5DF 3C 66                         cmp     al, 66h; 'f'
      //.text:0042E5E1 74 57                         jz      short loc_42E63A
      //.text : 0042E5E1
      //.text : 0042E5E3 3C 70                         cmp     al, 70h; 'p'
      //.text:0042E5E5 74 4C                         jz      short loc_42E633
      //.text : 0042E5E5
      //.text : 0042E5E7 3C 73                         cmp     al, 73h; 's'
      //.text:0042E5E9 74 37                         jz      short loc_42E622
      0x3c, 0x66,
      0x74, XX,
      0x3c, 0x70,
      0x74, XX,
      0x3c, 0x73,
      0x74, XX};
  auto addr1 = MemDbg::findBytes(bytes1, sizeof(bytes1), processStartAddress, processStopAddress);
  if (!addr1)
    return false;
  addr1 = findalign(addr1);
  if (!addr1)
    return false;
  ConsoleOutput("AIL1 %p", addr1);
  {
    HookParam hp;
    hp.address = addr1;
    hp.codepage = 932;
    hp.offset = stackoffset(3);
    hp.type = USING_STRING;
    succ |= NewHook(hp, "AIL1");
  }
  BYTE bytes[] = {// if ( v12 != 32 && v12 != 33088 )
                  0x3d, 0x40, 0x81, 0x00, 0x00, 0x0f};

  addr1 = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr1)
    return succ;
  addr1 = MemDbg::findEnclosingAlignedFunction(addr1);
  if (!addr1)
    return succ;
  {
    HookParam hp;
    hp.address = addr1;
    hp.codepage = 932;
    hp.offset = stackoffset(4);
    hp.type = USING_STRING | USING_SPLIT;
    hp.split_index = 0;
    succ |= NewHook(hp, "AIL2");
  }
  return succ;
}
bool AILold()
{
  // https://vndb.org/v6409
  //  エルフィーナ～淫夜へと売られた王国で…～
  // 其实这个同一个函数里面也有 cmp     al, 66h; 'f'这个pattern，不过不太一样。懒得分了就这样吧。
  BYTE bytes1[] = {
      /*
      .text:00431E87                 mov     edx, dword_4AD54C
  .text:00431E8D                 test    edx, edx
  .text:00431E8F                 jnz     loc_4326E0      ; jumptable 00431EB0 case 0
  .text:00431E95                 mov     edx, [esp+3Ch+lpString]
  .text:00431E99                 mov     dl, [edi+edx]
  .text:00431E9C                 movsx   esi, dl
  .text:00431E9F                 cmp     esi, 40h        ; switch 65 cases
  .text:00431EA2                 ja      def_431EB0      ; jumptable 00431EB0 default case, cases 1-34,38-42,44,46-63
  .text:00431EA8                 xor     ebx, ebx
  .text:00431EAA                 mov     bl, ds:byte_43270C[esi]
  .text:00431EB0                 jmp     ds:jpt_431EB0[ebx*4] ; switch jump
      */
      0x8b, 0x54, 0x24, XX,
      0x8a, 0x14, 0x17,
      0x0f, 0xbe, 0xf2,
      0x83, 0xfe, 0x40,
      0x0f, 0x87, XX4,
      0x33, 0xdb,
      0x8a, 0x9e, XX4,
      0xff, 0x24, 0x9d, XX4};
  auto addr1 = MemDbg::findBytes(bytes1, sizeof(bytes1), processStartAddress, processStopAddress);
  if (!addr1)
    return false;
  addr1 = MemDbg::findEnclosingAlignedFunction(addr1);
  if (!addr1)
    return false;
  HookParam hp;
  hp.address = addr1;
  hp.offset = stackoffset(3);
  hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
  hp.embed_hook_font = F_TextOutA;

  return NewHook(hp, "AIL");
}

bool AIL::attach_function()
{

  return InsertAIL2Hook() || AILold();
}