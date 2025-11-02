#include "TYPEMOON.h"
/*
if ( *a4 )
  {
    v35 = &a8[v17 + 12];
    do
    {
      v20 = *v19;
      if ( *v19 == 92 )
        break;
      if ( v20 == 13 )
      {
        if ( v25 == 1 )
        {
          v27 += v30;
          v24 = a2;
        }
        else
        {
          v27 += v30 >> 1;
          v24 = a2 >> 1;
        }
        v19 += 2;
        v28 = 0;
        ++v33;
        *++v35 = 0;
        goto LABEL_64;
      }
      if ( v20 == 60 )
      {
        ++v19;
        v38 = 1;
        strstr(v19, SubStr);
        v31 = v24;
        v41 = v27;
      }
      else if ( v38 == 2 )
      {
        if ( *v19 != 62 )
        {
          if ( *(_WORD *)(v49
                        + 2 * (unsigned __int16)(HIBYTE(*(_WORD *)v19) + ((unsigned __int8)*(_WORD *)v19 << 8))
                        - 66048) != 0xFFFF )
          {
            v21 = v40;
            sub_44CB00(
              v47,
              v37,
              v31,
              v41,
              v45
            + v50
            * *(unsigned __int16 *)(v49
                                  + 2
                                  * (unsigned __int16)((unsigned __int8)HIBYTE(*(_WORD *)v19)
                                                     + ((unsigned __int8)*(_WORD *)v19 << 8))
                                  - 66048)
            * (v40
             / (int)v43),
              v40,
              v50,
              v43,
              v25,
              v39,
              v51);
            v19 += 2;
            if ( v25 != 1 )
              v21 = v40 >> 1;
            v31 += v21;
            goto LABEL_64;
          }
          v19 += 2;
          v31 += v40;
          goto LABEL_63;
        }
        ++v19;
        v38 = 0;
      }
      else
      {
        if ( v38 != 1 || *v19 != 44 )
        {
          if ( *(_WORD *)(v42
                        + 2 * (unsigned __int16)(HIBYTE(*(_WORD *)v19) + ((unsigned __int8)*(_WORD *)v19 << 8))
                        - 66048) == 0xFFFF )
          {
            v19 += 2;
            v24 += v34;
          }
          else
          {
            v22 = v34;
            sub_44CB00(
              v48,
              v37,
              v24,
              v27,
              v46
            + v30
            * *(unsigned __int16 *)(v42
                                  + 2
                                  * (unsigned __int16)((unsigned __int8)HIBYTE(*(_WORD *)v19)
                                                     + ((unsigned __int8)*(_WORD *)v19 << 8))
                                  - 66048)
            * ((int)v34
             / v44),
              v34,
              v30,
              v44,
              v25,
              v39,
              v51);
            v19 += 2;
            if ( v25 != 1 )
              v22 = v34 >> 1;
            v24 += v22;
          }
LABEL_63:
          ++*v35;
          ++a8[9];
          ++v28;
          goto LABEL_64;
        }
        ++v19;
        v38 = 2;
        strstr(v19, asc_478550);
      }
LABEL_64:
      v16 = a1;
    }
    while ( *v19 );
  }
*/

bool TYPEMOON::attach_function()
{
  // https://vndb.org/v165
  //	Melty Blood ReACT
  const uint8_t bytes[] = {
      0x8a, 0x03,
      0x3c, 0x5c,
      0x0f, 0x84, XX4,
      0x3c, 0x0d,
      0x75, XX,
      0x83, 0x7c, 0x24, 0x14, 0x01,
      0x75, XX};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING | NO_CONTEXT;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto str = (char *)context->stack[4];
    char *end, *start = str;
    while (true)
    {
      end = strchr(start, '\\');
      if (!IsShiftjisLeadByte(*(end - 1)))
        break;
      start = end + 1;
    }
    buffer->from(str, end - str);
    CharFilter(buffer, '\n');
  };
  return NewHook(hp, "typemoon");
}