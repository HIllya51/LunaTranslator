#include "ransel.h"
// [020726][苺みるく] たんぽぽ ～Everything Nice～ (bin+cue)
// HS-8@4B377C
// int __fastcall sub_4B377C(int a1, char *a2)
// {
//   char *v3; // eax
//   int v4; // ebx
//   HWND v6; // [esp-10h] [ebp-18h]
//   unsigned int v7[2]; // [esp-Ch] [ebp-14h] BYREF
//   int *v8; // [esp-4h] [ebp-Ch]
//   char *v9; // [esp+4h] [ebp-4h] BYREF
//   int savedregs; // [esp+8h] [ebp+0h] BYREF

//   v9 = a2;
//   sub_4E2260(a2);
//   v8 = &savedregs;
//   v7[1] = (unsigned int)&loc_4B37CC;
//   v7[0] = (unsigned int)NtCurrentTeb()->NtTib.ExceptionList;
//   __writefsdword(0, (unsigned int)v7);
//   v6 = (HWND)sub_49B474(a1);
//   v3 = sub_4E2270(v9);
//   v4 = sub_4BEAC4(v6, (LPARAM)v3);
//   __writefsdword(0, v7[0]);
//   v8 = (int *)&loc_4B37D3;
//   sub_4E1DC0(&v9);
//   return v4;
// }
// HS-1C@4BECCC
// LRESULT __fastcall sub_4BECCC(HWND hWnd, WPARAM wParam, LPARAM a3, int a4)
// {
//   LPARAM lParam[10]; // [esp+8h] [ebp-28h] BYREF

//   lParam[2] = a3;
//   lParam[5] = a4;
//   return SendMessageA(hWnd, 0x102Eu, wParam, (LPARAM)lParam);
// }
bool ransel::attach_function()
{
  BYTE sig[] = {
      XX,
      XX,
      0x68, 0x2e, 0x10, 0x00, 0x00,
      XX,
      0xe8, XX4 // SendMessageA->__imp_SendMessageA
  };
  auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = findfuncstart(addr, 0x20);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING;
  hp.offset = regoffset(esi);
  return NewHook(hp, "ransel");
}
