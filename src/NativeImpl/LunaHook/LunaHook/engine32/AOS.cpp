#include "AOS.h"

/**
 *  jichi 4/1/2014: Insert AOS hook
 *  About 彩斤�: http://erogetrailers.com/brand/165
 *  About AOS: http://asmodean.reverse.net/pages/exaos.html
 *
 *  Sample games:
 *
 *  [140228] [Sugar Pot] 恋する少女と想�キセキ V1.00 H-CODE by �쿿
 *  - /HB8*0@3C2F0:恋する少女と想�キセキ.exe
 *  - /HBC*0@3C190:恋する少女と想�キセキ.exe
 *
 *  [120224] [Sugar Pot]  ヂ�モノツキ
 *
 *  LiLiM games
 *
 *  /HB8*0@3C2F0:恋する少女と想�キセ
 *  - addr: 246512 = 0x3c2f0
 *  - length_offset: 1
 *  - module: 1814017450
 *  - off: 8
 *  - type: 72 = 0x48
 *
 *  00e3c2ed     cc                         int3
 *  00e3c2ee     cc                         int3
 *  00e3c2ef     cc                         int3
 *  00e3c2f0  /$ 51                         push ecx    ; jichi: hook here, function starts
 *  00e3c2f1  |. a1 0c64eb00                mov eax,dword ptr ds:[0xeb640c]
 *  00e3c2f6  |. 8b0d 7846eb00              mov ecx,dword ptr ds:[0xeb4678]
 *  00e3c2fc  |. 53                         push ebx
 *  00e3c2fd  |. 55                         push ebp
 *  00e3c2fe  |. 8b6c24 10                  mov ebp,dword ptr ss:[esp+0x10]
 *  00e3c302  |. 56                         push esi
 *  00e3c303  |. 8b35 c446eb00              mov esi,dword ptr ds:[0xeb46c4]
 *  00e3c309  |. 57                         push edi
 *  00e3c30a  |. 0fb63d c746eb00            movzx edi,byte ptr ds:[0xeb46c7]
 *  00e3c311  |. 81e6 ffffff00              and esi,0xffffff
 *  00e3c317  |. 894424 18                  mov dword ptr ss:[esp+0x18],eax
 *  00e3c31b  |. 85ff                       test edi,edi
 *  00e3c31d  |. 74 6b                      je short 恋する�00e3c38a
 *  00e3c31f  |. 8bd9                       mov ebx,ecx
 *  00e3c321  |. 85db                       test ebx,ebx
 *  00e3c323  |. 74 17                      je short 恋する�00e3c33c
 *  00e3c325  |. 8b4b 28                    mov ecx,dword ptr ds:[ebx+0x28]
 *  00e3c328  |. 56                         push esi                                 ; /color
 *  00e3c329  |. 51                         push ecx                                 ; |hdc
 *  00e3c32a  |. ff15 3c40e800              call dword ptr ds:[<&gdi32.SetTextColor>>; \settextcolor
 *  00e3c330  |. 89b3 c8000000              mov dword ptr ds:[ebx+0xc8],esi
 *  00e3c336  |. 8b0d 7846eb00              mov ecx,dword ptr ds:[0xeb4678]
 *  00e3c33c  |> 0fbf55 1c                  movsx edx,word ptr ss:[ebp+0x1c]
 *  00e3c340  |. 0fbf45 0a                  movsx eax,word ptr ss:[ebp+0xa]
 *  00e3c344  |. 0fbf75 1a                  movsx esi,word ptr ss:[ebp+0x1a]
 *  00e3c348  |. 03d7                       add edx,edi
 *  00e3c34a  |. 03c2                       add eax,edx
 *  00e3c34c  |. 0fbf55 08                  movsx edx,word ptr ss:[ebp+0x8]
 *  00e3c350  |. 03f7                       add esi,edi
 *  00e3c352  |. 03d6                       add edx,esi
 *  00e3c354  |. 85c9                       test ecx,ecx
 *  00e3c356  |. 74 32                      je short 恋する�00e3c38a
 */

bool InsertAOS1Hook()
{
  // jichi 4/2/2014: The starting of this function is different from ヂ�モノツキ
  // So, use a pattern in the middle of the function instead.
  //
  // const BYTE bytes[] = {
  //  0x51,                                 // 00e3c2f0  /$ 51              push ecx    ; jichi: hook here, function begins
  //  0xa1, 0x0c,0x64,0xeb,0x00,            // 00e3c2f1  |. a1 0c64eb00     mov eax,dword ptr ds:[0xeb640c]
  //  0x8b,0x0d, 0x78,0x46,0xeb,0x00,       // 00e3c2f6  |. 8b0d 7846eb00   mov ecx,dword ptr ds:[0xeb4678]
  //  0x53,                                 // 00e3c2fc  |. 53              push ebx
  //  0x55,                                 // 00e3c2fd  |. 55              push ebp
  //  0x8b,0x6c,0x24, 0x10,                 // 00e3c2fe  |. 8b6c24 10       mov ebp,dword ptr ss:[esp+0x10]
  //  0x56,                                 // 00e3c302  |. 56              push esi
  //  0x8b,0x35, 0xc4,0x46,0xeb,0x00,       // 00e3c303  |. 8b35 c446eb00   mov esi,dword ptr ds:[0xeb46c4]
  //  0x57,                                 // 00e3c309  |. 57              push edi
  //  0x0f,0xb6,0x3d, 0xc7,0x46,0xeb,0x00,  // 00e3c30a  |. 0fb63d c746eb00 movzx edi,byte ptr ds:[0xeb46c7]
  //  0x81,0xe6, 0xff,0xff,0xff,0x00        // 00e3c311  |. 81e6 ffffff00   and esi,0xffffff
  //};
  // enum { addr_offset = 0 };

  const BYTE bytes[] = {
      0x0f, 0xbf, 0x55, 0x1c, // 00e3c33c  |> 0fbf55 1c                  movsx edx,word ptr ss:[ebp+0x1c]
      0x0f, 0xbf, 0x45, 0x0a, // 00e3c340  |. 0fbf45 0a                  movsx eax,word ptr ss:[ebp+0xa]
      0x0f, 0xbf, 0x75, 0x1a, // 00e3c344  |. 0fbf75 1a                  movsx esi,word ptr ss:[ebp+0x1a]
      0x03, 0xd7,             // 00e3c348  |. 03d7                       add edx,edi
      0x03, 0xc2,             // 00e3c34a  |. 03c2                       add eax,edx
      0x0f, 0xbf, 0x55, 0x08, // 00e3c34c  |. 0fbf55 08                  movsx edx,word ptr ss:[ebp+0x8]
      0x03, 0xf7,             // 00e3c350  |. 03f7                       add esi,edi
      0x03, 0xd6,             // 00e3c352  |. 03d6                       add edx,esi
      0x85, 0xc9              // 00e3c354  |. 85c9                       test ecx,ecx
  };
  enum
  {
    addr_offset = 0x00e3c2f0 - 0x00e3c33c
  }; // distance to the beginning of the function, which is 0x51 (push ecx)
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  // GROWL(reladdr);
  if (!addr)
  {
    ConsoleOutput("AOS1: pattern not found");
    return false;
  }
  addr += addr_offset;
  // GROWL(addr);
  enum
  {
    push_ecx = 0x51
  }; // beginning of the function
  if (*(BYTE *)addr != push_ecx)
  {
    ConsoleOutput("AOS1: beginning of the function not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(2);
  hp.type = DATA_INDIRECT;

  ConsoleOutput("INSERT AOS1");

  return NewHook(hp, "AOS1");
}

bool InsertAOS2Hook()
{
  const BYTE bytes[] = {
      0x51,       // 00C4E7E0  /$  51            PUSH ECX ; mireado: hook here, function begins
      0x33, 0xc0, // 00C4E7E1  |.  33C0          XOR EAX,EAX
      0x53,       // 00C4E7E3  |.  53            PUSH EBX
      0x55,       // 00C4E7E4  |.  55            PUSH EBP
      0x8b, 0x2d  //, XX4,           // 00C4E7E5  |.  8B2D 40A3CF00 MOV EBP,DWORD PTR DS:[0CFA340] ; mireado: some time changing 40A3CF00 => 40A3C000
                  // 0x89,0x07,             // 00C4E7EB  |.  8907          MOV DWORD PTR DS:[EDI],EAX
                  // 0x89,0x47, 0x04       // 00C4E7ED  |.  8947 04       MOV DWORD PTR DS:[EDI+4],EAX
                  // 0x56,                  // 00C4E7F0  |.  56            PUSH ESI
                  // 0x8b,0x75, 0x44        // 00C4E7F1  |.  8B75 44       MOV ESI,DWORD PTR SS:[EBP+44]
  };

  enum
  {
    addr_offset = 0
  }; // distance to the beginning of the function, which is 0x51 (push ecx)
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  // GROWL(reladdr);
  if (!addr)
  {
    ConsoleOutput("AOS2: pattern not found");
    return false;
  }
  addr += addr_offset;
  // GROWL(addr);
  enum
  {
    push_ecx = 0x51
  }; // beginning of the function
  if (*(BYTE *)addr != push_ecx)
  {
    ConsoleOutput("AOS2: beginning of the function not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(2);
  hp.type = DATA_INDIRECT;

  ConsoleOutput("INSERT AOS2");

  return NewHook(hp, "AOS2");
}

bool InsertAOSHook()
{
  return InsertAOS1Hook() || InsertAOS2Hook();
}

namespace
{

  DWORD calladdr(DWORD addr)
  {
    if (!addr)
      return 0;
    BYTE callop[] = {0xe8};
    addr = reverseFindBytes(callop, sizeof(callop), addr - 0x20, addr);
    if (!addr)
      return 0;
    auto calladdr = *(int *)((char *)addr + 1);
    ConsoleOutput("calladdr %p", calladdr);
    addr = calladdr + addr + 5;
    ConsoleOutput("funcaddr %p", addr);
    if (*(BYTE *)((BYTE *)addr - 1) != 0xcc)
      return 0;
    return addr;
  }
  DWORD lastcall()
  {
    auto addr = findiatcallormov((DWORD)TextOutA, processStartAddress, processStartAddress, processStopAddress, true);
    if (!addr)
      return 0;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    return addr;
  }
}
int mov_reg_ebpoffset(int reg)
{
  switch (reg)
  {
  case 0x4B:
    return regoffset(ebx);
  case 0x48:
    return regoffset(eax);
  case 0x49:
    return regoffset(ecx);
  case 0x4a:
    return regoffset(edx);
  case 0x4c:
    return regoffset(ebp);
  case 0x4d:
    return regoffset(esp);
  case 0x4e:
    return regoffset(esi);
  case 0x4f:
    return regoffset(edi);
  default:
    return -1;
  }
}
bool AOS_EX()
{
  BYTE aos_shared_bytes1[] = {
      0x3c, XX,
      0x74, XX,
      0x3c, XX,
      0x74, XX,
      0x3c, XX,
      0x74, XX,
      0x3c, XX,
      0x74, XX,
      0x3c, XX,
      0x74, XX};
  BYTE aos_shared_bytes2[] = {

      0x80, 0xfb, XX,
      0x74, XX,
      0x80, 0xfb, XX,
      0x74, XX,
      0x80, 0xfb, XX,
      0x74, XX,
      0x80, 0xfb, XX,
      0x74, XX};
  std::vector<DWORD> addrs;
  addrs.push_back(calladdr(MemDbg::findBytes(aos_shared_bytes1, sizeof(aos_shared_bytes1), processStartAddress, processStopAddress)));
  addrs.push_back(calladdr(MemDbg::findBytes(aos_shared_bytes2, sizeof(aos_shared_bytes2), processStartAddress, processStopAddress)));
  addrs.push_back(lastcall());
  for (auto addr : addrs)
  {
    if (!addr)
      continue;
    auto reg = mov_reg_ebpoffset(*(BYTE *)((BYTE *)addr + 5));
    int off;
    if (reg != -1)
    {
      // usercall
      off = reg;
    }
    else if (((*(WORD *)addr)) == 0xec83)
    {
      // 姫様LOVEライフ！
      // 也是usercall，但是第二个参数是栈上。
      off = stackoffset(1);
    }
    else
    {
      // 螺旋遡行のディストピア -The infinite set of alternative version- 官方中文
      BYTE sig[] = {0x89, 0x55, 0xFC};
      if (MemDbg::findBytes(sig, sizeof(sig), addr, addr + 0x20))
      {
        off = regoffset(edx);
      }
      else
      {
        // cdecl;
        off = stackoffset(2);
      }
    }
    HookParam hp;
    hp.address = addr;
    hp.offset = off;
    hp.type = NO_CONTEXT | DATA_INDIRECT;
    hp.index = 0;

    return NewHook(hp, "AOS_EX");
  }
  return false;
}

bool AOS::attach_function()
{
  bool b1 = InsertAOSHook();
  bool b3 = AOS_EX();
  return b1 || b3;
}