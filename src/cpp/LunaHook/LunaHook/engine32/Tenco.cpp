#include "Tenco.h"

/**
 *  jichi 4/1/2014: Insert AU hook
 *  Sample games:
 *  英雼�戦姫: /HBN-8*4@4AD807
 *  英雼�戦姫GOLD: /HB-8*4@4ADB50 (alternative)
 *
 *  /HBN-8*4@4AD807
 *  - addr: 4904967 = 0x4ad807
 *  - ind: 4
 *  - length_offset: 1
 *  - off: 4294967284 = 0xfffffff4 = -0xc
 *  - type: 1032 = 0x408
 *
 *  004ad76a  |. ff50 04        |call dword ptr ds:[eax+0x4]
 *  004ad76d  |. 48             |dec eax                                 ;  switch (cases 1..a)
 *  004ad76e  |. 83f8 09        |cmp eax,0x9
 *  004ad771  |. 0f87 37020000  |ja 英雼�戦.004ad9ae
 *  004ad777  |. ff2485 2cda4a0>|jmp dword ptr ds:[eax*4+0x4ada2c]
 *  004ad77e  |> 83bf c4000000 >|cmp dword ptr ds:[edi+0xc4],0x1         ;  case 1 of switch 004ad76d
 *  004ad785  |. 75 35          |jnz short 英雼�戦.004ad7bc
 *  004ad787  |. 39af c8000000  |cmp dword ptr ds:[edi+0xc8],ebp
 *  004ad78d  |. 72 08          |jb short 英雼�戦.004ad797
 *  004ad78f  |. 8b87 b4000000  |mov eax,dword ptr ds:[edi+0xb4]
 *  004ad795  |. eb 06          |jmp short 英雼�戦.004ad79d
 *  004ad797  |> 8d87 b4000000  |lea eax,dword ptr ds:[edi+0xb4]
 *  004ad79d  |> 0fb608         |movzx ecx,byte ptr ds:[eax]
 *  004ad7a0  |. 51             |push ecx
 *  004ad7a1  |. e8 d15b2a00    |call 英雼�戦.00753377
 *  004ad7a6  |. 83c4 04        |add esp,0x4
 *  004ad7a9  |. 85c0           |test eax,eax
 *  004ad7ab  |. 74 0f          |je short 英雼�戦.004ad7bc
 *  004ad7ad  |. 8d5424 20      |lea edx,dword ptr ss:[esp+0x20]
 *  004ad7b1  |. 52             |push edx
 *  004ad7b2  |. b9 88567a00    |mov ecx,英雼�戦.007a5688
 *  004ad7b7  |. e8 a40cf6ff    |call 英雼�戦.0040e460
 *  004ad7bc  |> 8b8424 e400000>|mov eax,dword ptr ss:[esp+0xe4]
 *  004ad7c3  |. 8a48 01        |mov cl,byte ptr ds:[eax+0x1]
 *  004ad7c6  |. 84c9           |test cl,cl
 *  004ad7c8  |. 75 2e          |jnz short 英雼�戦.004ad7f8
 *  004ad7ca  |. 8d9f b0000000  |lea ebx,dword ptr ds:[edi+0xb0]
 *  004ad7d0  |. be ac6e7a00    |mov esi,英雼�戦.007a6eac
 *  004ad7d5  |. 8bcb           |mov ecx,ebx
 *  004ad7d7  |. e8 e40af6ff    |call 英雼�戦.0040e2c0
 *  004ad7dc  |. 84c0           |test al,al
 *  004ad7de  |. 0f84 ca010000  |je 英雼�戦.004ad9ae
 *  004ad7e4  |. be a86e7a00    |mov esi,英雼�戦.007a6ea8
 *  004ad7e9  |. 8bcb           |mov ecx,ebx
 *  004ad7eb  |. e8 d00af6ff    |call 英雼�戦.0040e2c0
 *  004ad7f0  |. 84c0           |test al,al
 *  004ad7f2  |. 0f84 b6010000  |je 英雼�戦.004ad9ae
 *  004ad7f8  |> 6a 00          |push 0x0
 *  004ad7fa  |. 8d8f b0000000  |lea ecx,dword ptr ds:[edi+0xb0]
 *  004ad800  |. 83c8 ff        |or eax,0xffffffff
 *  004ad803  |. 8d5c24 24      |lea ebx,dword ptr ss:[esp+0x24]
 *  004ad807  |. e8 740cf6ff    |call 英雼�戦.0040e480     ; jichi: hook here
 *  004ad80c  |. e9 9d010000    |jmp 英雼�戦.004ad9ae
 *  004ad811  |> 8b8c24 e400000>|mov ecx,dword ptr ss:[esp+0xe4]         ;  case 4 of switch 004ad76d
 *  004ad818  |. 8039 00        |cmp byte ptr ds:[ecx],0x0
 *  004ad81b  |. 0f84 8d010000  |je 英雼�戦.004ad9ae
 *  004ad821  |. b8 04000000    |mov eax,0x4
 *  004ad826  |. b9 c86e7a00    |mov ecx,英雼�戦.007a6ec8                   ;  ascii "<br>"
 *  004ad82b  |. 8d5424 20      |lea edx,dword ptr ss:[esp+0x20]
 *  004ad82f  |. e8 3c0df6ff    |call 英雼�戦.0040e570
 *  004ad834  |. e9 75010000    |jmp 英雼�戦.004ad9ae
 *  004ad839  |> 8bbf b4000000  |mov edi,dword ptr ds:[edi+0xb4]         ;  case 5 of switch 004ad76d
 */
bool InsertTencoHook()
{
  const BYTE bytes[] = {
      0x6a, 0x00,                         // 004ad7f8  |> 6a 00          |push 0x0
      0x8d, 0x8f, 0xb0, 0x00, 0x00, 0x00, // 004ad7fa  |. 8d8f b0000000  |lea ecx,dword ptr ds:[edi+0xb0]
      0x83, 0xc8, 0xff,                   // 004ad800  |. 83c8 ff        |or eax,0xffffffff
      0x8d, 0x5c, 0x24, 0x24,             // 004ad803  |. 8d5c24 24      |lea ebx,dword ptr ss:[esp+0x24]
      0xe8                                // 740cf6ff                 // 004ad807  |. e8 740cf6ff    |call 英雼�戦.0040e480     ; jichi: hook here
  };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  // reladdr = 0x4ad807;
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr + sizeof(bytes) - 1;
  hp.index = 4;
  hp.offset = regoffset(ecx);
  hp.type = NO_CONTEXT | DATA_INDIRECT;

  ConsoleOutput("INSERT Tenco");
  return NewHook(hp, "Tenco");
}
bool LWScript()
{
  BYTE bytes[] = {
      0x33, 0xdb,
      0x53,
      0x8d, 0x87, XX4,
      0x50,
      0x55,
      0x57,
      0xe8};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(edx);
  hp.type = USING_STRING;
  return NewHook(hp, "LWScript");
}
bool LWScript2()
{
  BYTE bytes[] = {
      0x66, 0xC1, 0xE8, 0x08,
      0x3C, 0x81};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  int off;
  if (*(BYTE *)(addr + 3) == 0x4C)
    off = stackoffset(2);
  else
    off = regoffset(ecx);
  HookParam hp;
  hp.address = addr;
  hp.offset = off;
  hp.type = CODEC_ANSI_BE;
  auto succ = NewHook(hp, "LWScript2");

  auto addrs = findxref_reverse(addr, addr - 0x10000, addr);
  for (auto addr : addrs)
  {
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      continue;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(5);
    hp.type = CODEC_ANSI_BE;
    succ |= NewHook(hp, "LWScript2_xref");
  }
  return succ;
}
namespace
{
  // https://vndb.org/r64724
  bool h()
  {
    BYTE bytes[] = {
        0x83, 0x7e, 0x18, 0x10,
        0x8d, 0x7e, 0x04,
        0x72, 0x04,
        0x8b, 0x07,
        0xeb, 0x02,
        0x8b, 0xc7,
        0x80, 0x3c, 0x18, 0x3c,
        0x75, XX,
        0x43,
        0x3b, 0x5e, 0x14};
    auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = findfuncstart(addr, 0x100, true);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(edx);
    hp.type = USING_STRING;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      DWORD *a2 = (DWORD *)context->stack[2];
      auto v6 = a2;
      auto v8 = v6 + 1;
      DWORD *v9;
      if (v6[6] < 0x10u)
        v9 = v6 + 1;
      else
        v9 = (DWORD *)*v8;
      buffer->from((char *)v9, v6[5]);
      *split = *(DWORD *)context->eax;
    };
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      buffer->from(re::sub(buffer->strA(), R"(<.*?>)"));
      StringFilterBetween(buffer, TEXTANDLEN("("), TEXTANDLEN(")"));
      StringFilter(buffer, "&,", 1);
      StringFilter(buffer, "&.", 1);
    };
    return NewHook(hp, "Tenco");
  }
}
bool Tenco::attach_function()
{

  bool b3 = InsertTencoHook();
  bool b1 = LWScript();
  bool b2 = LWScript2();
  return b1 || b2 || b3 || h();
}