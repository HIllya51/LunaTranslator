#include "Minori.h"

void Minori1EngFilter(TextBuffer *buffer, HookParam *)
{
  StringCharReplacer(buffer, TEXTANDLEN("\\n"), ' ');
  StringFilter(buffer, TEXTANDLEN("\\a"));
  StringFilter(buffer, TEXTANDLEN("\\v"));
  CharReplacer(buffer, '\xC4', '-');
  CharReplacer(buffer, '\x93', '"');
  CharReplacer(buffer, '\x94', '"');
  CharReplacer(buffer, '\x92', '\'');
  StringCharReplacer(buffer, TEXTANDLEN("\\I"), '\'');
  StringCharReplacer(buffer, TEXTANDLEN("\\P"), '\'');
}

void Minori1JapFilter(TextBuffer *buffer, HookParam *)
{
  auto text = reinterpret_cast<LPSTR>(buffer->buff);
  StringFilter(buffer, TEXTANDLEN("\\a"));
  StringFilter(buffer, TEXTANDLEN("\\v"));
  StringFilter(buffer, TEXTANDLEN("\\N"));

  if (cpp_strnstr(text, "{", buffer->size))
  {
    StringFilterBetween(buffer, TEXTANDLEN("{"), TEXTANDLEN("}"));
  }
}

bool InsertMinori1Hook()
{

  /*
   * Sample games:
   * https://vndb.org/v19644
   * https://vndb.org/v12562
   */
  const BYTE bytes[] = {
      0x84, 0xC0,      // test al,al                      << hook here
      0x0F, 0x85, XX4, // jne trinoline_en_AA.exe+243E1
      0x68, XX4,       // push trinoline_en_AA.exe+118BF8 << alt eng hook
      0x33, 0xFF       // xor edi,edi
  };
  enum
  {
    alt_addr_offset = 8
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("Minori1: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(edx);
  hp.codepage = 932;
  hp.type = USING_STRING;
  hp.filter_fun = Minori1JapFilter;
  ConsoleOutput(" INSERT Minori1");
  auto succ = NewHook(hp, "Minori1");

  hp.address = addr + alt_addr_offset;
  hp.filter_fun = Minori1EngFilter;
  ConsoleOutput(" INSERT Minori1eng");
  succ |= NewHook(hp, "Minori1eng");

  return succ;
}

void Minori2Filter(TextBuffer *buffer, HookParam *)
{
  auto text = reinterpret_cast<LPSTR>(buffer->buff);
  StringCharReplacer(buffer, TEXTANDLEN("\\n"), ' ');

  if (cpp_strnstr(text, "{", buffer->size))
  {
    StringFilterBetween(buffer, TEXTANDLEN("{"), TEXTANDLEN("}"));
  }
}

bool InsertMinori2Hook()
{

  /*
   * Sample games:
   * https://vndb.org/v35
   */
  const BYTE bytes[] = {
      0x80, 0x38, 0x00,             // cmp byte ptr [eax],00  << hook here
      0x0F, 0x84, XX4,              // je WindRP.exe+2832A
      0xB8, 0x20, 0x03, 0x00, 0x00, // mov eax,00000320
      0x89, 0x44, 0x24, 0x10,       // mov [esp+10],eax
      0x89, 0x44, 0x24, 0x14,       // mov [esp+14],eax
      0x8B, 0x47, 0x20              // mov eax,[edi+20]
  };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("Minori2: pattern not found");
    return false;
  }

  ConsoleOutput(" INSERT Minori2");
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(eax);
  hp.type = USING_STRING;
  hp.filter_fun = Minori2Filter;
  ConsoleOutput(" INSERT Minori2");
  ConsoleOutput("Minori2: Please, set text to max speed");
  return NewHook(hp, "Minori2");
}

bool InsertMinoriHooks()
{
  return InsertMinori1Hook() || InsertMinori2Hook();
}

namespace
{ // unnamed
  namespace ScenarioHook
  {
    namespace Private
    {
      /**
       *  Sample game: 12の月のイヴ
       *  Remove \tag and leading #.
       */
      LPCSTR trim(LPCSTR text, int *size)
      {
        int length = *size;
        // handle prefix
        while (text[0] == '#' || text[0] == '@')
        {
          text++;
          length--;
        }
        while (text[0] == '\\' && ::isalpha(text[1]))
        {
          text += 2;
          length -= 2;
        }
        // handle suffix
        while (length >= 2 && text[length - 2] == '\\' && ::isalpha(text[length - 1]))
          length -= 2;
        *size = length;
        return text;
      }

      /**
       *  Sample game: ソレヨリノ前奏詩
       *
       *  013BEFAE   CC               INT3
       *  013BEFAF   CC               INT3
       *  013BEFB0   55               PUSH EBP
       *  013BEFB1   8BEC             MOV EBP,ESP
       *  013BEFB3   6A FF            PUSH -0x1
       *  013BEFB5   68 78654401      PUSH yorino_t.01446578
       *  013BEFBA   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
       *  013BEFC0   50               PUSH EAX
       *  013BEFC1   64:8925 00000000 MOV DWORD PTR FS:[0],ESP
       *  013BEFC8   83EC 54          SUB ESP,0x54
       *  013BEFCB   53               PUSH EBX
       *  013BEFCC   8B5D 08          MOV EBX,DWORD PTR SS:[EBP+0x8]
       *  013BEFCF   56               PUSH ESI
       *  013BEFD0   57               PUSH EDI
       *  013BEFD1   8BF3             MOV ESI,EBX
       *  013BEFD3   E8 68FFFFFF      CALL yorino_t.013BEF40
       *  013BEFD8   8883 6C2A0000    MOV BYTE PTR DS:[EBX+0x2A6C],AL
       *  013BEFDE   8B45 14          MOV EAX,DWORD PTR SS:[EBP+0x14]
       *  013BEFE1   33F6             XOR ESI,ESI
       *  013BEFE3   56               PUSH ESI
       *  013BEFE4   50               PUSH EAX
       *  013BEFE5   BF 0F000000      MOV EDI,0xF
       *  013BEFEA   83C8 FF          OR EAX,0xFFFFFFFF
       *  013BEFED   8D4D BC          LEA ECX,DWORD PTR SS:[EBP-0x44]
       *  013BEFF0   897D D0          MOV DWORD PTR SS:[EBP-0x30],EDI
       *  013BEFF3   8975 CC          MOV DWORD PTR SS:[EBP-0x34],ESI
       *  013BEFF6   C645 BC 00       MOV BYTE PTR SS:[EBP-0x44],0x0
       *  013BEFFA   E8 313AFAFF      CALL yorino_t.01362A30  ; jichi: name call
       *  013BEFFF   8B4D 18          MOV ECX,DWORD PTR SS:[EBP+0x18]
       *  013BF002   56               PUSH ESI
       *  013BF003   8975 FC          MOV DWORD PTR SS:[EBP-0x4],ESI
       *  013BF006   51               PUSH ECX
       *  013BF007   83C8 FF          OR EAX,0xFFFFFFFF
       *  013BF00A   8D4D D8          LEA ECX,DWORD PTR SS:[EBP-0x28]
       *  013BF00D   897D EC          MOV DWORD PTR SS:[EBP-0x14],EDI
       *  013BF010   8975 E8          MOV DWORD PTR SS:[EBP-0x18],ESI
       *  013BF013   C645 D8 00       MOV BYTE PTR SS:[EBP-0x28],0x0
       *  013BF017   E8 143AFAFF      CALL yorino_t.01362A30 ; jichi: scenario call
       *  013BF01C   C645 FC 01       MOV BYTE PTR SS:[EBP-0x4],0x1
       *  013BF020   8B8B 7C2A0000    MOV ECX,DWORD PTR DS:[EBX+0x2A7C]
       *  013BF026   3BCE             CMP ECX,ESI
       *  013BF028   74 1C            JE SHORT yorino_t.013BF046
       *  013BF02A   8B11             MOV EDX,DWORD PTR DS:[ECX]
       *  013BF02C   8B52 0C          MOV EDX,DWORD PTR DS:[EDX+0xC]
       *  013BF02F   8D45 BC          LEA EAX,DWORD PTR SS:[EBP-0x44]
       *  013BF032   50               PUSH EAX
       *  013BF033   FFD2             CALL EDX
       *  013BF035   8B8B 7C2A0000    MOV ECX,DWORD PTR DS:[EBX+0x2A7C]
       *  013BF03B   8B01             MOV EAX,DWORD PTR DS:[ECX]
       *  013BF03D   8B40 0C          MOV EAX,DWORD PTR DS:[EAX+0xC]
       *  013BF040   8D55 D8          LEA EDX,DWORD PTR SS:[EBP-0x28]
       *  013BF043   52               PUSH EDX
       *  013BF044   FFD0             CALL EAX
       *  013BF046   8B8B 1C130000    MOV ECX,DWORD PTR DS:[EBX+0x131C]
       *  013BF04C   8B7D 0C          MOV EDI,DWORD PTR SS:[EBP+0xC]
       *  013BF04F   3BCF             CMP ECX,EDI
       *  013BF051   0F95C0           SETNE AL
       *  013BF054   C683 411A0000 00 MOV BYTE PTR DS:[EBX+0x1A41],0x0
       *  013BF05B   8845 08          MOV BYTE PTR SS:[EBP+0x8],AL
       *  013BF05E   84C0             TEST AL,AL
       *  013BF060   74 15            JE SHORT yorino_t.013BF077
       *  013BF062   3BCE             CMP ECX,ESI
       *  013BF064   7C 11            JL SHORT yorino_t.013BF077
       *  013BF066   8BB3 0C1A0000    MOV ESI,DWORD PTR DS:[EBX+0x1A0C]
       *  013BF06C   85F6             TEST ESI,ESI
       *  013BF06E   74 05            JE SHORT yorino_t.013BF075
       *  013BF070   E8 8B500100      CALL yorino_t.013D4100
       *  013BF075   33F6             XOR ESI,ESI
       *  013BF077   56               PUSH ESI
       *  013BF078   8D4D D8          LEA ECX,DWORD PTR SS:[EBP-0x28]
       *  013BF07B   51               PUSH ECX
       *  013BF07C   8D8B 00130000    LEA ECX,DWORD PTR DS:[EBX+0x1300]
       *  013BF082   83C8 FF          OR EAX,0xFFFFFFFF
       *  013BF085   E8 A639FAFF      CALL yorino_t.01362A30
       *  013BF08A   56               PUSH ESI
       *  013BF08B   8D55 BC          LEA EDX,DWORD PTR SS:[EBP-0x44]
       *  013BF08E   52               PUSH EDX
       *  013BF08F   8D8B 20130000    LEA ECX,DWORD PTR DS:[EBX+0x1320]
       *  013BF095   83C8 FF          OR EAX,0xFFFFFFFF
       *  013BF098   89BB 1C130000    MOV DWORD PTR DS:[EBX+0x131C],EDI
       *  013BF09E   E8 8D39FAFF      CALL yorino_t.01362A30
       *  013BF0A3   8B45 10          MOV EAX,DWORD PTR SS:[EBP+0x10]
       *  013BF0A6   56               PUSH ESI
       *  013BF0A7   50               PUSH EAX
       *  013BF0A8   8D8B 3C130000    LEA ECX,DWORD PTR DS:[EBX+0x133C]
       *  013BF0AE   83C8 FF          OR EAX,0xFFFFFFFF
       *  013BF0B1   E8 7A39FAFF      CALL yorino_t.01362A30
       *  013BF0B6   8B15 00A74B01    MOV EDX,DWORD PTR DS:[0x14BA700]         ; yorino_t.0146603C
       *  013BF0BC   8B82 CC000000    MOV EAX,DWORD PTR DS:[EDX+0xCC]
       *  013BF0C2   B9 00A74B01      MOV ECX,yorino_t.014BA700
       *  013BF0C7   FFD0             CALL EAX
       *  013BF0C9   3BC6             CMP EAX,ESI
       *  013BF0CB   7E 15            JLE SHORT yorino_t.013BF0E2
       *  013BF0CD   3983 CC290000    CMP DWORD PTR DS:[EBX+0x29CC],EAX
       *  013BF0D3   7C 0D            JL SHORT yorino_t.013BF0E2
       *  013BF0D5   8BCB             MOV ECX,EBX
       *  013BF0D7   E8 14650000      CALL yorino_t.013C55F0
       *  013BF0DC   89B3 CC290000    MOV DWORD PTR DS:[EBX+0x29CC],ESI
       *  013BF0E2   8A45 1C          MOV AL,BYTE PTR SS:[EBP+0x1C]
       *  013BF0E5   8883 421A0000    MOV BYTE PTR DS:[EBX+0x1A42],AL
       *  013BF0EB   84C0             TEST AL,AL
       *  013BF0ED   75 1F            JNZ SHORT yorino_t.013BF10E
       *  013BF0EF   83BB A0120000 02 CMP DWORD PTR DS:[EBX+0x12A0],0x2
       *  013BF0F6   75 16            JNZ SHORT yorino_t.013BF10E
       *  013BF0F8   89B3 A0120000    MOV DWORD PTR DS:[EBX+0x12A0],ESI
       *  013BF0FE   8B15 00A74B01    MOV EDX,DWORD PTR DS:[0x14BA700]         ; yorino_t.0146603C
       *  013BF104   8B42 2C          MOV EAX,DWORD PTR DS:[EDX+0x2C]
       *  013BF107   B9 00A74B01      MOV ECX,yorino_t.014BA700
       *  013BF10C   FFD0             CALL EAX
       *  013BF10E   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
       *  013BF111   8B53 10          MOV EDX,DWORD PTR DS:[EBX+0x10]
       *  013BF114   8B52 3C          MOV EDX,DWORD PTR DS:[EDX+0x3C]
       *  013BF117   6A 00            PUSH 0x0
       *  013BF119   6A 01            PUSH 0x1
       *  013BF11B   50               PUSH EAX
       *  013BF11C   8D4D D8          LEA ECX,DWORD PTR SS:[EBP-0x28]
       *  013BF11F   51               PUSH ECX
       *  013BF120   8D45 BC          LEA EAX,DWORD PTR SS:[EBP-0x44]
       *  013BF123   50               PUSH EAX
       *  013BF124   8D4B 10          LEA ECX,DWORD PTR DS:[EBX+0x10]
       *  013BF127   FFD2             CALL EDX
       *  013BF129   8B43 10          MOV EAX,DWORD PTR DS:[EBX+0x10]
       *  013BF12C   8BB3 0C1A0000    MOV ESI,DWORD PTR DS:[EBX+0x1A0C]
       *  013BF132   8945 1C          MOV DWORD PTR SS:[EBP+0x1C],EAX
       *  013BF135   8B83 141A0000    MOV EAX,DWORD PTR DS:[EBX+0x1A14]
       *  013BF13B   E8 204B0100      CALL yorino_t.013D3C60
       *  013BF140   8B55 1C          MOV EDX,DWORD PTR SS:[EBP+0x1C]
       *  013BF143   50               PUSH EAX
       *  013BF144   8B42 4C          MOV EAX,DWORD PTR DS:[EDX+0x4C]
       *  013BF147   8BCF             MOV ECX,EDI
       *  013BF149   51               PUSH ECX
       *  013BF14A   8D4B 10          LEA ECX,DWORD PTR DS:[EBX+0x10]
       *  013BF14D   FFD0             CALL EAX
       *  013BF14F   8B53 10          MOV EDX,DWORD PTR DS:[EBX+0x10]
       *  013BF152   8B42 78          MOV EAX,DWORD PTR DS:[EDX+0x78]
       *  013BF155   8D4B 10          LEA ECX,DWORD PTR DS:[EBX+0x10]
       *  013BF158   FFD0             CALL EAX
       *  013BF15A   8BF3             MOV ESI,EBX
       *  013BF15C   8983 64130000    MOV DWORD PTR DS:[EBX+0x1364],EAX
       *  013BF162   E8 B9B0FFFF      CALL yorino_t.013BA220
       *  013BF167   84C0             TEST AL,AL
       *  013BF169   74 6D            JE SHORT yorino_t.013BF1D8
       *  013BF16B   8B53 10          MOV EDX,DWORD PTR DS:[EBX+0x10]
       *  013BF16E   8B42 40          MOV EAX,DWORD PTR DS:[EDX+0x40]
       *  013BF171   6A 00            PUSH 0x0
       *  013BF173   6A 01            PUSH 0x1
       *  013BF175   8D4B 10          LEA ECX,DWORD PTR DS:[EBX+0x10]
       *  013BF178   FFD0             CALL EAX
       *  013BF17A   E8 C1FDFFFF      CALL yorino_t.013BEF40
       *  013BF17F   33C9             XOR ECX,ECX
       *  013BF181   8BFB             MOV EDI,EBX
       *  013BF183   E8 C8B8FFFF      CALL yorino_t.013BAA50
       *  013BF188   33FF             XOR EDI,EDI
       *  013BF18A   89BB 181A0000    MOV DWORD PTR DS:[EBX+0x1A18],EDI
       *  013BF190   E8 3BF0FFFF      CALL yorino_t.013BE1D0
       *  013BF195   68 78CB4401      PUSH yorino_t.0144CB78
       *  013BF19A   8D75 A0          LEA ESI,DWORD PTR SS:[EBP-0x60]
       *  013BF19D   C745 B4 0F000000 MOV DWORD PTR SS:[EBP-0x4C],0xF
       *  013BF1A4   897D B0          MOV DWORD PTR SS:[EBP-0x50],EDI
       *  013BF1A7   C645 A0 00       MOV BYTE PTR SS:[EBP-0x60],0x0
       *  013BF1AB   E8 A065FAFF      CALL yorino_t.01365750
       *  013BF1B0   C645 FC 02       MOV BYTE PTR SS:[EBP-0x4],0x2
       *  013BF1B4   8B53 10          MOV EDX,DWORD PTR DS:[EBX+0x10]
       *  013BF1B7   8B52 6C          MOV EDX,DWORD PTR DS:[EDX+0x6C]
       *  013BF1BA   8D4B 10          LEA ECX,DWORD PTR DS:[EBX+0x10]
       *  013BF1BD   6A 01            PUSH 0x1
       *  013BF1BF   8BC6             MOV EAX,ESI
       *  013BF1C1   50               PUSH EAX
       *  013BF1C2   FFD2             CALL EDX
       *  013BF1C4   837D B4 10       CMP DWORD PTR SS:[EBP-0x4C],0x10
       *  013BF1C8   72 56            JB SHORT yorino_t.013BF220
       *  013BF1CA   8B45 A0          MOV EAX,DWORD PTR SS:[EBP-0x60]
       *  013BF1CD   50               PUSH EAX
       *  013BF1CE   E8 28B50500      CALL yorino_t.0141A6FB
       *  013BF1D3   83C4 04          ADD ESP,0x4
       *  013BF1D6   EB 48            JMP SHORT yorino_t.013BF220
       *  013BF1D8   8B7D 10          MOV EDI,DWORD PTR SS:[EBP+0x10]
       *  013BF1DB   C783 181A0000 04>MOV DWORD PTR DS:[EBX+0x1A18],0x4
       *  013BF1E5   837F 10 00       CMP DWORD PTR DS:[EDI+0x10],0x0
       *  013BF1E9   C705 64514801 00>MOV DWORD PTR DS:[0x1485164],0x0
       *  013BF1F3   76 2B            JBE SHORT yorino_t.013BF220
       *  013BF1F5   8BF3             MOV ESI,EBX
       *  013BF1F7   E8 D4EFFFFF      CALL yorino_t.013BE1D0
       *  013BF1FC   8B15 00A74B01    MOV EDX,DWORD PTR DS:[0x14BA700]         ; yorino_t.0146603C
       *  013BF202   8B82 8C000000    MOV EAX,DWORD PTR DS:[EDX+0x8C]
       *  013BF208   B9 00A74B01      MOV ECX,yorino_t.014BA700
       *  013BF20D   FFD0             CALL EAX
       *  013BF20F   84C0             TEST AL,AL
       *  013BF211   75 0D            JNZ SHORT yorino_t.013BF220
       *  013BF213   837F 10 00       CMP DWORD PTR DS:[EDI+0x10],0x0
       *  013BF217   76 07            JBE SHORT yorino_t.013BF220
       *  013BF219   57               PUSH EDI
       *  013BF21A   53               PUSH EBX
       *  013BF21B   E8 A0EAFFFF      CALL yorino_t.013BDCC0
       *  013BF220   BE 10000000      MOV ESI,0x10
       *  013BF225   C683 C8290000 00 MOV BYTE PTR DS:[EBX+0x29C8],0x0
       *  013BF22C   3975 EC          CMP DWORD PTR SS:[EBP-0x14],ESI
       *  013BF22F   72 0C            JB SHORT yorino_t.013BF23D
       *  013BF231   8B4D D8          MOV ECX,DWORD PTR SS:[EBP-0x28]
       *  013BF234   51               PUSH ECX
       *  013BF235   E8 C1B40500      CALL yorino_t.0141A6FB
       *  013BF23A   83C4 04          ADD ESP,0x4
       *  013BF23D   3975 D0          CMP DWORD PTR SS:[EBP-0x30],ESI
       *  013BF240   5F               POP EDI
       *  013BF241   5E               POP ESI
       *  013BF242   C745 EC 0F000000 MOV DWORD PTR SS:[EBP-0x14],0xF
       *  013BF249   C745 E8 00000000 MOV DWORD PTR SS:[EBP-0x18],0x0
       *  013BF250   C645 D8 00       MOV BYTE PTR SS:[EBP-0x28],0x0
       *  013BF254   5B               POP EBX
       *  013BF255   72 0C            JB SHORT yorino_t.013BF263
       *  013BF257   8B55 BC          MOV EDX,DWORD PTR SS:[EBP-0x44]
       *  013BF25A   52               PUSH EDX
       *  013BF25B   E8 9BB40500      CALL yorino_t.0141A6FB
       *  013BF260   83C4 04          ADD ESP,0x4
       *  013BF263   8B4D F4          MOV ECX,DWORD PTR SS:[EBP-0xC]
       *  013BF266   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
       *  013BF26D   8BE5             MOV ESP,EBP
       *  013BF26F   5D               POP EBP
       *  013BF270   C2 1800          RETN 0x18
       *  013BF273   CC               INT3
       *  013BF274   CC               INT3
       *  013BF275   CC               INT3
       *  013BF276   CC               INT3
       *  013BF277   CC               INT3
       *  013BF278   CC               INT3
       *  013BF279   CC               INT3
       *  013BF27A   CC               INT3
       *  013BF27B   CC               INT3
       *  013BF27C   CC               INT3
       *  013BF27D   CC               INT3
       *  013BF27E   CC               INT3
       *  013BF27F   CC               INT3
       *
       *  Sample text:
       *  00C3091C  57 48 49 54 45 2E 70 6E 67 00 00 00 00 00 00 00  WHITE.png.......
       *  00C3092C  09 00 00 00 0F 00 00 00 00 00 00 00 00 00 00 00  ...............
       */
      TextUnionA *arg_,
          argValue_;
      std::unordered_map<uintptr_t, int> addr_role;
      void hookBeforehookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
      {
        static std::string data_;
        // auto arg = (TextUnionA *)s->ecx;
        auto arg = (TextUnionA *)s->stack[0]; // arg1
        if (!arg || !arg->isValid())
          return;
        auto vw = arg->view();
        auto text = vw.data();
        if (all_ascii(text))
          return;
        int size = vw.size(),
            trimmedSize = size;
        auto trimmedText = trim(text, &trimmedSize);
        if (!trimmedSize || !*trimmedText)
          return;
        // auto sig = Engine::hashThreadSignature(role, retaddr);
        std::string oldData(trimmedText, trimmedSize);
        auto retaddr = s->stack[0];
        *role = addr_role[retaddr];
        if (*role == Engine::NameRole)
          strReplace(oldData, "\x81\x40"); // remove spaces in the middle of names

        buffer->from(oldData);
      }
      void hookafter(hook_context *s, TextBuffer buffer)
      {
        std::string newData = buffer.strA();
        auto arg = (TextUnionA *)s->stack[0]; // arg1
        auto vw = arg->view();
        auto text = vw.data();
        int size = vw.size(),
            trimmedSize = size;
        auto trimmedText = trim(text, &trimmedSize);
        int prefixSize = trimmedText - text,
            suffixSize = size - prefixSize - trimmedSize;
        if (prefixSize)
          newData.insert(0, std::string(text, prefixSize));
        if (suffixSize)
          newData.append(trimmedText + trimmedSize, suffixSize);
        arg_ = arg;
        argValue_ = *arg;
        arg->setText(newData);
      }
      void hookAfter(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        if (arg_)
        {
          *arg_ = argValue_;
          arg_ = nullptr;
        }
      }
    } // namespace Private

    /**
     *  Sample game: ソレヨリノ前奏詩
     *  arg1 is source, ecx is target.
     *
     *  01052A2D   CC               INT3
     *  01052A2E   CC               INT3
     *  01052A2F   CC               INT3
     *  01052A30   55               PUSH EBP
     *  01052A31   8BEC             MOV EBP,ESP
     *  01052A33   53               PUSH EBX
     *  01052A34   8B5D 0C          MOV EBX,DWORD PTR SS:[EBP+0xC]
     *  01052A37   56               PUSH ESI
     *  01052A38   8BF1             MOV ESI,ECX	; jichi: ecx is target address?
     *  01052A3A   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
     *  01052A3D   57               PUSH EDI
     *  01052A3E   8B79 10          MOV EDI,DWORD PTR DS:[ECX+0x10] ; jichi: source size
     *  01052A41   3BFB             CMP EDI,EBX
     *  01052A43   73 0A            JNB SHORT yorino_t.01052A4F
     *  01052A45   68 88CA1301      PUSH yorino_t.0113CA88                   ; ASCII "invalid string position"
     *  01052A4A   E8 337C0B00      CALL yorino_t.0110A682
     *  01052A4F   2BFB             SUB EDI,EBX
     *  01052A51   3BC7             CMP EAX,EDI
     *  01052A53   0F42F8           CMOVB EDI,EAX
     *  01052A56   3BF1             CMP ESI,ECX
     *  01052A58   75 1D            JNZ SHORT yorino_t.01052A77
     *  01052A5A   8D0C1F           LEA ECX,DWORD PTR DS:[EDI+EBX]
     *  01052A5D   83C8 FF          OR EAX,0xFFFFFFFF
     *  01052A60   E8 EBFCFFFF      CALL yorino_t.01052750
     *  01052A65   8BC3             MOV EAX,EBX
     *  01052A67   33C9             XOR ECX,ECX
     *  01052A69   E8 E2FCFFFF      CALL yorino_t.01052750
     *  01052A6E   5F               POP EDI
     *  01052A6F   8BC6             MOV EAX,ESI
     *  01052A71   5E               POP ESI
     *  01052A72   5B               POP EBX
     *  01052A73   5D               POP EBP
     *  01052A74   C2 0800          RETN 0x8
     *  01052A77   83FF FE          CMP EDI,-0x2
     *  01052A7A   76 0A            JBE SHORT yorino_t.01052A86
     *  01052A7C   68 B4CA1301      PUSH yorino_t.0113CAB4                   ; ASCII "string too long"
     *  01052A81   E8 AF7B0B00      CALL yorino_t.0110A635
     *  01052A86   8B46 14          MOV EAX,DWORD PTR DS:[ESI+0x14]
     *  01052A89   3BC7             CMP EAX,EDI
     *  01052A8B   73 27            JNB SHORT yorino_t.01052AB4
     *  01052A8D   8B46 10          MOV EAX,DWORD PTR DS:[ESI+0x10]
     *  01052A90   50               PUSH EAX
     *  01052A91   57               PUSH EDI
     *  01052A92   56               PUSH ESI
     *  01052A93   E8 88FDFFFF      CALL yorino_t.01052820
     *  01052A98   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
     *  01052A9B   85FF             TEST EDI,EDI
     *  01052A9D   74 68            JE SHORT yorino_t.01052B07
     *  01052A9F   B8 10000000      MOV EAX,0x10
     *  01052AA4   3941 14          CMP DWORD PTR DS:[ECX+0x14],EAX
     *  01052AA7   72 02            JB SHORT yorino_t.01052AAB
     *  01052AA9   8B09             MOV ECX,DWORD PTR DS:[ECX]
     *  01052AAB   3946 14          CMP DWORD PTR DS:[ESI+0x14],EAX
     *  01052AAE   72 2A            JB SHORT yorino_t.01052ADA
     *  01052AB0   8B06             MOV EAX,DWORD PTR DS:[ESI]
     *  01052AB2   EB 28            JMP SHORT yorino_t.01052ADC
     *  01052AB4   85FF             TEST EDI,EDI
     *  01052AB6  ^75 E7            JNZ SHORT yorino_t.01052A9F
     *  01052AB8   897E 10          MOV DWORD PTR DS:[ESI+0x10],EDI
     *  01052ABB   83F8 10          CMP EAX,0x10
     *  01052ABE   72 0E            JB SHORT yorino_t.01052ACE
     *  01052AC0   8B06             MOV EAX,DWORD PTR DS:[ESI]
     *  01052AC2   5F               POP EDI
     *  01052AC3   C600 00          MOV BYTE PTR DS:[EAX],0x0
     *  01052AC6   8BC6             MOV EAX,ESI
     *  01052AC8   5E               POP ESI
     *  01052AC9   5B               POP EBX
     *  01052ACA   5D               POP EBP
     *  01052ACB   C2 0800          RETN 0x8
     *  01052ACE   5F               POP EDI
     *  01052ACF   8BC6             MOV EAX,ESI
     *  01052AD1   5E               POP ESI
     *  01052AD2   C600 00          MOV BYTE PTR DS:[EAX],0x0
     *  01052AD5   5B               POP EBX
     *  01052AD6   5D               POP EBP
     *  01052AD7   C2 0800          RETN 0x8
     *  01052ADA   8BC6             MOV EAX,ESI	; jichi: esi is target address
     *  01052ADC   57               PUSH EDI	; jichi: source size
     *  01052ADD   03CB             ADD ECX,EBX
     *  01052ADF   51               PUSH ECX	; jichi: source
     *  01052AE0   50               PUSH EAX	; jichi: target
     *  01052AE1   E8 9AC80B00      CALL yorino_t.0110F380	; jichi: called here
     *  01052AE6   83C4 0C          ADD ESP,0xC
     *  01052AE9   837E 14 10       CMP DWORD PTR DS:[ESI+0x14],0x10
     *  01052AED   897E 10          MOV DWORD PTR DS:[ESI+0x10],EDI
     *  01052AF0   72 0F            JB SHORT yorino_t.01052B01
     *  01052AF2   8B06             MOV EAX,DWORD PTR DS:[ESI]
     *  01052AF4   C60438 00        MOV BYTE PTR DS:[EAX+EDI],0x0
     *  01052AF8   5F               POP EDI
     *  01052AF9   8BC6             MOV EAX,ESI
     *  01052AFB   5E               POP ESI
     *  01052AFC   5B               POP EBX
     *  01052AFD   5D               POP EBP
     *  01052AFE   C2 0800          RETN 0x8
     *  01052B01   8BC6             MOV EAX,ESI
     *  01052B03   C60438 00        MOV BYTE PTR DS:[EAX+EDI],0x0
     *  01052B07   5F               POP EDI
     *  01052B08   8BC6             MOV EAX,ESI
     *  01052B0A   5E               POP ESI
     *  01052B0B   5B               POP EBX
     *  01052B0C   5D               POP EBP
     *  01052B0D   C2 0800          RETN 0x8
     *  01052B10   6A 00            PUSH 0x0
     *  01052B12   50               PUSH EAX
     *  01052B13   C746 14 0F000000 MOV DWORD PTR DS:[ESI+0x14],0xF
     *  01052B1A   C746 10 00000000 MOV DWORD PTR DS:[ESI+0x10],0x0
     *  01052B21   83C8 FF          OR EAX,0xFFFFFFFF
     *  01052B24   8BCE             MOV ECX,ESI
     *  01052B26   C606 00          MOV BYTE PTR DS:[ESI],0x0
     *  01052B29   E8 02FFFFFF      CALL yorino_t.01052A30
     *  01052B2E   8BC6             MOV EAX,ESI
     *  01052B30   C3               RETN
     *  01052B31   CC               INT3
     *  01052B32   CC               INT3
     *  01052B33   CC               INT3
     *  01052B34   CC               INT3
     *  01052B35   CC               INT3
     *  01052B36   CC               INT3
     *  01052B37   CC               INT3
     *  01052B38   CC               INT3
     *  01052B39   CC               INT3
     *  01052B3A   CC               INT3
     *  01052B3B   CC               INT3
     *  01052B3C   CC               INT3
     *
     *  005CF5C4   01C17D68
     *  005CF5C8   00000026
     *  005CF5CC  /005CF5EC
     *  005CF5D0  |00172AE6  RETURN to yorino_t.00172AE6 from yorino_t.0022F380
     *  005CF5D4  |01C154F0	; jichi: target text
     *  005CF5D8  |01C15608	; jcihi: source text
     *  005CF5DC  |00000026	; jichi: source size
     *  005CF5E0  |00000082	; jichi: capacity? not sure
     *  005CF5E4  |00000000
     *  005CF5E8  |01C16A68
     *  005CF5EC  ]005CF668
     *  005CF5F0  |001CF08A  RETURN to yorino_t.001CF08A from yorino_t.00172A30
     *  005CF5F4  |005CF640
     *  005CF5F8  |00000000
     *  005CF5FC  |01C19500
     */
    bool attach(ULONG startAddress, ULONG stopAddress)
    {
      const uint8_t bytes[] = {
          0x8b, 0xc6, // 01052ada   8bc6             mov eax,esi	; jichi: esi is target address
          0x57,       // 01052adc   57               push edi	; jichi: source size
          0x03, 0xcb, // 01052add   03cb             add ecx,ebx
          0x51,       // 01052adf   51               push ecx	; jichi: source
          0x50        // 01052ae0   50               push eax	; jichi: target
                      // 0xe8, XX4,      // 01052ae1   e8 9ac80b00      call yorino_t.0110f380	; jichi: called here
                      // 0x83,0xc4, 0x0c // 01052ae6   83c4 0c          add esp,0xc
      };
      // enum { addr_offset = sizeof(bytes) - 8 };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return false;
      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        return false;
      // return winhook::hook_before(addr, Private::hookBefore);

      bool count = false;
      auto fun = [&count](ULONG addr) -> bool
      {
        // Sample game: ソレヨリノ前奏詩
        // 013BEFFA   E8 313AFAFF      CALL yorino_t.01362A30  ; jichi: name call
        // 013BEFFF   8B4D 18          MOV ECX,DWORD PTR SS:[EBP+0x18]
        // 013BF002   56               PUSH ESI
        // 013BF003   8975 FC          MOV DWORD PTR SS:[EBP-0x4],ESI
        // 013BF006   51               PUSH ECX
        // 013BF007   83C8 FF          OR EAX,0xFFFFFFFF
        // 013BF00A   8D4D D8          LEA ECX,DWORD PTR SS:[EBP-0x28]
        // 013BF00D   897D EC          MOV DWORD PTR SS:[EBP-0x14],EDI
        // 013BF010   8975 E8          MOV DWORD PTR SS:[EBP-0x18],ESI
        // 013BF013   C645 D8 00       MOV BYTE PTR SS:[EBP-0x28],0x0
        // 013BF017   E8 143AFAFF      CALL yorino_t.01362A30 ; jichi: scenario call
        // 013BF01C   C645 FC 01       MOV BYTE PTR SS:[EBP-0x4],0x1
        // 013BF020   8B8B 7C2A0000    MOV ECX,DWORD PTR DS:[EBX+0x2A7C]
        // 013BF026   3BCE             CMP ECX,ESI
        //
        // Bad scenario to skip:
        //
        // 0035A9A3   C745 E4 0F000000 MOV DWORD PTR SS:[EBP-0x1C],0xF
        // 0035A9AA   C745 E0 00000000 MOV DWORD PTR SS:[EBP-0x20],0x0
        // 0035A9B1   C645 D0 00       MOV BYTE PTR SS:[EBP-0x30],0x0
        // 0035A9B5  -E9 4656D001      JMP 02060000 ; jichi: here
        // 0035A9BA   C645 FC 01       MOV BYTE PTR SS:[EBP-0x4],0x1
        // 0035A9BE   8B7D E0          MOV EDI,DWORD PTR SS:[EBP-0x20]
        // 0035A9C1   83FF 01          CMP EDI,0x1
        // 0035A9C4   0F86 B0000000    JBE .0035AA7A
        auto retaddr = addr + 5;
        auto role = Engine::OtherRole;
        switch (*(DWORD *)retaddr)
        {
        case 0x56184d8b:
          // 013BEFFF   8B4D 18          MOV ECX,DWORD PTR SS:[EBP+0x18]
          // 013BF002   56               PUSH ESI
          role = Engine::NameRole;
          break;
        case 0x01fc45c6: // 013BF01C   C645 FC 01       MOV BYTE PTR SS:[EBP-0x4],0x1
          if (*(DWORD *)(retaddr - 5 - sizeof(DWORD)) == 0x00D845C6)
          { // previous instruction
            role = Engine::ScenarioRole;
            break;
          }
        default:
          return true;
        }
        Private::addr_role[retaddr] = role;
        {
          HookParam hp;
          hp.address = addr;
          hp.text_fun = Private::hookBeforehookBefore;
          hp.embed_fun = Private::hookafter;
          hp.type = EMBED_ABLE | USING_STRING | EMBED_DYNA_SJIS | NO_CONTEXT;
          hp.embed_hook_font = F_GetGlyphOutlineA;
          hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
          {
            buffer->from(re::sub(buffer->strA(), "\\{.*?\\}"));
          };
          count |= NewHook(hp, "EmbedMinori");
        }
        {
          HookParam hp;
          hp.address = addr + 5;
          hp.text_fun = Private::hookAfter;
          hp.embed_fun = Private::hookafter;
          count |= NewHook(hp, "EmbedMinori");
        }
        return true; // replace all functions
      };
      MemDbg::iterNearCallAddress(fun, addr, startAddress, stopAddress);

      return count;
    }

  } // namespace ScenarioHook

} // unnamed namespace

bool Minori::attach_function()
{
  bool embed = ScenarioHook::attach(processStartAddress, processStopAddress);
  return InsertMinoriHooks() || embed;
}