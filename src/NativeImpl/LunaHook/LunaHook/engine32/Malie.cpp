#include "Malie.h"
namespace
{ // unnamed Malie
  /********************************************************************************************
  Malie hook:
    Process name is malie.exe.
    This is the most complicate code I have made. Malie engine store text string in
    linked list. We need to insert a hook to where it travels the list. At that point
    EBX should point to a structure. We can find character at -8 and font size at +10.
    Also need to enable ITH suppress function.
  ********************************************************************************************/
  bool InsertMalieHook1()
  {
    const DWORD sig1 = 0x05e3c1;
    enum
    {
      sig1_size = 3
    };
    DWORD i = SearchPattern(processStartAddress, processStopAddress - processStartAddress, &sig1, sig1_size);
    if (!i)
    {
      return false;
    }

    const WORD sig2 = 0xc383;
    enum
    {
      sig2_size = 2
    };
    DWORD j = i + processStartAddress + sig1_size;
    i = SearchPattern(j, processStopAddress - j, &sig2, sig2_size);
    // if (!j)
    if (!i)
    { // jichi 8/19/2013: Change the condition fro J to I
      return false;
    }
    HookParam hp;
    hp.address = j + i;
    hp.offset = regoffset(ebx);
    hp.index = -0x8;
    hp.split = regoffset(ebx);
    hp.split_index = 0x10;
    hp.type = CODEC_UTF16 | USING_SPLIT | DATA_INDIRECT | SPLIT_INDIRECT;
    return NewHook(hp, "Malie");
    // RegisterEngineType(ENGINE_MALIE);
  }

  DWORD malie_furi_flag_; // jichi 8/20/2013: Make it global so that it can be reset
  void SpecialHookMalie(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    DWORD ch = context->eax & 0xffff,
          ptr = context->edi;

    if (malie_furi_flag_)
    {
      DWORD index = context->edx;
      if (*(WORD *)(ptr + index * 2 - 2) < 0xa)
        malie_furi_flag_ = 0;
    }
    else if (ch == 0xa)
    {
      malie_furi_flag_ = 1;
      // len = 0;  ??
    }
    *split = malie_furi_flag_;
    buffer->from_t<WORD>(ch);
  }

  bool InsertMalieHook2() // jichi 8/20/2013: Change return type to boolean
  {
    const BYTE bytes[] = {0x66, 0x3d, 0x1, 0x0};
    DWORD start = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!start)
    {
      return false;
    }
    BYTE *ptr = (BYTE *)start;
    while (true)
    {
      if (*(WORD *)ptr == 0x3d66)
      {
        ptr += 4;
        if (ptr[0] == 0x75)
        {
          ptr += ptr[1] + 2;
          continue;
        }
        if (*(WORD *)ptr == 0x850f)
        {
          ptr += *(DWORD *)(ptr + 2) + 6;
          continue;
        }
      }
      break;
    }
    malie_furi_flag_ = 0; // reset old malie flag
    HookParam hp;
    hp.address = (DWORD)ptr + 4;
    hp.offset = regoffset(eax);
    hp.text_fun = SpecialHookMalie;
    hp.type = USING_SPLIT | CODEC_UTF16 | NO_CONTEXT | USING_CHAR;
    return NewHook(hp, "Malie");
    // RegisterEngineType(ENGINE_MALIE);
  }

  /**
   *  jichi 12/17/2013: Added for Electro Arms
   *  Observations from Electro Arms:
   *  1. split = 0xC can handle most texts and its dwRetn is always zero
   *  2. The text containing furigana needed to split has non-zero dwRetn when split = 0
   *
   *  3/15/2015: logic modified as the plus operation would create so many threads
   */
  void SpecialHookMalie2(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    buffer->from_t((WORD)context->eax);
    // CC_UNUSED(data);
    //*len = GetHookDataLength(*hp, esp_base, (DWORD)data);

    DWORD s1 = context->stack[3], // base split, which is stable
        s2 = context->stack[0];   // used to split out furigana, but un stable
    // http://www.binaryhexconverter.com/decimal-to-binary-converter
    // enum : DWORD { mask = 0x14 };
    *split = s1 + (s2 ? 1 : 0);
  }

  //  static DWORD last_split; // FIXME: This makes the special function stateful
  //  DWORD s1 = *(DWORD *)esp_base; // current split at 0x0
  //  if (!s1)
  //    *split = last_split;
  //  else {
  //    DWORD s2 = *(DWORD *)(esp_base + 0xc); // second split
  //    *split = last_split = s1 + s2; // not sure if plus is a good way
  //  }

  /**
   *  jichi 8/20/2013: Add hook for sweet light BRAVA!!
   *  See: http://www.hongfire.com/forum/printthread.php?t=36807&pp=10&page=680
   *
   *  BRAVA!! /H code: "/HWN-4:C@1A3DF4:malie.exe"
   *  - addr: 1719796 = 0x1a3df4
   *  - text_fun: 0x0
   *  - function: 0
   *  - hook_len: 0
   *  - ind: 0
   *  - length_offset: 1
   *  - module: 751199171 = 0x2cc663c3
   *  - off: 4294967288 = 0xfffffff8L = -0x8
   *  - recover_len: 0
   *  - split: 12 = 0xc
   *  - split_ind: 0
   *  - type: 1106 = 0x452
   */
  bool InsertMalie2Hook()
  {
    // 001a3dee    6900 70000000   imul eax,dword ptr ds:[eax],70
    // 001a3df4    0200            add al,byte ptr ds:[eax]   ; this is the place to hook
    // 001a3df6    50              push eax
    // 001a3df7    0069 00         add byte ptr ds:[ecx],ch
    // 001a3dfa    0000            add byte ptr ds:[eax],al
    const BYTE bytes1[] = {
        0x40,             // inc eax
        0x89, 0x56, 0x08, // mov dword ptr ds:[esi+0x8],edx
        0x33, 0xd2,       // xor edx,edx
        0x89, 0x46, 0x04  // mov dword ptr ds:[esi+0x4],eax
    };
    ULONG range1 = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
    ULONG addr = MemDbg::findBytes(bytes1, sizeof(bytes1), processStartAddress, processStartAddress + range1);
    // reladdr = 0x1a3df4;
    if (!addr)
    {
      // ITH_MSG(0, "Wrong1", "t", 0);
      // ConsoleOutput("Not malie2 engine");
      return false;
    }

    addr += sizeof(bytes1); // skip bytes1
    // const BYTE bytes2[] = { 0x85, 0xc0 }; // test eax,eax
    const WORD bytes2 = 0xc085; // test eax,eax
    enum
    {
      range2 = 0x200
    };
    addr = MemDbg::findBytes(&bytes2, sizeof(bytes2), addr, addr + range2);
    if (!addr)
    {
      // ConsoleOutput("Not malie2 engine");
      return false;
    }

    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(eax);
    // hp.split = 0xc; // jichi 12/17/2013: Subcontext removed
    // hp.split = -0xc; // jichi 12/17/2013: This could split the furigana, but will mess up the text
    // hp.type = USING_SPLIT|CODEC_UTF16|NO_CONTEXT;
    //  jichi 12/17/2013: Need extern func for Electro Arms
    //  Though the hook parameter is quit similar to Malie, the original extern function does not work
    hp.type = USING_SPLIT | NO_CONTEXT | CODEC_UTF16 | USING_CHAR;
    hp.text_fun = SpecialHookMalie2;
    return NewHook(hp, "Malie2");

    // GROWL_DWORD2(hp.address, reladdr);
    // RegisterEngineType(ENGINE_MALIE);
  }

  // jichi 2/8/3014: Return the beginning and the end of the text
  // Remove the leading illegal characters
  enum
  {
    _MALIE3_MAX_LENGTH = VNR_TEXT_CAPACITY
  };
  LPCWSTR _Malie3LTrim(LPCWSTR p)
  {
    if (p)
      for (int count = 0; count < _MALIE3_MAX_LENGTH; count++,
               p++)
        if (p[0] == L'v' && p[1] == L'_')
        { // ex. v_akr0001, v_mzk0001
          p += 9;
          return p; // must return otherwise trimming more will break the ITH repetition elimination
        }
        else if (p[0] >= 0xa) // ltrim illegal characters less than 0xa
          return p;
    return nullptr;
  }
  // Remove the trailing illegal characters
  LPCWSTR _Malie3RTrim(LPCWSTR p)
  {
    if (p)
      for (int count = 0; count < _MALIE3_MAX_LENGTH; count++,
               p--)
        if (p[-1] >= 0xa)
        { // trim illegal characters less than 0xa
          if (p[-1] >= L'0' && p[-1] <= L'9' && p[-1 - 7] == L'_')
            p -= 9;
          else
            return p;
        }
    return nullptr;
  }

  // Example section in memory:
  // 0D7D7E00  07 00 08 00 76 00 5F 00 7A 00 65 00 70 00 30 00  v_zep0
  // 0D7D7E10  30 00 37 00 35 00 00 00 0C 30 42 30 41 30 01 30  075.「あぁ�// 0D7D7E20  41 30 26 20 26 20 07 00 09 00 07 00 06 00 07 00  ぁ…….
  // 0D7D7E30  08 00 76 00 5F 00 7A 00 65 00 70 00 30 00 30 00  v_zep00
  // 0D7D7E40  37 00 36 00 00 00 46 30 01 30 42 30 01 30 41 30  76.぀�あ、ぁ
  // 0D7D7E50  41 30 41 30 26 20 26 20 26 20 26 20 01 30 63 30  ぁぁ…………、っ
  // 0D7D7E60  07 00 09 00 0D 30 07 00 06 00 0A 00 0A 00 00 30  .�..
  // 0D7D7E70  16 60 44 30 01 30 16 60 44 30 01 30 4A 30 5E 30  怖い、怖い、お�// 0D7D7E80  7E 30 57 30 44 30 02 30 55 4F 4C 30 16 60 44 30  ましい。何が怖い
  // 0D7D7E90  6E 30 4B 30 55 30 48 30 01 30 06 52 4B 30 89 30  のかさえ、�から
  // 0D7D7EA0  6A 30 44 30 02 30 07 00 06 00 0A 00 00 30 8B 89  な぀.　�// 0D7D7EB0  8B 30 6A 30 88 30 02 30 8B 89 8B 30 6A 30 02 30  るなよ。見るな�// 0D7D7EC0  07 00 06 00 8B 89 8B 30 6A 30 01 30 8B 89 8B 30  見るな、見る
  // 0D7D7ED0  6A 30 8B 89 8B 30 6A 30 8B 89 8B 30 6A 30 01 30  な見るな見るな�// 0D7D7EE0  1F 75 4D 30 66 30 66 30 AA 60 44 30 4B 30 88 30  生きてて悪ぁ��// 0D7D7EF0  02 30 C5 60 51 30 6A 30 44 30 63 30 66 30 07 00  。情けなぁ�て
  // 0D7D7F00  01 00 E4 55 0A 00 8F 30 89 30 00 00 46 30 6A 30  嗤.わら.ぁ�
  // 0D7D7F10  88 30 02 30 07 00 06 00 BE 7C 00 4E 6F 67 6A 30  よ�精一杯な
  // 0D7D7F20  93 30 60 30 8B 89 03 90 57 30 66 30 4F 30 8C 30  んだ見送�てくれ
  // 0D7D7F30  02 30 4A 30 58 98 44 30 57 30 7E 30 59 30 01 30  。お願いします�// 0D7D7F40  60 30 4B 30 89 30 69 30 46 30 4B 30 5D 30 6E 30  �からどぁ�そ�
  // 0D7D7F50  EE 76 92 30 84 30 81 30 66 30 01 30 4F 30 60 30  目をやめて、く�
  // 0D7D7F60  55 30 44 30 01 30 5D 30 93 30 6A 30 02 30 07 00  さい、そんな�
  // 0D7D7F70  06 00 0A 00 00 30 07 00 01 00 BA 87 50 5B 0A 00  .　螺�
  // 0D7D7F80  59 30 4C 30 00 00 8B 30 88 30 46 30 6A 30 EE 76  すが.るよぁ�目
  // 0D7D7F90  67 30 00 25 00 25 07 00 06 00 BF 30 01 30 B9 30  で──タ、ス
  // 0D7D7FA0  01 30 B1 30 01 30 C6 30 01 30 6A 30 93 30 66 30  、ケ、テ、なんて
  // 0D7D7FB0  02 30 07 00 06 00 00 00 00 00 00 00 00 00 00 00  �.....
  // 0D7D7FC0  FC D8 C0 22 00 00 00 80 74 00 00 00 00 00 00 00  .耀t...
  //
  // Return the end of the line
  LPCWSTR _Malie3GetEOL(LPCWSTR p)
  {
    if (p)
      for (int count = 0; count < _MALIE3_MAX_LENGTH; count++,
               p++)
        switch (*p)
        {
        case 0:
        case 0xa: // stop at \0, or \n where the text after 0xa is furigana
          return p;
        case 0x7:
          // \x07\x00\x01\x00 is used to split furigana, which we want to keep
          // \x07\x00\x04\x00 is used to split sentences, observed in シルヴァリオ ヴェンヂ�ヂ�
          // \x07\x00\x06\x00 is used to split paragraph, observed in シルヴァリオ ヴェンヂ�ヂ�
          if (p[1] < 0xa && p[1] != 0x1)
            return p;
        }
    return nullptr;
  }

  /**
   *  jichi 3/8/2014: Add hook for 相州戦神館學�八命陣
   *  See: http://sakuradite.com/topic/157
   *  check 0x5b51ed for ecx+edx*2
   *  Also need to skip furigana.
   */

  void SpecialHookMalie3(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    // CC_UNUSED(split);
    DWORD ecx = context->ecx, // *(DWORD *)(esp_base + pusha_ecx_off - 4),
        edx = context->edx;   // *(DWORD *)(esp_base + pusha_edx_off - 4);
    //*data = ecx + edx*2; // [ecx+edx*2];
    //*len = wcslen((LPCWSTR)data) << 2;
    // There are garbage characters
    LPCWSTR start = _Malie3LTrim((LPCWSTR)(ecx + edx * 2)),
            stop = _Malie3RTrim(_Malie3GetEOL(start));

    *split = FIXED_SPLIT_VALUE;
    // GROWL_DWORD5((DWORD)start, (DWORD)stop, *len, (DWORD)*start, (DWORD)_Malie3GetEOL(start));
    buffer->from(start, max(0, stop - start) * 2);
  }

  /**
   *  jichi 8/20/2013: Add hook for 相州戦神館學�八命陣
   *  See: http://sakuradite.com/topic/157
   *  Credits: @ok123
   *
   *  Debugging method: insert hardware breakpoint into text
   *  There are four matches of text in the memory
   *
   *  Sample game: シルヴァリオ ヴェンヂ�ヂ�
   *  0065478B   90               NOP
   *  0065478C   90               NOP
   *  0065478D   90               NOP
   *  0065478E   90               NOP
   *  0065478F   90               NOP
   *  00654790   8B4424 04        MOV EAX,DWORD PTR SS:[ESP+0x4]
   *  00654794   56               PUSH ESI
   *  00654795   57               PUSH EDI
   *  00654796   8B50 08          MOV EDX,DWORD PTR DS:[EAX+0x8]
   *  00654799   8B08             MOV ECX,DWORD PTR DS:[EAX]
   *  0065479B   33F6             XOR ESI,ESI
   *  0065479D   66:8B3451        MOV SI,WORD PTR DS:[ECX+EDX*2]  ; jichi: text accessed here
   *  006547A1   42               INC EDX
   *  006547A2   8970 04          MOV DWORD PTR DS:[EAX+0x4],ESI
   *  006547A5   8950 08          MOV DWORD PTR DS:[EAX+0x8],EDX
   *  006547A8   8B50 04          MOV EDX,DWORD PTR DS:[EAX+0x4]
   *  006547AB   83FA 01          CMP EDX,0x1
   *  006547AE   75 2C            JNZ SHORT malie.006547DC
   *  006547B0   8B50 08          MOV EDX,DWORD PTR DS:[EAX+0x8]
   *  006547B3   33F6             XOR ESI,ESI
   *  006547B5   66:8B3451        MOV SI,WORD PTR DS:[ECX+EDX*2]
   *  006547B9   42               INC EDX
   *  006547BA   8970 04          MOV DWORD PTR DS:[EAX+0x4],ESI
   *  006547BD   33F6             XOR ESI,ESI
   *  006547BF   8950 08          MOV DWORD PTR DS:[EAX+0x8],EDX
   *  006547C2   66:8B3451        MOV SI,WORD PTR DS:[ECX+EDX*2]
   *  006547C6   8970 04          MOV DWORD PTR DS:[EAX+0x4],ESI
   *  006547C9   42               INC EDX
   *  006547CA   33F6             XOR ESI,ESI
   *  006547CC   8950 08          MOV DWORD PTR DS:[EAX+0x8],EDX
   *  006547CF   66:8B3451        MOV SI,WORD PTR DS:[ECX+EDX*2]
   *  006547D3   42               INC EDX
   *  006547D4   8970 04          MOV DWORD PTR DS:[EAX+0x4],ESI
   *  006547D7   8950 08          MOV DWORD PTR DS:[EAX+0x8],EDX
   *  006547DA  ^EB BF            JMP SHORT malie.0065479B
   *  006547DC   83FA 02          CMP EDX,0x2
   *  006547DF   0F84 59010000    JE malie.0065493E
   *  006547E5   83FA 03          CMP EDX,0x3
   *  006547E8   75 12            JNZ SHORT malie.006547FC
   *  006547EA   8B50 08          MOV EDX,DWORD PTR DS:[EAX+0x8]
   *  006547ED   33F6             XOR ESI,ESI
   *  006547EF   66:8B3451        MOV SI,WORD PTR DS:[ECX+EDX*2]
   *  006547F3   42               INC EDX
   *  006547F4   8970 04          MOV DWORD PTR DS:[EAX+0x4],ESI
   *  006547F7   8950 08          MOV DWORD PTR DS:[EAX+0x8],EDX
   *  006547FA  ^EB 9F            JMP SHORT malie.0065479B
   *  006547FC   83FA 04          CMP EDX,0x4
   *  006547FF   0F84 39010000    JE malie.0065493E
   *  00654805   83FA 07          CMP EDX,0x7
   *  00654808   0F85 27010000    JNZ malie.00654935
   *  0065480E   8B50 08          MOV EDX,DWORD PTR DS:[EAX+0x8]
   *  00654811   33F6             XOR ESI,ESI
   *  00654813   66:8B3451        MOV SI,WORD PTR DS:[ECX+EDX*2]
   *  00654817   8970 04          MOV DWORD PTR DS:[EAX+0x4],ESI
   *  0065481A   8D72 01          LEA ESI,DWORD PTR DS:[EDX+0x1]
   *  0065481D   8B50 04          MOV EDX,DWORD PTR DS:[EAX+0x4]
   *  00654820   8970 08          MOV DWORD PTR DS:[EAX+0x8],ESI
   *  00654823   8D7A FF          LEA EDI,DWORD PTR DS:[EDX-0x1]
   *  00654826   83FF 3B          CMP EDI,0x3B
   *  00654829  ^0F87 79FFFFFF    JA malie.006547A8
   *  0065482F   33D2             XOR EDX,EDX
   *  00654831   8A97 9C496500    MOV DL,BYTE PTR DS:[EDI+0x65499C]
   *  00654837   FF2495 80496500  JMP DWORD PTR DS:[EDX*4+0x654980]
   *  0065483E   8B50 0C          MOV EDX,DWORD PTR DS:[EAX+0xC]
   *  00654841   85D2             TEST EDX,EDX
   *  00654843   0F8F 2B010000    JG malie.00654974
   *  00654849   33D2             XOR EDX,EDX
   *  0065484B   66:8B1471        MOV DX,WORD PTR DS:[ECX+ESI*2]
   *  0065484F   46               INC ESI
   *  00654850   85D2             TEST EDX,EDX
   *  00654852   8950 04          MOV DWORD PTR DS:[EAX+0x4],EDX
   *  00654855   8970 08          MOV DWORD PTR DS:[EAX+0x8],ESI
   *  00654858   0F84 E0000000    JE malie.0065493E
   *  0065485E   8B50 08          MOV EDX,DWORD PTR DS:[EAX+0x8]
   *  00654861   33F6             XOR ESI,ESI
   *  00654863   66:8B3451        MOV SI,WORD PTR DS:[ECX+EDX*2]
   *  00654867   42               INC EDX
   *  00654868   8950 08          MOV DWORD PTR DS:[EAX+0x8],EDX
   *  0065486B   8BD6             MOV EDX,ESI
   *  0065486D   85D2             TEST EDX,EDX
   *  0065486F   8970 04          MOV DWORD PTR DS:[EAX+0x4],ESI
   *  00654872  ^75 EA            JNZ SHORT malie.0065485E
   *  00654874   8B50 08          MOV EDX,DWORD PTR DS:[EAX+0x8]
   */

  void IllegalCharsFilterW(TextBuffer *buffer, HookParam *)
  {
    CharsFilter(buffer,
                L"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0b\x0c\x0e\x0f\x10\x11\x12\x12\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f");
  }
  bool InsertMalie3Hook()
  {
    // i.e. 8b44240456578b50088b0833f6668b345142
    const BYTE bytes[] = {
        // 0x90 nop
        0x8b, 0x44, 0x24, 0x04, // 5b51e0  mov eax,dword ptr ss:[esp+0x4]   ; jichi: function starts
        0x56,                   // 5b51e4  push esi
        0x57,                   // 5b51e5  push edi
        0x8b, 0x50, 0x08,       // 5b51e6  mov edx,dword ptr ds:[eax+0x8]
        0x8b, 0x08,             // 5b51e9  mov ecx,dword ptr ds:[eax]
        0x33, 0xf6,             // 5b51eb  xor esi,esi
        0x66, 0x8b, 0x34, 0x51, // 5b51ed  mov si,word ptr ds:[ecx+edx*2] // jichi: hook here
        0x42                    // 5b51f1  inc edx
    };
    enum
    {
      addr_offset = 0x5b51ed - 0x5b51e0
    };
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
    {
      return false;
    }
    HookParam hp;
    hp.address = addr + addr_offset;
    // GROWL(hp.address);
    // hp.address = 0x5b51ed;
    // hp.address = 0x5b51f1;
    // hp.address = 0x5b51f2;
    //  jichi 3/15/2015: Remove 0704 in シルヴァリオ ヴェンッ�タ
    hp.filter_fun = IllegalCharsFilterW; // remove illegal control chars such as 0x07,0x01
    hp.text_fun = SpecialHookMalie3;
    hp.type = USING_SPLIT | NO_CONTEXT | CODEC_UTF16;
    // hp.filter_fun = Malie3Filter;
    return NewHook(hp, "Malie3");
  }

  bool InsertMalie4Hook()
  {
    // i.e. 50 8B 45 10 D9 9F ?? ?? ?? ?? 0F B7 04 58 50 51 E8 ?? ?? ?? ?? 8B 45 14 83 C4 10
    const BYTE bytes[] = {
        0x50,                   // 65904E | 50                       | push eax                                | mireado: pattern starts
        0x8B, 0x45, 0x10,       // 65904F | 8B 45 10                 | mov eax,dword ptr ss:[ebp+10]           |
        0xD9, 0x9F, XX4,        // 659052 | D9 9F E8 6B 87 00        | fstp dword ptr ds:[edi+876BE8]          |
        0x0F, 0xB7, 0x04, 0x58, // 659058 | 0F B7 04 58              | movzx eax,word ptr ds:[eax+ebx*2]       |
        0x50,                   // 65905C | 50                       | push eax                                |
        0x51,                   // 65905D | 51                       | push ecx                                |
        0xE8, XX4,              // 65905E | E8 DD 1D EA FF           | call malie.4FAE40                       | mireado: hook here
        0x8B, 0x45, 0x14,       // 659063 | 8B 45 14                 | mov eax,dword ptr ss:[ebp+14]           |
        0x83, 0xC4, 0x10        // 659066 | 83 C4 10                 | add esp,10                              |
    };
    enum
    {
      addr_offset = 0x65905E - 0x65904E
    };
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
    {
      return false;
    }

    HookParam hp;
    hp.address = addr + addr_offset;
    hp.offset = regoffset(eax); // pusha_eax_off - 4
    // hp.split = 0xc; // jichi 12/17/2013: Subcontext removed
    // hp.type = USING_SPLIT|CODEC_UTF16|NO_CONTEXT;
    //  jichi 12/17/2013: Need extern func for Electro Arms
    //  Though the hook parameter is quit similar to Malie, the original extern function does not work
    hp.split = regoffset(edx); // jichi 12/17/2013: This could split the furigana, but will mess up the text
    hp.type = USING_SPLIT | NO_CONTEXT | CODEC_UTF16;
    return NewHook(hp, "Malie4");

    // GROWL_DWORD2(hp.address, reladdr);
    // RegisterEngineType(ENGINE_MALIE);
  }

  // Artikash 1/19/2019: works on https://vndb.org/r52326
  bool InsertMalie5Hook()
  {
    const BYTE bytes[] = {
        0x8b, 0x49, 0x10, // mov ecx,[ecx+10]
        0x03, 0x08,       // add ecx,[eax]
        0x51              // push ecx
    };

    if (DWORD addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress))
    {
      HookParam hp;
      hp.address = addr + 5;
      hp.offset = regoffset(ecx);
      hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
      return NewHook(hp, "Malie5");
    }

    return false;
  }

  // jichi 3/12/2015: Return guessed Malie engine year
  // int GetMalieYear()
  //{
  //  if (Util::SearchResourceString(L"2013 light"))
  //    return 2013;
  //  if (Util::SearchResourceString(L"2014 light"))
  //    return 2014;
  //  return 2015;
  //}

} // unnamed Malie

bool InsertMalieHook()
{
  if (Util::CheckFile(L"tools.dll"))
    return InsertMalieHook1(); // jichi 3/5/2015: For old light games such as Dies irae.

  else
  { // For old Malie games before 2015
    // jichi 8/20/2013: Add hook for sweet light engine
    // Insert both malie and malie2 hook.
    bool ok = false;

    // jichi 3/12/2015: Disable MalieHook2 which will crash シルヴァリオ ヴェンッ�タ
    // if (!Util::CheckFile(L"gdiplus.dll"))
    if (Util::CheckFile(L"System\\*"))
    { // Insert old Malie hook. There are usually System/cursor.cur
      ok = InsertMalieHook2() || ok;
      ok = InsertMalie2Hook() || ok; // jichi 8/20/2013
    }

    // The main disadvantage of Malie3 is that it cannot find character name
    ok = InsertMalie3Hook() || ok; // jichi 3/7/2014
    ok = InsertMalie4Hook() || ok;
    ok = InsertMalie5Hook() || ok;
    return ok;
  }
}

namespace
{ // unnamed
  namespace ScenarioHook
  {
    namespace Private
    {

      /**
       *  Sample game: シルヴァリオ ヴェンデッタ
       *
       *  0706: long pause, text separator
       *  0704: short pause
       *  0708: voice start.
       *  0701: ruby start, 0a as separator
       *
       *  Sample plain unvoiced text:
       *
       *  0706 is used as pause char.
       *
       *  01FFF184  00 30 2A 8A 8C 30 8B 30 21 6B 6E 30 27 59 75 65  　訪れる次の大敵
       *  01FFF194  00 25 00 25 21 6B 6E 30 0D 4E 78 5E 02 30 21 6B  ──次の不幸。次
       *  01FFF1A4  6E 30 E6 82 E3 96 02 30 21 6B 6E 30 34 78 C5 6E  の苦難。次の破滅
       *  01FFF1B4  02 30 07 00 06 00 0A 00 00 30 B4 63 7F 30 D6 53  。.　掴み取
       *  01FFF1C4  63 30 5F 30 6F 30 5A 30 6E 30 2A 67 65 67 6F 30  ったはずの未来は
       *  01FFF1D4  97 66 D2 9E 6B 30 55 87 7E 30 8C 30 5F 30 7E 30  暗黒に蝕まれたま
       *  01FFF1E4  7E 30 9A 7D 4C 88 57 30 66 30 44 30 4F 30 02 30  ま続行していく。
       *  01FFF1F4  07 00 06 00 0A 00 00 30 80 30 57 30 8D 30 4B 62  .　むしろ手
       *  01FFF204  6B 30 57 30 5F 30 47 59 E1 8D 92 30 7C 54 73 30  にした奇跡を呼び
       *  01FFF214  34 6C 6B 30 01 30 88 30 8A 30 4A 30 5E 30 7E 30  水に、よりおぞま
       *  01FFF224  57 30 44 30 B0 65 5F 30 6A 30 66 8A F4 7D 92 30  しい新たな試練を
       *  01FFF234  44 7D 7F 30 BC 8F 93 30 67 30 4B 90 7D 54 92 30  組み込んで運命を
       *  01FFF244  C6 99 D5 52 55 30 5B 30 8B 30 6E 30 60 30 02 30  駆動させるのだ。
       *  01FFF254  07 00 06 00 00 00 00 00 00 00 00 00 00 00 00 00  ......
       *  01FFF264  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ........
       *  01FFF274  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ........
       *  01FFF284  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ........
       *  01FFF294  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ........
       *  01FFF2A4  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ........
       *
       *  Mixed unvoiced text and voiced text list:
       *  01FFF184  00 30 1C 20 DD 52 29 52 1D 20 4B 30 89 30 6F 30  　“勝利”からは
       *  01FFF194  03 90 52 30 89 30 8C 30 6A 30 44 30 02 30 07 00  逃げられない。
       *  01FFF1A4  06 00 0A 00 00 30 1C 20 DD 52 29 52 1D 20 4B 30  .　“勝利”か
       *  01FFF1B4  89 30 6F 30 03 90 52 30 89 30 8C 30 6A 30 44 30  らは逃げられない
       *  01FFF1C4  02 30 07 00 06 00 0A 00 00 30 1C 20 DD 52 29 52  。.　“勝利
       *  01FFF1D4  1D 20 4B 30 89 30 6F 30 03 90 52 30 89 30 8C 30  ”からは逃げられ
       *  01FFF1E4  6A 30 44 30 02 30 07 00 06 00 0A 00 0A 00 07 00  ない。..
       *  01FFF1F4  08 00 76 00 5F 00 76 00 6E 00 64 00 30 00 30 00  v_vnd00
       *  01FFF204  30 00 31 00 00 00 0C 30 6A 30 89 30 70 30 00 25  01.「ならば─
       *  01FFF214  00 25 00 25 00 25 0D 30 07 00 09 00 07 00 06 00  ───」.
       *  01FFF224  0A 00 0A 00 00 30 00 25 00 25 55 30 42 30 01 30  ..　──さあ、
       *  01FFF234  69 30 46 30 59 30 8B 30 4B 30 1F FF 07 00 06 00  どうするか？
       *  01FFF244  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ........
       *  01FFF254  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ........
       *  01FFF264  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ........
       *
       *  Sample voiced text:
       *
       *  0269F184  07 00 08 00 76 00 5F 00 7A 00 65 00 70 00 30 00  v_zep0
       *  0269F194  30 00 30 00 31 00 00 00 1C 20 DD 52 29 52 1D 20  001.“勝利”
       *  0269F1A4  68 30 6F 30 01 30 55 4F 60 30 1F FF 07 00 09 00  とは、何だ？.
       *  0269F1B4  07 00 06 00 0A 00 0A 00 07 00 08 00 76 00 5F 00  ..v_
       *  0269F1C4  7A 00 65 00 70 00 30 00 30 00 30 00 32 00 00 00  zep0002.
       *  0269F1D4  1C 20 04 68 49 51 1D 20 68 30 6F 30 01 30 55 4F  “栄光”とは、何
       *  0269F1E4  60 30 1F FF 07 00 09 00 07 00 06 00 0A 00 0A 00  だ？...
       *  0269F1F4  07 00 08 00 76 00 5F 00 7A 00 65 00 70 00 30 00  v_zep0
       *  0269F204  30 00 30 00 33 00 00 00 5D 30 8C 30 92 30 97 5F  003.それを得
       *  0269F214  8C 30 70 30 01 30 55 4F 82 30 31 59 8F 30 5A 30  れば、何も失わず
       *  0269F224  6B 30 08 6E 80 30 6E 30 60 30 8D 30 46 30 4B 30  に済むのだろうか
       *  0269F234  07 00 09 00 07 00 06 00 0A 00 0A 00 07 00 08 00  ...
       *  0269F244  76 00 5F 00 7A 00 65 00 70 00 30 00 30 00 30 00  v_zep000
       *  0269F254  34 00 00 00 51 65 48 30 8B 30 6E 30 4B 30 02 30  4.救えるのか。
       *  0269F264  88 5B 8C 30 8B 30 6E 30 4B 30 02 30 2C 67 53 5F  守れるのか。本当
       *  0269F274  6B 30 01 30 78 5E 5B 30 6B 30 6A 30 8C 30 8B 30  に、幸せになれる
       *  0269F284  6E 30 60 30 8D 30 46 30 4B 30 07 00 09 00 07 00  のだろうか.
       *  0269F294  06 00 00 00 00 00 00 00 D1 01 00 00 8C F3 69 02  ...Ǒ.ɩ
       *
       *  Ruby:
       *
       *  01FDF2B4  63 30 5F 30 07 00 01 00 14 90 EF 7A 0A 00 68 30  った途端.と
       *  01FDF2C4  5F 30 93 30 00 00 01 30 06 90 6B 30 40 62 09 67  たん.、逆に所有
       *
       *  Pause without 0a:
       *
       *  0271F184  07 00 08 00 76 00 5F 00 7A 00 65 00 70 00 30 00  v_zep0
       *  0271F194  30 00 34 00 34 00 00 00 00 30 51 30 8C 30 69 30  044.　けれど
       *  0271F1A4  00 25 00 25 07 00 09 00 07 00 06 00 07 00 08 00  ──.
       *  0271F1B4  76 00 5F 00 7A 00 65 00 70 00 30 00 30 00 34 00  v_zep004
       *  0271F1C4  35 00 00 00 5D 30 8C 30 67 30 82 30 01 30 88 5B  5.それでも、守
       *  0271F1D4  89 30 6A 30 51 30 8C 30 70 30 6A 30 89 30 6A 30  らなければならな
       *  0271F1E4  44 30 50 5B 4C 30 FA 51 65 67 5F 30 4B 30 89 30  い子が出来たから
       *  0271F1F4  02 30 07 00 09 00 07 00 06 00 07 00 04 00 00 30  。.　
       *  0271F204  07 00 08 00 76 00 5F 00 7A 00 65 00 70 00 30 00  v_zep0
       *  0271F214  30 00 34 00 36 00 00 00 7C 5F 73 59 92 30 51 65  046.彼女を救
       *  0271F224  46 30 5F 30 81 30 6B 30 01 30 53 30 6E 30 61 30  うために、このち
       *  0271F234  63 30 7D 30 51 30 6A 30 7D 54 92 30 F8 61 51 30  っぽけな命を懸け
       *  0271F244  8B 30 68 30 93 8A 63 30 5F 30 02 30 86 30 48 30  ると誓った。ゆえ
       *
       *  Scenario caller: 4637bf
       *
       *  0046377D   90               NOP
       *  0046377E   90               NOP
       *  0046377F   90               NOP
       *  00463780   81EC 00080000    SUB ESP,0x800
       *  00463786   56               PUSH ESI
       *  00463787   8BB424 08080000  MOV ESI,DWORD PTR SS:[ESP+0x808]
       *  0046378E   8B46 1C          MOV EAX,DWORD PTR DS:[ESI+0x1C]
       *  00463791   8B88 68020000    MOV ECX,DWORD PTR DS:[EAX+0x268]
       *  00463797   57               PUSH EDI
       *  00463798   51               PUSH ECX
       *  00463799   E8 D200FFFF      CALL malie.00453870
       *  0046379E   8BBC24 14080000  MOV EDI,DWORD PTR SS:[ESP+0x814]
       *  004637A5   68 C06C4100      PUSH malie.00416CC0
       *  004637AA   8D5424 10        LEA EDX,DWORD PTR SS:[ESP+0x10]
       *  004637AE   57               PUSH EDI
       *  004637AF   52               PUSH EDX
       *  004637B0   E8 AB041F00      CALL malie.00653C60
       *  004637B5   8D4424 18        LEA EAX,DWORD PTR SS:[ESP+0x18]
       *  004637B9   50               PUSH EAX
       *  004637BA   E8 21031F00      CALL malie.00653AE0   ; jichi: scenario caller
       *  004637BF   8B4E 1C          MOV ECX,DWORD PTR DS:[ESI+0x1C]
       *  004637C2   57               PUSH EDI
       *  004637C3   8981 68020000    MOV DWORD PTR DS:[ECX+0x268],EAX
       *  004637C9   E8 32E61E00      CALL malie.00651E00
       *  004637CE   83C4 18          ADD ESP,0x18
       *  004637D1   33D2             XOR EDX,EDX
       *  004637D3   85C0             TEST EAX,EAX
       *  004637D5   8B46 1C          MOV EAX,DWORD PTR DS:[ESI+0x1C]
       *  004637D8   0F9FC2           SETG DL
       *  004637DB   5F               POP EDI
       *  004637DC   5E               POP ESI
       *  004637DD   8990 7C020000    MOV DWORD PTR DS:[EAX+0x27C],EDX
       *  004637E3   81C4 00080000    ADD ESP,0x800
       *  004637E9   C3               RETN
       *  004637EA   90               NOP
       *  004637EB   90               NOP
       *  004637EC   90               NOP
       *
       *  Name caller: 46382e
       *
       * 004637EB   90               NOP
       * 004637EC   90               NOP
       * 004637ED   90               NOP
       * 004637EE   90               NOP
       * 004637EF   90               NOP
       * 004637F0   81EC 00080000    SUB ESP,0x800
       * 004637F6   56               PUSH ESI
       * 004637F7   8BB424 08080000  MOV ESI,DWORD PTR SS:[ESP+0x808]
       * 004637FE   8B46 1C          MOV EAX,DWORD PTR DS:[ESI+0x1C]
       * 00463801   8B88 6C020000    MOV ECX,DWORD PTR DS:[EAX+0x26C]
       * 00463807   51               PUSH ECX
       * 00463808   E8 6300FFFF      CALL malie.00453870
       * 0046380D   8B9424 10080000  MOV EDX,DWORD PTR SS:[ESP+0x810]
       * 00463814   68 C06C4100      PUSH malie.00416CC0
       * 00463819   52               PUSH EDX
       * 0046381A   8D4424 10        LEA EAX,DWORD PTR SS:[ESP+0x10]
       * 0046381E   50               PUSH EAX
       * 0046381F   E8 3C041F00      CALL malie.00653C60
       * 00463824   8D4C24 14        LEA ECX,DWORD PTR SS:[ESP+0x14]
       * 00463828   51               PUSH ECX
       * 00463829   E8 B2021F00      CALL malie.00653AE0 ; jichi: name
       * 0046382E   8B56 1C          MOV EDX,DWORD PTR DS:[ESI+0x1C]
       * 00463831   83C4 14          ADD ESP,0x14
       * 00463834   8982 6C020000    MOV DWORD PTR DS:[EDX+0x26C],EAX
       * 0046383A   5E               POP ESI
       * 0046383B   81C4 00080000    ADD ESP,0x800
       * 00463841   C3               RETN
       * 00463842   90               NOP
       * 00463843   90               NOP
       * 00463844   90               NOP
       *
       *  History caller: 418d0b
       *
       *  00418C9D   90               NOP
       *  00418C9E   90               NOP
       *  00418C9F   90               NOP
       *  00418CA0   81EC 00080000    SUB ESP,0x800
       *  00418CA6   53               PUSH EBX
       *  00418CA7   56               PUSH ESI
       *  00418CA8   57               PUSH EDI
       *  00418CA9   6A 6C            PUSH 0x6C
       *  00418CAB   FF15 20256900    CALL DWORD PTR DS:[<&MSVCRT.malloc>]     ; msvcrt.malloc
       *  00418CB1   8BD8             MOV EBX,EAX
       *  00418CB3   83C4 04          ADD ESP,0x4
       *  00418CB6   85DB             TEST EBX,EBX
       *  00418CB8   0F84 D1000000    JE malie.00418D8F
       *  00418CBE   8BB424 10080000  MOV ESI,DWORD PTR SS:[ESP+0x810]
       *  00418CC5   33C0             XOR EAX,EAX
       *  00418CC7   B9 1B000000      MOV ECX,0x1B
       *  00418CCC   8BFB             MOV EDI,EBX
       *  00418CCE   F3:AB            REP STOS DWORD PTR ES:[EDI]
       *  00418CD0   8B06             MOV EAX,DWORD PTR DS:[ESI]
       *  00418CD2   68 C06C4100      PUSH malie.00416CC0
       *  00418CD7   50               PUSH EAX
       *  00418CD8   8D4C24 14        LEA ECX,DWORD PTR SS:[ESP+0x14]
       *  00418CDC   51               PUSH ECX
       *  00418CDD   E8 7EAF2300      CALL malie.00653C60
       *  00418CE2   8D5424 18        LEA EDX,DWORD PTR SS:[ESP+0x18]
       *  00418CE6   52               PUSH EDX
       *  00418CE7   E8 F4AD2300      CALL malie.00653AE0
       *  00418CEC   8903             MOV DWORD PTR DS:[EBX],EAX
       *  00418CEE   8B46 04          MOV EAX,DWORD PTR DS:[ESI+0x4]
       *  00418CF1   68 C06C4100      PUSH malie.00416CC0
       *  00418CF6   50               PUSH EAX
       *  00418CF7   8D4C24 24        LEA ECX,DWORD PTR SS:[ESP+0x24]
       *  00418CFB   51               PUSH ECX
       *  00418CFC   E8 5FAF2300      CALL malie.00653C60
       *  00418D01   8D5424 28        LEA EDX,DWORD PTR SS:[ESP+0x28]
       *  00418D05   52               PUSH EDX
       *  00418D06   E8 D5AD2300      CALL malie.00653AE0 ; jichi: history caller
       *  00418D0B   8943 04          MOV DWORD PTR DS:[EBX+0x4],EAX
       *  00418D0E   8B46 08          MOV EAX,DWORD PTR DS:[ESI+0x8]
       *  00418D11   83C4 20          ADD ESP,0x20
       *  00418D14   85C0             TEST EAX,EAX
       *  00418D16   75 05            JNZ SHORT malie.00418D1D
       *  00418D18   B8 0CEF7000      MOV EAX,malie.0070EF0C
       *  00418D1D   50               PUSH EAX
       *  00418D1E   E8 3D6F2300      CALL malie.0064FC60
       *  00418D23   8943 08          MOV DWORD PTR DS:[EBX+0x8],EAX
       *  00418D26   8B46 0C          MOV EAX,DWORD PTR DS:[ESI+0xC]
       *  00418D29   83C4 04          ADD ESP,0x4
       *  00418D2C   85C0             TEST EAX,EAX
       *  00418D2E   75 05            JNZ SHORT malie.00418D35
       *  00418D30   B8 0CEF7000      MOV EAX,malie.0070EF0C
       *  00418D35   50               PUSH EAX
       *  00418D36   E8 256F2300      CALL malie.0064FC60
       *  00418D3B   8943 0C          MOV DWORD PTR DS:[EBX+0xC],EAX
       *  00418D3E   8B46 60          MOV EAX,DWORD PTR DS:[ESI+0x60]
       *  00418D41   8943 60          MOV DWORD PTR DS:[EBX+0x60],EAX
       *  00418D44   8B4E 64          MOV ECX,DWORD PTR DS:[ESI+0x64]
       *  00418D47   894B 64          MOV DWORD PTR DS:[EBX+0x64],ECX
       *  00418D4A   8B56 68          MOV EDX,DWORD PTR DS:[ESI+0x68]
       *  00418D4D   8D7E 10          LEA EDI,DWORD PTR DS:[ESI+0x10]
       *  00418D50   83C4 04          ADD ESP,0x4
       *  00418D53   85FF             TEST EDI,EDI
       *  00418D55   8953 68          MOV DWORD PTR DS:[EBX+0x68],EDX
       *  00418D58   74 35            JE SHORT malie.00418D8F
       *  00418D5A   55               PUSH EBP
       *  00418D5B   8BEB             MOV EBP,EBX
       *  00418D5D   2BEE             SUB EBP,ESI
       *  00418D5F   BE 14000000      MOV ESI,0x14
       *  00418D64   8B07             MOV EAX,DWORD PTR DS:[EDI]
       *  00418D66   66:8338 00       CMP WORD PTR DS:[EAX],0x0
       *  00418D6A   75 04            JNZ SHORT malie.00418D70
       *  00418D6C   33C0             XOR EAX,EAX
       *  00418D6E   EB 09            JMP SHORT malie.00418D79
       *  00418D70   50               PUSH EAX
       *  00418D71   E8 EA6E2300      CALL malie.0064FC60
       *  00418D76   83C4 04          ADD ESP,0x4
       *  00418D79   89042F           MOV DWORD PTR DS:[EDI+EBP],EAX
       *  00418D7C   83C7 04          ADD EDI,0x4
       *  00418D7F   4E               DEC ESI
       *  00418D80  ^75 E2            JNZ SHORT malie.00418D64
       *  00418D82   5D               POP EBP
       *  00418D83   5F               POP EDI
       *  00418D84   5E               POP ESI
       *  00418D85   8BC3             MOV EAX,EBX
       *  00418D87   5B               POP EBX
       *  00418D88   81C4 00080000    ADD ESP,0x800
       *  00418D8E   C3               RETN
       *  00418D8F   5F               POP EDI
       *  00418D90   5E               POP ESI
       *  00418D91   8BC3             MOV EAX,EBX
       *  00418D93   5B               POP EBX
       *  00418D94   81C4 00080000    ADD ESP,0x800
       *  00418D9A   C3               RETN
       *  00418D9B   90               NOP
       *  00418D9C   90               NOP
       *
       *  Exit dialog box caller:
       *  00475A8D   90               NOP
       *  00475A8E   90               NOP
       *  00475A8F   90               NOP
       *  00475A90   56               PUSH ESI
       *  00475A91   68 B09C7500      PUSH malie.00759CB0
       *  00475A96   FF15 F8206900    CALL DWORD PTR DS:[<&KERNEL32.EnterCriti>; ntdll.RtlEnterCriticalSection
       *  00475A9C   8B7424 08        MOV ESI,DWORD PTR SS:[ESP+0x8]
       *  00475AA0   85F6             TEST ESI,ESI
       *  00475AA2   74 4A            JE SHORT malie.00475AEE
       *  00475AA4   56               PUSH ESI
       *  00475AA5   E8 56000000      CALL malie.00475B00
       *  00475AAA   8B46 1C          MOV EAX,DWORD PTR DS:[ESI+0x1C]
       *  00475AAD   8B08             MOV ECX,DWORD PTR DS:[EAX]
       *  00475AAF   51               PUSH ECX
       *  00475AB0   E8 BBDDFDFF      CALL malie.00453870
       *  00475AB5   8B5424 14        MOV EDX,DWORD PTR SS:[ESP+0x14]
       *  00475AB9   52               PUSH EDX
       *  00475ABA   E8 21E01D00      CALL malie.00653AE0 ; jichi: called here
       *  00475ABF   8B4E 1C          MOV ECX,DWORD PTR DS:[ESI+0x1C]
       *  00475AC2   8901             MOV DWORD PTR DS:[ECX],EAX
       *  00475AC4   8B56 1C          MOV EDX,DWORD PTR DS:[ESI+0x1C]
       *  00475AC7   C782 94000000 00>MOV DWORD PTR DS:[EDX+0x94],0x0
       *  00475AD1   8B46 1C          MOV EAX,DWORD PTR DS:[ESI+0x1C]
       *  00475AD4   8B08             MOV ECX,DWORD PTR DS:[EAX]
       *  00475AD6   51               PUSH ECX
       *  00475AD7   E8 84C41D00      CALL malie.00651F60
       *  00475ADC   8B56 1C          MOV EDX,DWORD PTR DS:[ESI+0x1C]
       *  00475ADF   56               PUSH ESI
       *  00475AE0   8982 98000000    MOV DWORD PTR DS:[EDX+0x98],EAX
       *  00475AE6   E8 C5000000      CALL malie.00475BB0
       *  00475AEB   83C4 14          ADD ESP,0x14
       *  00475AEE   68 B09C7500      PUSH malie.00759CB0
       *  00475AF3   FF15 44226900    CALL DWORD PTR DS:[<&KERNEL32.LeaveCriti>; ntdll.RtlLeaveCriticalSection
       *  00475AF9   5E               POP ESI
       *  00475AFA   C3               RETN
       *  00475AFB   90               NOP
       *  00475AFC   90               NOP
       *  00475AFD   90               NOP
       *
       *  Sample game: 相州戦神館學園 八命陣 (older game0
       *  Scenario caller: 46314f
       *
       *  0046310B   90               NOP
       *  0046310C   90               NOP
       *  0046310D   90               NOP
       *  0046310E   90               NOP
       *  0046310F   90               NOP
       *  00463110   81EC 00080000    SUB ESP,0x800
       *  00463116   56               PUSH ESI
       *  00463117   8BB424 08080000  MOV ESI,DWORD PTR SS:[ESP+0x808]
       *  0046311E   8B46 20          MOV EAX,DWORD PTR DS:[ESI+0x20]
       *  00463121   8B88 68020000    MOV ECX,DWORD PTR DS:[EAX+0x268]
       *  00463127   57               PUSH EDI
       *  00463128   51               PUSH ECX
       *  00463129   E8 62240200      CALL .00485590
       *  0046312E   8BBC24 14080000  MOV EDI,DWORD PTR SS:[ESP+0x814]
       *  00463135   68 10634100      PUSH .00416310
       *  0046313A   8D5424 10        LEA EDX,DWORD PTR SS:[ESP+0x10]
       *  0046313E   57               PUSH EDI
       *  0046313F   52               PUSH EDX
       *  00463140   E8 AB841D00      CALL .0063B5F0
       *  00463145   8D4424 18        LEA EAX,DWORD PTR SS:[ESP+0x18]
       *  00463149   50               PUSH EAX
       *  0046314A   E8 41831D00      CALL .0063B490
       *  0046314F   8B4E 20          MOV ECX,DWORD PTR DS:[ESI+0x20] ; jichi: scenario retaddr
       *  00463152   57               PUSH EDI
       *  00463153   8981 68020000    MOV DWORD PTR DS:[ECX+0x268],EAX
       *  00463159   E8 82661D00      CALL .006397E0
       *  0046315E   83C4 18          ADD ESP,0x18
       *  00463161   33D2             XOR EDX,EDX
       *  00463163   85C0             TEST EAX,EAX
       *  00463165   8B46 20          MOV EAX,DWORD PTR DS:[ESI+0x20]
       *  00463168   0F9FC2           SETG DL
       *  0046316B   5F               POP EDI
       *  0046316C   5E               POP ESI
       *  0046316D   8990 7C020000    MOV DWORD PTR DS:[EAX+0x27C],EDX
       *  00463173   81C4 00080000    ADD ESP,0x800
       *  00463179   C3               RETN
       *  0046317A   90               NOP
       *  0046317B   90               NOP
       *  0046317C   90               NOP
       *  0046317D   90               NOP
       *  0046317E   90               NOP
       *
       *  Sample game: BRAVA!!
       *  Scenario retaddr: 42011f
       *
       *  004200FD   90               NOP
       *  004200FE   90               NOP
       *  004200FF   90               NOP
       *  00420100   56               PUSH ESI
       *  00420101   8B7424 08        MOV ESI,DWORD PTR SS:[ESP+0x8]
       *  00420105   8B46 20          MOV EAX,DWORD PTR DS:[ESI+0x20]
       *  00420108   8B88 F0000000    MOV ECX,DWORD PTR DS:[EAX+0xF0]
       *  0042010E   57               PUSH EDI
       *  0042010F   51               PUSH ECX
       *  00420110   E8 BB240200      CALL .004425D0
       *  00420115   8B7C24 14        MOV EDI,DWORD PTR SS:[ESP+0x14]
       *  00420119   57               PUSH EDI
       *  0042011A   E8 01031300      CALL .00550420
       *  0042011F   8B56 20          MOV EDX,DWORD PTR DS:[ESI+0x20]   ; jichi: scenario caller
       *  00420122   57               PUSH EDI
       *  00420123   8982 F0000000    MOV DWORD PTR DS:[EDX+0xF0],EAX
       *  00420129   E8 B2E61200      CALL .0054E7E0
       *  0042012E   8B56 20          MOV EDX,DWORD PTR DS:[ESI+0x20]
       *  00420131   83C4 0C          ADD ESP,0xC
       *  00420134   33C9             XOR ECX,ECX
       *  00420136   85C0             TEST EAX,EAX
       *  00420138   0F9FC1           SETG CL
       *  0042013B   5F               POP EDI
       *  0042013C   5E               POP ESI
       *  0042013D   898A FC000000    MOV DWORD PTR DS:[EDX+0xFC],ECX
       *  00420143   C3               RETN
       *  00420144   90               NOP
       *
       *  Name retaddr: 415a2c
       *
       *  004159DD   90               NOP
       *  004159DE   90               NOP
       *  004159DF   90               NOP
       *  004159E0   81EC 00080000    SUB ESP,0x800
       *  004159E6   53               PUSH EBX
       *  004159E7   56               PUSH ESI
       *  004159E8   57               PUSH EDI
       *  004159E9   6A 6C            PUSH 0x6C
       *  004159EB   FF15 40D45800    CALL DWORD PTR DS:[0x58D440]             ; msvcrt.malloc
       *  004159F1   8BD8             MOV EBX,EAX
       *  004159F3   83C4 04          ADD ESP,0x4
       *  004159F6   85DB             TEST EBX,EBX
       *  004159F8   0F84 D1000000    JE .00415ACF
       *  004159FE   8BB424 10080000  MOV ESI,DWORD PTR SS:[ESP+0x810]
       *  00415A05   33C0             XOR EAX,EAX
       *  00415A07   B9 1B000000      MOV ECX,0x1B
       *  00415A0C   8BFB             MOV EDI,EBX
       *  00415A0E   F3:AB            REP STOS DWORD PTR ES:[EDI]
       *  00415A10   8B06             MOV EAX,DWORD PTR DS:[ESI]
       *  00415A12   68 003B4100      PUSH .00413B00
       *  00415A17   50               PUSH EAX
       *  00415A18   8D4C24 14        LEA ECX,DWORD PTR SS:[ESP+0x14]
       *  00415A1C   51               PUSH ECX
       *  00415A1D   E8 5EAB1300      CALL .00550580
       *  00415A22   8D5424 18        LEA EDX,DWORD PTR SS:[ESP+0x18]
       *  00415A26   52               PUSH EDX
       *  00415A27   E8 F4A91300      CALL .00550420
       *  00415A2C   8903             MOV DWORD PTR DS:[EBX],EAX  ; jichi: name caller
       *  00415A2E   8B46 04          MOV EAX,DWORD PTR DS:[ESI+0x4]
       *  00415A31   68 003B4100      PUSH .00413B00
       *  00415A36   50               PUSH EAX
       *  00415A37   8D4C24 24        LEA ECX,DWORD PTR SS:[ESP+0x24]
       *  00415A3B   51               PUSH ECX
       *  00415A3C   E8 3FAB1300      CALL .00550580
       *  00415A41   8D5424 28        LEA EDX,DWORD PTR SS:[ESP+0x28]
       *  00415A45   52               PUSH EDX
       *  00415A46   E8 D5A91300      CALL .00550420
       *  00415A4B   8943 04          MOV DWORD PTR DS:[EBX+0x4],EAX
       *  00415A4E   8B46 08          MOV EAX,DWORD PTR DS:[ESI+0x8]
       *  00415A51   83C4 20          ADD ESP,0x20
       *  00415A54   85C0             TEST EAX,EAX
       *  00415A56   75 05            JNZ SHORT .00415A5D
       *  00415A58   B8 6C285E00      MOV EAX,.005E286C
       *  00415A5D   50               PUSH EAX
       *  00415A5E   E8 DD691300      CALL .0054C440
       *  00415A63   8943 08          MOV DWORD PTR DS:[EBX+0x8],EAX
       *  00415A66   8B46 0C          MOV EAX,DWORD PTR DS:[ESI+0xC]
       *  00415A69   83C4 04          ADD ESP,0x4
       *  00415A6C   85C0             TEST EAX,EAX
       *  00415A6E   75 05            JNZ SHORT .00415A75
       *  00415A70   B8 6C285E00      MOV EAX,.005E286C
       *  00415A75   50               PUSH EAX
       *  00415A76   E8 C5691300      CALL .0054C440
       *  00415A7B   8943 0C          MOV DWORD PTR DS:[EBX+0xC],EAX
       *  00415A7E   8B46 60          MOV EAX,DWORD PTR DS:[ESI+0x60]
       *  00415A81   8943 60          MOV DWORD PTR DS:[EBX+0x60],EAX
       *  00415A84   8B4E 64          MOV ECX,DWORD PTR DS:[ESI+0x64]
       *  00415A87   894B 64          MOV DWORD PTR DS:[EBX+0x64],ECX
       *  00415A8A   8B56 68          MOV EDX,DWORD PTR DS:[ESI+0x68]
       *  00415A8D   8D7E 10          LEA EDI,DWORD PTR DS:[ESI+0x10]
       *  00415A90   83C4 04          ADD ESP,0x4
       *  00415A93   85FF             TEST EDI,EDI
       *  00415A95   8953 68          MOV DWORD PTR DS:[EBX+0x68],EDX
       *  00415A98   74 35            JE SHORT .00415ACF
       *  00415A9A   55               PUSH EBP
       *  00415A9B   8BEB             MOV EBP,EBX
       *  00415A9D   2BEE             SUB EBP,ESI
       *  00415A9F   BE 14000000      MOV ESI,0x14
       *  00415AA4   8B07             MOV EAX,DWORD PTR DS:[EDI]
       *  00415AA6   66:8338 00       CMP WORD PTR DS:[EAX],0x0
       *  00415AAA   75 04            JNZ SHORT .00415AB0
       *  00415AAC   33C0             XOR EAX,EAX
       *  00415AAE   EB 09            JMP SHORT .00415AB9
       *  00415AB0   50               PUSH EAX
       *  00415AB1   E8 8A691300      CALL .0054C440
       *  00415AB6   83C4 04          ADD ESP,0x4
       *  00415AB9   89042F           MOV DWORD PTR DS:[EDI+EBP],EAX
       *  00415ABC   83C7 04          ADD EDI,0x4
       *  00415ABF   4E               DEC ESI
       *  00415AC0  ^75 E2            JNZ SHORT .00415AA4
       *  00415AC2   5D               POP EBP
       *  00415AC3   5F               POP EDI
       *  00415AC4   5E               POP ESI
       *  00415AC5   8BC3             MOV EAX,EBX
       *  00415AC7   5B               POP EBX
       *  00415AC8   81C4 00080000    ADD ESP,0x800
       *  00415ACE   C3               RETN
       *  00415ACF   5F               POP EDI
       *  00415AD0   5E               POP ESI
       *  00415AD1   8BC3             MOV EAX,EBX
       *  00415AD3   5B               POP EBX
       *  00415AD4   81C4 00080000    ADD ESP,0x800
       *  00415ADA   C3               RETN
       *  00415ADB   90               NOP
       *  00415ADC   90               NOP
       *  00415ADD   90               NOP
       *  00415ADE   90               NOP
       */

      size_t parseTextSize(LPCWSTR text)
      {
        size_t count = 0;
        bool skipNull = false;
        for (; *text || skipNull; text++, count++)
          if (text[0] == 0)
            skipNull = false;
          else if (text[0] == 0x7)
            switch (text[1])
            {
            case 0x1: // ruby
              skipNull = true;
              break;
            case 0x8: // voice
              return count;
            case 0x6: // pause
              return count + 2;
            }
        return count;
      }

      size_t rtrim(LPCWSTR text, size_t size)
      {
        while (size && (text[size - 1] <= 32 || text[size - 1] == 0x3000)) // trim trailing non-printable characters
          size--;
        return size;
      }

      std::string parseTextData(LPCWSTR text)
      {
        std::string ret;
        if (!wcschr(text, 0x7))
        {
          ret = std::string((LPCSTR)text, ::wcslen(text) * sizeof(wchar_t));
          return ret;
        }
        for (; *text; text++)
        {
          if (text[0] == 0x7)
            switch (text[1])
            {
            case 0x1: // ruby
              if (LPCWSTR p = ::wcschr(text + 2, 0xa))
              {
                ret.append(LPCSTR(text + 2), (p - text - 2) * sizeof(wchar_t));
                text = p + ::wcslen(p); // text now point to zero
                continue;
              } // mismatched ruby that should never happen
              return std::string();
            case 0x8: // voice
              return ret;
            case 0x6: // pause
              ret.append((LPCSTR)text, 2 * sizeof(wchar_t));
              return ret;
            }
          ret.append((LPCSTR)text, sizeof(wchar_t));
        }
        return ret;
      }
#define MALIE_0 L"[0]" // represent \0
      void filterTextData(std::string &text)
      {
        // remove short pause
        static std::string shortPause((LPCSTR)L"\x07\x04", 2 * sizeof(wchar_t));
        // text.replace(shortPause, ""); // there is no remove method in std::string
        strReplace(text, shortPause);
      }
      // I need a cache retainer here to make sure same text result in same result
      void hookafter(hook_context *s, TextBuffer buffer, HookParam *)
      {
        static std::unordered_set<uint64_t> hashes_;
        auto text = (LPCWSTR)s->stack[1];
        if (!text || !*text || !(text[0] == 0x7 && text[1] == 0x8) && all_ascii(text))
          return;
        std::string data;
        bool update = false;

        for (size_t size; *text; text += size)
        {
          if (text[0] == 0x7 && text[1] == 0x8)
          { // voiced
            size_t len = ::wcslen(text);
            data.append((LPCSTR)text, (len + 1) * sizeof(wchar_t));
            text += len + 1;
          }

          size = parseTextSize(text);
          std::string oldData = parseTextData(text);
          filterTextData(oldData);
          if (oldData.empty()) // this should never happen
            return;

          auto oldTextAddress = (LPCWSTR)oldData.c_str();
          size_t oldTextSize = oldData.size() / sizeof(wchar_t),
                 trimmedSize = rtrim(oldTextAddress, oldTextSize);
          if (trimmedSize == 0 || all_ascii(oldTextAddress, trimmedSize))
            data.append(oldData);
          else
          {
            std::wstring oldText = std::wstring(oldTextAddress, trimmedSize);
            auto newText = buffer.viewW();
            if (newText.empty() || newText == oldText)
              data.append(oldData);
            else
            {
              update = true;
              data.append((LPCSTR)newText.data(), newText.size() * sizeof(wchar_t));
              if (trimmedSize != oldTextSize)
                data.append(LPCSTR(oldTextAddress + trimmedSize), (oldTextSize - trimmedSize) * sizeof(wchar_t));
            }
          }
        }
        if (update)
        {
          {
            static const std::string zero_bytes(sizeof(wchar_t), '\0'),
                zero_repr((LPCSTR)MALIE_0, sizeof(MALIE_0) - sizeof(wchar_t)); // - \0's size
            // data.replace(zero_repr, zero_bytes);
            strReplace(data, zero_repr, zero_bytes);
          }

          // make sure there are 5 zeros at the end
          data.push_back(0);
          data.push_back(0);
          data.push_back(0);
          data.push_back(0);
          data.push_back(0);

          s->stack[1] = (ULONG)allocateString(data);
        }
      }
      void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
      {

        static std::string data_;
        static std::unordered_set<uint64_t> hashes_;
        auto text = (LPCWSTR)s->stack[1];
        if (!text || !*text || !(text[0] == 0x7 && text[1] == 0x8) && all_ascii(text))
          return;

        // if (::wcsstr(text, L"\x30DC\x30BF\x30F3")) // ボタン
        //   return true;
        // if (::wcsstr(text, L"\x30A4\x30E1\x30FC")) // イメージ
        //   return true;

        // Scenario caller:
        // 004637BA   E8 21031F00      CALL malie.00653AE0   ; jichi: scenario caller
        // 004637BF   8B4E 1C          MOV ECX,DWORD PTR DS:[ESI+0x1C]
        // 004637C2   57               PUSH EDI
        //
        // 0046314A   E8 41831D00      CALL .0063B490
        // 0046314F   8B4E 20          MOV ECX,DWORD PTR DS:[ESI+0x20] ; jichi: scenario retaddr
        // 00463152   57               PUSH EDI
        //
        // (balloon-like)
        // 0042011F   8B56 20          MOV EDX,DWORD PTR DS:[ESI+0x20]   ; jichi: scenario caller
        // 00420122   57               PUSH EDI
        //
        // Name caller:
        // 00463829   E8 B2021F00      CALL malie.00653AE0 ; jichi: name
        // 0046382E   8B56 1C          MOV EDX,DWORD PTR DS:[ESI+0x1C]
        // 00463831   83C4 14          ADD ESP,0x14
        //
        // (balloon-like)
        // 00415A2C   8903             MOV DWORD PTR DS:[EBX],EAX  ; jichi: name caller
        // 00415A2E   8B46 04          MOV EAX,DWORD PTR DS:[ESI+0x4]
        // 00415A31   68 003B4100      PUSH .00413B00
        *role = Engine::OtherRole;
        auto retaddr = s->stack[0];
        switch (*(DWORD *)retaddr & 0xff0000ff)
        {
        case 0x5700008b:
          *role = Engine::ScenarioRole;
          break;
        case 0x8300008b:
        case 0x46000089:
          *role = Engine::NameRole;
          break;
        }
        // auto sig = Engine::hashThreadSignature(role, retaddr); // this is not needed as the retaddr is used as split
        auto sig = retaddr;

        std::string data;
        bool update = false;
        std::wstring collect;
        for (size_t size; *text; text += size)
        {
          if (text[0] == 0x7 && text[1] == 0x8)
          { // voiced
            size_t len = ::wcslen(text);
            data.append((LPCSTR)text, (len + 1) * sizeof(wchar_t));
            text += len + 1;
          }

          size = parseTextSize(text);
          std::string oldData = parseTextData(text);
          filterTextData(oldData);
          if (oldData.empty()) // this should never happen
            return;

          auto oldTextAddress = (LPCWSTR)oldData.c_str();
          size_t oldTextSize = oldData.size() / sizeof(wchar_t),
                 trimmedSize = rtrim(oldTextAddress, oldTextSize);
          if (trimmedSize == 0 || all_ascii(oldTextAddress, trimmedSize))
            data.append(oldData);
          else
          {
            collect += std::wstring_view(oldTextAddress, trimmedSize);
            // 在屏上输出一大段文字的时候，这个只是其中一小段
          }
        }
        buffer->from(collect);
      }
    } // namespace Private

    /**
     *  Sample game: シルヴァリオ ヴェンデッタ
     *
     *  Text in arg1.
     *  Function found by debugging the text being accessed.
     *  It is the same as one of the parent call of Malie2.
     *
     *  The target text arg1 is on this function's caller's stack.
     *
     *  00653ADC   90               NOP
     *  00653ADD   90               NOP
     *  00653ADE   90               NOP
     *  00653ADF   90               NOP
     *  00653AE0   56               PUSH ESI
     *  00653AE1   8B7424 08        MOV ESI,DWORD PTR SS:[ESP+0x8]
     *  00653AE5   33C0             XOR EAX,EAX
     *  00653AE7   85F6             TEST ESI,ESI
     *  00653AE9   74 47            JE SHORT malie.00653B32
     *  00653AEB   53               PUSH EBX
     *  00653AEC   57               PUSH EDI
     *  00653AED   68 00C47F00      PUSH malie.007FC400
     *  00653AF2   FF15 F8206900    CALL DWORD PTR DS:[<&KERNEL32.EnterCriti>; ntdll.RtlEnterCriticalSection
     *  00653AF8   56               PUSH ESI
     *  00653AF9   E8 C2E4FFFF      CALL malie.00651FC0
     *  00653AFE   8D78 02          LEA EDI,DWORD PTR DS:[EAX+0x2]
     *  00653B01   57               PUSH EDI
     *  00653B02   FF15 20256900    CALL DWORD PTR DS:[<&MSVCRT.malloc>]     ; msvcrt.malloc
     *  00653B08   8BD8             MOV EBX,EAX
     *  00653B0A   83C4 08          ADD ESP,0x8
     *  00653B0D   85DB             TEST EBX,EBX
     *  00653B0F   74 12            JE SHORT malie.00653B23
     *  00653B11   8BCF             MOV ECX,EDI
     *  00653B13   8BFB             MOV EDI,EBX
     *  00653B15   8BC1             MOV EAX,ECX
     *  00653B17   C1E9 02          SHR ECX,0x2
     *  00653B1A   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]
     *  00653B1C   8BC8             MOV ECX,EAX
     *  00653B1E   83E1 03          AND ECX,0x3
     *  00653B21   F3:A4            REP MOVS BYTE PTR ES:[EDI],BYTE PTR DS:[ESI]
     *  00653B23   68 00C47F00      PUSH malie.007FC400
     *  00653B28   FF15 44226900    CALL DWORD PTR DS:[<&KERNEL32.LeaveCriti>; ntdll.RtlLeaveCriticalSection
     *  00653B2E   8BC3             MOV EAX,EBX
     *  00653B30   5F               POP EDI
     *  00653B31   5B               POP EBX
     *  00653B32   5E               POP ESI
     *  00653B33   C3               RETN
     *  00653B34   90               NOP
     *  00653B35   90               NOP
     *  00653B36   90               NOP
     *  00653B37   90               NOP
     *  00653B38   90               NOP
     *
     *  Malie2's pattern: 4089560833d2894604
     *
     *    const BYTE bytes1[] = {
     *      0x40,            // inc eax
     *      0x89,0x56, 0x08, // mov dword ptr ds:[esi+0x8],edx
     *      0x33,0xd2,       // xor edx,edx
     *      0x89,0x46, 0x04  // mov dword ptr ds:[esi+0x4],eax
     *    };
     *
     *  Malie2 not used as it produces too many garbage
     *
     *  Malie2's call stack:
     *
     *  026DF0D8   026DF0E0
     *  026DF0DC   026DF184	; jichi: source text
     *  026DF0E0   026DF184
     *  026DF0E4   00000000
     *  026DF0E8   000000B8
     *  026DF0EC   0627DFE8
     *  026DF0F0   016F0000
     *  026DF0F4   0627DFE0
     *  026DF0F8   0180B5E0
     *  026DF0FC   00000001
     *  026DF100   0180B8F0  ASCII ""=VH"
     *  026DF104  /026DF11C
     *  026DF108  |77492CE8  RETURN to ntdll.77492CE8 from ntdll.77492D0B
     *  026DF10C  |0180B8F8
     *  026DF110  |FFFFFFFF
     *  026DF114  |04A9103C
     *  026DF118  |0180B8F0  ASCII ""=VH"
     *  026DF11C  \026DF168
     *  026DF120   771B98CD  RETURN to msvcrt.771B98CD from ntdll.RtlFreeHeap
     *  026DF124   018B0000
     *  026DF128   00000000
     *  026DF12C   00000006
     *  026DF130   FFFFFFFF
     *  026DF134   FFFFFFFF
     *  026DF138   00000000
     *  026DF13C   026DF184	; jichi: text
     *  026DF140   0000000C
     *  026DF144   062671D8
     *  026DF148   00000000
     *  026DF14C  /026DFA08
     *  026DF150  |00653AFE  RETURN to malie.00653AFE from malie.00651FC0
     *  026DF154  |026DF184	; jichi: text
     *  026DF158  |007272A8  malie.007272A8
     *  026DF15C  |04A9103C
     *  026DF160  |0183DFE8
     *  026DF164  |004637BF  RETURN to malie.004637BF from malie.00653AE0
     *  026DF168  |026DF184	; jichi: text, two continous scenario text
     *  026DF16C  |026DF184	; jichi: text
     *  026DF170  |007272A8  malie.007272A8
     *  026DF174  |00416CC0  malie.00416CC0
     *  026DF178  |0180B8F8
     *  026DF17C  |FFFFFFFF
     *  026DF180  |0183DFE8
     *  026DF184  |00080007
     *  026DF188  |005F0076  malie.005F0076
     *  026DF18C  |0065007A  malie.0065007A
     *  026DF190  |00300070
     *  026DF194  |00300030
     *
     *  Sample game: 相州戦神館學園 八命陣 (older game without critical sections)
     *  0063B48D   90               NOP
     *  0063B48E   90               NOP
     *  0063B48F   90               NOP
     *  0063B490   56               PUSH ESI
     *  0063B491   8B7424 08        MOV ESI,DWORD PTR SS:[ESP+0x8]
     *  0063B495   33C0             XOR EAX,EAX
     *  0063B497   57               PUSH EDI
     *  0063B498   85F6             TEST ESI,ESI
     *  0063B49A   74 29            JE SHORT .0063B4C5
     *  0063B49C   56               PUSH ESI
     *  0063B49D   E8 FEE4FFFF      CALL .006399A0
     *  0063B4A2   8D78 02          LEA EDI,DWORD PTR DS:[EAX+0x2]
     *  0063B4A5   57               PUSH EDI
     *  0063B4A6   FF15 94946700    CALL DWORD PTR DS:[0x679494]             ; msvcrt.malloc
     *  0063B4AC   83C4 08          ADD ESP,0x8
     *  0063B4AF   85C0             TEST EAX,EAX
     *  0063B4B1   74 12            JE SHORT .0063B4C5
     *  0063B4B3   8BCF             MOV ECX,EDI
     *  0063B4B5   8BF8             MOV EDI,EAX
     *  0063B4B7   8BD1             MOV EDX,ECX
     *  0063B4B9   C1E9 02          SHR ECX,0x2
     *  0063B4BC   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]
     *  0063B4BE   8BCA             MOV ECX,EDX
     *  0063B4C0   83E1 03          AND ECX,0x3
     *  0063B4C3   F3:A4            REP MOVS BYTE PTR ES:[EDI],BYTE PTR DS:[ESI]
     *  0063B4C5   5F               POP EDI
     *  0063B4C6   5E               POP ESI
     *  0063B4C7   C3               RETN
     *  0063B4C8   90               NOP
     *  0063B4C9   90               NOP
     *  0063B4CA   90               NOP
     *  0063B4CB   90               NOP
     *
     *  Sample game: 神咒神威神楽WEB体験版
     *  FIXME: Texts get disappeared
     *  00517A8D   90               NOP
     *  00517A8E   90               NOP
     *  00517A8F   90               NOP
     *  00517A90   56               PUSH ESI
     *  00517A91   8B7424 08        MOV ESI,DWORD PTR SS:[ESP+0x8]
     *  00517A95   57               PUSH EDI
     *  00517A96   56               PUSH ESI
     *  00517A97   E8 64E5FFFF      CALL .00516000
     *  00517A9C   8D78 02          LEA EDI,DWORD PTR DS:[EAX+0x2]
     *  00517A9F   57               PUSH EDI
     *  00517AA0   FF15 40745500    CALL DWORD PTR DS:[0x557440]             ; msvcrt.malloc
     *  00517AA6   83C4 08          ADD ESP,0x8
     *  00517AA9   85C0             TEST EAX,EAX
     *  00517AAB   74 12            JE SHORT .00517ABF
     *  00517AAD   8BCF             MOV ECX,EDI
     *  00517AAF   8BF8             MOV EDI,EAX
     *  00517AB1   8BD1             MOV EDX,ECX
     *  00517AB3   C1E9 02          SHR ECX,0x2
     *  00517AB6   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
     *  00517AB8   8BCA             MOV ECX,EDX
     *  00517ABA   83E1 03          AND ECX,0x3
     *  00517ABD   F3:A4            REP MOVS BYTE PTR ES:[EDI],BYTE PTR DS:[>
     *  00517ABF   5F               POP EDI
     *  00517AC0   5E               POP ESI
     *  00517AC1   C3               RETN
     *  00517AC2   90               NOP
     *  00517AC3   90               NOP
     *  00517AC4   90               NOP
     */
    bool attach(ULONG startAddress, ULONG stopAddress)
    {
      const uint8_t bytes[] = {
          // FF15 20256900  // 00653B02   FF15 20256900    CALL DWORD PTR DS:[<&MSVCRT.malloc>]     ; msvcrt.malloc
          // 8BD8           // 00653B08   8BD8             MOV EBX,EAX
          0x83, 0xC4, 0x08, // 00653B0A   83C4 08          ADD ESP,0x8
          0x85, XX,         // 00653B0D   85DB             TEST EBX,EBX
          0x74, 0x12,       // 00653B0F   74 12            JE SHORT malie.00653B23
          0x8B, XX,         // 00653B11   8BCF             MOV ECX,EDI
          0x8B, XX,         // 00653B13   8BFB             MOV EDI,EBX
          0x8B, XX,         // 00653B15   8BC1             MOV EAX,ECX
          0xC1, 0xE9, 0x02, // 00653B17   C1E9 02          SHR ECX,0x2
          0xF3, 0xA5,       // 00653B1A   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]
          0x8B, XX,         // 00653B1C   8BC8             MOV ECX,EAX
          0x83, 0xE1, 0x03, // 00653B1E   83E1 03          AND ECX,0x3
          0xF3, 0xA4        // 00653B21   F3:A4            REP MOVS BYTE PTR ES:[EDI],BYTE PTR DS:[ESI]
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      // DOUT(addr);
      if (!addr)
        return false;
      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        return false;
      // addr = 0x00653AE0; // the actual hooked grant parent call function, text in arg1

      // Sample game: シルヴァリオ ヴェンデッタ
      // If there are untranslated function, hook to the following location and debug the function stack to find text address
      // addr = 0x006519B0; // the callee function, text in arg2, function called by two functions, including the callee. Hooking to this function causing history to crash
      // return winhook::hook_before(addr, Private::hookBefore);
      HookParam hp;
      hp.address = addr;
      hp.text_fun = Private::hookBefore;
      hp.embed_fun = Private::hookafter;
      hp.type = CODEC_UTF16 | EMBED_ABLE | NO_CONTEXT;
      return NewHook(hp, "EmbedMalie");
    }
  } // namespace ScenarioHook

  namespace Patch
  {
    namespace Private
    {
      void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        static std::wstring fontFace_;
        auto fontFamily = std::wstring(commonsharedmem->fontFamily);

        if (!fontFamily.empty())
        {
          if (fontFace_ != fontFamily)
            fontFace_ = fontFamily;
          s->stack[1] = (ULONG)fontFace_.c_str();
          //::memcpy((LPVOID)s->stack[2], fontFace_.utf16(), fontFace_.size() * sizeof(wchar_t));
        }
      }
    } // namespace Private

    /**
     *  Sample game: シルヴァリオ ヴェンデッタ
     *  Force changing font face, otherwise CreateFontIndirectW won't be invoked.
     *
     *  Default font is TelopMinPro.
     *
     *  There are two fonts that are needed to be changed for Malie engine.
     *  - Text font: can be changed in registry as "FontFace"
     *  - UI font: canb be changed in malie.ini using SystemFont
     *    Example:
     *
     *    ;フォント種類指定
     *    ;SystemFont=SimSun
     *    ;FONT01=SimSun
     *    SystemFont=TelopMinPro
     *    FONT01=TelopMinPro
     *
     *  This function is found by debugging CreateFontIndirectW.
     *  Font face in both arg1 and arg2.
     *
     *  0043A82C   90               NOP
     *  0043A82D   90               NOP
     *  0043A82E   90               NOP
     *  0043A82F   90               NOP
     *  0043A830   53               PUSH EBX
     *  0043A831   55               PUSH EBP
     *  0043A832   56               PUSH ESI
     *  0043A833   57               PUSH EDI
     *  0043A834   E8 C7FFFFFF      CALL malie.0043A800
     *  0043A839   8BF8             MOV EDI,EAX
     *  0043A83B   33F6             XOR ESI,ESI
     *  0043A83D   85FF             TEST EDI,EDI
     *  0043A83F   7E 20            JLE SHORT malie.0043A861
     *  0043A841   8B5C24 14        MOV EBX,DWORD PTR SS:[ESP+0x14]
     *  0043A845   8B2D 14256900    MOV EBP,DWORD PTR DS:[<&MSVCRT._wcsicmp>>; msvcrt._wcsicmp
     *  0043A84B   56               /PUSH ESI
     *  0043A84C   E8 6FFFFFFF      |CALL malie.0043A7C0
     *  0043A851   50               |PUSH EAX
     *  0043A852   53               |PUSH EBX
     *  0043A853   FFD5             |CALL EBP
     *  0043A855   83C4 0C          |ADD ESP,0xC
     *  0043A858   85C0             |TEST EAX,EAX
     *  0043A85A   74 0D            |JE SHORT malie.0043A869
     *  0043A85C   46               |INC ESI
     *  0043A85D   3BF7             |CMP ESI,EDI
     *  0043A85F  ^7C EA            \JL SHORT malie.0043A84B
     *  0043A861   5F               POP EDI
     *  0043A862   5E               POP ESI
     *  0043A863   5D               POP EBP
     *  0043A864   83C8 FF          OR EAX,0xFFFFFFFF
     *  0043A867   5B               POP EBX
     *  0043A868   C3               RETN
     *  0043A869   5F               POP EDI
     *  0043A86A   8BC6             MOV EAX,ESI
     *  0043A86C   5E               POP ESI
     *  0043A86D   5D               POP EBP
     *  0043A86E   5B               POP EBX
     *  0043A86F   C3               RETN
     *  0043A870   8B4424 04        MOV EAX,DWORD PTR SS:[ESP+0x4]
     *  0043A874   83F8 FF          CMP EAX,-0x1
     *  0043A877   75 05            JNZ SHORT malie.0043A87E
     *  0043A879   E8 92FFFFFF      CALL malie.0043A810
     *  0043A87E   50               PUSH EAX
     *  0043A87F   E8 3CFFFFFF      CALL malie.0043A7C0
     *  0043A884   33C9             XOR ECX,ECX
     *  0043A886   83C4 04          ADD ESP,0x4
     *  0043A889   66:8338 40       CMP WORD PTR DS:[EAX],0x40
     *  0043A88D   0F94C1           SETE CL
     *  0043A890   8BC1             MOV EAX,ECX
     *  0043A892   C3               RETN
     *  0043A893   90               NOP
     *  0043A894   90               NOP
     *  0043A895   90               NOP
     *  0043A896   90               NOP
     *  0043A897   90               NOP
     *  0043A898   90               NOP
     *
     *  0278F138   0043AB90  RETURN to malie.0043AB90 from malie.0043A830
     *  0278F13C   0278F154  UNICODE "telopminpro"
     *  0278F140   0278F154  UNICODE "telopminpro"
     *  0278F144   006D2AE8  UNICODE "%s"
     *  0278F148   0192C990  UNICODE "telopminpro"
     *  0278F14C   00000000
     *  0278F150   0A33AAE0
     *  0278F154   00650074  malie.00650074
     *  0278F158   006F006C  malie.006F006C
     *  0278F15C   006D0070  ASCII "Context"
     *  0278F160   006E0069  malie.006E0069
     *  0278F164   00720070  malie.00720070
     *  0278F168   0000006F
     *  0278F16C   3F088850
     *  0278F170   00000000
     *  0278F174   00000000
     *
     */
    bool attachFont(ULONG startAddress, ULONG stopAddress)
    {
      const uint8_t bytes[] = {
          0x50,             // 0043A851   50               |PUSH EAX
          0x53,             // 0043A852   53               |PUSH EBX
          0xFF, 0xD5,       // 0043A853   FFD5             |CALL EBP
          0x83, 0xC4, 0x0C, // 0043A855   83C4 0C          |ADD ESP,0xC
          0x85, 0xC0,       // 0043A858   85C0             |TEST EAX,EAX
          0x74, 0x0D,       // 0043A85A   74 0D            |JE SHORT malie.0043A869
          0x46,             // 0043A85C   46               |INC ESI
          0x3B, 0xF7        // 0043A85D   3BF7             |CMP ESI,EDI
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return false;
      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        return false;
      HookParam hp;
      hp.address = addr;
      hp.text_fun = Private::hookBefore;
      return NewHook(hp, "PatchMalieFont");
    }
  } // namespace Patch
} // unnamed namespace

namespace
{
  // Dies irae ~Acta est Fabula~ HD
  // Dies irae ~Interview with Kaziklu Bey~

  std::wstring readString(DWORD address)
  {
    std::wstring s = L"";
    uint16_t c;
    // console.log(hexdump(address))
    while ((c = *(uint16_t *)address) != 0)
    {
      // utf-16 characters
      if (c >= 0x20)
      {
        s += (wchar_t)c;       // String.fromCharCode(c);
        address = address + 2; //.add(2);
      }
      else
      {
        // start command
        if (c == 0x7)
        {
          address = address + 2; //.add(2);
          // let cmd = address.readU16();
          auto cmd = *(uint16_t *)address;
          address = address + 2; //.add(2); // skip cmd
          // voice id --> skip
          if (cmd == 0x8)
          {
            while ((c = *(uint16_t *)address) != 0)
            {
              address = address + 2; //.add(2);
            }
            address = address + 2; //.add(2);
          }
          // end line --> return string
          if (cmd == 0x6)
          {
            return s;
          }
          // ruby
          if (cmd == 0x1)
          {
            while ((c = *(uint16_t *)address) != 0)
            {
              // when we reach 0xa we have the kanji part
              if (c == 0xa)
              {
                address = address + 2; //.add(2);
                // let rubi = '';
                while ((c = *(uint16_t *)address) != 0)
                {
                  // rubi += String.fromCharCode(c);
                  address = address + 2; //.add(2);
                }
                // console.log('rubi: ' + rubi);
                break;
              }
              else
              {
                s += (wchar_t)c;       // String.fromCharCode(c);
                address = address + 2; //.add(2);
              }
            }
            address = address + 2; //.add(2);
          }
        }
        else
        {
          address = address + 2; //.add(2);
        }
      }
    }
    return {};
  }
  void textfun_light(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    DWORD eax = context->eax;
    DWORD ecx = *(DWORD *)eax;
    DWORD edx = context->edx;
    auto str = readString(ecx + edx * 2);
    static std::wstring _ws;
    if (_ws == str)
      return;
    _ws = std::move(str);
    *split = 0;
    buffer->from(_ws);
  }
  bool malie_light()
  {
    BYTE pattern[] = {
        0x8b, 0x08, // 往前两个字节，否则jump到下个指令（被hook截断）会崩溃
        0x0f, XX, XX, XX, 0x89, XX, XX, 0x8d, XX, XX, 0x89, XX, XX, 0x8d, XX, XX, 0x00, 0x00, 0x00, 0x00};
    ULONG addr = MemDbg::findBytes(pattern, sizeof(pattern), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp{};
    hp.address = addr;
    hp.text_fun = textfun_light;
    hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
    return NewHook(hp, "malie_6");
  }

}

bool Malie::attach_function()
{
  bool embed = ScenarioHook::attach(processStartAddress, processStopAddress);
  //   if(embed)Patch::attachFont(processStartAddress,processStopAddress); 导致闪退，放弃
  auto b1 = InsertMalieHook() || embed;
  b1 = malie_light() || b1;
  return b1;
}