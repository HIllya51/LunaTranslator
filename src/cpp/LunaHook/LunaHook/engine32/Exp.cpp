#include "Exp.h"

/** jichi 9/8/2014 EXP, http://www.exp-inc.jp
 *  Maker: EXP, 5pb
 *  Sample game: 剣の街�異邦人
 *
 *  There are three matched memory addresses with SHIFT-JIS.
 *  The middle one is used as it is aligned with zeros.
 *  The memory address is fixed.
 *
 *  There are three functions found using hardware breakpoints.
 *  The last one is used as the first two are looped.
 *
 *  reladdr = 0x138020
 *
 *  baseaddr = 0x00120000
 *
 *  0025801d   cc               int3
 *  0025801e   cc               int3
 *  0025801f   cc               int3
 *  00258020   55               push ebp  ; jichi: hook here
 *  00258021   8bec             mov ebp,esp
 *  00258023   8b45 08          mov eax,dword ptr ss:[ebp+0x8]
 *  00258026   83ec 08          sub esp,0x8
 *  00258029   85c0             test eax,eax
 *  0025802b   0f84 d8000000    je .00258109
 *  00258031   837d 10 00       cmp dword ptr ss:[ebp+0x10],0x0
 *  00258035   0f84 ce000000    je .00258109
 *  0025803b   8b10             mov edx,dword ptr ds:[eax]      ; jichi: edx is the text
 *  0025803d   8b45 0c          mov eax,dword ptr ss:[ebp+0xc]
 *  00258040   53               push ebx
 *  00258041   56               push esi
 *  00258042   c745 f8 00000000 mov dword ptr ss:[ebp-0x8],0x0
 *  00258049   8945 fc          mov dword ptr ss:[ebp-0x4],eax
 *  0025804c   57               push edi
 *  0025804d   8d49 00          lea ecx,dword ptr ds:[ecx]
 *  00258050   8a0a             mov cl,byte ptr ds:[edx]    jichi: text in accessed in edx
 *  00258052   8a45 14          mov al,byte ptr ss:[ebp+0x14]
 *  00258055   3ac1             cmp al,cl
 *  00258057   74 7a            je short .002580d3
 *  00258059   8b7d 10          mov edi,dword ptr ss:[ebp+0x10]
 *  0025805c   8b5d fc          mov ebx,dword ptr ss:[ebp-0x4]
 *  0025805f   33f6             xor esi,esi
 *  00258061   8bc2             mov eax,edx
 *  00258063   80f9 81          cmp cl,0x81
 *  00258066   72 05            jb short .0025806d
 *  00258068   80f9 9f          cmp cl,0x9f
 *  0025806b   76 0a            jbe short .00258077
 *  0025806d   80f9 e0          cmp cl,0xe0
 *  00258070   72 1d            jb short .0025808f
 *  00258072   80f9 fc          cmp cl,0xfc
 *  00258075   77 18            ja short .0025808f
 *  00258077   8b45 fc          mov eax,dword ptr ss:[ebp-0x4]
 *  0025807a   85c0             test eax,eax
 *  0025807c   74 05            je short .00258083
 *  0025807e   8808             mov byte ptr ds:[eax],cl
 *  00258080   8d58 01          lea ebx,dword ptr ds:[eax+0x1]
 *  00258083   8b7d 10          mov edi,dword ptr ss:[ebp+0x10]
 *  00258086   8d42 01          lea eax,dword ptr ds:[edx+0x1]
 *  00258089   be 01000000      mov esi,0x1
 *  0025808e   4f               dec edi
 *  0025808f   85ff             test edi,edi
 *  00258091   74 36            je short .002580c9
 *  00258093   85db             test ebx,ebx
 *  00258095   74 04            je short .0025809b
 *  00258097   8a08             mov cl,byte ptr ds:[eax]
 *  00258099   880b             mov byte ptr ds:[ebx],cl
 *  0025809b   46               inc esi
 *  0025809c   33c0             xor eax,eax
 *  0025809e   66:3bc6          cmp ax,si
 *  002580a1   7f 47            jg short .002580ea
 *  002580a3   0fbfce           movsx ecx,si
 *  002580a6   03d1             add edx,ecx
 *  002580a8   3945 fc          cmp dword ptr ss:[ebp-0x4],eax
 *  002580ab   74 03            je short .002580b0
 *  002580ad   014d fc          add dword ptr ss:[ebp-0x4],ecx
 *  002580b0   294d 10          sub dword ptr ss:[ebp+0x10],ecx
 *  002580b3   014d f8          add dword ptr ss:[ebp-0x8],ecx
 *  002580b6   8a0a             mov cl,byte ptr ds:[edx]
 *  002580b8   80f9 0a          cmp cl,0xa
 *  002580bb   74 20            je short .002580dd
 *  002580bd   80f9 0d          cmp cl,0xd
 *  002580c0   74 1b            je short .002580dd
 *  002580c2   3945 10          cmp dword ptr ss:[ebp+0x10],eax
 *  002580c5  ^75 89            jnz short .00258050
 *  002580c7   eb 21            jmp short .002580ea
 *  002580c9   85db             test ebx,ebx
 *  002580cb   74 1d            je short .002580ea
 *  002580cd   c643 ff 00       mov byte ptr ds:[ebx-0x1],0x0
 *  002580d1   eb 17            jmp short .002580ea
 *  002580d3   84c0             test al,al
 *  002580d5   74 13            je short .002580ea
 *  002580d7   42               inc edx
 *  002580d8   ff45 f8          inc dword ptr ss:[ebp-0x8]
 *  002580db   eb 0d            jmp short .002580ea
 *  002580dd   8a42 01          mov al,byte ptr ds:[edx+0x1]
 *  002580e0   42               inc edx
 *  002580e1   3c 0a            cmp al,0xa
 *  002580e3   74 04            je short .002580e9
 *  002580e5   3c 0d            cmp al,0xd
 *  002580e7   75 01            jnz short .002580ea
 *  002580e9   42               inc edx
 *  002580ea   8b45 fc          mov eax,dword ptr ss:[ebp-0x4]
 *  002580ed   5f               pop edi
 *  002580ee   5e               pop esi
 *  002580ef   5b               pop ebx
 *  002580f0   85c0             test eax,eax
 *  002580f2   74 09            je short .002580fd
 *  002580f4   837d 10 00       cmp dword ptr ss:[ebp+0x10],0x0
 *  002580f8   74 03            je short .002580fd
 *  002580fa   c600 00          mov byte ptr ds:[eax],0x0
 *  002580fd   8b4d 08          mov ecx,dword ptr ss:[ebp+0x8]
 *  00258100   8b45 f8          mov eax,dword ptr ss:[ebp-0x8]
 *  00258103   8911             mov dword ptr ds:[ecx],edx
 *  00258105   8be5             mov esp,ebp
 *  00258107   5d               pop ebp
 *  00258108   c3               retn
 *  00258109   33c0             xor eax,eax
 *  0025810b   8be5             mov esp,ebp
 *  0025810d   5d               pop ebp
 *  0025810e   c3               retn
 *  0025810f   cc               int3
 *
 *  Stack:
 *  0f14f87c   00279177  return to .00279177 from .00258020
 *  0f14f880   0f14f8b0 ; arg1  address of the text's pointer
 *  0f14f884   0f14f8c0 ; arg2  pointed to zero, maybe a buffer
 *  0f14f888   00000047 ; arg3  it is zero if no text, this value might be text size + 1
 *  0f14f88c   ffffff80 ; constant, used as split
 *  0f14f890   005768c8  .005768c8
 *  0f14f894   02924340 ; text is at 02924350
 *  0f14f898   00000001 ; this might also be a good split
 *  0f14f89c   1b520020
 *  0f14f8a0   00000000
 *  0f14f8a4   00000000
 *  0f14f8a8   029245fc
 *  0f14f8ac   0004bfd3
 *  0f14f8b0   0f14fae0
 *  0f14f8b4   00000000
 *  0f14f8b8   00000000
 *  0f14f8bc   02924340
 *  0f14f8c0   00000000
 *
 *  Registers:
 *  eax 0f14f8c0 ; floating at runtime
 *  ecx 0f14f8b0; floating at runtime
 *  edx 00000000
 *  ebx 0f14fae0; floating at runtime
 *  esp 0f14f87c; floating at runtime
 *  ebp 0f14facc; floating at runtime
 *  esi 00000047
 *  edi 02924340 ; text is in 02924350
 *  eip 00258020 .00258020
 *
 *  Memory access pattern:
 *  For long sentences, it first render the first line, then the second line, and so on.
 *  So, the second line is a subtext of the entire dialog.
 */
static void SpecialHookExp(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  static DWORD lasttext;
  // 00258020   55               push ebp  ; jichi: hook here
  // 00258021   8bec             mov ebp,esp
  // 00258023   8b45 08          mov eax,dword ptr ss:[ebp+0x8] ; jichi: move arg1 to eax
  // 00258029   85c0             test eax,eax   ; check if text is null
  // 0025802b   0f84 d8000000    je .00258109
  // 00258031   837d 10 00       cmp dword ptr ss:[ebp+0x10],0x0 ; jichi: compare 0 with arg3, which is size+1
  // 00258035   0f84 ce000000    je .00258109
  // 0025803b   8b10             mov edx,dword ptr ds:[eax] ; move text address to edx
  DWORD arg1 = context->stack[1], // mov eax,dword ptr ss:[ebp+0x8]
      arg3 = context->stack[3];   // size - 1
  if (arg1 && arg3)
    if (DWORD text = *(DWORD *)arg1)
      if (!(text > lasttext && text < lasttext + VNR_TEXT_CAPACITY))
      {                  // text is not a subtext of lastText
        lasttext = text; // mov edx,dword ptr ds:[eax]
        //*len = arg3 - 1; // the last char is the '\0', so -1, but this value is not reliable

        buffer->from((char *)text);
        // Registers are not used as split as all of them are floating at runtime
        //*split = argof(4, esp_base); // arg4, always -8, this will merge all threads and result in repetition
        *split = context->stack[7]; // reduce repetition, but still have sub-text repeat
      }
}
bool InsertExpHook()
{
  const BYTE bytes[] = {
      0x55,                                     // 00258020   55               push ebp  ; jichi: hook here, function starts, text in [arg1], size+1 in arg3
      0x8b, 0xec,                               // 00258021   8bec             mov ebp,esp
      0x8b, 0x45, 0x08,                         // 00258023   8b45 08          mov eax,dword ptr ss:[ebp+0x8]
      0x83, 0xec, 0x08,                         // 00258026   83ec 08          sub esp,0x8
      0x85, 0xc0,                               // 00258029   85c0             test eax,eax
      0x0f, 0x84, XX4,                          // 0025802b   0f84 d8000000    je .00258109
      0x83, 0x7d, 0x10, 0x00,                   // 00258031   837d 10 00       cmp dword ptr ss:[ebp+0x10],0x0
      0x0f, 0x84, XX4,                          // 00258035   0f84 ce000000    je .00258109
      0x8b, 0x10,                               // 0025803b   8b10             mov edx,dword ptr ds:[eax] ; jichi: edx is the text
      0x8b, 0x45, 0x0c,                         // 0025803d   8b45 0c          mov eax,dword ptr ss:[ebp+0xc]
      0x53,                                     // 00258040   53               push ebx
      0x56,                                     // 00258041   56               push esi
      0xc7, 0x45, 0xf8, 0x00, 0x00, 0x00, 0x00, // 00258042   c745 f8 00000000 mov dword ptr ss:[ebp-0x8],0x0
      0x89, 0x45, 0xfc,                         // 00258049   8945 fc          mov dword ptr ss:[ebp-0x4],eax
      0x57,                                     // 0025804c   57               push edi
      0x8d, 0x49, 0x00,                         // 0025804d   8d49 00          lea ecx,dword ptr ds:[ecx]
      0x8a, 0x0a                                // 00258050   8a0a             mov cl,byte ptr ds:[edx]  ; jichi: text accessed in edx
  };
  enum
  {
    addr_offset = 0
  };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  // GROWL_DWORD(addr);
  if (!addr)
  {
    ConsoleOutput("EXP: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr + addr_offset;
  hp.type = NO_CONTEXT | USING_STRING; // NO_CONTEXT to get rid of floating address
  hp.text_fun = SpecialHookExp;
  ConsoleOutput("INSERT EXP");

  ConsoleOutput("EXP: disable GDI hooks"); // There are no GDI functions hooked though

  return NewHook(hp, "EXP"); // FIXME: text displayed line by line
}

bool Exp::attach_function()
{

  return InsertExpHook();
}