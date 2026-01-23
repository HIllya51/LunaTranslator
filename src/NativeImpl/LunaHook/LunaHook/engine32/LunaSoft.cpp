#include "LunaSoft.h"
/** jichi 12/27/2014 LunaSoft
 * Sample game: [141226] [LunaSoft] 悪堕ラビリンス -- /hsn8@46C5EF
 *
 * /hsn8@46C5EF
 * - addr: 0x46C5EF
 * - off: 8
 * - type: 1025 = 0x401
 *
 * - 0046c57e   cc               int3
 * - 0046c57f   cc               int3
 * - 0046c580   55               push ebp       ; jichi: text in arg1
 * - 0046c581   8bec             mov ebp,esp
 * - 0046c583   83ec 08          sub esp,0x8
 * - 0046c586   894d f8          mov dword ptr ss:[ebp-0x8],ecx
 * - 0046c589   8b4d f8          mov ecx,dword ptr ss:[ebp-0x8]
 * - 0046c58c   83c1 1c          add ecx,0x1c
 * - 0046c58f   e8 2cebf9ff      call .0040b0c0
 * - 0046c594   8b00             mov eax,dword ptr ds:[eax]
 * - 0046c596   8945 fc          mov dword ptr ss:[ebp-0x4],eax
 * - 0046c599   837d fc 00       cmp dword ptr ss:[ebp-0x4],0x0
 * - 0046c59d   75 21            jnz short .0046c5c0
 * - 0046c59f   8b4d f8          mov ecx,dword ptr ss:[ebp-0x8]
 * - 0046c5a2   83c1 28          add ecx,0x28
 * - 0046c5a5   e8 16ebf9ff      call .0040b0c0
 * - 0046c5aa   8b08             mov ecx,dword ptr ds:[eax]
 * - 0046c5ac   894d fc          mov dword ptr ss:[ebp-0x4],ecx
 * - 0046c5af   8b55 fc          mov edx,dword ptr ss:[ebp-0x4]
 * - 0046c5b2   52               push edx
 * - 0046c5b3   8b4d f8          mov ecx,dword ptr ss:[ebp-0x8]
 * - 0046c5b6   83c1 28          add ecx,0x28
 * - 0046c5b9   e8 82d9f9ff      call .00409f40
 * - 0046c5be   eb 0f            jmp short .0046c5cf
 * - 0046c5c0   8b45 fc          mov eax,dword ptr ss:[ebp-0x4]
 * - 0046c5c3   50               push eax
 * - 0046c5c4   8b4d f8          mov ecx,dword ptr ss:[ebp-0x8]
 * - 0046c5c7   83c1 1c          add ecx,0x1c
 * - 0046c5ca   e8 71d9f9ff      call .00409f40
 * - 0046c5cf   837d fc 00       cmp dword ptr ss:[ebp-0x4],0x0
 * - 0046c5d3   75 02            jnz short .0046c5d7
 * - 0046c5d5   eb 61            jmp short .0046c638
 * - 0046c5d7   8b4d fc          mov ecx,dword ptr ss:[ebp-0x4]
 * - 0046c5da   e8 b1cdf9ff      call .00409390
 * - 0046c5df   8b4d 08          mov ecx,dword ptr ss:[ebp+0x8]
 * - 0046c5e2   51               push ecx                   ; jichi: text in ecx
 * - 0046c5e3   68 38010000      push 0x138
 * - 0046c5e8   8b55 fc          mov edx,dword ptr ss:[ebp-0x4]
 * - 0046c5eb   83c2 08          add edx,0x8
 * - 0046c5ee   52               push edx
 * - 0046c5ef   ff15 88b24c00    call dword ptr ds:[0x4cb288]  ; msvcr90.strcpy_s, jichi: text accessed here in arg2
 * - 0046c5f5   83c4 0c          add esp,0xc
 * - 0046c5f8   8b45 0c          mov eax,dword ptr ss:[ebp+0xc]
 * - 0046c5fb   50               push eax
 * - 0046c5fc   6a 10            push 0x10
 */
// Remove: \n\s*
// This is dangerous since \n could appear within SJIS
// static bool LunaSoftFilter(LPVOID data, size_t *size, HookParam *)
//{
//  size_t len = *size;
//  char *str = reinterpret_cast<char *>(data),
//       *cur;
//
//  while (len &&
//         (cur = ::memchr(str, '\n', len)) &&
//         --len) {
//    ::memmove(cur, cur + 1, len - (cur - str));
//    while (cur < str + len)
//      if (::isspace(*cur) && --len)
//        ::memmove(cur, cur + 1, len - (cur - str));
//      else if (len >= 2 && ::iswspace(*(LPCWSTR)cur) && (len-=2))
//        ::memmove(cur, cur + 2, len - (cur - str));
//      else
//        break;
//  }
//
//  *size = len;
//  return true;
//}
bool InsertLunaSoftHook()
{
  const BYTE bytes[] = {
      0xcc,             // 0046c57e   cc               int3
      0xcc,             // 0046c57f   cc               int3
      0x55,             // 0046c580   55               push ebp       ; jichi: text in arg1
      0x8b, 0xec,       // 0046c581   8bec             mov ebp,esp
      0x83, 0xec, 0x08, // 0046c583   83ec 08          sub esp,0x8
      0x89, 0x4d, 0xf8, // 0046c586   894d f8          mov dword ptr ss:[ebp-0x8],ecx
      0x8b, 0x4d, 0xf8, // 0046c589   8b4d f8          mov ecx,dword ptr ss:[ebp-0x8]
      0x83, 0xc1, 0x1c, // 0046c58c   83c1 1c          add ecx,0x1c
      0xe8              // 0046c58f   e8 2cebf9ff      call .0040b0c0
  };
  enum
  {
    addr_offset = 2
  };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  // GROWL(addr);
  if (!addr)
  {
    ConsoleOutput("LunaSoft: pattern not found");
    return false;
  }
  HookParam hp;
  hp.address = addr + addr_offset;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING;
  // hp.filter_fun = LunaSoftFilter; // remove \n
  ConsoleOutput("INSERT LunaSoft");
  return NewHook(hp, "LunaSoft");

  // There are no GDI functions anyway
  // ConsoleOutput("LunaSoft: disable GDI hooks");
  //
}
bool InsertXXkata()
{
  // アイリスフィールド

  // 素晴らしき国家の築き方
  // 浮遊都市の作り方
  // 正しい性奴隷の使い方

  // HSNc@0:user32.dll:wsprintfA
  auto addr = GetProcAddress(GetModuleHandleW(L"user32.dll"), "wsprintfA");
  if (!addr)
    return false;
  HookParam hp;
  hp.address = (uint64_t)addr;
  hp.type = USING_STRING | NO_CONTEXT;
  hp.offset = stackoffset(3);
  hp.filter_fun = all_ascii_Filter;
  return NewHook(hp, "XXkata");
}

namespace
{ // unnamed
  namespace ScenarioHook
  {
    namespace Private
    {
      lru_cache<std::string> cache_(100);

      /**
       *  Sample game: 悪堕ラビリンス, scenario return address: 0x42f6dc
       *
       *  0042F6C8   E8 335F0000      CALL lus004.00435600
       *  0042F6CD   8945 10          MOV DWORD PTR SS:[EBP+0x10],EAX
       *  0042F6D0   8B55 10          MOV EDX,DWORD PTR SS:[EBP+0x10]
       *  0042F6D3   52               PUSH EDX
       *  0042F6D4   8B4D EC          MOV ECX,DWORD PTR SS:[EBP-0x14]
       *  0042F6D7   E8 34850500      CALL lus004.00487C10
       *  0042F6DC   8B45 10          MOV EAX,DWORD PTR SS:[EBP+0x10]   ; jichi: retaddr
       *  0042F6DF   50               PUSH EAX
       *  0042F6E0   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
       *  0042F6E3   E8 785E0000      CALL lus004.00435560
       *  0042F6E8   8945 10          MOV DWORD PTR SS:[EBP+0x10],EAX
       *  0042F6EB   E9 5E010000      JMP lus004.0042F84E
       *  0042F6F0   8B4D 10          MOV ECX,DWORD PTR SS:[EBP+0x10]
       */
      void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
      {
        auto text = (LPCSTR)s->stack[1]; // arg1
        if (!text || !*text)             // || Util::allAscii(text))
          return;
        std::string oldData = text;
        if (cache_.exists(oldData))
          return;
        // 0042F6DC   8B45 10          MOV EAX,DWORD PTR SS:[EBP+0x10]   ; jichi: retaddr
        // 0042F6DF   50               PUSH EAX
        ULONG retaddr = s->stack[0];
        *role = Engine::OtherRole;
        if (*(DWORD *)retaddr == 0x5010458b)
          *role = Engine::ScenarioRole;
        buffer->from(oldData);
      }
      void hookafter1(hook_context *s, TextBuffer buffer, HookParam *)
      {
        auto newData = buffer.strA();
        cache_.put(newData);
        s->stack[1] = (ULONG)allocateString(newData); // arg1
      }
    } // namespace Private

    /**
     *  Sample game: 悪堕ラビリンス
     *
     *  Debugging method: Hook to all function that accessing the text
     *  Until find ones that can get text modified.
     *
     *  This is the first function accessing the text.
     *  It is used for text size allocation.
     *
     *  00487C0E   CC               INT3
     *  00487C0F   CC               INT3
     *  00487C10   55               PUSH EBP
     *  00487C11   8BEC             MOV EBP,ESP
     *  00487C13   51               PUSH ECX
     *  00487C14   894D FC          MOV DWORD PTR SS:[EBP-0x4],ECX
     *  00487C17   8B45 FC          MOV EAX,DWORD PTR SS:[EBP-0x4]
     *  00487C1A   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
     *  00487C1D   8988 AC020000    MOV DWORD PTR DS:[EAX+0x2AC],ECX
     *  00487C23   8B55 FC          MOV EDX,DWORD PTR SS:[EBP-0x4]
     *  00487C26   D9EE             FLDZ
     *  00487C28   D99A B0020000    FSTP DWORD PTR DS:[EDX+0x2B0]
     *  00487C2E   8B45 FC          MOV EAX,DWORD PTR SS:[EBP-0x4]
     *  00487C31   8B88 84000000    MOV ECX,DWORD PTR DS:[EAX+0x84]
     *  00487C37   81E1 00000F00    AND ECX,0xF0000
     *  00487C3D   C1E9 10          SHR ECX,0x10
     *  00487C40   83F9 02          CMP ECX,0x2
     *  00487C43   75 21            JNZ SHORT .00487C66
     *  00487C45   8B55 FC          MOV EDX,DWORD PTR SS:[EBP-0x4]
     *  00487C48   8B82 AC020000    MOV EAX,DWORD PTR DS:[EDX+0x2AC]
     *  00487C4E   50               PUSH EAX
     *  00487C4F   8B4D FC          MOV ECX,DWORD PTR SS:[EBP-0x4]
     *  00487C52   8B89 88000000    MOV ECX,DWORD PTR DS:[ECX+0x88]
     *  00487C58   E8 0323FAFF      CALL .00429F60
     *  00487C5D   8B55 FC          MOV EDX,DWORD PTR SS:[EBP-0x4]
     *  00487C60   8982 B8020000    MOV DWORD PTR DS:[EDX+0x2B8],EAX
     *  00487C66   8BE5             MOV ESP,EBP
     *  00487C68   5D               POP EBP
     *  00487C69   C2 0400          RETN 0x4
     *  00487C6C   CC               INT3
     *  00487C6D   CC               INT3
     *  00487C6E   CC               INT3
     *
     *  This is the function where text is being painted.
     *
     *  0042B1EE   CC               INT3
     *  0042B1EF   CC               INT3
     *  0042B1F0   55               PUSH EBP
     *  0042B1F1   8BEC             MOV EBP,ESP
     *  0042B1F3   81EC 44010000    SUB ESP,0x144
     *  0042B1F9   898D E8FEFFFF    MOV DWORD PTR SS:[EBP-0x118],ECX
     *  0042B1FF   8B85 E8FEFFFF    MOV EAX,DWORD PTR SS:[EBP-0x118]
     *  0042B205   8378 24 00       CMP DWORD PTR DS:[EAX+0x24],0x0
     *  0042B209   75 05            JNZ SHORT lus004.0042B210
     *  0042B20B   E9 2E070000      JMP lus004.0042B93E
     *  0042B210   837D 08 00       CMP DWORD PTR SS:[EBP+0x8],0x0
     *  0042B214   75 05            JNZ SHORT lus004.0042B21B
     *  0042B216   E9 23070000      JMP lus004.0042B93E
     *  0042B21B   C785 FCFEFFFF 00>MOV DWORD PTR SS:[EBP-0x104],0x0
     *  0042B225   C745 D0 00000000 MOV DWORD PTR SS:[EBP-0x30],0x0
     *  0042B22C   C785 40FFFFFF 00>MOV DWORD PTR SS:[EBP-0xC0],0x0
     *  0042B236   8B4D 14          MOV ECX,DWORD PTR SS:[EBP+0x14]
     *  0042B239   83E1 03          AND ECX,0x3
     *  0042B23C   83F9 01          CMP ECX,0x1
     *  0042B23F   75 07            JNZ SHORT lus004.0042B248
     *  0042B241   D9EE             FLDZ
     *  0042B243   D95D 88          FSTP DWORD PTR SS:[EBP-0x78]
     *  0042B246   EB 1B            JMP SHORT lus004.0042B263
     *  0042B248   8B55 14          MOV EDX,DWORD PTR SS:[EBP+0x14]
     *  0042B24B   83E2 03          AND EDX,0x3
     *  0042B24E   83FA 02          CMP EDX,0x2
     *  0042B251   75 07            JNZ SHORT lus004.0042B25A
     *  0042B253   D9E8             FLD1
     *  0042B255   D95D 88          FSTP DWORD PTR SS:[EBP-0x78]
     *  0042B258   EB 09            JMP SHORT lus004.0042B263
     *  0042B25A   D905 986A4E00    FLD DWORD PTR DS:[0x4E6A98]
     *  0042B260   D95D 88          FSTP DWORD PTR SS:[EBP-0x78]
     *  0042B263   8B45 14          MOV EAX,DWORD PTR SS:[EBP+0x14]
     *  0042B266   83E0 0C          AND EAX,0xC
     *  0042B269   83F8 04          CMP EAX,0x4
     *  0042B26C   75 07            JNZ SHORT lus004.0042B275
     *  0042B26E   D9EE             FLDZ
     *  0042B270   D95D AC          FSTP DWORD PTR SS:[EBP-0x54]
     *  0042B273   EB 1B            JMP SHORT lus004.0042B290
     *  0042B275   8B4D 14          MOV ECX,DWORD PTR SS:[EBP+0x14]
     *  0042B278   83E1 0C          AND ECX,0xC
     *  0042B27B   83F9 08          CMP ECX,0x8
     *  0042B27E   75 07            JNZ SHORT lus004.0042B287
     *  0042B280   D9E8             FLD1
     *  0042B282   D95D AC          FSTP DWORD PTR SS:[EBP-0x54]
     *  0042B285   EB 09            JMP SHORT lus004.0042B290
     *  0042B287   D905 986A4E00    FLD DWORD PTR DS:[0x4E6A98]
     *  0042B28D   D95D AC          FSTP DWORD PTR SS:[EBP-0x54]
     *  0042B290   8B55 0C          MOV EDX,DWORD PTR SS:[EBP+0xC]
     *  0042B293   D942 30          FLD DWORD PTR DS:[EDX+0x30]
     *  0042B296   D99D 74FFFFFF    FSTP DWORD PTR SS:[EBP-0x8C]
     *  0042B29C   8B45 0C          MOV EAX,DWORD PTR SS:[EBP+0xC]
     *  0042B29F   D940 34          FLD DWORD PTR DS:[EAX+0x34]
     *  0042B2A2   D99D 78FFFFFF    FSTP DWORD PTR SS:[EBP-0x88]
     *  0042B2A8   8B8D E8FEFFFF    MOV ECX,DWORD PTR SS:[EBP-0x118]
     *  0042B2AE   8B51 2C          MOV EDX,DWORD PTR DS:[ECX+0x2C]
     *  0042B2B1   8995 E0FEFFFF    MOV DWORD PTR SS:[EBP-0x120],EDX
     *  0042B2B7   C785 E4FEFFFF 00>MOV DWORD PTR SS:[EBP-0x11C],0x0
     *  0042B2C1   DFAD E0FEFFFF    FILD QWORD PTR SS:[EBP-0x120]
     *  0042B2C7   DC0D 186A4E00    FMUL QWORD PTR DS:[0x4E6A18]
     *  0042B2CD   D99D 68FFFFFF    FSTP DWORD PTR SS:[EBP-0x98]
     *  0042B2D3   D9EE             FLDZ
     *  0042B2D5   D99D 6CFFFFFF    FSTP DWORD PTR SS:[EBP-0x94]
     *  0042B2DB   D9EE             FLDZ
     *  0042B2DD   D95D D4          FSTP DWORD PTR SS:[EBP-0x2C]
     *  0042B2E0   8B85 E8FEFFFF    MOV EAX,DWORD PTR SS:[EBP-0x118]
     *  0042B2E6   8B48 2C          MOV ECX,DWORD PTR DS:[EAX+0x2C]
     *  0042B2E9   898D D8FEFFFF    MOV DWORD PTR SS:[EBP-0x128],ECX
     *  0042B2EF   C785 DCFEFFFF 00>MOV DWORD PTR SS:[EBP-0x124],0x0
     *  0042B2F9   DFAD D8FEFFFF    FILD QWORD PTR SS:[EBP-0x128]
     *  0042B2FF   D95D D8          FSTP DWORD PTR SS:[EBP-0x28]
     *  0042B302   8B55 0C          MOV EDX,DWORD PTR SS:[EBP+0xC]
     *  0042B305   52               PUSH EDX
     *  0042B306   8D85 00FFFFFF    LEA EAX,DWORD PTR SS:[EBP-0x100]
     *  0042B30C   50               PUSH EAX
     *  0042B30D   E8 3E6FFEFF      CALL lus004.00412250
     *  0042B312   83C4 04          ADD ESP,0x4
     *  0042B315   D9E8             FLD1
     *  0042B317   D91C24           FSTP DWORD PTR SS:[ESP]
     *  0042B31A   51               PUSH ECX
     *  0042B31B   D9EE             FLDZ
     *  0042B31D   D91C24           FSTP DWORD PTR SS:[ESP]
     *  0042B320   51               PUSH ECX
     *  0042B321   D9EE             FLDZ
     *  0042B323   D91C24           FSTP DWORD PTR SS:[ESP]
     *  0042B326   51               PUSH ECX
     *  0042B327   D9EE             FLDZ
     *  ...
     *
     *
     *  0012FC68   089E0060
     *  0012FC6C   08AD9D00
     *  0012FC70   01D66B60
     *  0012FC74   00000000
     *  0012FC78   0012FDD0
     *  0012FC7C   00000000
     *  0012FC80  /0012FDD0
     *  0012FC84  |0042B43B  RETURN to lus004.0042B43B from lus004.00429E50
     *  0012FC88  |02C2AB18 ; jichi: text is here
     *  0012FC8C  |0012FCAC
     *  0012FC90  |00000000
     *  0012FC94  |0012FCC4
     *  0012FC98  |6186B837  RETURN to d3d9.6186B837
     *  0012FC9C  |0029DFA0
     *  0012FCA0  |0012FCAC
     *  0012FCA4  |00000000
     *  0012FCA8  |00000018
     *  0012FCAC  |00000000
     *  0012FCB0  |00000018
     *  0012FCB4  |00000000
     *  0012FCB8  |01D66B60
     *  0012FCBC  |00000000
     *  0012FCC0  |00000002
     *  0012FCC4  |0012FD24
     *  0012FCC8  |6186B774  RETURN to d3d9.6186B774
     *  0012FCCC  |00000000
     *  0012FCD0  |3FA00000
     *  0012FCD4  |00000000
     *  0012FCD8  |00000000
     *  0012FCDC  |00000000
     *  0012FCE0  |00000000
     *  0012FCE4  |3FA00000
     *  0012FCE8  |00000000
     *  0012FCEC  |00000000
     *  0012FCF0  |00000000
     *  0012FCF4  |00000000
     *  0012FCF8  |3F800000
     *  0012FCFC  |00000000
     *  0012FD00  |00000000
     *  0012FD04  |00000000
     *  0012FD08  |00000000
     *  0012FD0C  |3F800000
     *  0012FD10  |00000000
     *  0012FD14  |FF000000
     *  0012FD18  |FF000000
     *  0012FD1C  |FF000000
     *  0012FD20  |FF000000
     *  0012FD24  |00000000
     *  0012FD28  |0043E66F  RETURN to lus004.0043E66F
     *  0012FD2C  |089E0060
     *  0012FD30  |00000005
     *  0012FD34  |01D670E0
     *  0012FD38  |41700000
     *  0012FD3C  |00000000
     *  0012FD40  |00000000
     *  0012FD44  |42EC0000
     *  0012FD48  |4413C000
     *  0012FD4C  |089E0060
     *  0012FD50  |01CC7504
     *  0012FD54  |00000000
     *  0012FD58  |00000000
     *  0012FD5C  |08A3B600
     *  0012FD60  |0012FD78
     *  0012FD64  |6F5980B8  RETURN to prl_umdd.6F5980B8 from prl_umdd.6F597B05
     *  0012FD68  |0029DFA0
     *  0012FD6C  |00000019
     *  0012FD70  |00000008
     *  0012FD74  |00000000
     *  0012FD78  |089E0060
     *  0012FD7C  |00000000
     *  0012FD80  |00000001
     *  0012FD84  |01D1E670
     *  0012FD88  |61845418  d3d9.61845418
     *  0012FD8C  |00000005
     *  0012FD90  |00000000
     *  0012FD94  |00000000
     *  0012FD98  |00000010
     *  0012FD9C  |00000002
     *  0012FDA0  |00000000
     *  0012FDA4  |00000000
     *  0012FDA8  |41F00000
     *  0012FDAC  |0012FDC8
     *  0012FDB0  |00406E55  RETURN to lus004.00406E55 from lus004.0043EC70
     *  0012FDB4  |00000000
     *  0012FDB8  |00000001
     *  0012FDBC  |00000004
     *  0012FDC0  |01D66BF0
     *  0012FDC4  |01D1E670
     *  0012FDC8  |0012FDE0
     *  0012FDCC  |00486701  RETURN to lus004.00486701 from lus004.00406E20
     *  0012FDD0  ]0012FE4C
     *  0012FDD4  |004871D7  RETURN to lus004.004871D7 from lus004.0042B1F0
     *  0012FDD8  |02C2AB18 ; jichi: text is here
     *  0012FDDC  |0012FDFC
     *  0012FDE0  |FF000000
     *  0012FDE4  |00000005
     *  0012FDE8  |3FC00000
     *  0012FDEC  |005039A8  lus004.005039A8
     *  0012FDF0  |00252FDD
     *  0012FDF4  |00000002
     *  0012FDF8  |00000002
     *  0012FDFC  |3FA00000
     *  0012FE00  |00000000
     *  0012FE04  |00000000
     *  0012FE08  |00000000
     *  0012FE0C  |00000000
     *  0012FE10  |3FA00000
     *  0012FE14  |00000000
     *  0012FE18  |00000000
     *  0012FE1C  |00000000
     *  0012FE20  |00000000
     *  0012FE24  |3F800000
     *  0012FE28  |00000000
     *  0012FE2C  |42EC0000
     *  0012FE30  |4413C000
     *  0012FE34  |00000000
     *  0012FE38  |3F800000
     *  0012FE3C  |00000005
     *  0012FE40  |00000004
     *  0012FE44  |029101F0
     *  0012FE48  |00000001
     *  0012FE4C  ]0012FE8C
     *  0012FE50  |004851B8  RETURN to lus004.004851B8
     *  0012FE54  |029101F0
     *  0012FE58  |000000EF
     *  0012FE5C  |00000000
     *  0012FE60  |000000EF
     *  0012FE64  |000000EF
     *  0012FE68  |000000EF
     *  0012FE6C  |01CB0B70
     *  0012FE70  |FFFFFFFF
     *  0012FE74  |00000000
     *  0012FE78  |01D70270
     *  0012FE7C  |00000000
     *  0012FE80  |000000EF
     *  0012FE84  |000000C1
     *  0012FE88  |029101F0
     *  0012FE8C  ]0012FEA0
     *  0012FE90  |004B55FB  RETURN to lus004.004B55FB from lus004.00485070
     *  0012FE94  |00000000
     *  0012FE98  |000000EF
     *  0012FE9C  |01DB7770  ASCII "XZN"
     *  0012FEA0  ]0012FEAC
     *  0012FEA4  |004AAD57  RETURN to lus004.004AAD57
     *  0012FEA8  |01C70288
     *  0012FEAC  ]0012FEBC
     *  0012FEB0  |004AB09C  RETURN to lus004.004AB09C from lus004.004AACD0
     *  0012FEB4  |01C70288
     *  0012FEB8  |01000000
     *  0012FEBC  ]0012FEE0
     *  0012FEC0  |004AC8F5  RETURN to lus004.004AC8F5 from lus004.004AB080
     *  0012FEC4  |00BF0752
     *  0012FEC8  |00000113
     */
    bool attach(ULONG startAddress, ULONG stopAddress) // attach scenario
    {
      ULONG addr1, addr2;
      {
        const uint8_t bytes1[] = {
            0x89, 0x88, 0xac, 0x02, 0x00, 0x00, // 00487c1d   8988 ac020000    mov dword ptr ds:[eax+0x2ac],ecx
            0x8b, 0x55, 0xfc,                   // 00487c23   8b55 fc          mov edx,dword ptr ss:[ebp-0x4]
            0xd9, 0xee                          // 00487c26   d9ee             fldz
        };
        addr1 = MemDbg::findBytes(bytes1, sizeof(bytes1), startAddress, stopAddress);
        if (!addr1)
          return false;
        addr1 = MemDbg::findEnclosingAlignedFunction(addr1);
        if (!addr1)
          return false;
        // addr1 = 0x00487c10;
      }
      {
        const uint8_t bytes2[] = {
            0x83, 0xe0, 0x0c, // 0042b266   83e0 0c          and eax,0xc
            0x83, 0xf8, 0x04, // 0042b269   83f8 04          cmp eax,0x4
            0x75, 0x07,       // 0042b26c   75 07            jnz short lus004.0042b275
            0xd9, 0xee        // 0042b26e   d9ee             fldz
        };
        addr2 = MemDbg::findBytes(bytes2, sizeof(bytes2), startAddress, stopAddress);
        if (!addr2)
          return false;
        addr2 = MemDbg::findEnclosingAlignedFunction(addr2);
        if (!addr2)
          return false;
        // addr2 = 0x0042b1f0;
      }
      HookParam hp;
      hp.address = addr1;
      hp.text_fun = Private::hookBefore;
      hp.embed_fun = Private::hookafter1;
      hp.type = EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT;
      auto succ = NewHook(hp, "EMBEDLUNA");
      hp.address = addr2;
      succ |= NewHook(hp, "EMBEDLUNA");

      return succ;
    }
  } // namespace ScenarioHook
} // unnamed namespace
namespace
{
  bool PrincessSoft()
  {
    // https://vndb.org/v5385
    // F ~ファナティック~
    auto _ = {L"pac/voice.hed", L"pac/voice.pac",
              L"pac/se.hed", L"pac/se.pac",
              L"pac/snd.hed", L"pac/snd.pac",
              L"pac/vis.hed", L"pac/vis.pac",
              L"pac/tak.hed", L"pac/tak.pac"};
    if (!std::all_of(_.begin(), _.end(), Util::CheckFile))
      return false;
    PcHooks::hookGDIFunctions(GetGlyphOutlineA);
    return true;
  }
}
bool LunaSoft::attach_function()
{
  if (PrincessSoft())
    return true;
  bool b1 = InsertLunaSoftHook();
  bool b2 = InsertXXkata();
  bool embed = ScenarioHook::attach(processStartAddress, processStopAddress);
  return b1 || b2 || embed;
}