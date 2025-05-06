#include "SideB.h"

/** jichi 8/2/2014 side-B
 *  Sample games:
 *  - [side-B] メルトピア -- /HS-4@B4452:Martopia.exe
 *
 *  Observations:
 *
 *  /HS-4@B4452:Martopia.exe
 *  - addr: 738386 = 0xb4452
 *  - module: 3040177000
 *  - off: 4294967288 = 0xfffffff8 = -0x8
 *  - type: 65 = 0x41
 *
 *  Sample stack structure:
 *  - 0016F558   00EB74E9  RETURN to Martopia.00EB74E9
 *  - 0016F55C   0060EE30 ; jichi: this is the text
 *  - 0016F560   0016F5C8
 *  - 0016F564   082CAA98
 *  - 0016F568   00EBE735  RETURN to Martopia.00EBE735 from Martopia.00EB74C0
 *
 *  00f6440e   cc               int3
 *  00f6440f   cc               int3
 *  00f64410   55               push ebp    ; jichi: hook here, text in arg1 ([EncodeSystemPointer(+4])
 *  00f64411   8bec             mov ebp,esp
 *  00f64413   6a ff            push -0x1
 *  00f64415   68 c025fb00      push martopia.00fb25c0
 *  00f6441a   64:a1 00000000   mov eax,dword ptr fs:[0]
 *  00f64420   50               push eax
 *  00f64421   83ec 3c          sub esp,0x3c
 *  00f64424   a1 c8620101      mov eax,dword ptr ds:[0x10162c8]
 *  00f64429   33c5             xor eax,ebp
 *  00f6442b   8945 f0          mov dword ptr ss:[ebp-0x10],eax
 *  00f6442e   53               push ebx
 *  00f6442f   56               push esi
 *  00f64430   57               push edi
 *  00f64431   50               push eax
 *  00f64432   8d45 f4          lea eax,dword ptr ss:[ebp-0xc]
 *  00f64435   64:a3 00000000   mov dword ptr fs:[0],eax
 *  00f6443b   8bf9             mov edi,ecx
 *  00f6443d   8b4d 08          mov ecx,dword ptr ss:[ebp+0x8]
 *  00f64440   33db             xor ebx,ebx
 *  00f64442   3bcb             cmp ecx,ebx
 *  00f64444   74 40            je short martopia.00f64486
 *  00f64446   8bc1             mov eax,ecx
 *  00f64448   c745 e8 0f000000 mov dword ptr ss:[ebp-0x18],0xf
 *  00f6444f   895d e4          mov dword ptr ss:[ebp-0x1c],ebx
 *  00f64452   885d d4          mov byte ptr ss:[ebp-0x2c],bl   ; jichi: or hook here, get text in eax
 *  00f64455   8d70 01          lea esi,dword ptr ds:[eax+0x1]
 *  00f64458   8a10             mov dl,byte ptr ds:[eax]
 *  00f6445a   40               inc eax
 *  00f6445b   3ad3             cmp dl,bl
 *  00f6445d  ^75 f9            jnz short martopia.00f64458
 *  00f6445f   2bc6             sub eax,esi
 *  00f64461   50               push eax
 *  00f64462   51               push ecx
 *  00f64463   8d4d d4          lea ecx,dword ptr ss:[ebp-0x2c]
 *  00f64466   e8 f543f5ff      call martopia.00eb8860
 *  00f6446b   8d45 d4          lea eax,dword ptr ss:[ebp-0x2c]
 *  00f6446e   50               push eax
 *  00f6446f   8d4f 3c          lea ecx,dword ptr ds:[edi+0x3c]
 *  00f64472   895d fc          mov dword ptr ss:[ebp-0x4],ebx
 *  00f64475   e8 16d7f8ff      call martopia.00ef1b90
 *  00f6447a   837d e8 10       cmp dword ptr ss:[ebp-0x18],0x10
 *  00f6447e   72 47            jb short martopia.00f644c7
 *  00f64480   8b4d d4          mov ecx,dword ptr ss:[ebp-0x2c]
 *  00f64483   51               push ecx
 *  00f64484   eb 38            jmp short martopia.00f644be
 *  00f64486   53               push ebx
 *  00f64487   68 a11efd00      push martopia.00fd1ea1
 *  00f6448c   8d4d b8          lea ecx,dword ptr ss:[ebp-0x48]
 *  00f6448f   c745 cc 0f000000 mov dword ptr ss:[ebp-0x34],0xf
 *  00f64496   895d c8          mov dword ptr ss:[ebp-0x38],ebx
 *  00f64499   885d b8          mov byte ptr ss:[ebp-0x48],bl
 *  00f6449c   e8 bf43f5ff      call martopia.00eb8860
 *  00f644a1   8d55 b8          lea edx,dword ptr ss:[ebp-0x48]
 *  00f644a4   52               push edx
 *  00f644a5   8d4f 3c          lea ecx,dword ptr ds:[edi+0x3c]
 *  00f644a8   c745 fc 01000000 mov dword ptr ss:[ebp-0x4],0x1
 *  00f644af   e8 dcd6f8ff      call martopia.00ef1b90
 *  00f644b4   837d cc 10       cmp dword ptr ss:[ebp-0x34],0x10
 *  00f644b8   72 0d            jb short martopia.00f644c7
 *  00f644ba   8b45 b8          mov eax,dword ptr ss:[ebp-0x48]
 *  00f644bd   50               push eax
 *  00f644be   ff15 f891fc00    call dword ptr ds:[<&msvcr100.??3@yaxpax>; msvcr100.??3@yaxpax@z
 *  00f644c4   83c4 04          add esp,0x4
 *  00f644c7   8b4d f4          mov ecx,dword ptr ss:[ebp-0xc]
 *  00f644ca   64:890d 00000000 mov dword ptr fs:[0],ecx
 *  00f644d1   59               pop ecx
 *  00f644d2   5f               pop edi
 *  00f644d3   5e               pop esi
 *  00f644d4   5b               pop ebx
 *  00f644d5   8b4d f0          mov ecx,dword ptr ss:[ebp-0x10]
 *  00f644d8   33cd             xor ecx,ebp
 *  00f644da   e8 77510400      call martopia.00fa9656
 *  00f644df   8be5             mov esp,ebp
 *  00f644e1   5d               pop ebp
 *  00f644e2   c2 0400          retn 0x4
 *  00f644e5   cc               int3
 *  00f644e6   cc               int3
 */
bool InsertSideBHook()
{
  const BYTE bytes[] = {
      0x64, 0xa3, 0x00, 0x00, 0x00, 0x00,       // 00f64435   64:a3 00000000   mov dword ptr fs:[0],eax
      0x8b, 0xf9,                               // 00f6443b   8bf9             mov edi,ecx
      0x8b, 0x4d, 0x08,                         // 00f6443d   8b4d 08          mov ecx,dword ptr ss:[ebp+0x8]
      0x33, 0xdb,                               // 00f64440   33db             xor ebx,ebx
      0x3b, 0xcb,                               // 00f64442   3bcb             cmp ecx,ebx
      0x74, 0x40,                               // 00f64444   74 40            je short martopia.00f64486
      0x8b, 0xc1,                               // 00f64446   8bc1             mov eax,ecx
      0xc7, 0x45, 0xe8, 0x0f, 0x00, 0x00, 0x00, // 00f64448   c745 e8 0f000000 mov dword ptr ss:[ebp-0x18],0xf
      0x89, 0x5d, 0xe4,                         // 00f6444f   895d e4          mov dword ptr ss:[ebp-0x1c],ebx
      0x88, 0x5d, 0xd4                          // 00f64452   885d d4          mov byte ptr ss:[ebp-0x2c],bl
  };
  enum
  {
    addr_offset = 0x00f64410 - 0x00f64435
  }; // distance to the beginning of the function
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  // GROWL_DWORD(addr); // supposed to be 0x4010e0
  if (!addr)
  {
    ConsoleOutput("SideB: pattern not found");
    return false;
  }
  addr += addr_offset;
  enum : BYTE
  {
    push_ebp = 0x55
  }; // 011d4c80  /$ 55             push ebp
  if (*(BYTE *)addr != push_ebp)
  {
    ConsoleOutput("SideB: pattern found but the function offset is invalid");
    return false;
  }
  // GROWL_DWORD(addr);

  HookParam hp;
  hp.address = addr;
  // hp.length_offset = 1;
  hp.offset = stackoffset(1);                        // [esp+4] == arg1
  hp.type = USING_STRING | NO_CONTEXT | USING_SPLIT; // NO_CONTEXT && RELATIVE_SPLIT to get rid of floating return address
  hp.split = 0;                                      // use retaddr as split
  ConsoleOutput("INSERT SideB");
  return NewHook(hp, "SideB");
}

bool SideB::attach_function()
{

  return InsertSideBHook();
}