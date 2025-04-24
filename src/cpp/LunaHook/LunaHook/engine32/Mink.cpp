#include "Mink.h"
/** 12/23/2014 jichi: Mink games (not sure the engine name)
 *  Sample game:
 *  - [130111] [Mink EGO] お�ちも�にはぜったい言えなぁ�ぁ�つなこと�-- /HB-4*0:64@45164A
 *  - [141219] [Mink] しすた�・すきーむ3
 *
 *  Observations from sisters3:
 *  - GetGlyphOutlineA can get text, but it is cached.
 *  - It's caller's first argument is the correct text, but I failed to find where it is called
 *  - Debugging text in memory caused looping
 *
 *  /HB-4*0:64@45164A
 *  - addr: 0x45164a
 *  - length_offset: 1
 *  - split: 0x64
 *  - off: 0xfffffff8 = -8
 *  - type: 0x18
 *
 *  Observations from Onechan:
 *  - There are lots of threads
 *  - The one with -1 split value is correct, but not sure for all games
 *  - The result texts still contain garbage, but can be split using return values.
 *
 *  00451611   e9 ee000000      jmp .00451704
 *  00451616   8b45 0c          mov eax,dword ptr ss:[ebp+0xc]
 *  00451619   3bc3             cmp eax,ebx
 *  0045161b   75 2b            jnz short .00451648
 *  0045161d   e8 a9340000      call .00454acb
 *  00451622   53               push ebx
 *  00451623   53               push ebx
 *  00451624   53               push ebx
 *  00451625   53               push ebx
 *  00451626   53               push ebx
 *  00451627   c700 16000000    mov dword ptr ds:[eax],0x16
 *  0045162d   e8 16340000      call .00454a48
 *  00451632   83c4 14          add esp,0x14
 *  00451635   385d f4          cmp byte ptr ss:[ebp-0xc],bl
 *  00451638   74 07            je short .00451641
 *  0045163a   8b45 f0          mov eax,dword ptr ss:[ebp-0x10]
 *  0045163d   8360 70 fd       and dword ptr ds:[eax+0x70],0xfffffffd
 *  00451641   33c0             xor eax,eax
 *  00451643   e9 bc000000      jmp .00451704
 *  00451648   3818             cmp byte ptr ds:[eax],bl
 *  0045164a   75 14            jnz short .00451660         ; jichi: hook here
 *  0045164c   385d f4          cmp byte ptr ss:[ebp-0xc],bl
 *  0045164f   74 07            je short .00451658
 *  00451651   8b45 f0          mov eax,dword ptr ss:[ebp-0x10]
 *  00451654   8360 70 fd       and dword ptr ds:[eax+0x70],0xfffffffd
 *  00451658   8b45 08          mov eax,dword ptr ss:[ebp+0x8]
 *  0045165b   e9 a4000000      jmp .00451704
 *  00451660   56               push esi
 *  00451661   8b75 08          mov esi,dword ptr ss:[ebp+0x8]
 *  00451664   3bf3             cmp esi,ebx
 *  00451666   75 28            jnz short .00451690
 *  00451668   e8 5e340000      call .00454acb
 *  0045166d   53               push ebx
 *  0045166e   53               push ebx
 *  0045166f   53               push ebx
 *  00451670   53               push ebx
 *  00451671   53               push ebx
 *  00451672   c700 16000000    mov dword ptr ds:[eax],0x16
 *  00451678   e8 cb330000      call .00454a48
 *  0045167d   83c4 14          add esp,0x14
 *  00451680   385d f4          cmp byte ptr ss:[ebp-0xc],bl
 *  00451683   74 07            je short .0045168c
 *  00451685   8b45 f0          mov eax,dword ptr ss:[ebp-0x10]
 *  00451688   8360 70 fd       and dword ptr ds:[eax+0x70],0xfffffffd
 *  0045168c   33c0             xor eax,eax
 *  0045168e   eb 73            jmp short .00451703
 *  00451690   57               push edi
 *  00451691   50               push eax
 *  00451692   8bfe             mov edi,esi
 *  00451694   e8 a7600000      call .00457740
 *  00451699   8975 f8          mov dword ptr ss:[ebp-0x8],esi
 *  0045169c   2945 f8          sub dword ptr ss:[ebp-0x8],eax
 *  0045169f   56               push esi
 *  004516a0   e8 9b600000      call .00457740
 *  004516a5   0345 f8          add eax,dword ptr ss:[ebp-0x8]
 *  004516a8   59               pop ecx
 *  004516a9   59               pop ecx
 *  004516aa   381e             cmp byte ptr ds:[esi],bl
 *  004516ac   74 46            je short .004516f4
 *  004516ae   2b75 0c          sub esi,dword ptr ss:[ebp+0xc]
 *  004516b1   3bf8             cmp edi,eax
 *  004516b3   77 3f            ja short .004516f4
 *  004516b5   8a17             mov dl,byte ptr ds:[edi]
 *  004516b7   8b4d 0c          mov ecx,dword ptr ss:[ebp+0xc]
 *  004516ba   8855 ff          mov byte ptr ss:[ebp-0x1],dl
 *  004516bd   3ad3             cmp dl,bl
 *  004516bf   74 11            je short .004516d2
 *  004516c1   8a11             mov dl,byte ptr ds:[ecx]
 *  004516c3   3ad3             cmp dl,bl
 *  004516c5   74 40            je short .00451707
 *  004516c7   38140e           cmp byte ptr ds:[esi+ecx],dl
 *  004516ca   75 06            jnz short .004516d2
 *  004516cc   41               inc ecx
 *  004516cd   381c0e           cmp byte ptr ds:[esi+ecx],bl
 *  004516d0  ^75 ef            jnz short .004516c1
 *  004516d2   3819             cmp byte ptr ds:[ecx],bl
 *  004516d4   74 31            je short .00451707
 *  004516d6   0fb64d ff        movzx ecx,byte ptr ss:[ebp-0x1]
 *  004516da   8b55 ec          mov edx,dword ptr ss:[ebp-0x14]
 *  004516dd   8a4c11 1d        mov cl,byte ptr ds:[ecx+edx+0x1d]
 */

#if 0  // hook to the caller of dynamic GetGlyphOutlineA
/**
 *  @param  addr  function address
 *  @param  frame  real address of the function, supposed to be the same as addr
 *  @param  stack  address of current stack - 4
 *  @return  If suceess
 */
static bool InsertMinkDynamicHook(LPVOID fun, DWORD frame, DWORD stack)
{
  CC_UNUSED(frame);
  if (fun != ::GetGlyphOutlineA)
    return false;
  DWORD addr = *(DWORD *)(stack + 4);
  if (!addr) {
    ConsoleOutput("Mink: missing function return addr, this should never happen");
    return true;
  }
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0x200); // range is around 0x120
  if (!addr) {
    ConsoleOutput("Mink: failed to caller address");
    return true;
  }

  HookParam hp;
  hp.address = addr; // hook to the beginning of the caller function
  hp.offset =stackoffset(1);
  hp.type = CODEC_ANSI_BE;
  return NewHook(hp, "Mink");
}
#endif // 0

static void SpecialHookMink(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  // DWORD addr = *(DWORD *)(esp_base + hp->offset); // default value
  DWORD addr = context->eax;
  if (!IthGetMemoryRange((LPVOID)(addr), 0, 0))
    return;
  DWORD ch = *(DWORD *)addr;
  DWORD size = LeadByteTable[ch & 0xff]; // Slightly faster than IsDBCSLeadByte
  if (size == 1 && ::ispunct(ch & 0xff)) // skip ascii punctuations, since garbage is like ":text:"
    return;
  if (!IsShiftjisLeadByte(ch))
    return;
  // Issue: still have lots of garbage
  *split = context->stack[25];
  //*split = *(DWORD *)(esp_base + 0x48);
  buffer->from(&ch, size);
}

bool InsertMinkHook()
{
  const BYTE bytes[] = {
      0x38, 0x18,             // 00451648   3818             cmp byte ptr ds:[eax],bl
      0x75, 0x14,             // 0045164a   75 14            jnz short .00451660         ; jichi: hook here
      0x38, 0x5d, 0xf4,       // 0045164c   385d f4          cmp byte ptr ss:[ebp-0xc],bl
      0x74, 0x07,             // 0045164f   74 07            je short .00451658
      0x8b, 0x45, 0xf0,       // 00451651   8b45 f0          mov eax,dword ptr ss:[ebp-0x10]
      0x83, 0x60, 0x70, 0xfd, // 00451654   8360 70 fd       and dword ptr ds:[eax+0x70],0xfffffffd
      0x8b, 0x45, 0x08        // 00451658   8b45 08          mov eax,dword ptr ss:[ebp+0x8]
  };
  enum
  {
    addr_offset = 2
  };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  // ULONG addr = 0x45164a;
  // ULONG addr = 0x451648;
  // ULONG addr = 0x4521a8;
  // GROWL_DWORD(addr);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr + addr_offset;
  hp.offset = regoffset(eax); // -8
  hp.split = 0x64;
  hp.type = USING_SPLIT | DATA_INDIRECT | USING_CHAR; // 0x18
  hp.text_fun = SpecialHookMink;
  return NewHook(hp, "Mink");

  // ConsoleOutput("Mink: disable GDI hooks");
  //
}

bool Mink2::attach_function()
{
  const BYTE pattern[] = {
      // 破談屋
      // https://vndb.org/v2719
      0xF7, 0xC7, 0x03, 0x00, 0x00, 0x00,
      0x75, XX,
      0xC1, 0xE9, 0x02,
      0x83, 0xE2, 0x03,
      0x83, 0xF9, 0x08,
      0x72, XX};
  bool found = false;
  for (auto addr : Util::SearchMemory(pattern, sizeof(pattern), PAGE_EXECUTE, processStartAddress, processStopAddress))
  {
    addr = MemDbg::findEnclosingAlignedFunction(addr, 0x100);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(2);
    hp.length_offset = 3;
    hp.type = USING_STRING;
    found |= NewHook(hp, "Mink");
  }
  return found;
}

static bool MdePink()
{
  // (18禁ゲーム) [100903][minkm_0012][M de Pink] しすたー・すきーむ2 アニメーション追加版 DL版
  // 催眠学級 HD https://vndb.org/r30973
  const BYTE pattern[] = {
      0X80, 0XFB, 0X81,
      0X72, 0X05,
      0X80, 0XFB, 0X9F,
      0X76, 0X08,
      0X8A, 0XC3,
      0X04, 0X20,
      0X3C, 0X1C,
      0X77, 0X13,
      0X0F, 0XB6, XX,
      0XC1, 0XE3, 0X08,
      0X03, XX,
      XX,
      0X89, XX, 0X24, 0X14,
      0X89, XX, 0X24, XX,
      0XEB, 0X08};
  auto addr = MemDbg::findBytes(pattern, sizeof(pattern), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    *split = context->stack[5];
    if (*split == 0xff000000 || *split == 0xffFFFFF || *split == 0x7f0f3f0f || *split == 0x1f000000)
      *split = 2;
    else if (*split == 0xff0f0f0f || *split == 0xff7f0f0f)
      *split = 1;
    else
      return;
    buffer->from((char *)context->edx);
  };
  return NewHook(hp, "MdePink");
}
bool Mink::attach_function()
{
  return MdePink() || InsertMinkHook();
}

bool Mink3::attach_function()
{
  const BYTE pattern[] = {
      // 夜勤病棟 復刻版+
      0xff, 0x15, XX4,
      0x33, 0xdb,
      0x89, 0x44, 0x24, XX,
      0x85, 0xc0,
      0x7e, XX,
      0x8a, 0x07,
      0x8d, 0x4c, 0x24, 0x10,
      0x50,
      0xe8, XX4,
      0x83, 0xf8, 0x02,
      0x75, 0x08,
      0x03, 0xd8,
      0x03, 0xf8,
      0x03, 0xf0,
      0xeb, XX,
      0x57,
      0x8b, 0xcd,
      0xe8, XX4,
      0x25, 0xff, 0x00, 0x00, 0x00,
      0x83, 0xe8, 0x00};
  auto addr = MemDbg::findBytes(pattern, sizeof(pattern), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0x100);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_OVERWRITE | EMBED_DYNA_SJIS;
  hp.embed_hook_font = F_TextOutA;
  hp.lineSeparator = L"\\n";
  PcHooks::hookGDIFunctions(TextOutA);
  return NewHook(hp, "Mink");
}