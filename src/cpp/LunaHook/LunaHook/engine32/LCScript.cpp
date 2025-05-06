#include "LCScript.h"
namespace
{ // unnamed
  namespace ScenarioHook
  {
    namespace Private
    {

      // Skip trailing 0203
      LPCSTR trim(LPCSTR text, int *size)
      {
        auto length = *size;
        while (length && (UINT8)text[0] <= 127)
        { // remove all leading ASCII characters including zeros
          text++;
          length--;
        }
        while (length && (UINT8)text[length - 1] == 0) // remove all trailing zeros
          length--;
        // remove all trailing illegal double-characters
        enum
        {
          MinimumByte = 0x6
        }; // the same as dynamicEncodingMinimumByte
        while (length >= 2 && (UINT8)text[length - 1] < MinimumByte && (UINT8)text[length - 2] < MinimumByte)
          length -= 2;
        *size = length;
        return text;
      }

      /**
       *  Sample game: 春恋＊乙女～乙女の園でごきげんよう。～
       *
       *  067C73FA  8F CD 90 6D 01 81 75 96 7B 93 96 82 C9 82 B1 82  章仁「本当にこ・
       *  067C740A  F1 82 C8 82 C6 82 B1 82 EB 82 AA 82 A0 82 E9 82  ﾈところがある・
       *  067C741A  F1 82 BE 82 C8 82 9F 81 63 81 63 81 76 02 03 00  ｾなぁ……」.
       *  067C742A  38 00 00 00 01 81 40 96 DA 82 CC 91 4F 82 C9 8D  8...　目の前に・
       *  067C743A  4C 82 AA 82 E9 8C F5 8C 69 82 F0 91 4F 82 C9 81  Lがる光景を前に・
       *
       *  Name/scenario splitter: 01 ()
       *  New line splitter: 0203 ()
       */

      // 0042FBE8   A1 E8234A00      MOV EAX,DWORD PTR DS:[0x4A23E8] ; jichi: text length here
      //
      // 0042FC03   8B15 E8234A00    MOV EDX,DWORD PTR DS:[0x4A23E8]	; jichi: text length here
      // 0042FC09   8B4C24 10        MOV ECX,DWORD PTR SS:[ESP+0x10]	; jichi: count is here
      // 0042FC0D   8B76 04          MOV ESI,DWORD PTR DS:[ESI+0x4]
      // 0042FC10   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
      // 0042FC14   8B92 44290000    MOV EDX,DWORD PTR DS:[EDX+0x2944]	; jichi: offset
      // 0042FC1A   8BF8             MOV EDI,EAX
      // 0042FC1C   8BC1             MOV EAX,ECX
      // 0042FC1E   83C4 04          ADD ESP,0x4
      // 0042FC21   8D7432 04        LEA ESI,DWORD PTR DS:[EDX+ESI+0x4]

      ULONG textBaseAddress_, // 0042FC03   8B15 E8234A00    MOV EDX,DWORD PTR DS:[0x4A23E8]
          textOffset_;        // 0042FC14   8B92 44290000    MOV EDX,DWORD PTR DS:[EDX+0x2944]

      std::string data_;

      /**
       *  Sample game: 姦獄学園
       *  Sample stack when hook1 is invoked:
       *  0012FE10   00000003
       *  0012FE14   00000008
       *  0012FE18   7FFDF000
       *  0012FE1C   00000000
       *  0012FE20   00000000
       *  0012FE24   0012FEB0  Pointer to next SEH record
       *  0012FE28   00480918  SE handler
       *  0012FE2C   00000000
       *  0012FE30   00419B16  RETURN to .00419B16 from .0040169F
       *  0012FE34   0012FE4C
       *  0012FE38   0012FE70
       *  0012FE3C   00000040
       *  0012FE40   77032EB2  user32.PeekMessageA
       *  0012FE44   00000000
       *  0012FE48   00000039
       *  0012FE4C   00000002
       *  0012FE50   00000039
       *  0012FE54   00000000
       *  0012FE58   00000000
       *
       *  Scenario thread caller:
       *
       *  0041C27C   E8 D65AFEFF      CALL .00401D57
       *  0041C281   8D5424 38        LEA EDX,DWORD PTR SS:[ESP+0x38]
       *  0041C285   68 00040000      PUSH 0x400
       *  0041C28A   8D4424 34        LEA EAX,DWORD PTR SS:[ESP+0x34]
       *  0041C28E   52               PUSH EDX
       *  0041C28F   50               PUSH EAX
       *  0041C290   E8 2354FEFF      CALL .004016B8  ; jichi: scenario caller here
       *  0041C295   83C4 0C          ADD ESP,0xC
       *  0041C298   8D4C24 38        LEA ECX,DWORD PTR SS:[ESP+0x38]
       *  0041C29C   8B15 B44E4A00    MOV EDX,DWORD PTR DS:[0x4A4EB4]
       *  0041C2A2   51               PUSH ECX
       *  0041C2A3   8B0D 5C0A4A00    MOV ECX,DWORD PTR DS:[0x4A0A5C]
       *  0041C2A9   8BC1             MOV EAX,ECX
       *
       *  Other thread callers:
       *
       *  00421298   8D8424 B0000000  LEA EAX,DWORD PTR SS:[ESP+0xB0]
       *  0042129F   50               PUSH EAX
       *  004212A0   51               PUSH ECX
       *  004212A1   895424 2C        MOV DWORD PTR SS:[ESP+0x2C],EDX
       *  004212A5   E8 0E04FEFF      CALL .004016B8  ; jichi: other caller
       *  004212AA   8D5424 38        LEA EDX,DWORD PTR SS:[ESP+0x38]
       *  004212AE   68 80000000      PUSH 0x80
       *  004212B3   8D4424 24        LEA EAX,DWORD PTR SS:[ESP+0x24]
       *  004212B7   52               PUSH EDX
       *  004212B8   50               PUSH EAX
       *  004212B9   E8 FA03FEFF      CALL .004016B8  ; jichi: other here
       *  004212BE   83C4 18          ADD ESP,0x18
       *  004212C1   83FF 01          CMP EDI,0x1
       *  004212C4   75 68            JNZ SHORT .0042132E
       *
       *
       *  Sample game: 春恋＊乙女～乙女の園でごきげんよう。～
       *  Sample scenario caller:
       *  0041C0C4   8D4424 38        LEA EAX,DWORD PTR SS:[ESP+0x38]
       *  0041C0C8   68 00040000      PUSH 0x400
       *  0041C0CD   8D4C24 34        LEA ECX,DWORD PTR SS:[ESP+0x34]
       *  0041C0D1   50               PUSH EAX
       *  0041C0D2   51               PUSH ECX
       *  0041C0D3   E8 C755FEFF      CALL .0040169F  ; jichi: called here
       *  0041C0D8   8B0D 4CE94900    MOV ECX,DWORD PTR DS:[0x49E94C]
       *  0041C0DE   8B35 00244A00    MOV ESI,DWORD PTR DS:[0x4A2400]
       *  0041C0E4   8BC1             MOV EAX,ECX
       *  0041C0E6   83C4 0C          ADD ESP,0xC
       *
       *  0012FA54   00000001
       *  0012FA58   00000006
       *  0012FA5C   7707EA71  user32.MessageBoxA
       *  0012FA60   00000000
       *  0012FA64   00000000
       *  0012FA68   0012FF78  Pointer to next SEH record
       *  0012FA6C   00480918  SE handler
       *  0012FA70   00000000
       *  0012FA74   0041C0D8  RETURN to .0041C0D8 from .0040169F
       *  0012FA78   0012FAB4
       *  0012FA7C   0012FABC
       *  0012FA80   00000400   ; jichi: used as split to identify scenario thread
       *  0012FA84   00000003
       *  0012FA88   77032EB2  user32.PeekMessageA
       *  0012FA8C   77033569  user32.DispatchMessageA
       *  0012FA90   7FFDF000
       *  0012FA94   00000000
       *  0012FA98   00000000
       *
       *  Other thread caller:
       *  0012FD60   00000001
       *  0012FD64   00000001
       *  0012FD68   7FFDF000
       *  0012FD6C   00000000
       *  0012FD70   00000000
       *  0012FD74   0012FF78  Pointer to next SEH record
       *  0012FD78   00480918  SE handler
       *  0012FD7C   00000000
       *  0012FD80   0042113A  RETURN to .0042113A from .0040169F
       *  0012FD84   0012FDAC
       *  0012FD88   0012FE3C
       *  0012FD8C   00000080   ; jichi: arg3
       *  0012FD90   00000003
       *  0012FD94   77032EB2  user32.PeekMessageA
       *  0012FD98   77033569  user32.DispatchMessageA
       *  0012FD9C   00000002
       *  0012FDA0   00000034
       *  0012FDA4   00000002
       *  0012FDA8   0000006D
       *  0012FDAC   00000002
       *  0012FDB0   00000034
       *  0012FDB4   00000000
       *  0012FDB8   00000001
       *  0012FDBC   001907D0
       *  0012FDC0   00000202
       *
       *  Sample game: 恋姫†無双
       *  ecx = 0x22
       *  Sample game text containing zeros
       *  01D6B13B  8E A9 8C 52 81 41 05 04 00 00 00 01 81 40 81 40  自軍、...　　
       *  01D6B14B  81 40 91 CE 01 93 47 8C 52 81 41 05 05 00 00 00  　対敵軍、...
       *  01D6B15B  02 00 14 00 00 00 5F 62 74 6C 5F 53 65 74 57 61  ...._btl_SetWa
       *  01D6B16B  7A 61 42 74 6E 53 72 63 59 00 0D 00 00 00 5F 62  zaBtnSrcY....._b
       *  01D6B17B  74 6C 5F 63 6D 64 63 68 69 70 00 0F 00 00 00 5F  tl_cmdchip...._
       *  01D6B18B  62 74 6C 5F 63 6D 64 63 68 69 70 5F 6D 00 0D 00  btl_cmdchip_m...
       *  01D6B19B  00 00 5F 62 74 6C 5F 6F 6E 6D 6F 75 73 65 00 0E  .._btl_onmouse.
       *  01D6B1AB  00 00 00 5F 62 74 6C 5F 73 65 6C 65 63 74 65 64  ..._btl_selected
       *  01D6B1BB  00 0B 00 00 00 5F 62 74 6C 5F 52 65 74 72 79 00  ...._btl_Retry.
       *  01D6B1CB  13 00 00 00 5F 62 74 6C 5F 43 6C 65 61 6E 75 70  ..._btl_Cleanup
       *
       *  ecx = 0x19
       *  01D6B317  81 40 04 6B 00 00 00 82 CC 91 B9 8A 51 82 F0 97  　k...の損害を・
       *  01D6B327  5E 82 A6 82 BD 81 42 02 00 10 00 00 00 5F 62 74  ^えた。...._bt
       *  01D6B337  6C 5F 57 61 7A 61 5F 43 68 6F 75 6E 00 17 00 00  l_Waza_Choun...
       *  01D6B347  00 5F 62 74 6C 5F 57 61 7A 61 45 6E 65 6D 79 5F  ._btl_WazaEnemy_
       *  01D6B357  42 75 66 66 41 54 4B 00 10 00 00 00 5F 62 74 6C  BuffATK...._btl
       *  01D6B367  5F 57 61 7A 61 5F 4B 6F 63 68 75 00 1C 00 00 00  _Waza_Kochu....
       */

      void hook1(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
      {
        data_.clear();

        int size = s->eax - 1;
        if (size <= 0)
          return;

        // 0042FC03   8B15 E8234A00    MOV EDX,DWORD PTR DS:[0x4A23E8]	; jichi: text here
        // 0042FC09   8B4C24 10        MOV ECX,DWORD PTR SS:[ESP+0x10]	; jichi: count is here
        // 0042FC0D   8B76 04          MOV ESI,DWORD PTR DS:[ESI+0x4]   ; jichi: [arg1+4]
        // 0042FC10   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
        // 0042FC14   8B92 44290000    MOV EDX,DWORD PTR DS:[EDX+0x2944] ; jichi: base addr, [[0x4A23E8] + 0x2944]
        // 0042FC1A   8BF8             MOV EDI,EAX
        // 0042FC1C   8BC1             MOV EAX,ECX
        // 0042FC1E   83C4 04          ADD ESP,0x4
        //
        // 0042FC21   8D7432 04        LEA ESI,DWORD PTR DS:[EDX+ESI+0x4]  ; jichi: hook2, text in esi

        ULONG edx, esi;
        {
          edx = *(DWORD *)textBaseAddress_;    // 0042FC03   8B15 E8234A00    MOV EDX,DWORD PTR DS:[0x4A23E8]
          edx = *(DWORD *)(edx + textOffset_); // 0042FC14   8B92 44290000    MOV EDX,DWORD PTR DS:[EDX+0x2944]
          esi = *(DWORD *)(s->esi + 0x4);      // 0042FC0D   8B76 04          MOV ESI,DWORD PTR DS:[ESI+0x4]
          esi = edx + esi + 0x4;               // 0042FC21   8D7432 04        LEA ESI,DWORD PTR DS:[EDX+ESI+0x4]
        }

        auto text = (LPCSTR)esi;
        if (!*text
            //|| ::strlen(text) != size
            || text[size]                               // text length not verified since there could be trailing zeros
            || ::isalpha(text[0]) && ::isalpha(text[1]) // Sample system text in 恋姫無双: bcg_剣道場a
            || all_ascii(text))
          return;

        auto trimmedSize = size;
        auto trimmedText = trim(text, &trimmedSize);
        if (trimmedSize <= 0)
          return;

        // auto size = s->ecx * 4;
        // auto dst = (LPSTR)s->edi;
        *role = Engine::OtherRole;
        auto retaddr = s->stack[8];
        // if ((*(DWORD *)retaddr & 0xffffff) == 0x0cc483) // 0041C295   83C4 0C          ADD ESP,0xC
        //   role = Engine::ScenarioRole;
        auto arg3 = s->stack[8 + 3];
        if (arg3 == 0x400)
          *role = Engine::ScenarioRole;
        // 8/7/2015: Here, I could also split choice and scenario from the retaddr.
        // But I didn't so that choice can also be display the same way asn scenario.
        // sig = retaddr;

        std::string oldData(trimmedText, trimmedSize);

        static const std::string zero_bytes(1, '\0');
        const char *zero_str = LCSE_0;

        bool containsZeros = false;
        if (oldData.find('\0') != oldData.npos)
        {
          containsZeros = true;
          strReplace(oldData, zero_bytes, zero_str);
          // oldData.replace(zero_bytes, zero_str);
          *role = Engine::OtherRole;
          // FIXME: There could be individual ascii letters before zeros (such as "k" and "n")
          // They should be escaped here.
          // Escaping not implemented since I am lazy.
        }
        buffer->from(oldData);
      }
      void hookafter(hook_context *s, TextBuffer buffer)
      {

        int size = s->eax - 1;
        if (size <= 0)
          return;

        ULONG edx, esi;
        {
          edx = *(DWORD *)textBaseAddress_;    // 0042FC03   8B15 E8234A00    MOV EDX,DWORD PTR DS:[0x4A23E8]
          edx = *(DWORD *)(edx + textOffset_); // 0042FC14   8B92 44290000    MOV EDX,DWORD PTR DS:[EDX+0x2944]
          esi = *(DWORD *)(s->esi + 0x4);      // 0042FC0D   8B76 04          MOV ESI,DWORD PTR DS:[ESI+0x4]
          esi = edx + esi + 0x4;               // 0042FC21   8D7432 04        LEA ESI,DWORD PTR DS:[EDX+ESI+0x4]
        }

        auto text = (LPCSTR)esi;
        if (!*text
            //|| ::strlen(text) != size
            || text[size]                               // text length not verified since there could be trailing zeros
            || ::isalpha(text[0]) && ::isalpha(text[1]) // Sample system text in 恋姫無双: bcg_剣道場a
            || all_ascii(text))
          return;

        auto trimmedSize = size;
        auto trimmedText = trim(text, &trimmedSize);
        if (trimmedSize <= 0)
          return;

        auto retaddr = s->stack[8];
        // if ((*(DWORD *)retaddr & 0xffffff) == 0x0cc483) // 0041C295   83C4 0C          ADD ESP,0xC
        //   role = Engine::ScenarioRole;
        auto arg3 = s->stack[8 + 3];

        std::string oldData(trimmedText, trimmedSize);

        static const std::string zero_bytes(1, '\0');
        const char *zero_str = LCSE_0;

        bool containsZeros = false;
        if (oldData.find('\0') != oldData.npos)
        {
          containsZeros = true;
          strReplace(oldData, zero_bytes, zero_str);
          // oldData.replace(zero_bytes, zero_str);

          // FIXME: There could be individual ascii letters before zeros (such as "k" and "n")
          // They should be escaped here.
          // Escaping not implemented since I am lazy.
        }
        std::string newData = buffer.strA();
        if (newData.empty() || newData == oldData)
          return;

        if (containsZeros)
          strReplace(newData, zero_str, zero_bytes);
        // newData.replace(zero_str, zero_bytes);

        int prefixSize = trimmedText - text,
            suffixSize = size - prefixSize - trimmedSize;
        if (prefixSize)
          newData.insert(0, std::string(text, prefixSize));
        if (suffixSize)
          newData.append(trimmedText + trimmedSize, suffixSize);

        data_ = newData;
        s->eax = data_.size() + 1;
        return;
      }
      void hook2(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        if (!data_.empty())
          s->esi = (ULONG)data_.c_str();
      }
    } // namespace Private

    /**
     *  Sample game: 春恋＊乙女～乙女の園でごきげんよう。～
     *
     *  0042FB1E   CC               INT3
     *  0042FB1F   CC               INT3
     *  0042FB20   6A FF            PUSH -0x1
     *  0042FB22   68 18094800      PUSH lcsebody.00480918
     *  0042FB27   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
     *  0042FB2D   50               PUSH EAX
     *  0042FB2E   64:8925 00000000 MOV DWORD PTR FS:[0],ESP
     *  0042FB35   83EC 08          SUB ESP,0x8
     *  0042FB38   53               PUSH EBX
     *  0042FB39   33DB             XOR EBX,EBX
     *  0042FB3B   56               PUSH ESI
     *  0042FB3C   57               PUSH EDI
     *  0042FB3D   895C24 0C        MOV DWORD PTR SS:[ESP+0xC],EBX
     *  0042FB41   895C24 10        MOV DWORD PTR SS:[ESP+0x10],EBX
     *  0042FB45   8B7424 24        MOV ESI,DWORD PTR SS:[ESP+0x24] ; jichi; arg1
     *  0042FB49   895C24 1C        MOV DWORD PTR SS:[ESP+0x1C],EBX
     *  0042FB4D   8B06             MOV EAX,DWORD PTR DS:[ESI]
     *  0042FB4F   83F8 05          CMP EAX,0x5
     *  0042FB52   75 2F            JNZ SHORT lcsebody.0042FB83
     *  0042FB54   8B76 04          MOV ESI,DWORD PTR DS:[ESI+0x4]
     *  0042FB57   8B3D E8234A00    MOV EDI,DWORD PTR DS:[0x4A23E8]
     *  0042FB5D   3BF3             CMP ESI,EBX
     *  0042FB5F   7C 08            JL SHORT lcsebody.0042FB69
     *  0042FB61   39B7 54290000    CMP DWORD PTR DS:[EDI+0x2954],ESI
     *  0042FB67   7F 12            JG SHORT lcsebody.0042FB7B
     *  0042FB69   53               PUSH EBX
     *  0042FB6A   68 20F54800      PUSH lcsebody.0048F520                   ; ASCII "err"
     *  0042FB6F   68 F4F44800      PUSH lcsebody.0048F4F4
     *  0042FB74   53               PUSH EBX
     *  0042FB75   FF15 EC874A00    CALL DWORD PTR DS:[<&USER32.MessageBoxA>>; user32.MessageBoxA
     *  0042FB7B   8B87 74290000    MOV EAX,DWORD PTR DS:[EDI+0x2974]
     *  0042FB81   EB 32            JMP SHORT lcsebody.0042FBB5
     *  0042FB83   83F8 08          CMP EAX,0x8 ; jichi: esi=arg1 jumped here
     *  0042FB86   75 57            JNZ SHORT lcsebody.0042FBDF
     *  0042FB88   8B76 04          MOV ESI,DWORD PTR DS:[ESI+0x4]
     *  0042FB8B   8B3D E8234A00    MOV EDI,DWORD PTR DS:[0x4A23E8]
     *  0042FB91   3BF3             CMP ESI,EBX
     *  0042FB93   7C 08            JL SHORT lcsebody.0042FB9D
     *  0042FB95   39B7 60290000    CMP DWORD PTR DS:[EDI+0x2960],ESI
     *  0042FB9B   7F 12            JG SHORT lcsebody.0042FBAF
     *  0042FB9D   53               PUSH EBX
     *  0042FB9E   68 20F54800      PUSH lcsebody.0048F520                   ; ASCII "err"
     *  0042FBA3   68 F4F44800      PUSH lcsebody.0048F4F4
     *  0042FBA8   53               PUSH EBX
     *  0042FBA9   FF15 EC874A00    CALL DWORD PTR DS:[<&USER32.MessageBoxA>>; user32.MessageBoxA
     *  0042FBAF   8B87 80290000    MOV EAX,DWORD PTR DS:[EDI+0x2980]
     *  0042FBB5   8D34F0           LEA ESI,DWORD PTR DS:[EAX+ESI*8]
     *  0042FBB8   8B06             MOV EAX,DWORD PTR DS:[ESI]
     *  0042FBBA   50               PUSH EAX
     *  0042FBBB   894424 10        MOV DWORD PTR SS:[ESP+0x10],EAX
     *  0042FBBF   E8 5E840000      CALL lcsebody.00438022
     *  0042FBC4   8B4C24 10        MOV ECX,DWORD PTR SS:[ESP+0x10]
     *  0042FBC8   83C4 04          ADD ESP,0x4
     *  0042FBCB   8BD1             MOV EDX,ECX
     *  0042FBCD   894424 10        MOV DWORD PTR SS:[ESP+0x10],EAX
     *  0042FBD1   8B76 04          MOV ESI,DWORD PTR DS:[ESI+0x4]
     *  0042FBD4   8BF8             MOV EDI,EAX
     *  0042FBD6   C1E9 02          SHR ECX,0x2
     *  0042FBD9   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
     *  0042FBDB   8BCA             MOV ECX,EDX
     *  0042FBDD   EB 4D            JMP SHORT lcsebody.0042FC2C
     *  0042FBDF   83F8 02          CMP EAX,0x2  ; jichi: esi=arg1 jumped here
     *  0042FBE2   0F85 A2000000    JNZ lcsebody.0042FC8A
     *  0042FBE8   A1 E8234A00      MOV EAX,DWORD PTR DS:[0x4A23E8] ; jichi: text length here
     *  0042FBED   8B56 04          MOV EDX,DWORD PTR DS:[ESI+0x4]
     *  0042FBF0   8B88 44290000    MOV ECX,DWORD PTR DS:[EAX+0x2944]
     *  0042FBF6   8B0411           MOV EAX,DWORD PTR DS:[ECX+EDX]
     *
     *  0042FBF9   50               PUSH EAX    ; jichi: hook1, text length pushed, new function
     *  0042FBFA   894424 10        MOV DWORD PTR SS:[ESP+0x10],EAX ; jichi: text length, is this the memory allocation
     *  0042FBFE   E8 1F840000      CALL lcsebody.00438022
     *
     *  0042FC03   8B15 E8234A00    MOV EDX,DWORD PTR DS:[0x4A23E8]	; jichi: text here
     *  0042FC09   8B4C24 10        MOV ECX,DWORD PTR SS:[ESP+0x10]	; jichi: count is here
     *  0042FC0D   8B76 04          MOV ESI,DWORD PTR DS:[ESI+0x4]  ; jichi: [arg1+4]
     *  0042FC10   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
     *  0042FC14   8B92 44290000    MOV EDX,DWORD PTR DS:[EDX+0x2944] ; jichi: base addr, [[0x4A23E8] + 0x2944]
     *  0042FC1A   8BF8             MOV EDI,EAX
     *  0042FC1C   8BC1             MOV EAX,ECX
     *  0042FC1E   83C4 04          ADD ESP,0x4
     *
     *  0042FC21   8D7432 04        LEA ESI,DWORD PTR DS:[EDX+ESI+0x4]  ; jichi: hook2, text in esi
     *  0042FC25   C1E9 02          SHR ECX,0x2	; jichi: ecx is now the count, here, the rep function is blocked by 4 for performance
     *  0042FC28   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS[ESI]	; jichi: text accessed here from esi to edi
     *
     *  0042FC2A   8BC8             MOV ECX,EAX
     *  0042FC2C   8B5424 28        MOV EDX,DWORD PTR SS:[ESP+0x28]
     *  0042FC30   83E1 03          AND ECX,0x3
     *  0042FC33   F3:A4            REP MOVS BYTE PTR ES:[EDI],BYTE PTR DS:[ESI]
     *  0042FC35   8B4C24 2C        MOV ECX,DWORD PTR SS:[ESP+0x2C]
     *  0042FC39   8D4424 0C        LEA EAX,DWORD PTR SS:[ESP+0xC]
     *  0042FC3D   51               PUSH ECX
     *  0042FC3E   52               PUSH EDX
     *  0042FC3F   50               PUSH EAX
     *  0042FC40   E8 AB14FDFF      CALL lcsebody.004010F0
     *  0042FC45   83C4 0C          ADD ESP,0xC
     *  0042FC48   C74424 1C FFFFFF>MOV DWORD PTR SS:[ESP+0x1C],-0x1
     *  0042FC50   84C0             TEST AL,AL
     *  0042FC52   8B4424 10        MOV EAX,DWORD PTR SS:[ESP+0x10]
     *  0042FC56   895C24 0C        MOV DWORD PTR SS:[ESP+0xC],EBX
     *  0042FC5A   74 21            JE SHORT lcsebody.0042FC7D
     *  0042FC5C   3BC3             CMP EAX,EBX
     *  0042FC5E   74 09            JE SHORT lcsebody.0042FC69
     *  0042FC60   50               PUSH EAX
     *  0042FC61   E8 467E0000      CALL lcsebody.00437AAC
     *  0042FC66   83C4 04          ADD ESP,0x4
     *  0042FC69   5F               POP EDI
     *  0042FC6A   5E               POP ESI
     *  0042FC6B   B0 01            MOV AL,0x1
     *  0042FC6D   5B               POP EBX
     *  0042FC6E   8B4C24 08        MOV ECX,DWORD PTR SS:[ESP+0x8]
     *  0042FC72   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
     *  0042FC79   83C4 14          ADD ESP,0x14
     *  0042FC7C   C3               RETN
     *  0042FC7D   3BC3             CMP EAX,EBX
     *  0042FC7F   74 09            JE SHORT lcsebody.0042FC8A
     *  0042FC81   50               PUSH EAX
     *  0042FC82   E8 257E0000      CALL lcsebody.00437AAC
     *  0042FC87   83C4 04          ADD ESP,0x4
     *  0042FC8A   8B4C24 14        MOV ECX,DWORD PTR SS:[ESP+0x14]
     *  0042FC8E   5F               POP EDI
     *  0042FC8F   5E               POP ESI
     *  0042FC90   32C0             XOR AL,AL
     *  0042FC92   5B               POP EBX
     *  0042FC93   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
     *  0042FC9A   83C4 14          ADD ESP,0x14
     *  0042FC9D   C3               RETN
     *  0042FC9E   90               NOP
     *  0042FC9F   90               NOP
     *  0042FCA0   CC               INT3
     *  0042FCA1   CC               INT3
     *  0042FCA2   CC               INT3
     *  0042FCA3   CC               INT3
     *  0042FCA4   CC               INT3
     *  0042FCA5   CC               INT3
     *  0042FCA6   CC               INT3
     *
     *  Sample game: 姦獄学園
     *
     *  00430CAB   CC               INT3
     *  00430CAC   CC               INT3
     *  00430CAD   CC               INT3
     *  00430CAE   CC               INT3
     *  00430CAF   CC               INT3
     *  00430CB0   6A FF            PUSH -0x1
     *  00430CB2   68 08204800      PUSH .00482008
     *  00430CB7   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
     *  00430CBD   50               PUSH EAX
     *  00430CBE   64:8925 00000000 MOV DWORD PTR FS:[0],ESP
     *  00430CC5   83EC 08          SUB ESP,0x8
     *  00430CC8   53               PUSH EBX
     *  00430CC9   33DB             XOR EBX,EBX
     *  00430CCB   56               PUSH ESI
     *  00430CCC   57               PUSH EDI
     *  00430CCD   895C24 0C        MOV DWORD PTR SS:[ESP+0xC],EBX
     *  00430CD1   895C24 10        MOV DWORD PTR SS:[ESP+0x10],EBX
     *  00430CD5   8B7424 24        MOV ESI,DWORD PTR SS:[ESP+0x24]
     *  00430CD9   895C24 1C        MOV DWORD PTR SS:[ESP+0x1C],EBX
     *  00430CDD   8B06             MOV EAX,DWORD PTR DS:[ESI]
     *  00430CDF   83F8 05          CMP EAX,0x5
     *  00430CE2   75 2F            JNZ SHORT .00430D13
     *  00430CE4   8B76 04          MOV ESI,DWORD PTR DS:[ESI+0x4]
     *  00430CE7   8B3D 9C4E4A00    MOV EDI,DWORD PTR DS:[0x4A4E9C]
     *  00430CED   3BF3             CMP ESI,EBX
     *  00430CEF   7C 08            JL SHORT .00430CF9
     *  00430CF1   39B7 54310000    CMP DWORD PTR DS:[EDI+0x3154],ESI
     *  00430CF7   7F 12            JG SHORT .00430D0B
     *  00430CF9   53               PUSH EBX
     *  00430CFA   68 98154900      PUSH .00491598                           ; ASCII "err"
     *  00430CFF   68 D8254900      PUSH .004925D8
     *  00430D04   53               PUSH EBX
     *  00430D05   FF15 2CC84A00    CALL DWORD PTR DS:[0x4AC82C]             ; user32.MessageBoxA
     *  00430D0B   8B87 74310000    MOV EAX,DWORD PTR DS:[EDI+0x3174]
     *  00430D11   EB 32            JMP SHORT .00430D45
     *  00430D13   83F8 08          CMP EAX,0x8
     *  00430D16   75 57            JNZ SHORT .00430D6F
     *  00430D18   8B76 04          MOV ESI,DWORD PTR DS:[ESI+0x4]
     *  00430D1B   8B3D 9C4E4A00    MOV EDI,DWORD PTR DS:[0x4A4E9C]
     *  00430D21   3BF3             CMP ESI,EBX
     *  00430D23   7C 08            JL SHORT .00430D2D
     *  00430D25   39B7 60310000    CMP DWORD PTR DS:[EDI+0x3160],ESI
     *  00430D2B   7F 12            JG SHORT .00430D3F
     *  00430D2D   53               PUSH EBX
     *  00430D2E   68 98154900      PUSH .00491598                           ; ASCII "err"
     *  00430D33   68 AC254900      PUSH .004925AC
     *  00430D38   53               PUSH EBX
     *  00430D39   FF15 2CC84A00    CALL DWORD PTR DS:[0x4AC82C]             ; user32.MessageBoxA
     *  00430D3F   8B87 80310000    MOV EAX,DWORD PTR DS:[EDI+0x3180]
     *  00430D45   8D34F0           LEA ESI,DWORD PTR DS:[EAX+ESI*8]
     *  00430D48   8B06             MOV EAX,DWORD PTR DS:[ESI]
     *  00430D4A   50               PUSH EAX
     *  00430D4B   894424 10        MOV DWORD PTR SS:[ESP+0x10],EAX
     *  00430D4F   E8 BE890000      CALL .00439712
     *  00430D54   8B4C24 10        MOV ECX,DWORD PTR SS:[ESP+0x10]
     *  00430D58   83C4 04          ADD ESP,0x4
     *  00430D5B   8BD1             MOV EDX,ECX
     *  00430D5D   894424 10        MOV DWORD PTR SS:[ESP+0x10],EAX
     *  00430D61   8B76 04          MOV ESI,DWORD PTR DS:[ESI+0x4]
     *  00430D64   8BF8             MOV EDI,EAX
     *  00430D66   C1E9 02          SHR ECX,0x2
     *  00430D69   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
     *  00430D6B   8BCA             MOV ECX,EDX
     *  00430D6D   EB 4D            JMP SHORT .00430DBC
     *  00430D6F   83F8 02          CMP EAX,0x2
     *  00430D72   0F85 A2000000    JNZ .00430E1A
     *  00430D78   A1 9C4E4A00      MOV EAX,DWORD PTR DS:[0x4A4E9C]
     *  00430D7D   8B56 04          MOV EDX,DWORD PTR DS:[ESI+0x4]
     *  00430D80   8B88 44310000    MOV ECX,DWORD PTR DS:[EAX+0x3144]
     *  00430D86   8B0411           MOV EAX,DWORD PTR DS:[ECX+EDX]
     *  00430D89   50               PUSH EAX
     *  00430D8A   894424 10        MOV DWORD PTR SS:[ESP+0x10],EAX
     *  00430D8E   E8 7F890000      CALL .00439712
     *  00430D93   8B15 9C4E4A00    MOV EDX,DWORD PTR DS:[0x4A4E9C]
     *  00430D99   8B4C24 10        MOV ECX,DWORD PTR SS:[ESP+0x10]
     *  00430D9D   8B76 04          MOV ESI,DWORD PTR DS:[ESI+0x4]
     *  00430DA0   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
     *  00430DA4   8B92 44310000    MOV EDX,DWORD PTR DS:[EDX+0x3144]
     *  00430DAA   8BF8             MOV EDI,EAX
     *  00430DAC   8BC1             MOV EAX,ECX
     *  00430DAE   83C4 04          ADD ESP,0x4
     *  00430DB1   8D7432 04        LEA ESI,DWORD PTR DS:[EDX+ESI+0x4]	; jichi: the other game's access point
     *  00430DB5   C1E9 02          SHR ECX,0x2
     *  00430DB8   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]
     *  00430DBA   8BC8             MOV ECX,EAX
     *  00430DBC   8B5424 28        MOV EDX,DWORD PTR SS:[ESP+0x28]
     *  00430DC0   83E1 03          AND ECX,0x3
     *  00430DC3   F3:A4            REP MOVS BYTE PTR ES:[EDI],BYTE PTR DS:[ESI]
     *  00430DC5   8B4C24 2C        MOV ECX,DWORD PTR SS:[ESP+0x2C]
     *  00430DC9   8D4424 0C        LEA EAX,DWORD PTR SS:[ESP+0xC]
     *  00430DCD   51               PUSH ECX
     *  00430DCE   52               PUSH EDX
     *  00430DCF   50               PUSH EAX
     *  00430DD0   E8 2503FDFF      CALL .004010FA
     *  00430DD5   83C4 0C          ADD ESP,0xC
     *  00430DD8   C74424 1C FFFFFF>MOV DWORD PTR SS:[ESP+0x1C],-0x1
     *  00430DE0   84C0             TEST AL,AL
     *  00430DE2   8B4424 10        MOV EAX,DWORD PTR SS:[ESP+0x10]
     *  00430DE6   895C24 0C        MOV DWORD PTR SS:[ESP+0xC],EBX
     *  00430DEA   74 21            JE SHORT .00430E0D
     *  00430DEC   3BC3             CMP EAX,EBX
     *  00430DEE   74 09            JE SHORT .00430DF9
     *  00430DF0   50               PUSH EAX
     *  00430DF1   E8 A6830000      CALL .0043919C
     *  00430DF6   83C4 04          ADD ESP,0x4
     *  00430DF9   5F               POP EDI
     *  00430DFA   5E               POP ESI
     *  00430DFB   B0 01            MOV AL,0x1
     *  00430DFD   5B               POP EBX
     *  00430DFE   8B4C24 08        MOV ECX,DWORD PTR SS:[ESP+0x8]
     *  00430E02   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
     *  00430E09   83C4 14          ADD ESP,0x14
     *  00430E0C   C3               RETN
     *  00430E0D   3BC3             CMP EAX,EBX
     *  00430E0F   74 09            JE SHORT .00430E1A
     *  00430E11   50               PUSH EAX
     *  00430E12   E8 85830000      CALL .0043919C
     *  00430E17   83C4 04          ADD ESP,0x4
     *  00430E1A   8B4C24 14        MOV ECX,DWORD PTR SS:[ESP+0x14]
     *  00430E1E   5F               POP EDI
     *  00430E1F   5E               POP ESI
     *  00430E20   32C0             XOR AL,AL
     *  00430E22   5B               POP EBX
     *  00430E23   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
     *  00430E2A   83C4 14          ADD ESP,0x14
     *  00430E2D   C3               RETN
     *  00430E2E   90               NOP
     *  00430E2F   90               NOP
     *  00430E30   CC               INT3
     *  00430E31   CC               INT3
     *  00430E32   CC               INT3
     *  00430E33   CC               INT3
     *  00430E34   CC               INT3
     */
    bool isLeadByteChar(const char *s)
    {
      return dynsjis::isleadstr(s);
      // return ::IsDBCSLeadByte(HIBYTE(testChar));
    }
    bool attach(ULONG startAddress, ULONG stopAddress, ULONG dyna)
    {
      const uint8_t bytes[] = {
          0x8d, 0x74, 0x32, 0x04, // 0042fc21   8d7432 04        lea esi,dword ptr ds:[edx+esi+0x4]
          0xc1, 0xe9, 0x02,       // 0042fc25   c1e9 02          shr ecx,0x2
          0xf3, 0xa5              // 0042fc28   f3:a5            rep movs dword ptr es:[edi],dword ptr ds[esi]	; jichi: text accessed here from esi to edi
      };
      ULONG addr2 = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr2)
        return false;

      // 0042FBF9   50               PUSH EAX    ; jichi: hook1, text length pushed, new function
      // 0042FBFA   894424 10        MOV DWORD PTR SS:[ESP+0x10],EAX ; jichi: text length, is this the memory allocation?
      // 0042FBFE   E8 1F840000      CALL lcsebody.00438022
      // 0042FC03   8B15 E8234A00    MOV EDX,DWORD PTR DS:[0x4A23E8]	; jichi: text here
      // 0042FC09   8B4C24 10        MOV ECX,DWORD PTR SS:[ESP+0x10]	; jichi: count is here
      // 0042FC0D   8B76 04          MOV ESI,DWORD PTR DS:[ESI+0x4]  ; jichi: [arg1+4]
      // 0042FC10   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
      // 0042FC14   8B92 44290000    MOV EDX,DWORD PTR DS:[EDX+0x2944]	; jichi: base addr, [[0x4A23E8] + 0x2944]
      // 0042FC1A   8BF8             MOV EDI,EAX
      // 0042FC1C   8BC1             MOV EAX,ECX
      // 0042FC1E   83C4 04          ADD ESP,0x4
      //
      // 0042FC21   8D7432 04        LEA ESI,DWORD PTR DS:[EDX+ESI+0x4] ; jichi: hook2, text in esi
      // 0042FC25   C1E9 02          SHR ECX,0x2	; jichi: ecx is now the count, here, the rep function is blocked by 4 for performance
      // 0042FC28   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS[ESI]	; jichi: text accessed here from esi to edi
      ULONG addr1 = addr2 + 0x0042fbf9 - 0x0042fc21;
      if (*(BYTE *)addr1 != 0x50) // push_eax
        return false;

      // 0042FC03   8B15 E8234A00    MOV EDX,DWORD PTR DS:[0x4A23E8]	; jichi: text here
      // 0042FC09   8B4C24 10        MOV ECX,DWORD PTR SS:[ESP+0x10]	; jichi: count is here
      // 0042FC0D   8B76 04          MOV ESI,DWORD PTR DS:[ESI+0x4]  ; jichi: [arg1+4]
      // 0042FC10   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
      // 0042FC14   8B92 44290000    MOV EDX,DWORD PTR DS:[EDX+0x2944]	; jichi: offset addr, [[0x4A23E8] + 0x2944]
      {
        ULONG addr = addr2 + 0x0042fc03 - 0x0042fc21;
        if (*(WORD *)addr != 0x158b) // 0042FC03   8B15 E8234A00    MOV EDX,DWORD PTR DS:[0x4A23E8]
          return false;
        addr += 2;
        Private::textBaseAddress_ = *(DWORD *)addr;
      }
      {
        ULONG addr = addr2 + 0x0042fc14 - 0x0042fc21;
        if (*(WORD *)addr != 0x928b) // 0042FC14   8B92 44290000    MOV EDX,DWORD PTR DS:[EDX+0x2944]
          return false;
        addr += 2;
        Private::textOffset_ = *(DWORD *)addr;
      }
      HookParam hp;
      hp.address = addr1;
      hp.text_fun = Private::hook1;
      hp.embed_fun = Private::hookafter;
      hp.type = EMBED_ABLE | NO_CONTEXT;
      hp.lineSeparator = L"\x01";
      hp.embed_hook_font = F_GetGlyphOutlineA;
      if (dyna)
      {
        hp.type |= EMBED_DYNA_SJIS;
        hp.embed_hook_font = F_GetGlyphOutlineA;
        dynamiccodec->setMinimumSecondByte(6); //// skip 0x1,0x2,0x3 in case dynamic encoding could crash the game
        patch_fun_ptrs = {{(void *)dyna, (PVOID)(ULONG)isLeadByteChar}};
      }
      auto succ = NewHook(hp, "EmbedLCSE");
      hp.address = addr2 + 4;
      hp.text_fun = Private::hook2;
      succ |= NewHook(hp, "EmbedLCSE");
      return succ;
    }
  } // namespace ScenarioHook

  namespace Patch
  {

    namespace Private
    {
      bool isLeadByteChar(const char *s)
      {
        return dynsjis::isleadstr(s);
        // return ::IsDBCSLeadByte(HIBYTE(testChar));
      }

    } // namespace Private

    /**
     *  Sample game: 春恋＊乙女～乙女の園でごきげんよう。～
     *
     *  Debugging method: Find text in memory, and then insert hardware breakpoint.
     *  It will be accessed only ONCE in the following function.
     *
     *  This function can also be found by searching the following instruction:
     *  0040A389   3C 81                                  CMP AL,0x81
     *
     *  This function is very similar to that in CatSystem2.
     *
     *  0040A37E   CC                                     INT3
     *  0040A37F   CC                                     INT3
     *  0040A380   8B4C24 04                              MOV ECX,DWORD PTR SS:[ESP+0x4]
     *  0040A384   8A01                                   MOV AL,BYTE PTR DS:[ECX]  ; jichi: first byte
     *  0040A386   8A49 01                                MOV CL,BYTE PTR DS:[ECX+0x1]  ; jichi: second byte
     *  0040A389   3C 81                                  CMP AL,0x81
     *  0040A38B   72 04                                  JB SHORT lcsebody.0040A391
     *  0040A38D   3C 9F                                  CMP AL,0x9F
     *  0040A38F   76 08                                  JBE SHORT lcsebody.0040A399
     *  0040A391   3C E0                                  CMP AL,0xE0
     *  0040A393   72 1B                                  JB SHORT lcsebody.0040A3B0
     *  0040A395   3C FC                                  CMP AL,0xFC
     *  0040A397   77 17                                  JA SHORT lcsebody.0040A3B0
     *  0040A399   80F9 40                                CMP CL,0x40
     *  0040A39C   72 05                                  JB SHORT lcsebody.0040A3A3
     *  0040A39E   80F9 7E                                CMP CL,0x7E
     *  0040A3A1   76 0A                                  JBE SHORT lcsebody.0040A3AD
     *  0040A3A3   80F9 80                                CMP CL,0x80
     *  0040A3A6   72 08                                  JB SHORT lcsebody.0040A3B0
     *  0040A3A8   80F9 FC                                CMP CL,0xFC
     *  0040A3AB   77 03                                  JA SHORT lcsebody.0040A3B0
     *  0040A3AD   B0 01                                  MOV AL,0x1
     *  0040A3AF   C3                                     RETN
     *  0040A3B0   32C0                                   XOR AL,AL
     *  0040A3B2   C3                                     RETN
     *  0040A3B3   90                                     NOP
     *  0040A3B4   90                                     NOP
     *  0040A3B5   90                                     NOP
     *  0040A3B6   90                                     NOP
     *
     *  This function is found by tracing the caller of GetGlyphOutlineA, as follows:
     *
     *  00416B6B   CC                INT3
     *  00416B6C   CC                INT3
     *  00416B6D   CC                INT3
     *  00416B6E   CC                INT3
     *  00416B6F   CC                INT3
     *  00416B70   83EC 08           SUB ESP,0x8
     *  00416B73   53                PUSH EBX
     *  00416B74   56                PUSH ESI
     *  00416B75   8BF1              MOV ESI,ECX
     *  00416B77   33DB              XOR EBX,EBX	; jichi: zero ebx
     *  00416B79   57                PUSH EDI
     *  00416B7A   8B86 EC000000     MOV EAX,DWORD PTR DS:[ESI+0xEC]
     *  00416B80   8A9430 08010000   MOV DL,BYTE PTR DS:[EAX+ESI+0x108]	; jichi: byte accessed here
     *  00416B87   8D8C30 08010000   LEA ECX,DWORD PTR DS:[EAX+ESI+0x108]	; jichi: byte accessed here
     *  00416B8E   3AD3              CMP DL,BL	; jichi: bl is zero, dl is the current byte
     *  00416B90   75 0C             JNZ SHORT lcsebody.00416B9E
     *  00416B92   B8 FF000000       MOV EAX,0xFF
     *  00416B97   5F                POP EDI
     *  00416B98   5E                POP ESI
     *  00416B99   5B                POP EBX
     *  00416B9A   83C4 08           ADD ESP,0x8
     *  00416B9D   C3                RETN
     *  00416B9E   8B96 F0000000     MOV EDX,DWORD PTR DS:[ESI+0xF0]
     *  00416BA4   4A                DEC EDX
     *  00416BA5   3BC2              CMP EAX,EDX
     *  00416BA7   0F8D 31010000     JGE lcsebody.00416CDE
     *  00416BAD   51                PUSH ECX
     *  00416BAE   E8 31B1FEFF       CALL lcsebody.00401CE4	; jichi: ecx point to the current character, return 0 or 1
     *  00416BB3   83C4 04           ADD ESP,0x4
     *  00416BB6   84C0              TEST AL,AL
     *  00416BB8   0F84 20010000     JE lcsebody.00416CDE	; jichi: wrong here
     *  00416BBE   8B86 EC000000     MOV EAX,DWORD PTR DS:[ESI+0xEC]
     *  00416BC4   33C9              XOR ECX,ECX
     *  00416BC6   03C6              ADD EAX,ESI
     *  00416BC8   889E 20050000     MOV BYTE PTR DS:[ESI+0x520],BL
     *  00416BCE   8AA8 08010000     MOV CH,BYTE PTR DS:[EAX+0x108]	; jichi: high bits
     *  00416BD4   8A88 09010000     MOV CL,BYTE PTR DS:[EAX+0x109]
     *  00416BDA   8BF9              MOV EDI,ECX	; jichi: low bits, edi is now the full character
     *  00416BDC   8BCE              MOV ECX,ESI	; jichi: recover ecx to esi
     *  00416BDE   E8 13AEFEFF       CALL lcsebody.004019F6	; jichi: eax is zero when edi is legal
     *  00416BE3   3BC3              CMP EAX,EBX	; jichi: ebx is always zero as well
     *  00416BE5   74 4A             JE SHORT lcsebody.00416C31
     *  00416BE7   389E 2C050000     CMP BYTE PTR DS:[ESI+0x52C],BL
     *  00416BED   0F84 9A020000     JE lcsebody.00416E8D
     *  00416BF3   389E 20050000     CMP BYTE PTR DS:[ESI+0x520],BL
     *  00416BF9   74 1B             JE SHORT lcsebody.00416C16
     *  00416BFB   B9 34F14800       MOV ECX,lcsebody.0048F134
     *  00416C00   3B39              CMP EDI,DWORD PTR DS:[ECX]
     *  00416C02   74 2D             JE SHORT lcsebody.00416C31
     *  00416C04   83C1 04           ADD ECX,0x4
     *  00416C07   81F9 50F14800     CMP ECX,lcsebody.0048F150
     *  00416C0D  ^7C F1             JL SHORT lcsebody.00416C00
     *  00416C0F   5F                POP EDI
     *  00416C10   5E                POP ESI
     *  00416C11   5B                POP EBX
     *  00416C12   83C4 08           ADD ESP,0x8
     *  00416C15   C3                RETN
     *  00416C16   B9 00F14800       MOV ECX,lcsebody.0048F100
     *  00416C1B   3B39              CMP EDI,DWORD PTR DS:[ECX]
     *  00416C1D   74 12             JE SHORT lcsebody.00416C31
     *  00416C1F   83C1 04           ADD ECX,0x4
     *  00416C22   81F9 34F14800     CMP ECX,lcsebody.0048F134
     *  00416C28  ^7C F1             JL SHORT lcsebody.00416C1B
     *  00416C2A   5F                POP EDI
     *  00416C2B   5E                POP ESI
     *  00416C2C   5B                POP EBX
     *  00416C2D   83C4 08           ADD ESP,0x8
     *  00416C30   C3                RETN
     *  00416C31   8A8E 20050000     MOV CL,BYTE PTR DS:[ESI+0x520]
     *  00416C37   3ACB              CMP CL,BL
     *  00416C39   74 15             JE SHORT lcsebody.00416C50
     *  00416C3B   B8 70F14800       MOV EAX,lcsebody.0048F170
     *  00416C40   3B38              CMP EDI,DWORD PTR DS:[EAX]
     *  00416C42   74 21             JE SHORT lcsebody.00416C65
     *  00416C44   83C0 04           ADD EAX,0x4
     *  00416C47   3D 7CF14800       CMP EAX,lcsebody.0048F17C
     *  00416C4C  ^7C F2             JL SHORT lcsebody.00416C40
     *  00416C4E   EB 1B             JMP SHORT lcsebody.00416C6B
     *  00416C50   B8 50F14800       MOV EAX,lcsebody.0048F150
     *  00416C55   3B38              CMP EDI,DWORD PTR DS:[EAX]	; jichi: compare current wide character with a threshold (0x8169 = "（")
     *  00416C57   74 0C             JE SHORT lcsebody.00416C65
     *  00416C59   83C0 04           ADD EAX,0x4
     *  00416C5C   3D 70F14800       CMP EAX,lcsebody.0048F170
     *  00416C61  ^7C F2             JL SHORT lcsebody.00416C55
     *  00416C63   EB 06             JMP SHORT lcsebody.00416C6B
     *  00416C65   FF86 24050000     INC DWORD PTR DS:[ESI+0x524]
     *  00416C6B   3ACB              CMP CL,BL
     *  00416C6D   74 15             JE SHORT lcsebody.00416C84
     *  00416C6F   B8 9CF14800       MOV EAX,lcsebody.0048F19C
     *  00416C74   3B38              CMP EDI,DWORD PTR DS:[EAX]
     *  00416C76   74 21             JE SHORT lcsebody.00416C99
     *  00416C78   83C0 04           ADD EAX,0x4
     *  00416C7B   3D A8F14800       CMP EAX,lcsebody.0048F1A8
     *  00416C80  ^7C F2             JL SHORT lcsebody.00416C74
     *  00416C82   EB 2A             JMP SHORT lcsebody.00416CAE
     *  00416C84   B8 7CF14800       MOV EAX,lcsebody.0048F17C
     *  00416C89   3B38              CMP EDI,DWORD PTR DS:[EAX]
     *  00416C8B   74 0C             JE SHORT lcsebody.00416C99
     *  00416C8D   83C0 04           ADD EAX,0x4
     *  00416C90   3D 9CF14800       CMP EAX,lcsebody.0048F19C
     *  00416C95  ^7C F2             JL SHORT lcsebody.00416C89
     *  00416C97   EB 15             JMP SHORT lcsebody.00416CAE
     *  00416C99   8B86 24050000     MOV EAX,DWORD PTR DS:[ESI+0x524]
     *  00416C9F   48                DEC EAX
     *  00416CA0   8986 24050000     MOV DWORD PTR DS:[ESI+0x524],EAX
     *  00416CA6   79 06             JNS SHORT lcsebody.00416CAE
     *  00416CA8   899E 24050000     MOV DWORD PTR DS:[ESI+0x524],EBX
     *  00416CAE   57                PUSH EDI
     *  00416CAF   8BCE              MOV ECX,ESI
     *  00416CB1   E8 20A5FEFF       CALL lcsebody.004011D6
     *  00416CB6   8B86 EC000000     MOV EAX,DWORD PTR DS:[ESI+0xEC]
     *  00416CBC   8A9430 08010000   MOV DL,BYTE PTR DS:[EAX+ESI+0x108]
     *  00416CC3   83C0 02           ADD EAX,0x2
     *  00416CC6   885424 0C         MOV BYTE PTR SS:[ESP+0xC],DL
     *  00416CCA   8A8C30 07010000   MOV CL,BYTE PTR DS:[EAX+ESI+0x107]
     *  00416CD1   884C24 0D         MOV BYTE PTR SS:[ESP+0xD],CL
     *  00416CD5   885C24 0E         MOV BYTE PTR SS:[ESP+0xE],BL
     *  00416CD9   E9 77010000       JMP lcsebody.00416E55
     *  00416CDE   8B96 EC000000     MOV EDX,DWORD PTR DS:[ESI+0xEC]
     *  00416CE4   C686 20050000 01  MOV BYTE PTR DS:[ESI+0x520],0x1
     *  00416CEB   8A8C16 08010000   MOV CL,BYTE PTR DS:[ESI+EDX+0x108]
     *  00416CF2   8D8416 08010000   LEA EAX,DWORD PTR DS:[ESI+EDX+0x108]
     *  00416CF9   80F9 1F           CMP CL,0x1F
     *  00416CFC   77 54             JA SHORT lcsebody.00416D52
     *  00416CFE   80F9 03           CMP CL,0x3
     *  00416D01   75 06             JNZ SHORT lcsebody.00416D09
     *  00416D03   899E 28050000     MOV DWORD PTR DS:[ESI+0x528],EBX
     *  00416D09   8A00              MOV AL,BYTE PTR DS:[EAX]
     *  00416D0B   83EC 0C           SUB ESP,0xC
     *  00416D0E   8D5424 18         LEA EDX,DWORD PTR SS:[ESP+0x18]
     *  00416D12   8BCC              MOV ECX,ESP
     *  00416D14   896424 1C         MOV DWORD PTR SS:[ESP+0x1C],ESP
     *  00416D18   8DBE FC000000     LEA EDI,DWORD PTR DS:[ESI+0xFC]
     *  00416D1E   52                PUSH EDX
     *  00416D1F   51                PUSH ECX
     *  00416D20   8BCF              MOV ECX,EDI
     *  00416D22   884424 20         MOV BYTE PTR SS:[ESP+0x20],AL
     *  00416D26   885C24 21         MOV BYTE PTR SS:[ESP+0x21],BL
     *  00416D2A   E8 D0A8FEFF       CALL lcsebody.004015FF
     *  00416D2F   8BCF              MOV ECX,EDI
     *  00416D31   E8 A1A8FEFF       CALL lcsebody.004015D7
     *  00416D36   8B8E EC000000     MOV ECX,DWORD PTR DS:[ESI+0xEC]
     *  00416D3C   0FBE8431 0801000> MOVSX EAX,BYTE PTR DS:[ECX+ESI+0x108]
     *  00416D44   41                INC ECX
     *  00416D45   898E EC000000     MOV DWORD PTR DS:[ESI+0xEC],ECX
     *  00416D4B   5F                POP EDI
     *  00416D4C   5E                POP ESI
     *  00416D4D   5B                POP EBX
     *  00416D4E   83C4 08           ADD ESP,0x8
     *  00416D51   C3                RETN
     *  00416D52   8BCE              MOV ECX,ESI
     *  00416D54   E8 9DACFEFF       CALL lcsebody.004019F6
     *  00416D59   3BC3              CMP EAX,EBX
     *  00416D5B   74 4A             JE SHORT lcsebody.00416DA7
     *  00416D5D   389E 2C050000     CMP BYTE PTR DS:[ESI+0x52C],BL
     *  00416D63   0F84 24010000     JE lcsebody.00416E8D
     *  00416D69   389E 20050000     CMP BYTE PTR DS:[ESI+0x520],BL
     *  00416D6F   74 1B             JE SHORT lcsebody.00416D8C
     *  00416D71   B9 34F14800       MOV ECX,lcsebody.0048F134
     *  00416D76   3919              CMP DWORD PTR DS:[ECX],EBX
     *  00416D78   74 2D             JE SHORT lcsebody.00416DA7
     *  00416D7A   83C1 04           ADD ECX,0x4
     *  00416D7D   81F9 50F14800     CMP ECX,lcsebody.0048F150
     *  00416D83  ^7C F1             JL SHORT lcsebody.00416D76
     *  00416D85   5F                POP EDI
     *  00416D86   5E                POP ESI
     *  00416D87   5B                POP EBX
     *  00416D88   83C4 08           ADD ESP,0x8
     *  00416D8B   C3                RETN
     *  00416D8C   B9 00F14800       MOV ECX,lcsebody.0048F100
     *  00416D91   3919              CMP DWORD PTR DS:[ECX],EBX
     *  00416D93   74 12             JE SHORT lcsebody.00416DA7
     *  00416D95   83C1 04           ADD ECX,0x4
     *  00416D98   81F9 34F14800     CMP ECX,lcsebody.0048F134
     *  00416D9E  ^7C F1             JL SHORT lcsebody.00416D91
     *  00416DA0   5F                POP EDI
     *  00416DA1   5E                POP ESI
     *  00416DA2   5B                POP EBX
     *  00416DA3   83C4 08           ADD ESP,0x8
     *  00416DA6   C3                RETN
     *  00416DA7   8B86 EC000000     MOV EAX,DWORD PTR DS:[ESI+0xEC]
     *  00416DAD   8A96 20050000     MOV DL,BYTE PTR DS:[ESI+0x520]
     *  00416DB3   0FBEBC06 08010000 MOVSX EDI,BYTE PTR DS:[ESI+EAX+0x108]	; jichi: edi get assigned to the illegal character
     *  00416DBB   8BCF              MOV ECX,EDI
     *  00416DBD   C1E1 08           SHL ECX,0x8
     *  00416DC0   3AD3              CMP DL,BL
     *  00416DC2   74 15             JE SHORT lcsebody.00416DD9
     *  00416DC4   B8 70F14800       MOV EAX,lcsebody.0048F170
     *  00416DC9   3B08              CMP ECX,DWORD PTR DS:[EAX]
     *  00416DCB   74 21             JE SHORT lcsebody.00416DEE
     *  00416DCD   83C0 04           ADD EAX,0x4
     *  00416DD0   3D 7CF14800       CMP EAX,lcsebody.0048F17C
     *  00416DD5  ^7C F2             JL SHORT lcsebody.00416DC9
     *  00416DD7   EB 1B             JMP SHORT lcsebody.00416DF4
     *  00416DD9   B8 50F14800       MOV EAX,lcsebody.0048F150
     *  00416DDE   3B08              CMP ECX,DWORD PTR DS:[EAX]
     *  00416DE0   74 0C             JE SHORT lcsebody.00416DEE
     *  00416DE2   83C0 04           ADD EAX,0x4
     *  00416DE5   3D 70F14800       CMP EAX,lcsebody.0048F170
     *  00416DEA  ^7C F2             JL SHORT lcsebody.00416DDE
     *  00416DEC   EB 06             JMP SHORT lcsebody.00416DF4
     *  00416DEE   FF86 24050000     INC DWORD PTR DS:[ESI+0x524]
     *  00416DF4   3AD3              CMP DL,BL
     *  00416DF6   74 15             JE SHORT lcsebody.00416E0D
     *  00416DF8   B8 9CF14800       MOV EAX,lcsebody.0048F19C
     *  00416DFD   3B08              CMP ECX,DWORD PTR DS:[EAX]
     *  00416DFF   74 21             JE SHORT lcsebody.00416E22
     *  00416E01   83C0 04           ADD EAX,0x4
     *  00416E04   3D A8F14800       CMP EAX,lcsebody.0048F1A8
     *  00416E09  ^7C F2             JL SHORT lcsebody.00416DFD
     *  00416E0B   EB 2A             JMP SHORT lcsebody.00416E37
     *  00416E0D   B8 7CF14800       MOV EAX,lcsebody.0048F17C
     *  00416E12   3B08              CMP ECX,DWORD PTR DS:[EAX]
     *  00416E14   74 0C             JE SHORT lcsebody.00416E22
     *  00416E16   83C0 04           ADD EAX,0x4
     *  00416E19   3D 9CF14800       CMP EAX,lcsebody.0048F19C
     *  00416E1E  ^7C F2             JL SHORT lcsebody.00416E12
     *  00416E20   EB 15             JMP SHORT lcsebody.00416E37
     *  00416E22   8B86 24050000     MOV EAX,DWORD PTR DS:[ESI+0x524]
     *  00416E28   48                DEC EAX
     *  00416E29   8986 24050000     MOV DWORD PTR DS:[ESI+0x524],EAX
     *  00416E2F   79 06             JNS SHORT lcsebody.00416E37
     *  00416E31   899E 24050000     MOV DWORD PTR DS:[ESI+0x524],EBX
     *  00416E37   57                PUSH EDI	; jichi: invalid character
     *  00416E38   8BCE              MOV ECX,ESI
     *  00416E3A   E8 97A3FEFF       CALL lcsebody.004011D6	; jichi: char in arg1
     *  00416E3F   8B86 EC000000     MOV EAX,DWORD PTR DS:[ESI+0xEC]
     */

    ULONG patchEncoding(ULONG startAddress, ULONG stopAddress)
    {
      const uint8_t bytes[] = {
          0x8b, 0x4c, 0x24, 0x04, // 0040a380   8b4c24 04                              mov ecx,dword ptr ss:[esp+0x4]
          0x8a, 0x01,             // 0040a384   8a01                                   mov al,byte ptr ds:[ecx]
          0x8a, 0x49, 0x01,       // 0040a386   8a49 01                                mov cl,byte ptr ds:[ecx+0x1]
          0x3c, 0x81              // 0040a389   3c 81                                  cmp al,0x81
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      return addr; // && winhook::replace_fun(addr, (ULONG)Private::isLeadByteChar);
    }

  } // namespace Patch
} // unnamed namespace

bool LCScript::attach_function()
{

  if (!ScenarioHook::attach(processStartAddress, processStopAddress, Patch::patchEncoding(processStartAddress, processStopAddress)))
    return false;

  return true;
}