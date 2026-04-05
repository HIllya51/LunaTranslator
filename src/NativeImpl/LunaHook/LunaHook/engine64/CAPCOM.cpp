#include "CAPCOM.h"
/*
__int64 __fastcall sub_1402C3810(__int64 a1, __int64 a2, unsigned int a3)
{
  unsigned __int16 v3; // ax
  __int16 v6; // ax
  int v7; // ecx
  int v8; // ebp
  int v9; // ecx
  int v10; // ecx
  bool v11; // si
  bool v12; // zf
  __int64 result; // rax
  int v14; // ecx
  unsigned int v15; // ebx
  __int64 v16; // rcx
  __int64 v17; // rax
  __int64 v18; // rax
  __int64 v19; // rbx
  __int64 v20; // rax
  __int64 v21; // rax
  __int64 (__fastcall **v22)(); // [rsp+30h] [rbp-28h] BYREF
  __int128 v23; // [rsp+38h] [rbp-20h]
  __int64 v24; // [rsp+48h] [rbp-10h]

  v3 = *(_WORD *)(a1 + 1922);
  if ( v3 >= 0x80u )
    sub_140323C10(off_140AC1BB0, "偙傟埲忋僾僢僔儏偱偒傑偣傫丅\n");
  v6 = v3 + 1;
  *(_WORD *)(a1 + 1922) = v6;
  *(_DWORD *)(a1 + 4 * ((((_BYTE)v6 + (unsigned __int8)*(_WORD *)(a1 + 1920) - 1) & 0x7F) + 352i64)) = a3;
  if ( (*(_BYTE *)(a1 + 787) & 1) == 0
    && !(*(unsigned __int8 (__fastcall **)(_QWORD, __int64))(**(_QWORD **)(qword_140B89B88 + 262864) + 224i64))(
          *(_QWORD *)(qword_140B89B88 + 262864),
          a2)
    && (*(_DWORD *)(a1 + 784) & 0x8000000) == 0
    && *(float *)(*(_QWORD *)(a1 + 760) + 468i64) > 0.0
    && ((*(_DWORD *)(a1 + 784) & 0x20000000) == 0 || *(float *)(a1 + 1924) > 0.0) )
  {
    v7 = *(_DWORD *)(a1 + 864);
    v8 = -1;
    if ( v7 )
    {
      v9 = v7 - 1;
      if ( v9 )
      {
        v10 = v9 - 1;
        if ( v10 )
        {
          v11 = v10 == 1;
        }
        else
        {
          v8 = 2;
          v11 = 0;
        }
      }
      else
      {
        v8 = 1;
        v11 = (unsigned __int8)sub_140162820(qword_140B8C6B0, 0i64, 1i64) != 0;
      }
    }
    else
    {
      v8 = 0;
      v11 = (unsigned __int8)sub_140162820(qword_140B8C6B0, 0i64, 0i64) != 0;
    }
    v12 = *(_DWORD *)(qword_140B8B9F0 + 68) ? a3 == 32 : a3 == 12288;
    if ( !v12 && !v11 )
    {
      if ( *(int *)(a1 + 864) < 12 )
        sub_140164A80(qword_140B8C6B0, 0, v8, 0, 1);
      *(_DWORD *)(a1 + 784) |= 0x1000000u;
    }
  }
  result = qword_140B8B9F0;
  if ( *(_DWORD *)(qword_140B8B9F0 + 68) )
  {
    if ( a3 == 40 )
    {
      if ( *(_DWORD *)(a1 + 880) == -338152 )
        *(_DWORD *)(a1 + 784) |= 0x40000u;
    }
    else if ( a3 == 41 )
    {
      if ( *(_DWORD *)(a1 + 880) == -338152 )
        *(_DWORD *)(a1 + 784) &= ~0x40000u;
    }
    else
    {
      if ( a3 > 0x3F )
      {
        v15 = a3 - 8211;
        if ( v15 <= 0xA )
        {
          result = 1633i64;
LABEL_48:
          if ( _bittest((const int *)&result, v15) )
            return result;
        }
LABEL_49:
        v16 = *(_QWORD *)(a1 + 848);
        if ( !v16 || (result = *(unsigned int *)(a1 + 856), *(_DWORD *)(v16 + 7092) != (_DWORD)result) )
        {
          v17 = sub_1400C1990(*(_QWORD *)(qword_140B89B88 + 262864));
          v18 = sub_1402BE570(v17, *(unsigned int *)(a1 + 856));
          v24 = 0i64;
          v19 = v18;
          v23 = 0i64;
          v22 = off_14095D730;
          v20 = sub_1405C2FB0();
          sub_1405C2ED0(v20, &v22);
          v24 = v19;
          *(_QWORD *)(a1 + 848) = v19;
          v22 = off_14095D730;
          v21 = sub_1405C2FB0();
          result = sub_1405C2F40(v21, &v22);
          v16 = *(_QWORD *)(a1 + 848);
        }
        if ( v16 )
          *(_DWORD *)(v16 + 8888) &= ~0x20u;
        return result;
      }
      if ( a3 == 63 )
        return result;
    }
    switch ( a3 )
    {
      case ' ':
      case '!':
      case '(':
      case ')':
      case ',':
      case '-':
      case '.':
        return result;
      default:
        goto LABEL_49;
    }
  }
  else
  {
    if ( a3 == 65288 )
    {
      if ( *(_DWORD *)(a1 + 880) == -338152 )
        *(_DWORD *)(a1 + 784) |= 0x40000u;
      return result;
    }
    if ( a3 == 65289 )
    {
      if ( *(_DWORD *)(a1 + 880) == -338152 )
        *(_DWORD *)(a1 + 784) &= ~0x40000u;
      return result;
    }
    result = a3 - 12288;
    if ( (unsigned int)result > 0xF || (v14 = 49159, !_bittest(&v14, result)) )
    {
      result = a3 - 8220;
      if ( (unsigned int)result > 1 && a3 != 8229 )
      {
        v15 = a3 - 65281;
        if ( v15 <= 0x1E )
        {
          result = 1073742209i64;
          goto LABEL_48;
        }
        goto LABEL_49;
      }
    }
  }
  return result;
}
*/
bool CAPCOM::attach_function()
{
  char asc_1409B3A28[] = "\x82\xB1\x82\xEA\x88\xC8\x8F\xE3\x83\x76\x83\x62\x83\x56\x83\x85\x82\xC5\x82\xAB\x82\xDC\x82\xB9\x82\xF1\x81\x42\x0A";
  auto addr = MemDbg::findBytes(asc_1409B3A28, sizeof(asc_1409B3A28), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  bool succ = false;
  for (auto add : MemDbg::find_leaorpush_addr_all(addr, processStartAddress, processStopAddress))
  {
    addr = MemDbg::findEnclosingAlignedFunction(add, 0x40);
    if (!addr)
      continue;
    HookParam hp;
    hp.address = addr;
    hp.type = CODEC_UTF32 | USING_CHAR;
    hp.offset = regoffset(r8);
    succ |= NewHook(hp, "CAPCOM");
  }
  return succ;
}