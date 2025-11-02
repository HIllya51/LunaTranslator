#include "AdobeFlash10.h"

/** jichi 10/31/2014 Adobe Flash Player v10
 *
 *  Sample game: [141031] [ヂ�ンクルベル] 輪舞曲Duo
 *
 *  Debug method: Hex utf16 text, then insert hw breakpoints
 *    21:51 3110% hexstr 『何よ utf16
 *    0e30554f8830
 *
 *  There are also UTF-8 strings in the memory. I could not find a good place to hook
 *  using hw breakpoints.
 *
 *  There are lots of matches. One is selected. Then, the enclosing function is selected.
 *  arg1 is the UNICODE text.
 *
 *  Pattern:
 *
 *  0161293a   8bc6             mov eax,esi
 *  0161293c   5e               pop esi
 *  0161293d   c2 0800          retn 0x8
 *
 *  Function starts
 *  01612940   8b4c24 0c        mov ecx,dword ptr ss:[esp+0xc] ; jichi: hook here
 *  01612944   53               push ebx
 *  01612945   55               push ebp
 *  01612946   56               push esi
 *  01612947   57               push edi
 *  01612948   33ff             xor edi,edi
 *  0161294a   85c9             test ecx,ecx
 *  0161294c   0f84 5f010000    je ron2.01612ab1
 *  01612952   397c24 18        cmp dword ptr ss:[esp+0x18],edi
 *  01612956   0f8e ba010000    jle ron2.01612b16
 *  0161295c   8b6c24 14        mov ebp,dword ptr ss:[esp+0x14]
 *  01612960   be 01000000      mov esi,0x1
 *  01612965   eb 09            jmp short ron2.01612970
 *  01612967   8da424 00000000  lea esp,dword ptr ss:[esp]
 *  0161296e   8bff             mov edi,edi
 *  01612970   0fb755 00        movzx edx,word ptr ss:[ebp]
 *  01612974   297424 18        sub dword ptr ss:[esp+0x18],esi
 *  01612978   b8 80000000      mov eax,0x80
 *  0161297d   66:3bd0          cmp dx,ax
 *  01612980   73 15            jnb short ron2.01612997
 *  01612982   297424 20        sub dword ptr ss:[esp+0x20],esi
 *  01612986   0f88 1d010000    js ron2.01612aa9
 *  0161298c   8811             mov byte ptr ds:[ecx],dl
 *  0161298e   03ce             add ecx,esi
 *  01612990   03fe             add edi,esi
 *  01612992   e9 fd000000      jmp ron2.01612a94
 *  01612997   b8 00080000      mov eax,0x800
 *  0161299c   66:3bd0          cmp dx,ax
 *  0161299f   73 2a            jnb short ron2.016129cb
 *  016129a1   836c24 20 02     sub dword ptr ss:[esp+0x20],0x2
 *  016129a6   0f88 fd000000    js ron2.01612aa9
 *  016129ac   8bc2             mov eax,edx
 *  016129ae   c1e8 06          shr eax,0x6
 *  016129b1   24 1f            and al,0x1f
 *  016129b3   0c c0            or al,0xc0
 *  016129b5   8801             mov byte ptr ds:[ecx],al
 *  016129b7   80e2 3f          and dl,0x3f
 *  016129ba   03ce             add ecx,esi
 *  016129bc   80ca 80          or dl,0x80
 *  016129bf   8811             mov byte ptr ds:[ecx],dl
 *  016129c1   03ce             add ecx,esi
 *  016129c3   83c7 02          add edi,0x2
 *  016129c6   e9 c9000000      jmp ron2.01612a94
 *  016129cb   8d82 00280000    lea eax,dword ptr ds:[edx+0x2800]
 *  016129d1   bb ff030000      mov ebx,0x3ff
 *  016129d6   66:3bc3          cmp ax,bx
 *  016129d9   77 7b            ja short ron2.01612a56
 *  016129db   297424 18        sub dword ptr ss:[esp+0x18],esi
 *  016129df   0f88 c4000000    js ron2.01612aa9
 *  016129e5   0fb775 02        movzx esi,word ptr ss:[ebp+0x2]
 *  016129e9   83c5 02          add ebp,0x2
 *  016129ec   8d86 00240000    lea eax,dword ptr ds:[esi+0x2400]
 *  016129f2   66:3bc3          cmp ax,bx
 *  016129f5   77 58            ja short ron2.01612a4f
 *  016129f7   0fb7d2           movzx edx,dx
 *  016129fa   81ea f7d70000    sub edx,0xd7f7
 *  01612a00   0fb7c6           movzx eax,si
 *  01612a03   c1e2 0a          shl edx,0xa
 *  01612a06   03d0             add edx,eax
 *  01612a08   836c24 20 04     sub dword ptr ss:[esp+0x20],0x4
 *  01612a0d   0f88 96000000    js ron2.01612aa9
 *  01612a13   8bc2             mov eax,edx
 *  01612a15   c1e8 12          shr eax,0x12
 *  01612a18   24 07            and al,0x7
 *  01612a1a   0c f0            or al,0xf0
 *  01612a1c   8801             mov byte ptr ds:[ecx],al
 *  01612a1e   8bc2             mov eax,edx
 *  01612a20   c1e8 0c          shr eax,0xc
 *  01612a23   24 3f            and al,0x3f
 *  01612a25   be 01000000      mov esi,0x1
 *  01612a2a   0c 80            or al,0x80
 *  01612a2c   880431           mov byte ptr ds:[ecx+esi],al
 *  01612a2f   03ce             add ecx,esi
 *  01612a31   8bc2             mov eax,edx
 *  01612a33   c1e8 06          shr eax,0x6
 *  01612a36   03ce             add ecx,esi
 *  01612a38   24 3f            and al,0x3f
 *  01612a3a   0c 80            or al,0x80
 *  01612a3c   8801             mov byte ptr ds:[ecx],al
 *  01612a3e   80e2 3f          and dl,0x3f
 *  01612a41   03ce             add ecx,esi
 *  01612a43   80ca 80          or dl,0x80
 *  01612a46   8811             mov byte ptr ds:[ecx],dl
 *  01612a48   03ce             add ecx,esi
 *  01612a4a   83c7 04          add edi,0x4
 *  01612a4d   eb 45            jmp short ron2.01612a94
 *  01612a4f   be 01000000      mov esi,0x1
 *  01612a54   eb 0b            jmp short ron2.01612a61
 *  01612a56   8d82 00240000    lea eax,dword ptr ds:[edx+0x2400]
 *  01612a5c   66:3bc3          cmp ax,bx
 *  01612a5f   77 05            ja short ron2.01612a66
 *  01612a61   ba fdff0000      mov edx,0xfffd
 *  01612a66   836c24 20 03     sub dword ptr ss:[esp+0x20],0x3
 *  01612a6b   78 3c            js short ron2.01612aa9
 *  01612a6d   8bc2             mov eax,edx
 *  01612a6f   c1e8 0c          shr eax,0xc
 *  01612a72   24 0f            and al,0xf
 *  01612a74   0c e0            or al,0xe0
 *  01612a76   8801             mov byte ptr ds:[ecx],al
 *  01612a78   8bc2             mov eax,edx
 *  01612a7a   c1e8 06          shr eax,0x6
 *  01612a7d   03ce             add ecx,esi
 *  01612a7f   24 3f            and al,0x3f
 *  01612a81   0c 80            or al,0x80
 *  01612a83   8801             mov byte ptr ds:[ecx],al
 *  01612a85   80e2 3f          and dl,0x3f
 *  01612a88   03ce             add ecx,esi
 *  01612a8a   80ca 80          or dl,0x80
 *  01612a8d   8811             mov byte ptr ds:[ecx],dl
 *  01612a8f   03ce             add ecx,esi
 *  01612a91   83c7 03          add edi,0x3
 *  01612a94   83c5 02          add ebp,0x2
 *  01612a97   837c24 18 00     cmp dword ptr ss:[esp+0x18],0x0
 *  01612a9c  ^0f8f cefeffff    jg ron2.01612970
 *  01612aa2   8bc7             mov eax,edi
 *  01612aa4   5f               pop edi
 *  01612aa5   5e               pop esi
 *  01612aa6   5d               pop ebp
 *  01612aa7   5b               pop ebx
 *  01612aa8   c3               retn
 *  01612aa9   5f               pop edi
 *  01612aaa   5e               pop esi
 *  01612aab   5d               pop ebp
 *  01612aac   83c8 ff          or eax,0xffffffff
 *  01612aaf   5b               pop ebx
 *  01612ab0   c3               retn
 *  01612ab1   8b4424 18        mov eax,dword ptr ss:[esp+0x18]
 *  01612ab5   85c0             test eax,eax
 *  01612ab7   7e 5d            jle short ron2.01612b16
 *  01612ab9   8b5424 14        mov edx,dword ptr ss:[esp+0x14]
 *  01612abd   8d49 00          lea ecx,dword ptr ds:[ecx]
 *  01612ac0   0fb70a           movzx ecx,word ptr ds:[edx] ; jichi: this is where the text is accessed
 *  01612ac3   be 80000000      mov esi,0x80
 *  01612ac8   48               dec eax
 *  01612ac9   66:3bce          cmp cx,si
 *  01612acc   73 03            jnb short ron2.01612ad1
 *  01612ace   47               inc edi
 *  01612acf   eb 3e            jmp short ron2.01612b0f
 *  01612ad1   be 00080000      mov esi,0x800
 *  01612ad6   66:3bce          cmp cx,si
 *  01612ad9   73 05            jnb short ron2.01612ae0
 *  01612adb   83c7 02          add edi,0x2
 *  01612ade   eb 2f            jmp short ron2.01612b0f
 *  01612ae0   81c1 00280000    add ecx,0x2800
 *  01612ae6   be ff030000      mov esi,0x3ff
 *  01612aeb   66:3bce          cmp cx,si
 *  01612aee   77 1c            ja short ron2.01612b0c
 *  01612af0   83e8 01          sub eax,0x1
 *  01612af3  ^78 b4            js short ron2.01612aa9
 *  01612af5   0fb74a 02        movzx ecx,word ptr ds:[edx+0x2]
 *  01612af9   83c2 02          add edx,0x2
 *  01612afc   81c1 00240000    add ecx,0x2400
 *  01612b02   66:3bce          cmp cx,si
 *  01612b05   77 05            ja short ron2.01612b0c
 *  01612b07   83c7 04          add edi,0x4
 *  01612b0a   eb 03            jmp short ron2.01612b0f
 *  01612b0c   83c7 03          add edi,0x3
 *  01612b0f   83c2 02          add edx,0x2
 *  01612b12   85c0             test eax,eax
 *  01612b14  ^7f aa            jg short ron2.01612ac0
 *  01612b16   8bc7             mov eax,edi
 *  01612b18   5f               pop edi
 *  01612b19   5e               pop esi
 *  01612b1a   5d               pop ebp
 *  01612b1b   5b               pop ebx
 *  01612b1c   c3               retn
 *  01612b1d   cc               int3
 *  01612b1e   cc               int3
 *  01612b1f   cc               int3
 *
 *  Runtime stack:
 *  0019e974   0161640e  return to Ron2.0161640e from Ron2.01612940
 *  0019e978   1216c180  UNICODE "Dat/Chr/HAL_061.swf"
 *  0019e97c   00000013
 *  0019e980   12522838
 *  0019e984   00000013
 *  0019e988   0210da80
 *  0019e98c   0019ecb0
 *  0019e990   0019e9e0
 *  0019e994   0019ea24
 *  0019e998   0019e9cc
 *
 *  Runtime registers:
 *  EAX 12522838
 *  ECX 1216C180 UNICODE "Dat/Chr/HAL_061.swf"
 *  EDX 0C5E9898
 *  EBX 12532838
 *  ESP 0019E974
 *  EBP 00000013
 *  ESI 00000013
 *  EDI 0019E9CC
 *  EIP 01612940 Ron2.01612940
 */
// Skip ASCII garbage such as: Dat/Chr/HAL_061.swf
static void AdobeFlashFilter(TextBuffer *buffer, HookParam *)
{
  // TODO: Remove [0-9a-zA-Z./]{4,} as garbage
  LPCWSTR p = reinterpret_cast<LPCWSTR>(buffer->buff);
  for (size_t i = 0; i < buffer->size / 2; i++)
    if (p[i] & 0xff00)
      return;
  buffer->clear();
}
bool InsertAdobeFlash10Hook()
{
  const BYTE bytes[] = {
      0x8b, 0x4c, 0x24, 0x0c, // 01612940   8b4c24 0c        mov ecx,dword ptr ss:[esp+0xc] ; jichi: hook here
      0x53,                   // 01612944   53               push ebx
      0x55,                   // 01612945   55               push ebp
      0x56,                   // 01612946   56               push esi
      0x57,                   // 01612947   57               push edi
      0x33, 0xff,             // 01612948   33ff             xor edi,edi
      0x85, 0xc9,             // 0161294a   85c9             test ecx,ecx
      0x0f, 0x84              //, 5f010000  // 0161294c   0f84 5f010000    je ron2.01612ab1
  };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  // addr = 0x01612940;
  // addr = 0x01612AC0;
  if (!addr)
  {
    ConsoleOutput("AdobeFlash10: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  // hp.length_offset = 2 * 4; // arg2 might be the length
  hp.type = CODEC_UTF16 | USING_STRING;
  hp.filter_fun = AdobeFlashFilter;
  ConsoleOutput("INSERT Adobe Flash 10");

  ConsoleOutput("AdobeFlash10: disable GDI hooks");

  return NewHook(hp, "Adobe Flash 10");
}
namespace
{
  bool __()
  {
    //[yosino] ANCIENT
    // https://ci-en.dlsite.com/creator/5059/
    const BYTE bytes[] = {
        0x55, 0x8b, 0xec,
        0x51, 0x51, 0x8b, 0x45, 0x10,
        0x53, 0x8b, 0xd9, 0x89, 0x43, 0x08,
        0x8a, 0x45, 0x0c};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);

    if (!addr)
      return false;

    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(4);
    hp.type = CODEC_UTF16 | USING_STRING;
    return NewHook(hp, "Adobe Flash 11");
  }
}
bool AdobeFlash10::attach_function()
{

  return InsertAdobeFlash10Hook() | __();
}