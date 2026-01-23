#include "HorkEye.h"

/** 10/20/2014 jichi: HorkEye, http://horkeye.com
 *  Sample game: [150226] 結城友奈�勀��ある 体験版
 *
 *  No GDI functions are used by this game.
 *
 *  Debug method:
 *  There are two matched texts.
 *  The one having fixed address is used to insert hw breakpoints.
 *
 *  I found are two functions addressing the address, both of which seems to be good.
 *  The first one is used:
 *
 *  013cda60   8d4c24 1c        lea ecx,dword ptr ss:[esp+0x1c]
 *  013cda64   51               push ecx
 *  013cda65   68 48a8c201      push .01c2a848                                     ; ascii "if"
 *  013cda6a   e8 d1291600      call .01530440
 *  013cda6f   83c4 0c          add esp,0xc
 *  013cda72   6a 01            push 0x1
 *  013cda74   83ec 1c          sub esp,0x1c
 *  013cda77   8bcc             mov ecx,esp
 *  013cda79   896424 30        mov dword ptr ss:[esp+0x30],esp
 *  013cda7d   6a 10            push 0x10
 *  013cda7f   c741 14 0f000000 mov dword ptr ds:[ecx+0x14],0xf
 *  013cda86   c741 10 00000000 mov dword ptr ds:[ecx+0x10],0x0
 *  013cda8d   68 80125601      push .01561280
 *  013cda92   c601 00          mov byte ptr ds:[ecx],0x0
 *  013cda95   e8 5681ffff      call .013c5bf0
 *  013cda9a   e8 717a0900      call .01465510
 *  013cda9f   83c4 20          add esp,0x20
 *  013cdaa2   b8 01000000      mov eax,0x1
 *  013cdaa7   8b8c24 b8000000  mov ecx,dword ptr ss:[esp+0xb8]
 *  013cdaae   5f               pop edi
 *  013cdaaf   5e               pop esi
 *  013cdab0   5d               pop ebp
 *  013cdab1   5b               pop ebx
 *  013cdab2   33cc             xor ecx,esp
 *  013cdab4   e8 c7361600      call .01531180
 *  013cdab9   81c4 ac000000    add esp,0xac
 *  013cdabf   c3               retn
 *  013cdac0   83ec 40          sub esp,0x40
 *  013cdac3   a1 24805d01      mov eax,dword ptr ds:[0x15d8024]
 *  013cdac8   8b15 c4709901    mov edx,dword ptr ds:[0x19970c4]
 *  013cdace   8d0c00           lea ecx,dword ptr ds:[eax+eax]
 *  013cdad1   a1 9c506b01      mov eax,dword ptr ds:[0x16b509c]
 *  013cdad6   0305 18805d01    add eax,dword ptr ds:[0x15d8018]
 *  013cdadc   53               push ebx
 *  013cdadd   8b5c24 48        mov ebx,dword ptr ss:[esp+0x48]
 *  013cdae1   55               push ebp
 *  013cdae2   8b6c24 50        mov ebp,dword ptr ss:[esp+0x50]
 *  013cdae6   894c24 34        mov dword ptr ss:[esp+0x34],ecx
 *  013cdaea   8b0d 20805d01    mov ecx,dword ptr ds:[0x15d8020]
 *  013cdaf0   894424 18        mov dword ptr ss:[esp+0x18],eax
 *  013cdaf4   a1 1c805d01      mov eax,dword ptr ds:[0x15d801c]
 *  013cdaf9   03c8             add ecx,eax
 *  013cdafb   56               push esi
 *  013cdafc   33f6             xor esi,esi
 *  013cdafe   d1f8             sar eax,1
 *  013cdb00   45               inc ebp
 *  013cdb01   896c24 24        mov dword ptr ss:[esp+0x24],ebp
 *  013cdb05   897424 0c        mov dword ptr ss:[esp+0xc],esi
 *  013cdb09   894c24 18        mov dword ptr ss:[esp+0x18],ecx
 *  013cdb0d   8a0c1a           mov cl,byte ptr ds:[edx+ebx]        jichi: here
 *  013cdb10   894424 30        mov dword ptr ss:[esp+0x30],eax
 *  013cdb14   8a441a 01        mov al,byte ptr ds:[edx+ebx+0x1]
 *  013cdb18   57               push edi
 *  013cdb19   897424 14        mov dword ptr ss:[esp+0x14],esi
 *  013cdb1d   3935 c8709901    cmp dword ptr ds:[0x19970c8],esi
 *
 *  The hooked place is only accessed once.
 *  013cdb0d   8a0c1a           mov cl,byte ptr ds:[edx+ebx]        jichi: here
 *  ebx is the text to be base address.
 *  edx is the offset to skip character name.
 *
 *  023B66A0  81 79 89 C4 EA A3 2C 53 30 30 35 5F 42 5F 30 30  【夏偾,S005_B_00
 *  023B66B0  30 32 81 7A 81 75 83 6F 81 5B 83 65 83 62 83 4E  02】「バーッ�ク
 *  023B66C0  83 58 82 CD 82 B1 82 C1 82 BF 82 CC 93 73 8D 87  スはこっちの都� *  023B66D0  82 C8 82 C7 82 A8 8D 5C 82 A2 82 C8 82 B5 81 63  などお構いなし…
 *
 *  There are garbage in character name.
 *
 *  1/15/2015
 *  Alternative hook that might not need a text filter:
 *  http://www.hongfire.com/forum/showthread.php/36807-AGTH-text-extraction-tool-for-games-translation/page753
 *  /HA-4@552B5:姉小路直子と銀色の死�exe
 *  If this hook no longer works, try that one instead.

 *  Artikash 12/26/2018: Old HorkEye hook can't be found in shukusei no girlfriend https://vndb.org/v22880
 *  This function can be used instead. Hook code: /HS4@funcaddr
0022DD80 - 83 EC 44              - sub esp,44 { 68 }
0022DD83 - A1 3C704400           - mov eax,[0044703C] { [0000001C] }
0022DD88 - 8B 0D 34704400        - mov ecx,[00447034] { [00000014] }
0022DD8E - 03 C0                 - add eax,eax
0022DD90 - 8B 54 24 48           - mov edx,[esp+48]
0022DD94 - 89 44 24 2C           - mov [esp+2C],eax
0022DD98 - A1 C87E5500           - mov eax,[00557EC8] { [00000002] }
0022DD9D - 03 05 30704400        - add eax,[00447030] { [00000014] }
0022DDA3 - 89 44 24 18           - mov [esp+18],eax
0022DDA7 - A1 38704400           - mov eax,[00447038] { [00000008] }
0022DDAC - 03 C1                 - add eax,ecx
0022DDAE - D1 F9                 - sar ecx,1
0022DDB0 - 53                    - push ebx
0022DDB1 - 55                    - push ebp
0022DDB2 - 56                    - push esi
0022DDB3 - 8B 74 24 58           - mov esi,[esp+58]
0022DDB7 - 33 DB                 - xor ebx,ebx
0022DDB9 - 89 4C 24 48           - mov [esp+48],ecx
0022DDBD - 46                    - inc esi
0022DDBE - 8B 0D 5CA28300        - mov ecx,[0083A25C] { [00000000] }
0022DDC4 - 57                    - push edi
0022DDC5 - 8B 3D 887E5500        - mov edi,[00557E88] { [00000040] }
0022DDCB - 89 74 24 2C           - mov [esp+2C],esi
0022DDCF - 89 44 24 34           - mov [esp+34],eax
0022DDD3 - 89 5C 24 18           - mov [esp+18],ebx
0022DDD7 - 8A 24 11              - mov ah,[ecx+edx]
0022DDDA - 8A 44 11 01           - mov al,[ecx+edx+01]
0022DDDE - 89 7C 24 20           - mov [esp+20],edi
0022DDE2 - 39 1D 60A28300        - cmp [0083A260],ebx { [00000000] }
0022DDE8 - 0F85 DD000000         - jne 0022DECB
0022DDEE - 80 FC 5B              - cmp ah,5B { 91 }
0022DDF1 - 0F85 9C000000         - jne 0022DE93
0022DDF7 - 8B C1                 - mov eax,ecx
0022DDF9 - 3B C6                 - cmp eax,esi
0022DDFB - 7D 10                 - jnl 0022DE0D
0022DDFD - 0F1F 00               - nop [eax]
0022DE00 - 80 3C 10  5D          - cmp byte ptr [eax+edx],5D { 93 }
0022DE04 - 74 79                 - je 0022DE7F
0022DE06 - 40                    - inc eax
0022DE07 - 3B 44 24 2C           - cmp eax,[esp+2C]
0022DE0B - 7C F3                 - jl 0022DE00
0022DE0D - A1 BC7E5500           - mov eax,[00557EBC] { [00000001] }
0022DE12 - 85 C0                 - test eax,eax
0022DE14 - 0F84 A7000000         - je 0022DEC1
0022DE1A - BE 02000000           - mov esi,00000002 { 2 }
0022DE1F - 89 74 24 1C           - mov [esp+1C],esi
0022DE23 - 89 35 68A28300        - mov [0083A268],esi { [00000000] }
0022DE29 - 83 F8 01              - cmp eax,01 { 1 }
0022DE2C - 0F85 A3000000         - jne 0022DED5
0022DE32 - 83 3D C07E5500 00     - cmp dword ptr [00557EC0],00 { 0 }
0022DE39 - 8B 2D 506D5500        - mov ebp,[00556D50] { [00000028] }
0022DE3F - 75 2D                 - jne 0022DE6E
0022DE41 - 8B C7                 - mov eax,edi
0022DE43 - 8D 8D 50855100        - lea ecx,[ebp+00518550]
0022DE49 - C1 E0 0A              - shl eax,0A { 10 }
0022DE4C - 03 C8                 - add ecx,eax
0022DE4E - 66 A1 58704400        - mov ax,[00447058] { [00004081] }
0022DE54 - 83 C5 02              - add ebp,02 { 2 }
0022DE57 - 89 2D 506D5500        - mov [00556D50],ebp { [00000028] }
0022DE5D - 66 89 01              - mov [ecx],ax
0022DE60 - A0 5A704400           - mov al,[0044705A] { [0] }
0022DE65 - 88 41 02              - mov [ecx+02],al
0022DE68 - 8B 0D 5CA28300        - mov ecx,[0083A25C] { [00000000] }
...
*/
// Skip text between "," and "�, and remove [n]
// ex:【夏偾,S005_B_0002】「バーッ�ク
static void HorkEyeFilter(TextBuffer *buffer, HookParam *)
{
  char *str = reinterpret_cast<char *>(buffer->data),
       *start,
       *stop;

  // Remove text between , and ]
  // FIXME: This does not work well because of the ascii encoding
  if ((start = (char *)::memchr(str, ',', buffer->size)) &&
      (stop = cpp_strnstr(start, "\x81\x7a", buffer->size - (start - str))) &&
      (buffer->size -= stop - start)) // = u'�.encode('sjis')
    ::memmove(start, stop, buffer->size - (start - str));

  // Remove [n]
  enum
  {
    skip_len = 3
  }; // = length of "[n]"
  while (buffer->size >= skip_len &&
         (start = cpp_strnstr(str, "[n]", buffer->size)) &&
         (buffer->size -= skip_len))
    ::memmove(start, start + skip_len, buffer->size - (start - str));
}
namespace
{
  template <typename strT>
  strT ltrim(strT text)
  {
    strT lastText = nullptr;
    while (*text && text != lastText)
    {
      lastText = text;
      if (text[0] == 0x20)
        text++;
      if ((UINT8)text[0] == 0x81 && (UINT8)text[1] == 0x40) // skip space \u3000 (0x8140 in sjis)
        text += 2;
      if (text[0] == '\\')
      {
        text++;
        while (::islower(text[0]) || text[0] == '@')
          text++;
      }
    }
    while ((signed char)text[0] > 0 && text[0] != '[') // skip all leading ascii characters except "[" needed for ruby
      text++;
    return text;
  }
  template <int offset = 1>
  void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto str = (LPSTR)(s->stack[offset]); // stack-2:eax
    int len = strlen(str);                // s->ecx;
    char *stop;
    if ((stop = cpp_strnstr(str, "\x81\x7a", len)) &&
        (len -= (stop - str + 2)))
    {
      str = stop + 2;
    } // = u'�.encode('sjis')
    auto old = std::string(str, len);
    buffer->from(old);
  }
  template <int offset = 1>
  void hookafter(hook_context *s, TextBuffer buffer, HookParam *)
  {

    auto newData = buffer.strA();
    auto str = (LPSTR)(s->stack[offset]); // stack-2:eax
    int len = strlen(str);                // s->ecx;
    int lensave = len;
    char *stop;
    if ((stop = cpp_strnstr(str, "\x81\x7a", len)) &&
        (len -= (stop - str + 2)))
    {
      auto old = std::string(str, stop + 2 - str);
      newData = old + newData;
    }
    for (int i = 0; i < lensave - newData.size(); i++)
      newData.push_back(' ');
    memcpy((void *)str, newData.c_str(), lensave);
    //   s->ecx=newData.size(); 修改ecx没用
  }
}
bool InsertHorkEyeHook()
{
  const BYTE bytes[] = {
      0x89, 0x6c, 0x24, 0x24, // 013cdb01   896c24 24        mov dword ptr ss:[esp+0x24],ebp
      0x89, 0x74, 0x24, 0x0c, // 013cdb05   897424 0c        mov dword ptr ss:[esp+0xc],esi
      0x89, 0x4c, 0x24, 0x18, // 013cdb09   894c24 18        mov dword ptr ss:[esp+0x18],ecx
      0x8a, 0x0c, 0x1a        // 013cdb0d   8a0c1a           mov cl,byte ptr ds:[edx+ebx]        jichi: here
  };
  enum
  {
    addr_offset = sizeof(bytes) - 3
  }; // 8a0c1a
  ;
  if (ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress))
  {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.offset = regoffset(ebx);
    hp.type = USING_STRING | NO_CONTEXT | FIXING_SPLIT | EMBED_ABLE | EMBED_DYNA_SJIS;
    hp.text_fun = hookBefore<-4 - 1>;
    hp.embed_fun = hookafter<-4 - 1>;
    hp.filter_fun = HorkEyeFilter;
    hp.lineSeparator = L"[n]";

    return NewHook(hp, "HorkEye");
  }

  memcpy(spDefault.pattern, Array<BYTE>{0xcc, 0xcc, 0xcc, XX, 0xec}, spDefault.length = 5);
  spDefault.offset = 3;

  const BYTE bytes2[] =
      {
          0x83, 0xec, XX,  // sub esp,??
          0xa1, XX4,       // mov eax,??
          0x8b, 0x0d, XX4, // mov ecx,??
          0x03, 0xc0       // add eax,eax
      };

  for (auto addr : MemDbg::findBytesAll(bytes2, sizeof(bytes2), processStartAddress, processStopAddress))
  {
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING | EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT;
    hp.text_fun = hookBefore<1>;
    hp.embed_fun = hookafter<1>;

    return NewHook(hp, "HorkEye2");
  }

  return false;
}

bool InsertHorkEye3Hook()
{
  const BYTE bytes2[] =
      {
          0x55,
          0x8d, 0xac, 0x24, XX4,
          0x81, 0xec, XX4,
          0x6a, 0xff,
          0x68, XX4,
          0x64, 0xa1, 0x00, 0x00, 0x00, 0x00,
          0x50,
          0x83, 0xec, 0x38, // 必须是0x38，不能是XX，否则有重的。

          //.text:0042E7F0 55                            push    ebp
          //.text : 0042E7F1 8D AC 24 24 FF FF FF          lea     ebp,[esp - 0DCh]
          //.text : 0042E7F8 81 EC DC 00 00 00             sub     esp, 0DCh
          //.text : 0042E7FE 6A FF                         push    0FFFFFFFFh
          //.text : 0042E800 68 51 1E 5C 00                push    offset SEH_42E7F0
          //.text : 0042E805 64 A1 00 00 00 00             mov     eax, large fs : 0
          //.text : 0042E80B 50                            push    eax
          //.text : 0042E80C 83 EC 38                      sub     esp, 38h
          //.text : 0042E80F A1 24 D0 64 00                mov     eax, ___security_cookie
          //.text : 0042E814 33 C5 xor eax, ebp
          //.text : 0042E816 89 85 D8 00 00 00             mov[ebp + 0DCh + var_4], eax
      };

  auto addr = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING | EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT;
  hp.text_fun = hookBefore<1>;
  hp.embed_fun = hookafter<1>;

  return NewHook(hp, "HorkEye3");
}

bool InsertHorkEye4Hook()
{
  // 辻堂さんのバージンロード
  // 辻堂さんの純愛ロード
  const BYTE bytes2[] =
      {
          0xf7, 0xd8,
          0x1b, 0xc0,
          0x83, 0xc0, 0x02};
  auto addr = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  const BYTE bytebetter[] = {
      0x8b, XX, XX, XX,
      0xa1, XX4,
      0x83, 0xc4, XX,
      0x8b, XX};
  auto addr1 = MemDbg::findBytes(bytebetter, sizeof(bytebetter), addr - 0x100, addr);
  if (addr1)
    addr = addr1;
  else
    addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(eax);
  hp.type = USING_STRING | NO_CONTEXT | EMBED_ABLE | EMBED_DYNA_SJIS;
  hp.text_fun = hookBefore<-1 - 1>;
  hp.embed_fun = hookafter<-1 - 1>;

  return NewHook(hp, "HorkEye4");
}

bool InsertHorkEye6Hook()
{
  // みなとカーニバルFD

  const BYTE bytes2[] =
      {
          0x83, 0xc2, 0x6c,
          0x52,
          0xe8};
  auto addr = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  ConsoleOutput("hk6 %p", addr);
  const BYTE start[] = {0x6A, 0xFF};
  addr = reverseFindBytes(start, sizeof(start), addr - 0x1000, addr);
  if (!addr)
    return false;
  ConsoleOutput("hk6 %p", addr);
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(3);
  hp.type = CODEC_ANSI_BE;
  ConsoleOutput("INSERT HorkEye6 %p", addr);

  return NewHook(hp, "HorkEye6");
}

bool HorkEye::attach_function()
{
  bool b1 = InsertHorkEyeHook();
  bool b2 = InsertHorkEye3Hook();
  bool b3 = InsertHorkEye4Hook();
  bool b4 = InsertHorkEye6Hook();
  return b1 || b2 || b3 || b4;
}