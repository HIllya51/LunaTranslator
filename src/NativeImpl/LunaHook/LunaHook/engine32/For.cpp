#include "For.h"
/*
void *__cdecl sub_40D1F3(LPCSTR lpString, int a2, int a3)
{
  int v4; // esi
  void *v5; // eax
  int v6; // eax
  int v7; // esi
  int v8; // eax
  int v9; // edi
  _BYTE *v10; // esi
  int v11; // eax
  int v12; // edx
  int v13; // ebx
  _BYTE *v14; // [esp-Ch] [ebp-C0h]
  size_t v15; // [esp-4h] [ebp-B8h]
  void *v16; // [esp+Ch] [ebp-A8h]
  HGDIOBJ v17; // [esp+1Ch] [ebp-98h]
  int v18[17]; // [esp+20h] [ebp-94h]
  HDC hdc; // [esp+64h] [ebp-50h]
  char v20[24]; // [esp+68h] [ebp-4Ch] BYREF
  int j; // [esp+80h] [ebp-34h]
  void *v22; // [esp+84h] [ebp-30h]
  int i; // [esp+88h] [ebp-2Ch]
  HGDIOBJ h; // [esp+8Ch] [ebp-28h] BYREF
  void *v25; // [esp+90h] [ebp-24h]
  int v26; // [esp+94h] [ebp-20h]
  void *Src; // [esp+98h] [ebp-1Ch]
  int v28; // [esp+9Ch] [ebp-18h]
  int v29; // [esp+A0h] [ebp-14h]
  int v30; // [esp+A4h] [ebp-10h]
  int v31; // [esp+B0h] [ebp-4h]

  h = 0;
  sub_4086F0(v20);
  v31 = 0;
  v30 = 4;
  if ( dword_4485D8 && a2 )
  {
    v28 = a2;
    sub_40CF3F((int)&h, 4 * a3);
    sub_40B9D8(4 * a3, 4 * a3);
    hdc = (HDC)sub_4087E0(v20);
    v17 = SelectObject(hdc, h);
    SetBkMode(hdc, 1);
    SetTextColor(hdc, 0xFFFFFFu);
    v22 = operator new(v28 * a3 * a3);
    v25 = v22;
    v26 = unknown_libname_3(v20);
    v18[0] = 0;
    v18[1] = 0;
    v18[2] = 16;
    v18[3] = 32;
    v18[4] = 48;
    v18[5] = 64;
    v18[6] = 80;
    v18[7] = 96;
    v18[8] = 112;
    v18[9] = 128;
    v18[10] = 144;
    v18[11] = 160;
    v18[12] = 176;
    v18[13] = 192;
    v18[14] = 224;
    v18[15] = 240;
    v18[16] = 255;
    --v28;
    while ( v28 >= 0 )
    {
      if ( *(_WORD *)lpString == 28252 )
      {
        lpString += 2;
      }
      else if ( dword_4485DC && dword_4485E0 == a3 && (Src = (void *)sub_40D6B0(lpString)) != 0 )
      {
        memcpy(v25, Src, a3 * a3);
        v25 = (char *)v25 + a3 * a3;
        lpString += 2;
      }
      else
      {
        v4 = unknown_libname_3(v20);
        v15 = sub_4086C0(v20) * v4;
        v5 = (void *)sub_408680(v20);
        memset(v5, 0, v15);
        TextOutA(hdc, 0, 0, lpString, 2);
*/
bool For::attach_function()
{
  BYTE bytes[] = {
      0X8B, 0X55, 0X08,
      0X33, 0XC0,
      0X66, 0X8B, 0X02,
      0X3D, 0X5C, 0X6E, 0X00, 0X00,
      0X75, 0X0B,
      0X8B, 0X4D, 0X08,
      0X83, 0XC1, 0X02,
      0X89, 0X4D, 0X08,
      0XEB, XX};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = findfuncstart(addr, 0x200);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = FULL_STRING | USING_STRING;
  return NewHook(hp, "For");
}