#include "Syuntada.h"

/** jichi 2/6/2015 Syuntada
 *  Sample game: [140816] [平安亭] カノジョのお母さん�好きですか-- /HA-18@6944C:kanojo.exe
 *
 *  /HA-18@6944C:kanojo.exe
 *  - addr: 431180 = 0x6944c
 *  - module: 1301076281
 *  - off: 4294967268 = 0xffffffe4 = - 0x1c
 *  - length_offset: 1
 *  - type: 68 = 0x44
 *
 *  004692bd   cc               int3
 *  004692be   cc               int3
 *  004692bf   cc               int3
 *  004692c0   83ec 48          sub esp,0x48
 *  004692c3   53               push ebx
 *  004692c4   55               push ebp
 *  004692c5   56               push esi
 *  004692c6   8bf1             mov esi,ecx
 *  004692c8   8b86 d4000000    mov eax,dword ptr ds:[esi+0xd4]
 *  004692ce   0386 8c040000    add eax,dword ptr ds:[esi+0x48c]
 *  004692d4   8b8e c8010000    mov ecx,dword ptr ds:[esi+0x1c8]
 *  004692da   8b9e 90040000    mov ebx,dword ptr ds:[esi+0x490]
 *  004692e0   03c0             add eax,eax
 *  004692e2   03c0             add eax,eax
 *  004692e4   894424 24        mov dword ptr ss:[esp+0x24],eax
 *  004692e8   8b86 c4010000    mov eax,dword ptr ds:[esi+0x1c4]
 *  004692ee   8986 94040000    mov dword ptr ds:[esi+0x494],eax
 *  004692f4   8b4424 60        mov eax,dword ptr ss:[esp+0x60]
 *  004692f8   898e 98040000    mov dword ptr ds:[esi+0x498],ecx
 *  004692fe   0fb628           movzx ebp,byte ptr ds:[eax]
 *  00469301   0fb650 01        movzx edx,byte ptr ds:[eax+0x1]
 *  00469305   c1e5 08          shl ebp,0x8
 *  00469308   0bea             or ebp,edx
 *  0046930a   03db             add ebx,ebx
 *  0046930c   03db             add ebx,ebx
 *  0046930e   8d8d 617dffff    lea ecx,dword ptr ss:[ebp+0xffff7d61]
 *  00469314   57               push edi
 *  00469315   895c24 30        mov dword ptr ss:[esp+0x30],ebx
 *  00469319   c74424 38 100000>mov dword ptr ss:[esp+0x38],0x10
 *  00469321   896c24 34        mov dword ptr ss:[esp+0x34],ebp
 *  00469325   b8 02000000      mov eax,0x2
 *  0046932a   83f9 52          cmp ecx,0x52
 *  0046932d   77 02            ja short .00469331
 *  0046932f   33c0             xor eax,eax
 *  00469331   81fd 41810000    cmp ebp,0x8141
 *  00469337   7c 08            jl short .00469341
 *  00469339   81fd 9a820000    cmp ebp,0x829a
 *  0046933f   7e 0e            jle short .0046934f
 *  00469341   8d95 c07cffff    lea edx,dword ptr ss:[ebp+0xffff7cc0]
 *  00469347   81fa 4f040000    cmp edx,0x44f
 *  0046934d   77 09            ja short .00469358
 *  0046934f   bf 01000000      mov edi,0x1
 *  00469354   8bc7             mov eax,edi
 *  00469356   eb 05            jmp short .0046935d
 *  00469358   bf 01000000      mov edi,0x1
 *  0046935d   83e8 00          sub eax,0x0
 *  00469360   74 2a            je short .0046938c
 *  00469362   2bc7             sub eax,edi
 *  00469364   74 0c            je short .00469372
 *  00469366   2bc7             sub eax,edi
 *  00469368   75 3a            jnz short .004693a4
 *  0046936a   8b96 68010000    mov edx,dword ptr ds:[esi+0x168]
 *  00469370   eb 20            jmp short .00469392
 *  00469372   8b96 7c090000    mov edx,dword ptr ds:[esi+0x97c]
 *  00469378   8b86 64010000    mov eax,dword ptr ds:[esi+0x164]
 *  0046937e   8b52 28          mov edx,dword ptr ds:[edx+0x28]
 *  00469381   8d8e 7c090000    lea ecx,dword ptr ds:[esi+0x97c]
 *  00469387   50               push eax
 *  00469388   ffd2             call edx
 *  0046938a   eb 18            jmp short .004693a4
 *  0046938c   8b96 60010000    mov edx,dword ptr ds:[esi+0x160]
 *  00469392   8b86 7c090000    mov eax,dword ptr ds:[esi+0x97c]
 *  00469398   8b40 28          mov eax,dword ptr ds:[eax+0x28]
 *  0046939b   8d8e 7c090000    lea ecx,dword ptr ds:[esi+0x97c]
 *  004693a1   52               push edx
 *  004693a2   ffd0             call eax
 *  004693a4   39be d40f0000    cmp dword ptr ds:[esi+0xfd4],edi
 *  004693aa   75 45            jnz short .004693f1
 *  004693ac   8b8e 90040000    mov ecx,dword ptr ds:[esi+0x490]
 *  004693b2   b8 d0020000      mov eax,0x2d0
 *  004693b7   2bc1             sub eax,ecx
 *  004693b9   2b86 c8010000    sub eax,dword ptr ds:[esi+0x1c8]
 *  004693bf   68 000f0000      push 0xf00
 *  004693c4   8d0480           lea eax,dword ptr ds:[eax+eax*4]
 *  004693c7   c1e0 08          shl eax,0x8
 *  004693ca   0386 c4010000    add eax,dword ptr ds:[esi+0x1c4]
 *  004693d0   8d1440           lea edx,dword ptr ds:[eax+eax*2]
 *  004693d3   8b4424 60        mov eax,dword ptr ss:[esp+0x60]
 *  004693d7   52               push edx
 *  004693d8   8b50 40          mov edx,dword ptr ds:[eax+0x40]
 *  004693db   8b86 c8000000    mov eax,dword ptr ds:[esi+0xc8]
 *  004693e1   0386 8c040000    add eax,dword ptr ds:[esi+0x48c]
 *  004693e7   52               push edx
 *  004693e8   50               push eax
 *  004693e9   51               push ecx
 *  004693ea   8bce             mov ecx,esi
 *  004693ec   e8 9fc4ffff      call .00465890
 *  004693f1   39be d00f0000    cmp dword ptr ds:[esi+0xfd0],edi
 *  004693f7   0f85 f2010000    jnz .004695ef
 *  004693fd   8d86 20100000    lea eax,dword ptr ds:[esi+0x1020]
 *  00469403   50               push eax
 *  00469404   55               push ebp
 *  00469405   8bce             mov ecx,esi
 *  00469407   e8 64f4ffff      call .00468870
 *  0046940c   8a4e 25          mov cl,byte ptr ds:[esi+0x25]
 *  0046940f   8a56 26          mov dl,byte ptr ds:[esi+0x26]
 *  00469412   884c24 18        mov byte ptr ss:[esp+0x18],cl
 *  00469416   8b4c24 5c        mov ecx,dword ptr ss:[esp+0x5c]
 *  0046941a   885424 14        mov byte ptr ss:[esp+0x14],dl
 *  0046941e   8b51 40          mov edx,dword ptr ds:[ecx+0x40]
 *  00469421   895424 20        mov dword ptr ss:[esp+0x20],edx
 *  00469425   b9 d0020000      mov ecx,0x2d0
 *  0046942a   2bcb             sub ecx,ebx
 *  0046942c   ba 00000000      mov edx,0x0
 *  00469431   0f98c2           sets dl
 *  00469434   8bf8             mov edi,eax
 *  00469436   8a46 24          mov al,byte ptr ds:[esi+0x24]
 *  00469439   884424 1c        mov byte ptr ss:[esp+0x1c],al
 *  0046943d   4a               dec edx
 *  0046943e   23d1             and edx,ecx
 *  00469440   69d2 000f0000    imul edx,edx,0xf00
 *  00469446   8bca             mov ecx,edx
 *  00469448   894c24 24        mov dword ptr ss:[esp+0x24],ecx
 *  0046944c   85ff             test edi,edi    ; jichi: hook here
 *  0046944e   74 3a            je short .0046948a
 *  00469450   8b5424 14        mov edx,dword ptr ss:[esp+0x14]
 *  00469454   6a 00            push 0x0
 *  00469456   57               push edi
 *  00469457   8d86 c80c0000    lea eax,dword ptr ds:[esi+0xcc8]
 *  0046945d   50               push eax
 *  0046945e   8b4424 24        mov eax,dword ptr ss:[esp+0x24]
 *  00469462   6a 10            push 0x10
 *  00469464   52               push edx
 *  00469465   8b5424 30        mov edx,dword ptr ss:[esp+0x30]
 *  00469469   50               push eax
 *  0046946a   8b4424 38        mov eax,dword ptr ss:[esp+0x38]
 *  0046946e   52               push edx
 *  0046946f   68 000f0000      push 0xf00
 *  00469474   51               push ecx
 *  00469475   8b4c24 4c        mov ecx,dword ptr ss:[esp+0x4c]
 */
bool InsertSyuntadaHook()
{
  const BYTE bytes[] = {
      0x4a,                               // 0046943d   4a               dec edx
      0x23, 0xd1,                         // 0046943e   23d1             and edx,ecx
      0x69, 0xd2, 0x00, 0x0f, 0x00, 0x00, // 00469440   69d2 000f0000    imul edx,edx,0xf00
      0x8b, 0xca,                         // 00469446   8bca             mov ecx,edx
      0x89, 0x4c, 0x24, 0x24,             // 00469448   894c24 24        mov dword ptr ss:[esp+0x24],ecx
      0x85, 0xff,                         // 0046944c   85ff             test edi,edi    ; jichi: hook here
      0x74, 0x3a                          // 0046944e   74 3a            je short .0046948a
  };
  enum
  {
    addr_offset = 0x0046944c - 0x0046943d
  };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  // GROWL(addr);
  if (!addr)
  {
    ConsoleOutput("Syuntada: pattern not found");
    return false;
  }
  HookParam hp;
  hp.address = addr + addr_offset;
  hp.offset = regoffset(ebp);
  hp.type = CODEC_ANSI_BE; // 0x4
  ConsoleOutput("INSERT Syuntada");

  // TextOutA will produce repeated texts
  ConsoleOutput("Syuntada: disable GDI hooks");

  return NewHook(hp, "Syuntada");
}
namespace
{
  bool __()
  {
    // 平凡な奥さんは好きですか～真面目な主婦をエッチ漬けにしちゃおう!～
    // 奪母姦
    // 友達のお母さんは好きですか？～息子の友人にハマったオバちゃん妻～
    const BYTE bytes[] = {
        0x81, 0xFD, 0x41, 0x81, 0x00, 0x00,
        0x7C, XX,
        0x81, 0xFD, 0x9A, 0x82, 0x00, 0x00,
        0x7E};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);

    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr, 0x1000);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(3);
    hp.type = USING_STRING;
    return NewHook(hp, "Syuntada");
  }
}
bool Syuntada::attach_function()
{

  return InsertSyuntadaHook() || __();
}