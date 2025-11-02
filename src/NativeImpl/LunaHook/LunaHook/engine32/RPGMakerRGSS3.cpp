#include "RPGMakerRGSS3.h"
namespace
{ // unnamed

  namespace RGSS3
  {

    namespace Private
    {
      std::vector<std::wstring> glob(const std::wstring &relpath)
      {
        std::wstring path = std::wstring(MAX_PATH, 0);
        GetModuleFileNameW(nullptr, &path[0], MAX_PATH);

        size_t i = relpath.rfind(L'/');
        if (i != std::wstring::npos)
        {
          std::wstring dir_path = path + L"/" + relpath.substr(0, i);
          WIN32_FIND_DATAW find_data;
          HANDLE hFind = FindFirstFileW((dir_path + L"/*").c_str(), &find_data);
          if (hFind == INVALID_HANDLE_VALUE)
            return {};

          std::vector<std::wstring> results;
          do
          {
            if ((find_data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) ||
                PathMatchSpecW(find_data.cFileName, relpath.substr(i + 1).c_str()))
            {
              results.push_back(dir_path + L"/" + find_data.cFileName);
            }
          } while (FindNextFileW(hFind, &find_data));
          FindClose(hFind);

          return results;
        }
        else
        {
          WIN32_FIND_DATAW find_data;
          HANDLE hFind = FindFirstFileW(relpath.c_str(), &find_data);
          if (hFind == INVALID_HANDLE_VALUE)
            return {};

          std::vector<std::wstring> results;
          do
          {
            if (!(find_data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY))
              results.push_back(find_data.cFileName);
          } while (FindNextFileW(hFind, &find_data));
          FindClose(hFind);

          return results;
        }
      }
      std::wstring getDllModuleName()
      {
        for (const auto &dll : glob(L"System/RGSS3*.dll"))
          if (::GetModuleHandleW((LPCWSTR)dll.c_str()))
            return dll;
        return {};
      }

    } // namespace Private

    bool getMemoryRange(ULONG *startAddress, ULONG *stopAddress)
    {
      std::wstring module = Private::getDllModuleName();
      if (module.empty())
        return false;
      auto [_1, _2] = Util::QueryModuleLimits(GetModuleHandle(module.c_str()));
      *startAddress = _1;
      *stopAddress = _2;
      return 1;
    }

    namespace ScenarioHook
    {

      /**
       *  Sample game:
       *  - Mogeko Castle with RGSS 3.01
       *  - 魔鎧の少女騎士エルトリンデ with RGSS 3.02
       *
       *  1004149D   CC               INT3
       *  1004149E   CC               INT3
       *  1004149F   CC               INT3
       *  100414A0   8B4C24 08        MOV ECX,DWORD PTR SS:[ESP+0x8]
       *  100414A4   8BC1             MOV EAX,ECX
       *  100414A6   E8 75030500      CALL RGSS301.10091820
       *  100414AB   83F8 05          CMP EAX,0x5
       *  100414AE   74 19            JE SHORT RGSS301.100414C9
       *  100414B0   68 649D1A10      PUSH RGSS301.101A9D64                    ; ASCII "to_str"
       *  100414B5   68 74931A10      PUSH RGSS301.101A9374                    ; ASCII "String"
       *  100414BA   6A 05            PUSH 0x5
       *  100414BC   51               PUSH ECX
       *  100414BD   E8 AE2FFFFF      CALL RGSS301.10034470
       *  100414C2   83C4 10          ADD ESP,0x10
       *  100414C5   894424 08        MOV DWORD PTR SS:[ESP+0x8],EAX
       *  100414C9   53               PUSH EBX
       *  100414CA   55               PUSH EBP
       *  100414CB   56               PUSH ESI
       *  100414CC   8B7424 10        MOV ESI,DWORD PTR SS:[ESP+0x10]
       *  100414D0   57               PUSH EDI
       *  100414D1   8B7C24 18        MOV EDI,DWORD PTR SS:[ESP+0x18]
       *  100414D5   57               PUSH EDI
       *  100414D6   56               PUSH ESI
       *  100414D7   E8 B4490100      CALL RGSS301.10055E90
       *  100414DC   8BE8             MOV EBP,EAX
       *  100414DE   8B06             MOV EAX,DWORD PTR DS:[ESI]
       *  100414E0   83C4 08          ADD ESP,0x8
       *  100414E3   A9 00200000      TEST EAX,0x2000
       *  100414E8   75 08            JNZ SHORT RGSS301.100414F2
       *  100414EA   C1E8 0E          SHR EAX,0xE
       *  100414ED   83E0 1F          AND EAX,0x1F
       *  100414F0   EB 03            JMP SHORT RGSS301.100414F5
       *  100414F2   8B46 08          MOV EAX,DWORD PTR DS:[ESI+0x8]
       *  100414F5   8B0F             MOV ECX,DWORD PTR DS:[EDI]
       *  100414F7   F7C1 00200000    TEST ECX,0x2000
       *  100414FD   75 08            JNZ SHORT RGSS301.10041507
       *  100414FF   C1E9 0E          SHR ECX,0xE
       *  10041502   83E1 1F          AND ECX,0x1F
       *  10041505   EB 03            JMP SHORT RGSS301.1004150A
       *  10041507   8B4F 08          MOV ECX,DWORD PTR DS:[EDI+0x8]
       *  1004150A   8D3401           LEA ESI,DWORD PTR DS:[ECX+EAX]
       *  1004150D   A1 70C02A10      MOV EAX,DWORD PTR DS:[0x102AC070]
       *  10041512   50               PUSH EAX
       *  10041513   33FF             XOR EDI,EDI
       *  10041515   E8 B64EFFFF      CALL RGSS301.100363D0
       *  1004151A   8B5424 18        MOV EDX,DWORD PTR SS:[ESP+0x18] ; jichi: edx = arg1 on the stack
       *  1004151E   8BD8             MOV EBX,EAX
       *  10041520   8B02             MOV EAX,DWORD PTR DS:[EDX]  ; jichi: eax = ecx = [arg1]
       *  10041522   8BC8             MOV ECX,EAX
       *  10041524   83C4 04          ADD ESP,0x4
       *  10041527   81E1 00200000    AND ECX,0x2000
       *  1004152D   75 08            JNZ SHORT RGSS301.10041537
       *  1004152F   C1E8 0E          SHR EAX,0xE
       *  10041532   83E0 1F          AND EAX,0x1F
       *  10041535   EB 03            JMP SHORT RGSS301.1004153A
       *  10041537   8B42 08          MOV EAX,DWORD PTR DS:[EDX+0x8] ; jichi: [edx+0x8] text length
       *  1004153A   85C9             TEST ECX,ECX
       *  1004153C   75 05            JNZ SHORT RGSS301.10041543
       *  1004153E   83C2 08          ADD EDX,0x8
       *  10041541   EB 03            JMP SHORT RGSS301.10041546
       *  10041543   8B52 0C          MOV EDX,DWORD PTR DS:[EDX+0xC] ; jichi: [edx + 0xc] could be the text address
       *  10041546   F703 00200000    TEST DWORD PTR DS:[EBX],0x2000
       *  1004154C   8D4B 08          LEA ECX,DWORD PTR DS:[EBX+0x8]
       *  1004154F   74 03            JE SHORT RGSS301.10041554
       *  10041551   8B4B 0C          MOV ECX,DWORD PTR DS:[EBX+0xC]
       *  10041554   50               PUSH EAX
       *  10041555   52               PUSH EDX
       *  10041556   51               PUSH ECX
       *  10041557   E8 E4F21300      CALL RGSS301.10180840   ; jichi: text is in edx
       *  1004155C   8B5424 24        MOV EDX,DWORD PTR SS:[ESP+0x24]
       *  10041560   8B02             MOV EAX,DWORD PTR DS:[EDX]
       *  10041562   8BC8             MOV ECX,EAX
       *  10041564   83C4 0C          ADD ESP,0xC
       *  10041567   81E1 00200000    AND ECX,0x2000
       *  1004156D   75 08            JNZ SHORT RGSS301.10041577
       *
       *  Stack:
       *  00828EB4   1002E5E6  RETURN to RGSS301.1002E5E6 from RGSS301.100414A0
       *  00828EB8   03F13B20
       *  00828EBC   069F42CC
       *  00828EC0   00000000
       *  00828EC4   01699298
       *  00828EC8   01699298
       *  00828ECC   03EB41B8
       *  00828ED0   01692A00
       *  00828ED4   06A34548
       *  00828ED8   00000000
       *  00828EDC   00000168
       *  00828EE0   00000280
       *  00828EE4   000001E0
       *  00828EE8   1019150F  RETURN to RGSS301.1019150F from RGSS301.1018DF45
       *
       *  Here's the strncpy-like function for UTF8 strings, which is found using hardware breakpoints
       *  Parameters:
       *  - arg1 char *dest
       *  - arg2 const char *src
       *  - arg3 size_t size  length of src excluding \0 at the end
       *
       *  1018083A   CC               INT3
       *  1018083B   CC               INT3
       *  1018083C   CC               INT3
       *  1018083D   CC               INT3
       *  1018083E   CC               INT3
       *  1018083F   CC               INT3
       *  10180840   55               PUSH EBP
       *  10180841   8BEC             MOV EBP,ESP
       *  10180843   57               PUSH EDI
       *  10180844   56               PUSH ESI
       *  10180845   8B75 0C          MOV ESI,DWORD PTR SS:[EBP+0xC]
       *  10180848   8B4D 10          MOV ECX,DWORD PTR SS:[EBP+0x10]
       *  1018084B   8B7D 08          MOV EDI,DWORD PTR SS:[EBP+0x8]
       *  1018084E   8BC1             MOV EAX,ECX
       *  10180850   8BD1             MOV EDX,ECX
       *  10180852   03C6             ADD EAX,ESI
       *  10180854   3BFE             CMP EDI,ESI
       *  10180856   76 08            JBE SHORT RGSS301.10180860
       *  10180858   3BF8             CMP EDI,EAX
       *  1018085A   0F82 A4010000    JB RGSS301.10180A04
       *  10180860   81F9 00010000    CMP ECX,0x100
       *  10180866   72 1F            JB SHORT RGSS301.10180887
       *  10180868   833D 4CC12A10 00 CMP DWORD PTR DS:[0x102AC14C],0x0
       *  1018086F   74 16            JE SHORT RGSS301.10180887
       *  10180871   57               PUSH EDI
       *  10180872   56               PUSH ESI
       *  10180873   83E7 0F          AND EDI,0xF
       *  10180876   83E6 0F          AND ESI,0xF
       *  10180879   3BFE             CMP EDI,ESI
       *  1018087B   5E               POP ESI
       *  1018087C   5F               POP EDI
       *  1018087D   75 08            JNZ SHORT RGSS301.10180887
       *  1018087F   5E               POP ESI
       *  10180880   5F               POP EDI
       *  10180881   5D               POP EBP
       *  10180882   E9 05F80000      JMP RGSS301.1019008C
       *  10180887   F7C7 03000000    TEST EDI,0x3
       *  1018088D   75 15            JNZ SHORT RGSS301.101808A4
       *  1018088F   C1E9 02          SHR ECX,0x2
       *  10180892   83E2 03          AND EDX,0x3
       *  10180895   83F9 08          CMP ECX,0x8
       *  10180898   72 2A            JB SHORT RGSS301.101808C4
       *  1018089A   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
       *  1018089C   FF2495 B4091810  JMP DWORD PTR DS:[EDX*4+0x101809B4]
       *  101808A3   90               NOP
       *  101808A4   8BC7             MOV EAX,EDI
       *  101808A6   BA 03000000      MOV EDX,0x3
       *  101808AB   83E9 04          SUB ECX,0x4
       *  101808AE   72 0C            JB SHORT RGSS301.101808BC
       *  101808B0   83E0 03          AND EAX,0x3
       *  101808B3   03C8             ADD ECX,EAX
       *  101808B5   FF2485 C8081810  JMP DWORD PTR DS:[EAX*4+0x101808C8]
       *  101808BC   FF248D C4091810  JMP DWORD PTR DS:[ECX*4+0x101809C4]
       *  101808C3   90               NOP
       *  101808C4   FF248D 48091810  JMP DWORD PTR DS:[ECX*4+0x10180948]
       *  101808CB   90               NOP
       *  101808CC   D808             FMUL DWORD PTR DS:[EAX]
       *  101808CE   1810             SBB BYTE PTR DS:[EAX],DL
       *  101808D0   04 09            ADD AL,0x9
       *  101808D2   1810             SBB BYTE PTR DS:[EAX],DL
       *  101808D4   2809             SUB BYTE PTR DS:[ECX],CL
       *  101808D6   1810             SBB BYTE PTR DS:[EAX],DL
       *  101808D8   23D1             AND EDX,ECX
       *  101808DA   8A06             MOV AL,BYTE PTR DS:[ESI]
       *  101808DC   8807             MOV BYTE PTR DS:[EDI],AL
       *  101808DE   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
       *  101808E1   8847 01          MOV BYTE PTR DS:[EDI+0x1],AL
       *  101808E4   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
       *  101808E7   C1E9 02          SHR ECX,0x2
       *  101808EA   8847 02          MOV BYTE PTR DS:[EDI+0x2],AL
       *  101808ED   83C6 03          ADD ESI,0x3
       *  101808F0   83C7 03          ADD EDI,0x3
       *  101808F3   83F9 08          CMP ECX,0x8
       *  101808F6  ^72 CC            JB SHORT RGSS301.101808C4
       *  101808F8   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
       *  101808FA   FF2495 B4091810  JMP DWORD PTR DS:[EDX*4+0x101809B4]
       *  10180901   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
       *  10180904   23D1             AND EDX,ECX
       *  10180906   8A06             MOV AL,BYTE PTR DS:[ESI]
       *  10180908   8807             MOV BYTE PTR DS:[EDI],AL
       *  1018090A   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
       *  1018090D   C1E9 02          SHR ECX,0x2
       *  10180910   8847 01          MOV BYTE PTR DS:[EDI+0x1],AL
       *  10180913   83C6 02          ADD ESI,0x2
       *  10180916   83C7 02          ADD EDI,0x2
       *  10180919   83F9 08          CMP ECX,0x8
       *  1018091C  ^72 A6            JB SHORT RGSS301.101808C4
       *  1018091E   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
       *  10180920   FF2495 B4091810  JMP DWORD PTR DS:[EDX*4+0x101809B4]
       *  10180927   90               NOP
       *  10180928   23D1             AND EDX,ECX
       *  1018092A   8A06             MOV AL,BYTE PTR DS:[ESI]
       *  1018092C   8807             MOV BYTE PTR DS:[EDI],AL
       *  1018092E   83C6 01          ADD ESI,0x1
       *  10180931   C1E9 02          SHR ECX,0x2
       *  10180934   83C7 01          ADD EDI,0x1
       *  10180937   83F9 08          CMP ECX,0x8
       *  1018093A  ^72 88            JB SHORT RGSS301.101808C4
       *  1018093C   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
       *  1018093E   FF2495 B4091810  JMP DWORD PTR DS:[EDX*4+0x101809B4]
       *  10180945   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
       *  10180948   AB               STOS DWORD PTR ES:[EDI]
       *  10180949   0918             OR DWORD PTR DS:[EAX],EBX
       *  1018094B   1098 09181090    ADC BYTE PTR DS:[EAX+0x90101809],BL
       *  10180951   0918             OR DWORD PTR DS:[EAX],EBX
       *  10180953   1088 09181080    ADC BYTE PTR DS:[EAX+0x80101809],CL
       *  10180959   0918             OR DWORD PTR DS:[EAX],EBX
       *  1018095B   1078 09          ADC BYTE PTR DS:[EAX+0x9],BH
       *  1018095E   1810             SBB BYTE PTR DS:[EAX],DL
       *  10180960   70 09            JO SHORT RGSS301.1018096B
       *  10180962   1810             SBB BYTE PTR DS:[EAX],DL
       *  10180964   68 0918108B      PUSH 0x8B101809
       *  10180969   44               INC ESP
       *  1018096A   8EE4             MOV FS,SP                                ; Modification of segment register
       *  1018096C   89448F E4        MOV DWORD PTR DS:[EDI+ECX*4-0x1C],EAX
       *  10180970   8B448E E8        MOV EAX,DWORD PTR DS:[ESI+ECX*4-0x18]
       *  10180974   89448F E8        MOV DWORD PTR DS:[EDI+ECX*4-0x18],EAX
       *  10180978   8B448E EC        MOV EAX,DWORD PTR DS:[ESI+ECX*4-0x14]
       *  1018097C   89448F EC        MOV DWORD PTR DS:[EDI+ECX*4-0x14],EAX
       *  10180980   8B448E F0        MOV EAX,DWORD PTR DS:[ESI+ECX*4-0x10]
       *  10180984   89448F F0        MOV DWORD PTR DS:[EDI+ECX*4-0x10],EAX
       *  10180988   8B448E F4        MOV EAX,DWORD PTR DS:[ESI+ECX*4-0xC]
       *  1018098C   89448F F4        MOV DWORD PTR DS:[EDI+ECX*4-0xC],EAX
       *  10180990   8B448E F8        MOV EAX,DWORD PTR DS:[ESI+ECX*4-0x8]
       *  10180994   89448F F8        MOV DWORD PTR DS:[EDI+ECX*4-0x8],EAX
       *  10180998   8B448E FC        MOV EAX,DWORD PTR DS:[ESI+ECX*4-0x4]
       *  1018099C   89448F FC        MOV DWORD PTR DS:[EDI+ECX*4-0x4],EAX
       *  101809A0   8D048D 00000000  LEA EAX,DWORD PTR DS:[ECX*4]
       *  101809A7   03F0             ADD ESI,EAX
       *  101809A9   03F8             ADD EDI,EAX
       *  101809AB   FF2495 B4091810  JMP DWORD PTR DS:[EDX*4+0x101809B4]
       *  101809B2   8BFF             MOV EDI,EDI
       *  101809B4   C409             LES ECX,FWORD PTR DS:[ECX]               ; Modification of segment register
       *  101809B6   1810             SBB BYTE PTR DS:[EAX],DL
       *  101809B8   CC               INT3
       *  101809B9   0918             OR DWORD PTR DS:[EAX],EBX
       *  101809BB   10D8             ADC AL,BL
       *  101809BD   0918             OR DWORD PTR DS:[EAX],EBX
       *  101809BF   10EC             ADC AH,CH
       *  101809C1   0918             OR DWORD PTR DS:[EAX],EBX
       *  101809C3   108B 45085E5F    ADC BYTE PTR DS:[EBX+0x5F5E0845],CL
       *  101809C9   C9               LEAVE
       *  101809CA   C3               RETN
       *  101809CB   90               NOP
       *  101809CC   8A06             MOV AL,BYTE PTR DS:[ESI]
       *  101809CE   8807             MOV BYTE PTR DS:[EDI],AL
       *  101809D0   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
       *  101809D3   5E               POP ESI
       *  101809D4   5F               POP EDI
       *  101809D5   C9               LEAVE
       *  101809D6   C3               RETN
       *  101809D7   90               NOP
       *  101809D8   8A06             MOV AL,BYTE PTR DS:[ESI]
       *  101809DA   8807             MOV BYTE PTR DS:[EDI],AL
       *  101809DC   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
       *  101809DF   8847 01          MOV BYTE PTR DS:[EDI+0x1],AL
       *  101809E2   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
       *  101809E5   5E               POP ESI
       *  101809E6   5F               POP EDI
       *  101809E7   C9               LEAVE
       *  101809E8   C3               RETN
       *  101809E9   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
       *  101809EC   8A06             MOV AL,BYTE PTR DS:[ESI]
       *  101809EE   8807             MOV BYTE PTR DS:[EDI],AL
       *  101809F0   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
       *  101809F3   8847 01          MOV BYTE PTR DS:[EDI+0x1],AL
       *  101809F6   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
       *  101809F9   8847 02          MOV BYTE PTR DS:[EDI+0x2],AL
       *  101809FC   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
       *  101809FF   5E               POP ESI
       *  10180A00   5F               POP EDI
       *  10180A01   C9               LEAVE
       *  10180A02   C3               RETN
       *  10180A03   90               NOP
       *  10180A04   8D7431 FC        LEA ESI,DWORD PTR DS:[ECX+ESI-0x4]
       *  10180A08   8D7C39 FC        LEA EDI,DWORD PTR DS:[ECX+EDI-0x4]
       *  10180A0C   F7C7 03000000    TEST EDI,0x3
       *  10180A12   75 24            JNZ SHORT RGSS301.10180A38
       *  10180A14   C1E9 02          SHR ECX,0x2
       *  10180A17   83E2 03          AND EDX,0x3
       *  10180A1A   83F9 08          CMP ECX,0x8
       *  10180A1D   72 0D            JB SHORT RGSS301.10180A2C
       *  10180A1F   FD               STD
       *  10180A20   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
       *  10180A22   FC               CLD
       *  10180A23   FF2495 500B1810  JMP DWORD PTR DS:[EDX*4+0x10180B50]
       *  10180A2A   8BFF             MOV EDI,EDI
       *  10180A2C   F7D9             NEG ECX
       *  10180A2E   FF248D 000B1810  JMP DWORD PTR DS:[ECX*4+0x10180B00]
       *  10180A35   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
       *  10180A38   8BC7             MOV EAX,EDI
       *  10180A3A   BA 03000000      MOV EDX,0x3
       *  10180A3F   83F9 04          CMP ECX,0x4
       *  10180A42   72 0C            JB SHORT RGSS301.10180A50
       *  10180A44   83E0 03          AND EAX,0x3
       *  10180A47   2BC8             SUB ECX,EAX
       *  10180A49   FF2485 540A1810  JMP DWORD PTR DS:[EAX*4+0x10180A54]
       *  10180A50   FF248D 500B1810  JMP DWORD PTR DS:[ECX*4+0x10180B50]
       *  10180A57   90               NOP
       *  10180A58   64:0A18          OR BL,BYTE PTR FS:[EAX]
       *  10180A5B   1088 0A1810B0    ADC BYTE PTR DS:[EAX+0xB010180A],CL
       *  10180A61   0A18             OR BL,BYTE PTR DS:[EAX]
       *  10180A63   108A 460323D1    ADC BYTE PTR DS:[EDX+0xD1230346],CL
       *  10180A69   8847 03          MOV BYTE PTR DS:[EDI+0x3],AL
       *  10180A6C   83EE 01          SUB ESI,0x1
       *  10180A6F   C1E9 02          SHR ECX,0x2
       *  10180A72   83EF 01          SUB EDI,0x1
       *  10180A75   83F9 08          CMP ECX,0x8
       *  10180A78  ^72 B2            JB SHORT RGSS301.10180A2C
       *  10180A7A   FD               STD
       *  10180A7B   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
       *  10180A7D   FC               CLD
       *  10180A7E   FF2495 500B1810  JMP DWORD PTR DS:[EDX*4+0x10180B50]
       *  10180A85   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
       *  10180A88   8A46 03          MOV AL,BYTE PTR DS:[ESI+0x3]
       *  10180A8B   23D1             AND EDX,ECX
       *  10180A8D   8847 03          MOV BYTE PTR DS:[EDI+0x3],AL
       *  10180A90   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
       *  10180A93   C1E9 02          SHR ECX,0x2
       *  10180A96   8847 02          MOV BYTE PTR DS:[EDI+0x2],AL
       *  10180A99   83EE 02          SUB ESI,0x2
       *  10180A9C   83EF 02          SUB EDI,0x2
       *  10180A9F   83F9 08          CMP ECX,0x8
       *  10180AA2  ^72 88            JB SHORT RGSS301.10180A2C
       *  10180AA4   FD               STD
       *  10180AA5   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
       *  10180AA7   FC               CLD
       *  10180AA8   FF2495 500B1810  JMP DWORD PTR DS:[EDX*4+0x10180B50]
       *  10180AAF   90               NOP
       *  10180AB0   8A46 03          MOV AL,BYTE PTR DS:[ESI+0x3]
       *  10180AB3   23D1             AND EDX,ECX
       *  10180AB5   8847 03          MOV BYTE PTR DS:[EDI+0x3],AL
       *  10180AB8   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
       *  10180ABB   8847 02          MOV BYTE PTR DS:[EDI+0x2],AL
       *  10180ABE   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
       *  10180AC1   C1E9 02          SHR ECX,0x2
       *  10180AC4   8847 01          MOV BYTE PTR DS:[EDI+0x1],AL
       *  10180AC7   83EE 03          SUB ESI,0x3
       *  10180ACA   83EF 03          SUB EDI,0x3
       *  10180ACD   83F9 08          CMP ECX,0x8
       *  10180AD0  ^0F82 56FFFFFF    JB RGSS301.10180A2C
       *  10180AD6   FD               STD
       *  10180AD7   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
       *  10180AD9   FC               CLD
       *  10180ADA   FF2495 500B1810  JMP DWORD PTR DS:[EDX*4+0x10180B50]
       *  10180AE1   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
       *  10180AE4   04 0B            ADD AL,0xB
       *  10180AE6   1810             SBB BYTE PTR DS:[EAX],DL
       *  10180AE8   0C 0B            OR AL,0xB
       *  10180AEA   1810             SBB BYTE PTR DS:[EAX],DL
       *  10180AEC   14 0B            ADC AL,0xB
       *  10180AEE   1810             SBB BYTE PTR DS:[EAX],DL
       *  10180AF0   1C 0B            SBB AL,0xB
       *  10180AF2   1810             SBB BYTE PTR DS:[EAX],DL
       *  10180AF4   24 0B            AND AL,0xB
       *  10180AF6   1810             SBB BYTE PTR DS:[EAX],DL
       *  10180AF8   2C 0B            SUB AL,0xB
       *  10180AFA   1810             SBB BYTE PTR DS:[EAX],DL
       *  10180AFC   34 0B            XOR AL,0xB
       *  10180AFE   1810             SBB BYTE PTR DS:[EAX],DL
       *  10180B00   47               INC EDI
       *  10180B01   0B18             OR EBX,DWORD PTR DS:[EAX]
       *  10180B03   108B 448E1C89    ADC BYTE PTR DS:[EBX+0x891C8E44],CL
       *  10180B09   44               INC ESP
       *  10180B0A   8F               ???                                      ; Unknown command
       *  10180B0B   1C 8B            SBB AL,0x8B
       *  10180B0D   44               INC ESP
       *  10180B0E   8E18             MOV DS,WORD PTR DS:[EAX]                 ; Modification of segment register
       *  10180B10   89448F 18        MOV DWORD PTR DS:[EDI+ECX*4+0x18],EAX
       *  10180B14   8B448E 14        MOV EAX,DWORD PTR DS:[ESI+ECX*4+0x14]
       *  10180B18   89448F 14        MOV DWORD PTR DS:[EDI+ECX*4+0x14],EAX
       *  10180B1C   8B448E 10        MOV EAX,DWORD PTR DS:[ESI+ECX*4+0x10]
       *  10180B20   89448F 10        MOV DWORD PTR DS:[EDI+ECX*4+0x10],EAX
       *  10180B24   8B448E 0C        MOV EAX,DWORD PTR DS:[ESI+ECX*4+0xC]
       *  10180B28   89448F 0C        MOV DWORD PTR DS:[EDI+ECX*4+0xC],EAX
       *  10180B2C   8B448E 08        MOV EAX,DWORD PTR DS:[ESI+ECX*4+0x8]
       *  10180B30   89448F 08        MOV DWORD PTR DS:[EDI+ECX*4+0x8],EAX
       *  10180B34   8B448E 04        MOV EAX,DWORD PTR DS:[ESI+ECX*4+0x4]
       *  10180B38   89448F 04        MOV DWORD PTR DS:[EDI+ECX*4+0x4],EAX
       *  10180B3C   8D048D 00000000  LEA EAX,DWORD PTR DS:[ECX*4]
       *  10180B43   03F0             ADD ESI,EAX
       *  10180B45   03F8             ADD EDI,EAX
       *  10180B47   FF2495 500B1810  JMP DWORD PTR DS:[EDX*4+0x10180B50]
       *  10180B4E   8BFF             MOV EDI,EDI
       *  10180B50   60               PUSHAD
       *  10180B51   0B18             OR EBX,DWORD PTR DS:[EAX]
       *  10180B53   1068 0B          ADC BYTE PTR DS:[EAX+0xB],CH
       *  10180B56   1810             SBB BYTE PTR DS:[EAX],DL
       *  10180B58   78 0B            JS SHORT RGSS301.10180B65
       *  10180B5A   1810             SBB BYTE PTR DS:[EAX],DL
       *  10180B5C   8C0B             MOV WORD PTR DS:[EBX],CS
       *  10180B5E   1810             SBB BYTE PTR DS:[EAX],DL
       *  10180B60   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
       *  10180B63   5E               POP ESI
       *  10180B64   5F               POP EDI
       *  10180B65   C9               LEAVE
       *  10180B66   C3               RETN
       *  10180B67   90               NOP
       *  10180B68   8A46 03          MOV AL,BYTE PTR DS:[ESI+0x3]
       *  10180B6B   8847 03          MOV BYTE PTR DS:[EDI+0x3],AL
       *  10180B6E   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
       *  10180B71   5E               POP ESI
       *  10180B72   5F               POP EDI
       *  10180B73   C9               LEAVE
       *  10180B74   C3               RETN
       *  10180B75   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
       *  10180B78   8A46 03          MOV AL,BYTE PTR DS:[ESI+0x3]
       *  10180B7B   8847 03          MOV BYTE PTR DS:[EDI+0x3],AL
       *  10180B7E   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
       *  10180B81   8847 02          MOV BYTE PTR DS:[EDI+0x2],AL
       *  10180B84   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
       *  10180B87   5E               POP ESI
       *  10180B88   5F               POP EDI
       *  10180B89   C9               LEAVE
       *  10180B8A   C3               RETN
       *  10180B8B   90               NOP
       *  10180B8C   8A46 03          MOV AL,BYTE PTR DS:[ESI+0x3]
       *  10180B8F   8847 03          MOV BYTE PTR DS:[EDI+0x3],AL
       *  10180B92   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
       *  10180B95   8847 02          MOV BYTE PTR DS:[EDI+0x2],AL
       *  10180B98   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
       *  10180B9B   8847 01          MOV BYTE PTR DS:[EDI+0x1],AL
       *  10180B9E   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
       *  10180BA1   5E               POP ESI
       *  10180BA2   5F               POP EDI
       *  10180BA3   C9               LEAVE
       *  10180BA4   C3               RETN
       *  10180BA5   CC               INT3
       *  10180BA6   CC               INT3
       *  10180BA7   CC               INT3
       *  10180BA8   CC               INT3
       *  10180BA9   CC               INT3
       *  10180BAA   CC               INT3
       *  10180BAB   CC               INT3
       */
      namespace Private
      {

        // enum { MaxTextSize = 0x1000 };
        // char oldText_[MaxTextSize + 1]; // 1 extra 0 that is always 0
        // size_t oldSize_;

        struct HookArgument
        {
          LPDWORD type;    // 0x0
          LPDWORD unknown; // 0x4
          size_t size;     // 0x8
          LPCSTR text;     // 0xc, editable though

          bool isValid() const
          {
            return Engine::isAddressReadable(type) && *type && size && size < 1500 && Engine::isAddressWritable(text, size + 1) && *text && text[size] == 0 && ::strlen(text) == size // validate size
                                                                                                                                                                                      //&& !::strchr(text, '/')
                   && !all_ascii(text);
          }

          // int size() const { return (*type >> 0xe) & 0x1f; }
        };

        inline bool _trims(const wchar_t &ch)
        {
          return ch <= 127 || std::isspace(ch, std::locale("ja_JP.SJIS"));
        }

        std::wstring trim(const std::wstring &text, std::wstring *prefix = nullptr, std::wstring *suffix = nullptr)
        {
          if (text.empty() ||
              !_trims(text[0]) && !_trims(text[text.size() - 1]))
            return text;
          std::wstring ret = text;
          if (_trims(ret[0]))
          {
            int pos = 1;
            for (; pos < ret.size() && _trims(ret[pos]); pos++)
              ;
            if (prefix)
              *prefix = ret.substr(0, pos);
            ret = ret.substr(pos);
          }
          if (!ret.empty() && _trims(ret[ret.size() - 1]))
          {
            int pos = ret.size() - 2;
            for (; pos >= 0 && _trims(ret[pos]); pos--)
              ;
            if (suffix)
              *suffix = ret.substr(pos + 1);
            ret = ret.substr(0, pos + 1);
          }
          return ret;
        }

        // bool textsContains(const QSet<QString> &texts, const QString &text)
        //{
        //   if (texts.contains(text))
        //     return true;
        //   if (text.contains('\n'))  // 0xa, skip translation if any of the part has been translated
        //     foreach (const QString &it, text.split('\n', QString::SkipEmptyParts))
        //       if (texts.contains(it))
        //         return true;
        //   return false;
        // }

        int guessTextRole(const std::wstring &text)
        {
          enum
          {
            MaxNameSize = 100
          };
          enum : wchar_t
          {
            w_square_open = 0x3010 /* 【 */
            ,
            w_square_close = 0x3011 /* 】 */
          };
          if (text.size() > 2 && text.size() < MaxNameSize && text[0] == w_square_open && text[text.size() - 1] == w_square_close)
            return Engine::NameRole;
          return Engine::ScenarioRole;
        }

        std::string data_;
        HookArgument *arg_;
        LPCSTR oldText_;
        size_t oldSize_;
        std::unordered_set<std::wstring> texts_;
        void hookafter2(hook_context *s, TextBuffer buffer)
        {

          enum
          {
            RecentTextCapacity = 4
          };
          static std::vector<std::wstring> recentTexts_; // used to eliminate recent duplicates

          auto arg = (HookArgument *)s->stack[0]; // arg1
          if (arg && arg->isValid())
          {                                                                                                     // && (quint8)arg->text[0] > 127) { // skip translate text beginning with ascii character
            std::wstring oldText = StringToWideString(std::string_view(arg->text, arg->size), CP_UTF8).value(), // QString::fromUtf8(arg->text, arg->size),
                prefix,
                         suffix,
                         trimmedText = trim(oldText, &prefix, &suffix);

            if (!trimmedText.empty() && (!texts_.count(trimmedText)))
            { // skip text beginning with ascii character

              // ULONG split = arg->unknown2[0]; // always 2
              // ULONG split = s->stack[0]; // return address
              std::wstring newText = buffer.strW();

              if (newText != trimmedText)
              {
                texts_.insert(newText);
                texts_.insert(trim(newText)); // in case there are leading/trailing English letters in the translation

                if (!prefix.empty())
                  newText.insert(0, prefix);
                if (!suffix.empty())
                  newText.append(suffix);

                // texts_.insert(newText);

                data_ = WideStringToString(newText, CP_UTF8); // newText.toUtf8();

                arg_ = arg;
                oldSize_ = arg->size;
                oldText_ = arg->text;
                //::memcpy(oldText_, arg->text, qMin(arg->size + 1, MaxTextSize)); // memcpy also works

                arg->size = data_.size();
                arg->text = data_.c_str();
              }
            }
          }
        }
        void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
        {

          enum
          {
            RecentTextCapacity = 4
          };
          static std::vector<std::wstring> recentTexts_; // used to eliminate recent duplicates

          auto arg = (HookArgument *)s->stack[0]; // arg1
          if (arg && arg->isValid())
          {                                                                                                     // && (quint8)arg->text[0] > 127) { // skip translate text beginning with ascii character
            std::wstring oldText = StringToWideString(std::string_view(arg->text, arg->size), CP_UTF8).value(), // QString::fromUtf8(arg->text, arg->size),
                prefix,
                         suffix,
                         trimmedText = trim(oldText, &prefix, &suffix);

            if (!trimmedText.empty() && (!texts_.count(trimmedText)))
            { // skip text beginning with ascii character

              const bool sendAllowed = (std::find(recentTexts_.begin(), recentTexts_.end(), oldText) == recentTexts_.end());
              if (sendAllowed)
              {
                recentTexts_.push_back(oldText);
                if (recentTexts_.size() > RecentTextCapacity)
                  recentTexts_.erase(recentTexts_.begin());
              }

              // ULONG split = arg->unknown2[0]; // always 2
              // ULONG split = s->stack[0]; // return address
              buffer->from(trimmedText);
            }
          }
        }
        void hookAfter(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
        {
          if (arg_)
          {
            arg_->size = oldSize_;
            arg_->text = oldText_;
            //::strcpy(arg_->text, oldText_);
            arg_ = nullptr;
          }
        }
      } // namespace Private

      bool attach(ULONG startAddress, ULONG stopAddress) // attach scenario
      {
        const uint8_t bytes[] = {
            0x8b, 0x54, 0x24, 0x24,            // 1004155c   8b5424 24        mov edx,dword ptr ss:[esp+0x24]
            0x8b, 0x02,                        // 10041560   8b02             mov eax,dword ptr ds:[edx]
            0x8b, 0xc8,                        // 10041562   8bc8             mov ecx,eax
            0x83, 0xc4, 0x0c,                  // 10041564   83c4 0c          add esp,0xc
            0x81, 0xe1, 0x00, 0x20, 0x00, 0x00 // 10041567   81e1 00200000    and ecx,0x2000
        };
        ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
        if (!addr)
          return false;
        addr = MemDbg::findEnclosingAlignedFunction(addr);
        if (!addr)
          return false;
        // addr = MemDbg::findPushAddress(addr, startAddress, stopAddress);
        // addr = 0x10041557;
        // addr = 0x100414a0;
        // addr = 0x10056BC0;
        // addr = 0x1002e5e1;
        addr = MemDbg::findNearCallAddress(addr, startAddress, stopAddress);
        if (!addr)
          return false;
        // return winhook::hook_both(addr, Private::hookBefore, Private::hookAfter);
        HookParam hp;
        hp.address = addr;
        hp.text_fun = Private::hookBefore;
        hp.embed_fun = Private::hookafter2;
        hp.type = USING_STRING | CODEC_UTF16 | EMBED_ABLE | NO_CONTEXT;
        hp.embed_hook_font = F_GetGlyphOutlineW;
        auto succ = NewHook(hp, "EmbedRGSS3");
        hp.address = addr + 5;
        hp.text_fun = Private::hookAfter;
        succ |= NewHook(hp, "EmbedRGSS3");
        return succ;
      }
    } // namespace ScenarioHook

    namespace ChoiceHook
    {

      namespace Private
      {

        struct HookArgument
        {
          LPDWORD unknown1,
              unknown2,
              unknown3;
          LPSTR text; // arg2 + 0xc

          bool isValid() const
          {
            return text && Engine::isAddressReadable(text) && *text && Engine::isAddressWritable(text, ::strlen(text));
          }

          // int size() const { return (*type >> 0xe) & 0x1f; }
        };

        void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
        {
          *role = Engine::OtherRole;
          auto arg = (HookArgument *)s->stack[2]; // arg2
          if (arg->isValid())
          {
            auto oldText = StringToWideString(std::string_view(arg->text), CP_UTF8).value();
            auto split = s->stack[0]; // return address
            buffer->from(oldText);
            //   std::wstring newText = EngineController::instance()->dispatchTextWSTD(oldText, role, sig);
            //   if (newText != oldText) {
            //     if (newText.size() < oldText.size())
            //       ::memset(arg->text, 0, ::strlen(arg->text));
            //     ::strcpy(arg->text, WideStringToString(newText, CP_UTF8).c_str());// newText.toUtf8());
            //   }
          }
        }
        void hookafter2(hook_context *s, TextBuffer buffer)
        {
          {
            auto arg = (HookArgument *)s->stack[2]; // arg2
            if (arg->isValid())
            {
              auto oldText = StringToWideString(std::string_view(arg->text), CP_UTF8).value();
              auto split = s->stack[0]; // return address
              std::wstring old = oldText;

              std::wstring newText = buffer.strW();
              if (newText != oldText)
              {
                if (newText.size() < oldText.size())
                  ::memset(arg->text, 0, ::strlen(arg->text));
                ::strcpy(arg->text, WideStringToString(newText, CP_UTF8).c_str()); // newText.toUtf8());
              }
            }
          }
        } // namespace Private

        /**
         *  Sample game: Mogeko Castle
         *
         *  One of the caller of the three GetGlyphOutlineW
         *
         *  The paint function, where text get lost. Text in [[arg2]+0xc] in UTF8 encoding.
         *  1000751D   CC               INT3
         *  1000751E   CC               INT3
         *  1000751F   CC               INT3
         *  10007520   55               PUSH EBP
         *  10007521   8BEC             MOV EBP,ESP
         *  10007523   83EC 28          SUB ESP,0x28
         *  10007526   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
         *  10007529   50               PUSH EAX
         *  1000752A   E8 51E6FFFF      CALL RGSS301.10005B80
         *  1000752F   83C4 04          ADD ESP,0x4
         *  10007532   8945 D8          MOV DWORD PTR SS:[EBP-0x28],EAX
         *  10007535   68 08781A10      PUSH RGSS301.101A7808                    ; ASCII "font"
         *  1000753A   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
         *  1000753D   51               PUSH ECX
         *  1000753E   E8 6D0E0600      CALL RGSS301.100683B0
         *  10007543   83C4 08          ADD ESP,0x8
         *  10007546   8945 E4          MOV DWORD PTR SS:[EBP-0x1C],EAX
         *  10007549   8B55 E4          MOV EDX,DWORD PTR SS:[EBP-0x1C]
         *  1000754C   8B42 10          MOV EAX,DWORD PTR DS:[EDX+0x10]
         *  1000754F   8945 F8          MOV DWORD PTR SS:[EBP-0x8],EAX
         *  10007552   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
         *  10007555   51               PUSH ECX
         *  10007556   E8 15F90200      CALL RGSS301.10036E70
         *  1000755B   83C4 04          ADD ESP,0x4
         *  1000755E   8945 E0          MOV DWORD PTR SS:[EBP-0x20],EAX
         *  10007561   8D55 E0          LEA EDX,DWORD PTR SS:[EBP-0x20]
         *  10007564   52               PUSH EDX
         *  10007565   E8 36070300      CALL RGSS301.10037CA0
         *  1000756A   83C4 04          ADD ESP,0x4
         *  1000756D   8945 DC          MOV DWORD PTR SS:[EBP-0x24],EAX
         *  10007570   8B45 D8          MOV EAX,DWORD PTR SS:[EBP-0x28]
         *  10007573   8B48 08          MOV ECX,DWORD PTR DS:[EAX+0x8]
         *  10007576   E8 651F0100      CALL RGSS301.100194E0
         *  1000757B   8945 F4          MOV DWORD PTR SS:[EBP-0xC],EAX
         *  1000757E   83EC 08          SUB ESP,0x8
         *  10007581   D9E8             FLD1
         *  10007583   DD1C24           FSTP QWORD PTR SS:[ESP]
         *  10007586   8B4D F4          MOV ECX,DWORD PTR SS:[EBP-0xC]
         *  10007589   E8 A2210100      CALL RGSS301.10019730
         *  1000758E   6A 00            PUSH 0x0
         *  10007590   6A 00            PUSH 0x0
         *  10007592   6A 00            PUSH 0x0
         *  10007594   8D4D EC          LEA ECX,DWORD PTR SS:[EBP-0x14]
         *  10007597   51               PUSH ECX
         *  10007598   8B55 DC          MOV EDX,DWORD PTR SS:[EBP-0x24]
         *  1000759B   52               PUSH EDX
         *  1000759C   E8 CF500000      CALL RGSS301.1000C670  ; jichi: convert utf8 text in edx to utf16 in eax
         *  100075A1   83C4 04          ADD ESP,0x4
         *  100075A4   50               PUSH EAX
         *  100075A5   8B45 D8          MOV EAX,DWORD PTR SS:[EBP-0x28]
         *  100075A8   8B48 08          MOV ECX,DWORD PTR DS:[EAX+0x8]
         *  100075AB   E8 A07B0100      CALL RGSS301.1001F150   ; jichi: utf16 text paint here
         *  100075B0   E8 7BAB0000      CALL RGSS301.10012130
         *  100075B5   8945 FC          MOV DWORD PTR SS:[EBP-0x4],EAX
         *  100075B8   8B4D FC          MOV ECX,DWORD PTR SS:[EBP-0x4]
         *  100075BB   8B51 10          MOV EDX,DWORD PTR DS:[ECX+0x10]
         *  100075BE   8955 E8          MOV DWORD PTR SS:[EBP-0x18],EDX
         *  100075C1   8B45 E8          MOV EAX,DWORD PTR SS:[EBP-0x18]
         *  100075C4   C740 08 00000000 MOV DWORD PTR DS:[EAX+0x8],0x0
         *  100075CB   8B4D E8          MOV ECX,DWORD PTR SS:[EBP-0x18]
         *  100075CE   C741 0C 00000000 MOV DWORD PTR DS:[ECX+0xC],0x0
         *  100075D5   8B55 E8          MOV EDX,DWORD PTR SS:[EBP-0x18]
         *  100075D8   8B45 EC          MOV EAX,DWORD PTR SS:[EBP-0x14]
         *  100075DB   8942 10          MOV DWORD PTR DS:[EDX+0x10],EAX
         *  100075DE   8B4D E8          MOV ECX,DWORD PTR SS:[EBP-0x18]
         *  100075E1   8B55 F0          MOV EDX,DWORD PTR SS:[EBP-0x10]
         *  100075E4   8951 14          MOV DWORD PTR DS:[ECX+0x14],EDX
         *  100075E7   8B45 FC          MOV EAX,DWORD PTR SS:[EBP-0x4]
         *  100075EA   8BE5             MOV ESP,EBP
         *  100075EC   5D               POP EBP
         *  100075ED   C3               RETN
         *  100075EE   CC               INT3
         */
        ULONG functionAddress;                             // the function address being hooked
        bool attach(ULONG startAddress, ULONG stopAddress) // attach other text
        {
          const uint8_t bytes[] = {
              0x89, 0x45, 0xfc, // 100075b5   8945 fc          mov dword ptr ss:[ebp-0x4],eax
              0x8b, 0x4d, 0xfc, // 100075b8   8b4d fc          mov ecx,dword ptr ss:[ebp-0x4]
              0x8b, 0x51, 0x10, // 100075bb   8b51 10          mov edx,dword ptr ds:[ecx+0x10]
              0x89, 0x55, 0xe8, // 100075be   8955 e8          mov dword ptr ss:[ebp-0x18],edx
              0x8b, 0x45, 0xe8  // 100075c1   8b45 e8          mov eax,dword ptr ss:[ebp-0x18]
          };
          if (ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress))
            if (addr = MemDbg::findEnclosingAlignedFunction(addr))
            {
              HookParam hp;
              hp.address = addr;
              hp.text_fun = Private::hookBefore;
              hp.embed_fun = Private::hookafter2;
              hp.type = USING_STRING | CODEC_UTF16 | EMBED_ABLE | NO_CONTEXT;
              hp.embed_hook_font = F_GetGlyphOutlineW;

              functionAddress = addr;
              return NewHook(hp, "EmbedRGSS3Choice");
            }

          return false;
        }

      } // namespace ChoiceHook

    }
    namespace OtherHook
    {

      namespace Private
      {

        void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
        {
          {
            *role = Engine::OtherRole;
          };
          auto retaddr = s->stack[0];
          if (retaddr > ChoiceHook::Private::functionAddress && retaddr - ChoiceHook::Private::functionAddress < 0xff)
            return; // skip translate already-hooked function

          auto text = (LPWSTR)s->stack[1]; // arg1
          if (text && *text)
          {
            std::wstring_view oldText(text);
            if (oldText.size() > 1)
            {
              buffer->from(oldText);
            }
          }
        }
        void hookafter2(hook_context *s, TextBuffer buffer)
        {
          {
            auto retaddr = s->stack[0];
            if (retaddr > ChoiceHook::Private::functionAddress && retaddr - ChoiceHook::Private::functionAddress < 0xff)
              return; // skip translate already-hooked function

            auto text = (LPWSTR)s->stack[1]; // arg1
            if (text && *text)
            {
              std::wstring oldText(text);
              if (oldText.size() > 1)
              {

                std::wstring newText = buffer.strW();
                if (newText != oldText)
                  ::wcscpy(text, (LPCWSTR)newText.c_str());
              }
            }
          }
        } // namespace Private

        /**
         *  Sample game: Mogeko Castle
         *
         *  There are three GetGlyphIndicesW.
         *  The caller of the first one is hooked.
         *
         *  The first caller of GetGlyphOutlineW, text in arg1, which is other thread:
         *
         *  00826D48   10007251  RETURN to RGSS301.10007251 from RGSS301.1001F150
         *  00826D4C   00826D9C ; jichi: text here
         *  00826D50   00828DC8  ASCII "H?"
         *  00826D54   00000001
         *  00826D58   00000001
         *  00826D5C   00828DEC
         *  00826D60   40000000
         *  00826D64   008283A8
         *  00826D68   1018DF60  RGSS301.1018DF60
         *
         *  1001F14B   CC               INT3
         *  1001F14C   CC               INT3
         *  1001F14D   CC               INT3
         *  1001F14E   CC               INT3
         *  1001F14F   CC               INT3
         *  1001F150   55               PUSH EBP
         *  1001F151   8BEC             MOV EBP,ESP
         *  1001F153   81EC 88000000    SUB ESP,0x88
         *  1001F159   894D 8C          MOV DWORD PTR SS:[EBP-0x74],ECX
         *  1001F15C   837D 18 00       CMP DWORD PTR SS:[EBP+0x18],0x0
         *  1001F160   74 09            JE SHORT RGSS301.1001F16B
         *  1001F162   8B45 18          MOV EAX,DWORD PTR SS:[EBP+0x18]
         *  1001F165   C700 01000000    MOV DWORD PTR DS:[EAX],0x1
         *  1001F16B   8B4D 8C          MOV ECX,DWORD PTR SS:[EBP-0x74]
         *  1001F16E   E8 6DA3FFFF      CALL RGSS301.100194E0
         *  1001F173   85C0             TEST EAX,EAX
         *  1001F175   75 07            JNZ SHORT RGSS301.1001F17E
         *  1001F177   33C0             XOR EAX,EAX
         *  1001F179   E9 D1010000      JMP RGSS301.1001F34F
         *  1001F17E   8B4D 8C          MOV ECX,DWORD PTR SS:[EBP-0x74]
         *  1001F181   E8 5AA3FFFF      CALL RGSS301.100194E0
         *  1001F186   8BC8             MOV ECX,EAX
         *  1001F188   E8 D3A6FFFF      CALL RGSS301.10019860
         *  1001F18D   8945 FC          MOV DWORD PTR SS:[EBP-0x4],EAX
         *  1001F190   837D FC 00       CMP DWORD PTR SS:[EBP-0x4],0x0
         *  1001F194   75 07            JNZ SHORT RGSS301.1001F19D
         *  1001F196   33C0             XOR EAX,EAX
         *  1001F198   E9 B2010000      JMP RGSS301.1001F34F
         *  1001F19D   8D4D BC          LEA ECX,DWORD PTR SS:[EBP-0x44]
         *  1001F1A0   51               PUSH ECX
         *  1001F1A1   8B55 FC          MOV EDX,DWORD PTR SS:[EBP-0x4]
         *  1001F1A4   52               PUSH EDX
         *  1001F1A5   FF15 3C201A10    CALL DWORD PTR DS:[0x101A203C]           ; gdi32.GetTextMetricsW
         *  1001F1AB   8B45 0C          MOV EAX,DWORD PTR SS:[EBP+0xC]
         *  1001F1AE   C700 00000000    MOV DWORD PTR DS:[EAX],0x0
         *  1001F1B4   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
         *  1001F1B7   C741 04 00000000 MOV DWORD PTR DS:[ECX+0x4],0x0
         *  1001F1BE   33D2             XOR EDX,EDX
         *  1001F1C0   66:8955 AC       MOV WORD PTR SS:[EBP-0x54],DX
         *  1001F1C4   B8 01000000      MOV EAX,0x1
         *  1001F1C9   66:8945 AE       MOV WORD PTR SS:[EBP-0x52],AX
         *  1001F1CD   33C9             XOR ECX,ECX
         *  1001F1CF   66:894D B0       MOV WORD PTR SS:[EBP-0x50],CX
         *  1001F1D3   33D2             XOR EDX,EDX
         *  1001F1D5   66:8955 B2       MOV WORD PTR SS:[EBP-0x4E],DX
         *  1001F1D9   33C0             XOR EAX,EAX
         *  1001F1DB   66:8945 B4       MOV WORD PTR SS:[EBP-0x4C],AX
         *  1001F1DF   33C9             XOR ECX,ECX
         *  1001F1E1   66:894D B6       MOV WORD PTR SS:[EBP-0x4A],CX
         *  1001F1E5   33D2             XOR EDX,EDX
         *  1001F1E7   66:8955 B8       MOV WORD PTR SS:[EBP-0x48],DX
         *  1001F1EB   B8 01000000      MOV EAX,0x1
         *  1001F1F0   66:8945 BA       MOV WORD PTR SS:[EBP-0x46],AX
         *  1001F1F4   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
         *  1001F1F7   894D 88          MOV DWORD PTR SS:[EBP-0x78],ECX
         *  1001F1FA   8B55 88          MOV EDX,DWORD PTR SS:[EBP-0x78]
         *  1001F1FD   83C2 02          ADD EDX,0x2
         *  1001F200   8955 84          MOV DWORD PTR SS:[EBP-0x7C],EDX
         *  1001F203   8B45 88          MOV EAX,DWORD PTR SS:[EBP-0x78]
         *  1001F206   66:8B08          MOV CX,WORD PTR DS:[EAX]
         *  1001F209   66:894D 82       MOV WORD PTR SS:[EBP-0x7E],CX
         *  1001F20D   8345 88 02       ADD DWORD PTR SS:[EBP-0x78],0x2
         *  1001F211   66:837D 82 00    CMP WORD PTR SS:[EBP-0x7E],0x0
         *  1001F216  ^75 EB            JNZ SHORT RGSS301.1001F203
         *  1001F218   8B55 88          MOV EDX,DWORD PTR SS:[EBP-0x78]
         *  1001F21B   2B55 84          SUB EDX,DWORD PTR SS:[EBP-0x7C]
         *  1001F21E   D1FA             SAR EDX,1
         *  1001F220   8995 7CFFFFFF    MOV DWORD PTR SS:[EBP-0x84],EDX
         *  1001F226   8B85 7CFFFFFF    MOV EAX,DWORD PTR SS:[EBP-0x84]
         *  1001F22C   8945 F8          MOV DWORD PTR SS:[EBP-0x8],EAX
         *  1001F22F   C745 A8 00000000 MOV DWORD PTR SS:[EBP-0x58],0x0
         *  1001F236   EB 09            JMP SHORT RGSS301.1001F241
         *  1001F238   8B4D A8          MOV ECX,DWORD PTR SS:[EBP-0x58]
         *  1001F23B   83C1 01          ADD ECX,0x1
         *  1001F23E   894D A8          MOV DWORD PTR SS:[EBP-0x58],ECX
         *  1001F241   8B55 A8          MOV EDX,DWORD PTR SS:[EBP-0x58]
         *  1001F244   3B55 F8          CMP EDX,DWORD PTR SS:[EBP-0x8]
         *  1001F247   0F8D C2000000    JGE RGSS301.1001F30F
         *  1001F24D   8D45 AC          LEA EAX,DWORD PTR SS:[EBP-0x54]
         *  1001F250   50               PUSH EAX
         *  1001F251   6A 00            PUSH 0x0
         *  1001F253   6A 00            PUSH 0x0
         *  1001F255   8D4D 90          LEA ECX,DWORD PTR SS:[EBP-0x70]
         *  1001F258   51               PUSH ECX
         *  1001F259   6A 06            PUSH 0x6
         *  1001F25B   8B55 A8          MOV EDX,DWORD PTR SS:[EBP-0x58]
         *  1001F25E   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
         *  1001F261   0FB70C50         MOVZX ECX,WORD PTR DS:[EAX+EDX*2]
         *  1001F265   51               PUSH ECX
         *  1001F266   8B55 FC          MOV EDX,DWORD PTR SS:[EBP-0x4]
         *  1001F269   52               PUSH EDX
         *  1001F26A   FF15 30201A10    CALL DWORD PTR DS:[0x101A2030]           ; gdi32.GetGlyphOutlineW
         *  1001F270   8945 A4          MOV DWORD PTR SS:[EBP-0x5C],EAX
         *  1001F273   837D 18 00       CMP DWORD PTR SS:[EBP+0x18],0x0
         *  1001F277   74 12            JE SHORT RGSS301.1001F28B
         *  1001F279   8B45 18          MOV EAX,DWORD PTR SS:[EBP+0x18]
         *  1001F27C   8B4D A4          MOV ECX,DWORD PTR SS:[EBP-0x5C]
         *  1001F27F   3B08             CMP ECX,DWORD PTR DS:[EAX]
         *  1001F281   76 08            JBE SHORT RGSS301.1001F28B
         *  1001F283   8B55 18          MOV EDX,DWORD PTR SS:[EBP+0x18]
         *  1001F286   8B45 A4          MOV EAX,DWORD PTR SS:[EBP-0x5C]
         *  1001F289   8902             MOV DWORD PTR DS:[EDX],EAX
         *  1001F28B   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
         *  1001F28E   8B11             MOV EDX,DWORD PTR DS:[ECX]
         *  1001F290   0355 98          ADD EDX,DWORD PTR SS:[EBP-0x68]
         *  1001F293   79 0A            JNS SHORT RGSS301.1001F29F
         *
         *  Caller of the other two GetGlyphOutlineW, where text is in arg5.
         *
         *  00826D34   100074F7  RETURN to RGSS301.100074F7 from RGSS301.1001F360
         *  00826D38   00000088
         *  00826D3C   000000E8
         *  00826D40   00000058
         *  00826D44   00000018
         *  00826D48   00826D9C ; jichi: text here
         *  00826D4C   FFFFFFFF
         *  00826D50   80000000
         *  00826D54   00000001
         *  00826D58   00000000
         *  00826D5C   00000140
         *  00826D60   000000C0
         *  00826D64   008283A8
         *  00826D68   1018DF60  RGSS301.1018DF60
         *
         *  1001F35C   CC               INT3
         *  1001F35D   CC               INT3
         *  1001F35E   CC               INT3
         *  1001F35F   CC               INT3
         *  1001F360   55               PUSH EBP
         *  1001F361   8BEC             MOV EBP,ESP
         *  1001F363   81EC 4C010000    SUB ESP,0x14C
         *  1001F369   898D C4FEFFFF    MOV DWORD PTR SS:[EBP-0x13C],ECX
         *  1001F36F   8B8D C4FEFFFF    MOV ECX,DWORD PTR SS:[EBP-0x13C]
         *  1001F375   E8 66A1FFFF      CALL RGSS301.100194E0
         *  1001F37A   85C0             TEST EAX,EAX
         *  1001F37C   75 07            JNZ SHORT RGSS301.1001F385
         *  1001F37E   33C0             XOR EAX,EAX
         *  1001F380   E9 12060000      JMP RGSS301.1001F997
         *  1001F385   8B8D C4FEFFFF    MOV ECX,DWORD PTR SS:[EBP-0x13C]
         *  1001F38B   E8 50A1FFFF      CALL RGSS301.100194E0
         *  1001F390   8BC8             MOV ECX,EAX
         *  1001F392   E8 C9A4FFFF      CALL RGSS301.10019860
         *  1001F397   8945 F8          MOV DWORD PTR SS:[EBP-0x8],EAX
         *  1001F39A   837D F8 00       CMP DWORD PTR SS:[EBP-0x8],0x0
         *  1001F39E   75 07            JNZ SHORT RGSS301.1001F3A7
         *  1001F3A0   33C0             XOR EAX,EAX
         *  1001F3A2   E9 F0050000      JMP RGSS301.1001F997
         *  1001F3A7   8D45 A0          LEA EAX,DWORD PTR SS:[EBP-0x60]
         *  1001F3AA   50               PUSH EAX
         *  1001F3AB   8B4D F8          MOV ECX,DWORD PTR SS:[EBP-0x8]
         *  1001F3AE   51               PUSH ECX
         *  1001F3AF   FF15 3C201A10    CALL DWORD PTR DS:[0x101A203C]           ; gdi32.GetTextMetricsW
         *  1001F3B5   837D 2C 00       CMP DWORD PTR SS:[EBP+0x2C],0x0
         *  1001F3B9   77 4C            JA SHORT RGSS301.1001F407
         *  1001F3BB   8D55 2C          LEA EDX,DWORD PTR SS:[EBP+0x2C]
         *  1001F3BE   52               PUSH EDX
         *  1001F3BF   8B45 24          MOV EAX,DWORD PTR SS:[EBP+0x24]
         *  1001F3C2   50               PUSH EAX
         *  1001F3C3   6A 01            PUSH 0x1
         *  1001F3C5   8D8D 3CFFFFFF    LEA ECX,DWORD PTR SS:[EBP-0xC4]
         *  1001F3CB   51               PUSH ECX
         *  1001F3CC   8B55 18          MOV EDX,DWORD PTR SS:[EBP+0x18]
         *  1001F3CF   52               PUSH EDX
         *  1001F3D0   8B8D C4FEFFFF    MOV ECX,DWORD PTR SS:[EBP-0x13C]
         *  1001F3D6   E8 75FDFFFF      CALL RGSS301.1001F150
         *  1001F3DB   83BD 3CFFFFFF 00 CMP DWORD PTR SS:[EBP-0xC4],0x0
         *  1001F3E2   74 09            JE SHORT RGSS301.1001F3ED
         *  1001F3E4   83BD 40FFFFFF 00 CMP DWORD PTR SS:[EBP-0xC0],0x0
         *  1001F3EB   75 0A            JNZ SHORT RGSS301.1001F3F7
         *  1001F3ED   B8 01000000      MOV EAX,0x1
         *  1001F3F2   E9 A0050000      JMP RGSS301.1001F997
         *  1001F3F7   837D 2C 00       CMP DWORD PTR SS:[EBP+0x2C],0x0
         *  1001F3FB   77 0A            JA SHORT RGSS301.1001F407
         *  1001F3FD   B8 01000000      MOV EAX,0x1
         *  1001F402   E9 90050000      JMP RGSS301.1001F997
         *  1001F407   8B45 0C          MOV EAX,DWORD PTR SS:[EBP+0xC]
         *  1001F40A   8985 58FFFFFF    MOV DWORD PTR SS:[EBP-0xA8],EAX
         *  1001F410   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
         *  1001F413   898D 54FFFFFF    MOV DWORD PTR SS:[EBP-0xAC],ECX
         *  1001F419   8B95 54FFFFFF    MOV EDX,DWORD PTR SS:[EBP-0xAC]
         *  1001F41F   0355 10          ADD EDX,DWORD PTR SS:[EBP+0x10]
         *  1001F422   8995 5CFFFFFF    MOV DWORD PTR SS:[EBP-0xA4],EDX
         *  1001F428   8B85 58FFFFFF    MOV EAX,DWORD PTR SS:[EBP-0xA8]
         *  1001F42E   0345 14          ADD EAX,DWORD PTR SS:[EBP+0x14]
         *  1001F431   8985 60FFFFFF    MOV DWORD PTR SS:[EBP-0xA0],EAX
         *  1001F437   C745 E0 00000000 MOV DWORD PTR SS:[EBP-0x20],0x0
         *  1001F43E   C745 DC 00000000 MOV DWORD PTR SS:[EBP-0x24],0x0
         *  1001F445   8B4D 10          MOV ECX,DWORD PTR SS:[EBP+0x10]
         *  1001F448   894D E4          MOV DWORD PTR SS:[EBP-0x1C],ECX
         *  1001F44B   8B55 14          MOV EDX,DWORD PTR SS:[EBP+0x14]
         *  1001F44E   8955 E8          MOV DWORD PTR SS:[EBP-0x18],EDX
         *  1001F451   837D 24 00       CMP DWORD PTR SS:[EBP+0x24],0x0
         *  1001F455   74 1F            JE SHORT RGSS301.1001F476
         *  1001F457   6A FF            PUSH -0x1
         *  1001F459   6A FF            PUSH -0x1
         *  1001F45B   8D85 54FFFFFF    LEA EAX,DWORD PTR SS:[EBP-0xAC]
         *  1001F461   50               PUSH EAX
         *  1001F462   FF15 E8231A10    CALL DWORD PTR DS:[0x101A23E8]           ; user32.InflateRect
         *  1001F468   6A FF            PUSH -0x1
         *  1001F46A   6A FF            PUSH -0x1
         *  1001F46C   8D4D DC          LEA ECX,DWORD PTR SS:[EBP-0x24]
         *  1001F46F   51               PUSH ECX
         *  1001F470   FF15 E8231A10    CALL DWORD PTR DS:[0x101A23E8]           ; user32.InflateRect
         *  1001F476   68 E0010000      PUSH 0x1E0
         *  1001F47B   68 80020000      PUSH 0x280
         *  1001F480   E8 DBFF0E00      CALL RGSS301.1010F460
         *  1001F485   8BC8             MOV ECX,EAX
         *  1001F487   E8 54010F00      CALL RGSS301.1010F5E0
         *  1001F48C   8945 F0          MOV DWORD PTR SS:[EBP-0x10],EAX
         *  1001F48F   837D F0 00       CMP DWORD PTR SS:[EBP-0x10],0x0
         *  1001F493   75 07            JNZ SHORT RGSS301.1001F49C
         *  1001F495   33C0             XOR EAX,EAX
         *  1001F497   E9 FB040000      JMP RGSS301.1001F997
         *  1001F49C   6A 00            PUSH 0x0
         *  1001F49E   8D55 DC          LEA EDX,DWORD PTR SS:[EBP-0x24]
         *  1001F4A1   52               PUSH EDX
         *  1001F4A2   8B4D F0          MOV ECX,DWORD PTR SS:[EBP-0x10]
         *  1001F4A5   E8 A6CF0E00      CALL RGSS301.1010C450
         *  1001F4AA   8B45 18          MOV EAX,DWORD PTR SS:[EBP+0x18]
         *  1001F4AD   8985 C0FEFFFF    MOV DWORD PTR SS:[EBP-0x140],EAX
         *  1001F4B3   8B8D C0FEFFFF    MOV ECX,DWORD PTR SS:[EBP-0x140]
         *  1001F4B9   83C1 02          ADD ECX,0x2
         *  1001F4BC   898D BCFEFFFF    MOV DWORD PTR SS:[EBP-0x144],ECX
         *  1001F4C2   8B95 C0FEFFFF    MOV EDX,DWORD PTR SS:[EBP-0x140]
         *  1001F4C8   66:8B02          MOV AX,WORD PTR DS:[EDX]
         *  1001F4CB   66:8985 BAFEFFFF MOV WORD PTR SS:[EBP-0x146],AX
         *  1001F4D2   8385 C0FEFFFF 02 ADD DWORD PTR SS:[EBP-0x140],0x2
         *  1001F4D9   66:83BD BAFEFFFF>CMP WORD PTR SS:[EBP-0x146],0x0
         *  1001F4E1  ^75 DF            JNZ SHORT RGSS301.1001F4C2
         *  1001F4E3   8B8D C0FEFFFF    MOV ECX,DWORD PTR SS:[EBP-0x140]
         *  1001F4E9   2B8D BCFEFFFF    SUB ECX,DWORD PTR SS:[EBP-0x144]
         *  1001F4EF   D1F9             SAR ECX,1
         *  1001F4F1   898D B4FEFFFF    MOV DWORD PTR SS:[EBP-0x14C],ECX
         *  1001F4F7   8B95 B4FEFFFF    MOV EDX,DWORD PTR SS:[EBP-0x14C]
         *  1001F4FD   8955 EC          MOV DWORD PTR SS:[EBP-0x14],EDX
         *  1001F500   C745 F4 00000000 MOV DWORD PTR SS:[EBP-0xC],0x0
         *  1001F507   33C0             XOR EAX,EAX
         *  1001F509   66:8985 44FFFFFF MOV WORD PTR SS:[EBP-0xBC],AX
         *  1001F510   B9 01000000      MOV ECX,0x1
         *  1001F515   66:898D 46FFFFFF MOV WORD PTR SS:[EBP-0xBA],CX
         *  1001F51C   33D2             XOR EDX,EDX
         *  1001F51E   66:8995 48FFFFFF MOV WORD PTR SS:[EBP-0xB8],DX
         *  1001F525   33C0             XOR EAX,EAX
         *  1001F527   66:8985 4AFFFFFF MOV WORD PTR SS:[EBP-0xB6],AX
         *  1001F52E   33C9             XOR ECX,ECX
         *  1001F530   66:898D 4CFFFFFF MOV WORD PTR SS:[EBP-0xB4],CX
         *  1001F537   33D2             XOR EDX,EDX
         *  1001F539   66:8995 4EFFFFFF MOV WORD PTR SS:[EBP-0xB2],DX
         *  1001F540   33C0             XOR EAX,EAX
         *  1001F542   66:8985 50FFFFFF MOV WORD PTR SS:[EBP-0xB0],AX
         *  1001F549   B9 01000000      MOV ECX,0x1
         *  1001F54E   66:898D 52FFFFFF MOV WORD PTR SS:[EBP-0xAE],CX
         *  1001F555   8B55 2C          MOV EDX,DWORD PTR SS:[EBP+0x2C]
         *  1001F558   52               PUSH EDX
         *  1001F559   E8 0EF31500      CALL RGSS301.1017E86C
         *  1001F55E   83C4 04          ADD ESP,0x4
         *  1001F561   8985 D0FEFFFF    MOV DWORD PTR SS:[EBP-0x130],EAX
         *  1001F567   8B85 D0FEFFFF    MOV EAX,DWORD PTR SS:[EBP-0x130]
         *  1001F56D   8985 64FFFFFF    MOV DWORD PTR SS:[EBP-0x9C],EAX
         *  1001F573   C785 38FFFFFF 00>MOV DWORD PTR SS:[EBP-0xC8],0x0
         *  1001F57D   EB 0F            JMP SHORT RGSS301.1001F58E
         *  1001F57F   8B8D 38FFFFFF    MOV ECX,DWORD PTR SS:[EBP-0xC8]
         *  1001F585   83C1 01          ADD ECX,0x1
         *  1001F588   898D 38FFFFFF    MOV DWORD PTR SS:[EBP-0xC8],ECX
         *  1001F58E   8B95 38FFFFFF    MOV EDX,DWORD PTR SS:[EBP-0xC8]
         *  1001F594   3B55 EC          CMP EDX,DWORD PTR SS:[EBP-0x14]
         *  1001F597   0F8D E6010000    JGE RGSS301.1001F783
         *  1001F59D   8B45 2C          MOV EAX,DWORD PTR SS:[EBP+0x2C]
         *  1001F5A0   50               PUSH EAX
         *  1001F5A1   6A 00            PUSH 0x0
         *  1001F5A3   8B8D 64FFFFFF    MOV ECX,DWORD PTR SS:[EBP-0x9C]
         *  1001F5A9   51               PUSH ECX
         *  1001F5AA   E8 E1FC1500      CALL RGSS301.1017F290
         *  1001F5AF   83C4 0C          ADD ESP,0xC
         *  1001F5B2   8D95 44FFFFFF    LEA EDX,DWORD PTR SS:[EBP-0xBC]
         *  1001F5B8   52               PUSH EDX
         *  1001F5B9   6A 00            PUSH 0x0
         *  1001F5BB   6A 00            PUSH 0x0
         *  1001F5BD   8D85 08FFFFFF    LEA EAX,DWORD PTR SS:[EBP-0xF8]
         *  1001F5C3   50               PUSH EAX
         *  1001F5C4   6A 00            PUSH 0x0
         *  1001F5C6   8B8D 38FFFFFF    MOV ECX,DWORD PTR SS:[EBP-0xC8]
         *  1001F5CC   8B55 18          MOV EDX,DWORD PTR SS:[EBP+0x18]
         *  1001F5CF   0FB7044A         MOVZX EAX,WORD PTR DS:[EDX+ECX*2]
         *  1001F5D3   50               PUSH EAX
         *  1001F5D4   8B4D F8          MOV ECX,DWORD PTR SS:[EBP-0x8]
         *  1001F5D7   51               PUSH ECX
         *  1001F5D8   FF15 30201A10    CALL DWORD PTR DS:[0x101A2030]           ; gdi32.GetGlyphOutlineW
         *  1001F5DE   8D95 44FFFFFF    LEA EDX,DWORD PTR SS:[EBP-0xBC]
         *  1001F5E4   52               PUSH EDX
         *  1001F5E5   8B85 64FFFFFF    MOV EAX,DWORD PTR SS:[EBP-0x9C]
         *  1001F5EB   50               PUSH EAX
         *  1001F5EC   8B4D 2C          MOV ECX,DWORD PTR SS:[EBP+0x2C]
         *  1001F5EF   51               PUSH ECX
         *  1001F5F0   8D95 08FFFFFF    LEA EDX,DWORD PTR SS:[EBP-0xF8]
         *  1001F5F6   52               PUSH EDX
         *  1001F5F7   6A 06            PUSH 0x6
         *  1001F5F9   8B85 38FFFFFF    MOV EAX,DWORD PTR SS:[EBP-0xC8]
         *  1001F5FF   8B4D 18          MOV ECX,DWORD PTR SS:[EBP+0x18]
         *  1001F602   0FB71441         MOVZX EDX,WORD PTR DS:[ECX+EAX*2]
         *  1001F606   52               PUSH EDX
         *  1001F607   8B45 F8          MOV EAX,DWORD PTR SS:[EBP-0x8]
         *  1001F60A   50               PUSH EAX
         *  1001F60B   FF15 30201A10    CALL DWORD PTR DS:[0x101A2030]           ; gdi32.GetGlyphOutlineW
         *  1001F611   8B4D F4          MOV ECX,DWORD PTR SS:[EBP-0xC]
         *  1001F614   038D 10FFFFFF    ADD ECX,DWORD PTR SS:[EBP-0xF0]
         *  1001F61A   79 0B            JNS SHORT RGSS301.1001F627
         *  1001F61C   8B95 10FFFFFF    MOV EDX,DWORD PTR SS:[EBP-0xF0]
         *  1001F622   F7DA             NEG EDX
         *  1001F624   8955 F4          MOV DWORD PTR SS:[EBP-0xC],EDX
         *  1001F627   8B85 08FFFFFF    MOV EAX,DWORD PTR SS:[EBP-0xF8]
         *  1001F62D   8985 28FFFFFF    MOV DWORD PTR SS:[EBP-0xD8],EAX
         *
         *  Additionally, text to paint is converted here from UTF-8 to UTF-16:
         *  1000C62D   CC               INT3
         *  1000C62E   CC               INT3
         *  1000C62F   CC               INT3
         *  1000C630   55               PUSH EBP
         *  1000C631   8BEC             MOV EBP,ESP
         *  1000C633   8B45 10          MOV EAX,DWORD PTR SS:[EBP+0x10]
         *  1000C636   D1E0             SHL EAX,1
         *  1000C638   50               PUSH EAX
         *  1000C639   6A 00            PUSH 0x0
         *  1000C63B   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
         *  1000C63E   51               PUSH ECX
         *  1000C63F   E8 4C2C1700      CALL RGSS301.1017F290
         *  1000C644   83C4 0C          ADD ESP,0xC
         *  1000C647   8B55 10          MOV EDX,DWORD PTR SS:[EBP+0x10]
         *  1000C64A   52               PUSH EDX
         *  1000C64B   8B45 0C          MOV EAX,DWORD PTR SS:[EBP+0xC]
         *  1000C64E   50               PUSH EAX
         *  1000C64F   6A FF            PUSH -0x1
         *  1000C651   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
         *  1000C654   51               PUSH ECX
         *  1000C655   6A 00            PUSH 0x0
         *  1000C657   68 E9FD0000      PUSH 0xFDE9
         *  1000C65C   FF15 38221A10    CALL DWORD PTR DS:[0x101A2238]           ; kernel32.MultiByteToWideChar
         *  1000C662   5D               POP EBP
         *  1000C663   C3               RETN
         *  1000C664   CC               INT3
         *  1000C665   CC               INT3
         *  1000C666   CC               INT3
         *  1000C667   CC               INT3
         *  1000C668   CC               INT3
         *  1000C669   CC               INT3
         *  1000C66A   CC               INT3
         *  1000C66B   CC               INT3
         *  1000C66C   CC               INT3
         *  1000C66D   CC               INT3
         *  1000C66E   CC               INT3
         *  1000C66F   CC               INT3
         *  1000C670   55               PUSH EBP
         *  1000C671   8BEC             MOV EBP,ESP
         *  1000C673   68 00100000      PUSH 0x1000
         *  1000C678   68 68302610      PUSH RGSS301.10263068
         *  1000C67D   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
         *  1000C680   50               PUSH EAX
         *  1000C681   E8 AAFFFFFF      CALL RGSS301.1000C630
         *  1000C686   83C4 0C          ADD ESP,0xC
         *  1000C689   33C9             XOR ECX,ECX
         *  1000C68B   66:890D 66502610 MOV WORD PTR DS:[0x10265066],CX
         *  1000C692   B8 68302610      MOV EAX,RGSS301.10263068
         *  1000C697   5D               POP EBP
         *  1000C698   C3               RETN
         *  1000C699   CC               INT3
         *  1000C69A   CC               INT3
         *  1000C69B   CC               INT3
         *  1000C69C   CC               INT3
         *  1000C69D   CC               INT3
         */
        ULONG functionAddress;                             // the beginning of the function being hooked
        bool attach(ULONG startAddress, ULONG stopAddress) // attach other text
        {
          ULONG addr = MemDbg::findCallerAddressAfterInt3((ULONG)::GetGlyphOutlineW, startAddress, stopAddress);
          if (!addr)
            return 0;
          HookParam hp;
          hp.address = addr;
          hp.text_fun = Private::hookBefore;
          hp.embed_fun = Private::hookafter2;
          hp.type = USING_STRING | CODEC_UTF16 | EMBED_ABLE | NO_CONTEXT;
          hp.embed_hook_font = F_GetGlyphOutlineW;

          return NewHook(hp, "EmbedRGSS3Other");
        }
      }
    } // namespace OtherHook

  } // namespace RGSS3Hook

#if 0

/**
 *  Sample game: Mogeko Castle with RGSS 3.01
 *  0x10036758: LOAD
 *  0x1004155c: DATA
 *
 *  Text accessed character by character
 *  0x10036463: LOAD    character by character
 *
 *  0x100378ed: $100
 *  0x100378ed: キャンセル
 *
 *  0x10038a44: 駅のホーム
 */
namespace DebugHook {

bool beforeStrcpy(winhook::hook_context *s)
{
  auto arg = (LPCSTR)s->stack[1]; // arg1
  auto sig = s->stack[0]; // retaddr
  //enum { role = Engine::OtherRole };
  //if (!::strstr(arg, "\xe3\x82\xaa\xe3\x83\xac\xe3\x83\xb3\xe7\x97\x94"))
  //  return true;
  QString text = QString::fromUtf16((LPCWSTR)arg);
  //QString text = QString::fromUtf8((LPCSTR)arg, s->stack[3]);
  //if (!text.isEmpty() && text[0].unicode() >= 128 && text.size() == 5)
  //if (!text.isEmpty() && sig == 0x100378ed)
  EngineController::instance()->dispatchTextW(text, role, sig);
  return true;
}

bool attach()
{
  //ULONG addr = 0x10180840;
  ULONG addr = 0x1001f150;
  winhook::hook_before(addr, beforeStrcpy);
  return true;
}

} // namespace DebugHook

#endif // 0

} // unnamed namespace

bool RPGMakerRGSS3::attach_function()
{
  ULONG startAddress, stopAddress;
  if (!RGSS3::getMemoryRange(&startAddress, &stopAddress))
    return false;

  if (!RGSS3::ScenarioHook::attach(startAddress, stopAddress))
    return false;
  RGSS3::ChoiceHook::Private::attach(startAddress, stopAddress);
  RGSS3::OtherHook::Private::attach(startAddress, stopAddress);

  return true;
}
bool RPGMakerRGSS300::attach_function()
{
  PcHooks::hookGDIFunctions();
  trigger_fun = [](LPVOID addr1, hook_context *context)
  {
    if (addr1 != GetGlyphOutlineW)
      return false;
    auto addr = context->retaddr;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | CODEC_UTF16;
    hp.offset = stackoffset(1);
    NewHook(hp, "RGSS30x.dll");
    return true;
  };
  return GetModuleHandle(L"RGSS300.dll") || GetModuleHandle(L"RGSS301.dll");
}