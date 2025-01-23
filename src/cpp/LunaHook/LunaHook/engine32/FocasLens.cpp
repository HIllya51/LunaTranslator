#include "FocasLens.h"

/** jichi 2/6/2015 FocasLens (Touhou)
 *  Sample game: [141227] [FocasLens] 幻想人形演�
 *
 *  Debugging method:
 *  1. Find first matched text, which has stable address
 *  2. Insert WRITE hw break point
 *  3. Find where the text is assigned
 *
 *  The game also invokes GDI functions (GetGlyphOutlineA), where the access is cached and looped.
 *
 *  Issues:
 *  - This hook cannot find name thread
 *  - Selected character name is hard-coded to the thread
 *
 *  001faaed   cc               int3
 *  001faaee   cc               int3
 *  001faaef   cc               int3
 *  001faaf0   55               push ebp
 *  001faaf1   8bec             mov ebp,esp
 *  001faaf3   51               push ecx
 *  001faaf4   53               push ebx
 *  001faaf5   56               push esi
 *  001faaf6   57               push edi
 *  001faaf7   8bf0             mov esi,eax
 *  001faaf9   e8 98281500      call .0034d396
 *  001faafe   50               push eax
 *  001faaff   a1 b08bb100      mov eax,dword ptr ds:[0xb18bb0]
 *  001fab04   03c6             add eax,esi
 *  001fab06   50               push eax
 *  001fab07   e8 9b241500      call .0034cfa7
 *  001fab0c   8b0d e88bb100    mov ecx,dword ptr ds:[0xb18be8]
 *  001fab12   8b3d b08bb100    mov edi,dword ptr ds:[0xb18bb0]
 *  001fab18   83c1 f7          add ecx,-0x9
 *  001fab1b   83c4 08          add esp,0x8
 *  001fab1e   8bd8             mov ebx,eax
 *  001fab20   390d ec8bb100    cmp dword ptr ds:[0xb18bec],ecx
 *  001fab26   7c 65            jl short .001fab8d
 *  001fab28   803c37 20        cmp byte ptr ds:[edi+esi],0x20
 *  001fab2c   74 41            je short .001fab6f
 *  001fab2e   803c37 81        cmp byte ptr ds:[edi+esi],0x81
 *  001fab32   75 4d            jnz short .001fab81
 *  001fab34   807c37 01 42     cmp byte ptr ds:[edi+esi+0x1],0x42
 *  001fab39   74 34            je short .001fab6f
 *  001fab3b   803c37 81        cmp byte ptr ds:[edi+esi],0x81
 *  001fab3f   75 40            jnz short .001fab81
 *  001fab41   807c37 01 41     cmp byte ptr ds:[edi+esi+0x1],0x41
 *  001fab46   74 27            je short .001fab6f
 *  001fab48   803c37 81        cmp byte ptr ds:[edi+esi],0x81
 *  001fab4c   75 33            jnz short .001fab81
 *  001fab4e   807c37 01 48     cmp byte ptr ds:[edi+esi+0x1],0x48
 *  001fab53   74 1a            je short .001fab6f
 *  001fab55   803c37 81        cmp byte ptr ds:[edi+esi],0x81
 *  001fab59   75 26            jnz short .001fab81
 *  001fab5b   807c37 01 49     cmp byte ptr ds:[edi+esi+0x1],0x49
 *  001fab60   74 0d            je short .001fab6f
 *  001fab62   803c37 81        cmp byte ptr ds:[edi+esi],0x81
 *  001fab66   75 19            jnz short .001fab81
 *  001fab68   807c37 01 40     cmp byte ptr ds:[edi+esi+0x1],0x40
 *  001fab6d   75 12            jnz short .001fab81
 *  001fab6f   803d c58bb100 00 cmp byte ptr ds:[0xb18bc5],0x0
 *  001fab76   75 09            jnz short .001fab81
 *  001fab78   c605 c58bb100 01 mov byte ptr ds:[0xb18bc5],0x1
 *  001fab7f   eb 0c            jmp short .001fab8d
 *  001fab81   e8 7a000000      call .001fac00
 *  001fab86   c605 c58bb100 00 mov byte ptr ds:[0xb18bc5],0x0
 *  001fab8d   8b0d e48bb100    mov ecx,dword ptr ds:[0xb18be4]
 *  001fab93   33c0             xor eax,eax
 *  001fab95   85db             test ebx,ebx
 *  001fab97   7e 2b            jle short .001fabc4
 *  001fab99   8d1437           lea edx,dword ptr ds:[edi+esi]
 *  001fab9c   8b35 ec8bb100    mov esi,dword ptr ds:[0xb18bec]
 *  001faba2   8955 fc          mov dword ptr ss:[ebp-0x4],edx
 *  001faba5   8bd1             mov edx,ecx
 *  001faba7   0faf15 e88bb100  imul edx,dword ptr ds:[0xb18be8]
 *  001fabae   0315 bc8bb100    add edx,dword ptr ds:[0xb18bbc]          ; .00b180f8
 *  001fabb4   03f2             add esi,edx
 *  001fabb6   8b55 fc          mov edx,dword ptr ss:[ebp-0x4]
 *  001fabb9   8a1402           mov dl,byte ptr ds:[edx+eax]
 *  001fabbc   881406           mov byte ptr ds:[esi+eax],dl    ; jichi: text is in dl in byte
 *  001fabbf   40               inc eax
 *  001fabc0   3bc3             cmp eax,ebx
 *  001fabc2  ^7c f2            jl short .001fabb6
 *  001fabc4   0faf0d e88bb100  imul ecx,dword ptr ds:[0xb18be8]
 *  001fabcb   030d bc8bb100    add ecx,dword ptr ds:[0xb18bbc]          ; .00b180f8
 *  001fabd1   a1 ec8bb100      mov eax,dword ptr ds:[0xb18bec]
 *  001fabd6   03fb             add edi,ebx
 *  001fabd8   893d b08bb100    mov dword ptr ds:[0xb18bb0],edi
 *  001fabde   5f               pop edi
 *  001fabdf   03c8             add ecx,eax
 *  001fabe1   03c3             add eax,ebx
 *  001fabe3   5e               pop esi
 *  001fabe4   c60419 00        mov byte ptr ds:[ecx+ebx],0x0
 *  001fabe8   a3 ec8bb100      mov dword ptr ds:[0xb18bec],eax
 *  001fabed   5b               pop ebx
 *  001fabee   8be5             mov esp,ebp
 *  001fabf0   5d               pop ebp
 *  001fabf1   c3               retn
 *  001fabf2   cc               int3
 *  001fabf3   cc               int3
 *  001fabf4   cc               int3
 *  001fabf5   cc               int3
 *  001fabf6   cc               int3
 *  001fabf7   cc               int3
 */
static void SpecialHookFocasLens(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  DWORD addr = (DWORD)context->base + regoffset(edx);
  if (*(char *)addr)
  {
    buffer->from(addr, 1);
    *split = FIXED_SPLIT_VALUE;
  }
}
bool InsertFocasLensHook()
{
  const BYTE bytes[] = {
      0x8a, 0x14, 0x02, // 001fabb9   8a1402           mov dl,byte ptr ds:[edx+eax]
      0x88, 0x14, 0x06, // 001fabbc   881406           mov byte ptr ds:[esi+eax],dl    ; jichi: text is in dl in byte
      0x40,             // 001fabbf   40               inc eax
      0x3b, 0xc3        // 001fabc0   3bc3             cmp eax,ebx
  };
  enum
  {
    addr_offset = 0x001fabbc - 0x001fabb9
  };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  // GROWL(addr);
  if (!addr)
  {
    ConsoleOutput("FocasLens: pattern not found");
    return false;
  }
  HookParam hp;
  hp.address = addr + addr_offset;
  hp.text_fun = SpecialHookFocasLens;                               // use special hook to force byte access
  hp.type = USING_STRING | USING_SPLIT | FIXING_SPLIT | NO_CONTEXT; // no context to get rid of relative function address
  ConsoleOutput("INSERT FocasLens");

  // GDI functions are kept in case the font is not cached
  //
  return NewHook(hp, "FocasLens");
}

bool FocasLens::attach_function()
{

  return InsertFocasLensHook();
}