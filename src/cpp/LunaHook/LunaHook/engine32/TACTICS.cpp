#include "TACTICS.h"
// 鈴がうたう日
// https://vndb.org/v8528

/*
不同的速度有不同的函数，但这几个函数核心完全一样，且都是读一个固定的全局指针
__int16 sub_40488C()
{
  UINT v0; // ebx

  if ( !word_4ABF8E )
  {
    word_4ABF8E = 1;
    word_4ABF88 = strlen(&Str) + 1;
    word_4ABF8A = 0;
    word_4ABF8C = 0;
    dword_43ACE4 = 0;
  }
LABEL_35:
  while ( word_4ABF8E < word_4ABF88 )
  {
    if ( IsDBCSLeadByteEx(0, *(&Str + word_4ABF8E)) )
    {
      v0 = (unsigned __int8)byte_4ABB89[word_4ABF8E] + ((unsigned __int8)*(&Str + word_4ABF8E) << 8);
      word_4ABF8E += 2;
    }
    else
    {
      v0 = *(&Str + word_4ABF8E++);
    }
    switch ( v0 )
    {
      case 0u:
        if ( !dword_43ACE4 )
          sub_401334(v0);
        return 3;
      case 1u:
        word_4ABF8A = word_4ABF8C;
        word_4ABF90 = word_438956 + 19 * word_4ABF8C;
        word_4ABF92 += 28;
        goto LABEL_35;
      case 2u:
        sub_4012B4(v0);
        sub_4150CC(&unk_48966C, 50);
        word_4ABF90 = word_438956;
        word_4ABF92 = 343;
        goto LABEL_35;
      case 3u:
        goto LABEL_35;
      case 4u:
        dword_43ACE4 = 1;
        goto LABEL_35;
      case 5u:
        sub_401334(v0);
        dword_43ACE4 = 1;
        goto LABEL_35;
      case 0x11u:
        strcpy(byte_4ABD88, &Str + word_4ABF8E);
        strcat(&Str, byte_4ABD88);
        word_4ABF88 = strlen(&Str) + 1;
        goto LABEL_35;
      default:
        if ( v0 == 33141 || v0 == 33156 )
          word_4ABF8C = word_4ABF8A + 1;
        if ( v0 == 33142 || v0 == 33156 )
        {
          word_4ABF8C = 0;
          dword_43ACDC = 0;
        }
        if ( v0 == 33155 )
          v0 = 33129;
        if ( v0 == 33156 )
          v0 = 33130;
        if ( word_438958 >= ++word_4ABF8A )
          goto LABEL_34;
        if ( (unsigned __int16)v0 > 0x816Au )
        {
          if ( (unsigned __int16)v0 != 33142 && (unsigned __int16)v0 != 33144 )
          {
LABEL_33:
            word_4ABF8A = word_4ABF8C + 1;
            word_4ABF90 = word_438956 + 19 * word_4ABF8C;
            word_4ABF92 += 28;
          }
        }
        else if ( (unsigned __int16)v0 != 33130
               && (unsigned __int16)v0 != 41
               && (unsigned int)(unsigned __int16)v0 - 33089 >= 2 )
        {
          goto LABEL_33;
        }
LABEL_34:
        sub_4155DC((int)&unk_4BC804, dword_47D52C, word_4ABF90, word_4ABF92, v0, 1);
        sub_4155DC((int)&unk_4BC804, dword_48967C, word_4ABF90 - 45, word_4ABF92 - 322, v0, 1);
        word_4ABF90 += 19;
        break;
    }
  }
  return 0;
}
*/
bool TACTICSattach_function1()
{
  BYTE sig[] = {
      0x0f, 0xbf, 0x05, XX4,
      0X33, 0XD2,
      0X8A, 0x98, XX4,
      0x80, 0xe3, 0xff,
      0x8a, 0x80, XX4,
      0x81, 0xe3, 0xff, 0x00, 0x00, 0x00,
      0x24, 0xff,
      0xc1, 0xe3, 0x08,
      0x8a, 0xd0,
      0x03, 0xda,
      0x66, 0x83, 0x05, XX4, 0x02,
      0xeb, 0x15,
      0x0f, 0xbf, 0x0d, XX4,
      0x0f, 0xbe, 0x99, XX4,
      0x66, 0xff, 0x05, XX4};
  auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = addr + 7 + 2 + 6 + 3 + 2;

  HookParam hp;
  hp.address = *(DWORD *)addr;
  hp.type = USING_STRING | DIRECT_READ;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    CharFilter(buffer, '\x01');
    CharFilter(buffer, '\x02');
    CharFilter(buffer, '\x03');
    CharFilter(buffer, '\x04');
    CharFilter(buffer, '\x05');
    CharFilter(buffer, '\x11');
  };
  return NewHook(hp, "TACTICS_R");
}

bool TACTICSattach_function2()
{
  BYTE sig[] = {
      0x2d, 0x40, 0x81, 0x00, 0x00,
      0x89, 0x83, XX, 0x00, 0x00, 0x00,
      0x3d, 0x57, 0x02, 0x00, 0x00,
      0x0f, 0x82, XX4,
      0xbf, 0x57, 0x02, 0x00, 0x00};
  auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_CHAR | CODEC_ANSI_BE;
  hp.offset = regoffset(eax);
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    static int idx = 0;
    if ((idx++) % 2)
      buffer->clear();
  };
  return NewHook(hp, "TACTICS_H");
}

namespace
{
  // https://vndb.org/v2274
  //[010119][Tactics] Cheerio! ～ちぇりお～ (bin+cue)
  bool h3()
  {
    /*
    if ( a5 != 33088 )
  {
    v6 = a5 - 33088;
    if ( a5 - 33088 < 0 || v6 > 597 )
    {
      v6 = 598;
      sub_417F5C(a1, a5, 598);
    }
    */
    BYTE sig[] = {
        0x3d, 0x40, 0x81, 0x00, 0x00,
        0x0f, 0x84, XX4,
        0x8b, 0xf0,
        0x81, 0xee, 0x40, 0x81, 0x00, 0x00,
        0x85, 0xf6,
        0x7c, 0x08,
        0x81, 0xfe, 0x55, 0x02, 0x00, 0x00,
        0x7e, XX,
        0xbe, 0x56, 0x02, 0x00, 0x00};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = findfuncstart(addr, 0x20); // v1.0不对齐
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_CHAR | CODEC_ANSI_BE | NO_CONTEXT;
    hp.offset = stackoffset(5);
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      static int idx = 0;
      if ((idx++) % 2)
        buffer->clear();
    };
    return NewHook(hp, "TACTICS_2");
  }
}
bool TACTICS::attach_function()
{
  return (TACTICSattach_function1() | TACTICSattach_function2()) || h3();
}