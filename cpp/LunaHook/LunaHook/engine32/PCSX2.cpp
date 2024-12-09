#include"PCSX2.h"

#include"ppsspp/psputils.hpp"
/** 7/19/2014 jichi
 *  Tested game: Fate/stay night [Realta Nua]
 *
 *  Fixed memory address.
 *  Text is incrementally increased.
 *
 *  Debug method: Debug next text location at \0.
 *  There are three locations that are OK to hook.
 *  The first one is used.
 *
 *  Runtime stack:
 *  0dc1f7e0   055be7c0
 *  0dc1f7e4   023105b0  pcsx2.023105b0
 *  0dc1f7e8   0dc1f804
 *  0dc1f7ec   023a406b  pcsx2.023a406b
 *  0dc1f7f0   00000000
 *  0dc1f7f4   000027e5
 *
 *  305a5424   2b05 809e9500    sub eax,dword ptr ds:[0x959e80]
 *  305a542a   0f88 05000000    js 305a5435
 *  305a5430  -e9 cbebdfd1      jmp pcsx2.023a4000
 *  305a5435   8b0d 20ac9600    mov ecx,dword ptr ds:[0x96ac20]
 *  305a543b   89c8             mov eax,ecx
 *  305a543d   c1e8 0c          shr eax,0xc
 *  305a5440   8b0485 30009e12  mov eax,dword ptr ds:[eax*4+0x129e0030]
 *  305a5447   bb 57545a30      mov ebx,0x305a5457
 *  305a544c   01c1             add ecx,eax
 *  305a544e  -0f88 ecbcd7d1    js pcsx2.02321140
 *  305a5454   0fbe01           movsx eax,byte ptr ds:[ecx] ; jichi: hook here
 *  305a5457   99               cdq
 *  305a5458   a3 f0ab9600      mov dword ptr ds:[0x96abf0],eax
 *  305a545d   8915 f4ab9600    mov dword ptr ds:[0x96abf4],edx
 *  305a5463   a1 40ac9600      mov eax,dword ptr ds:[0x96ac40]
 *  305a5468   3b05 f0ab9600    cmp eax,dword ptr ds:[0x96abf0]
 *  305a546e   75 11            jnz short 305a5481
 *  305a5470   a1 44ac9600      mov eax,dword ptr ds:[0x96ac44]
 *  305a5475   3b05 f4ab9600    cmp eax,dword ptr ds:[0x96abf4]
 *  305a547b   0f84 3a000000    je 305a54bb
 *  305a5481   8305 00ac9600 24 add dword ptr ds:[0x96ac00],0x24
 *  305a5488   9f               lahf
 *  305a5489   66:c1f8 0f       sar ax,0xf
 *  305a548d   98               cwde
 *  305a548e   a3 04ac9600      mov dword ptr ds:[0x96ac04],eax
 *  305a5493   c705 a8ad9600 6c>mov dword ptr ds:[0x96ada8],0x10e26c
 *  305a549d   a1 c0ae9600      mov eax,dword ptr ds:[0x96aec0]
 *  305a54a2   83c0 04          add eax,0x4
 *
 *  3038c78e  -0f88 ac4af9d1    js pcsx2.02321240
 *  3038c794   8911             mov dword ptr ds:[ecx],edx
 *  3038c796   8b0d 60ab9600    mov ecx,dword ptr ds:[0x96ab60]
 *  3038c79c   89c8             mov eax,ecx
 *  3038c79e   c1e8 0c          shr eax,0xc
 *  3038c7a1   8b0485 30009e12  mov eax,dword ptr ds:[eax*4+0x129e0030]
 *  3038c7a8   bb b8c73830      mov ebx,0x3038c7b8
 *  3038c7ad   01c1             add ecx,eax
 *  3038c7af  -0f88 8b49f9d1    js pcsx2.02321140
 *  3038c7b5   0fbe01           movsx eax,byte ptr ds:[ecx] ; jichi: or hook here
 *  3038c7b8   99               cdq
 *  3038c7b9   a3 e0ab9600      mov dword ptr ds:[0x96abe0],eax
 *  3038c7be   8915 e4ab9600    mov dword ptr ds:[0x96abe4],edx
 *  3038c7c4   c705 20ab9600 00>mov dword ptr ds:[0x96ab20],0x0
 *  3038c7ce   c705 24ab9600 00>mov dword ptr ds:[0x96ab24],0x0
 *  3038c7d8   c705 f0ab9600 25>mov dword ptr ds:[0x96abf0],0x25
 *  3038c7e2   c705 f4ab9600 00>mov dword ptr ds:[0x96abf4],0x0
 *  3038c7ec   833d e0ab9600 25 cmp dword ptr ds:[0x96abe0],0x25
 *  3038c7f3   75 0d            jnz short 3038c802
 *  3038c7f5   833d e4ab9600 00 cmp dword ptr ds:[0x96abe4],0x0
 *  3038c7fc   0f84 34000000    je 3038c836
 *  3038c802   31c0             xor eax,eax
 *
 *  304e1a0a   8b0d 40ab9600    mov ecx,dword ptr ds:[0x96ab40]
 *  304e1a10   89c8             mov eax,ecx
 *  304e1a12   c1e8 0c          shr eax,0xc
 *  304e1a15   8b0485 30009e12  mov eax,dword ptr ds:[eax*4+0x129e0030]
 *  304e1a1c   bb 2c1a4e30      mov ebx,0x304e1a2c
 *  304e1a21   01c1             add ecx,eax
 *  304e1a23  -0f88 17f7e3d1    js pcsx2.02321140
 *  304e1a29   0fbe01           movsx eax,byte ptr ds:[ecx] ; jichi: or hook here
 *  304e1a2c   99               cdq
 *  304e1a2d   a3 f0ab9600      mov dword ptr ds:[0x96abf0],eax
 *  304e1a32   8915 f4ab9600    mov dword ptr ds:[0x96abf4],edx
 *  304e1a38   a1 f0ab9600      mov eax,dword ptr ds:[0x96abf0]
 *  304e1a3d   3b05 d0ab9600    cmp eax,dword ptr ds:[0x96abd0]
 *  304e1a43   75 11            jnz short 304e1a56
 *  304e1a45   a1 f4ab9600      mov eax,dword ptr ds:[0x96abf4]
 *  304e1a4a   3b05 d4ab9600    cmp eax,dword ptr ds:[0x96abd4]
 *  304e1a50   0f84 3c000000    je 304e1a92
 *  304e1a56   a1 f0ab9600      mov eax,dword ptr ds:[0x96abf0]
 *  304e1a5b   83c0 d0          add eax,-0x30
 *  304e1a5e   99               cdq
 */
namespace { // unnamed
bool _typemoongarbage_ch(char c)
{
  return c == '%' || c == '.' || c == ' ' || c == ','
      || c >= '0' && c <= '9'
      || c >= 'A' && c <= 'z'; // also ignore ASCII 91-96: [ \ ] ^ _ `
}

// Trim leading garbage
LPCSTR _typemoonltrim(LPCSTR p)
{
  enum { MAX_LENGTH = VNR_TEXT_CAPACITY };
  if (p && p[0] == '%')
    for (int count = 0; *p && count < MAX_LENGTH; count++, p++)
      if (!_typemoongarbage_ch(*p))
        return p;
  return nullptr;
}

// Remove trailing garbage such as %n
size_t _typemoonstrlen(LPCSTR text)
{
  size_t len = ::strlen(text);
  size_t ret = len;
  while (len && _typemoongarbage_ch(text[len - 1])) {
    len--;
    if (text[len] == '%')
      ret = len;
  }
  return ret;
}

} // unnamed namespace

// Use last text size to determine
static void SpecialPS2HookTypeMoon(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  static LPCSTR lasttext; // this value should be the same for the same game
  static size_t lastsize;

  LPCSTR cur = LPCSTR(context->ecx);
  if (!*cur)
    return;

  LPCSTR text = reverse_search_begin(cur);
  if (!text)
    return;
  //text = _typemoonltrim(text);
  if (lasttext != text) {
    lasttext = text;
    lastsize = 0; // reset last size
  }

  size_t size = ::strlen(text);
  if (size == lastsize)
    return;
  if (size > lastsize) // incremental
    text += lastsize;
  lastsize = size;

  text = _typemoonltrim(text);
  size = _typemoonstrlen(text);
  //size = ::strlen(text);
 
  buffer->from(text, size);
  *split = FIXED_SPLIT_VALUE << 2; // merge all threads
  //*split = *(DWORD *)(esp_base + 4); // use [esp+4] as split
  //*split = regof(eax, esp_base);
  //*split = regof(esi, esp_base);
}

bool InsertTypeMoonPS2Hook()
{
  ConsoleOutput("TypeMoon PS2: enter");
  const BYTE bytes[] =  {
    0x2b,0x05, XX4,       // 305a5424   2b05 809e9500    sub eax,dword ptr ds:[0x959e80]
    0x0f,0x88, 0x05,0x00,0x00,0x00, // 305a542a   0f88 05000000    js 305a5435
    0xe9, XX4,            // 305a5430  -e9 cbebdfd1      jmp pcsx2.023a4000
    0x8b,0x0d, XX4,       // 305a5435   8b0d 20ac9600    mov ecx,dword ptr ds:[0x96ac20]
    0x89,0xc8,            // 305a543b   89c8             mov eax,ecx
    0xc1,0xe8, 0x0c,      // 305a543d   c1e8 0c          shr eax,0xc
    0x8b,0x04,0x85, XX4,  // 305a5440   8b0485 30009e12  mov eax,dword ptr ds:[eax*4+0x129e0030]
    0xbb, XX4,            // 305a5447   bb 57545a30      mov ebx,0x305a5457
    0x01,0xc1,            // 305a544c   01c1             add ecx,eax
    // Following pattern is not sufficient
    0x0f,0x88, XX4,       // 305a544e  -0f88 ecbcd7d1    js pcsx2.02321140
    0x0f,0xbe,0x01,       // 305a5454   0fbe01           movsx eax,byte ptr ds:[ecx] ; jichi: hook here
    0x99,                 // 305a5457   99               cdq
    0xa3, XX4,            // 305a5458   a3 f0ab9600      mov dword ptr ds:[0x96abf0],eax
    0x89,0x15, XX4,       // 305a545d   8915 f4ab9600    mov dword ptr ds:[0x96abf4],edx
    0xa1, XX4,            // 305a5463   a1 40ac9600      mov eax,dword ptr ds:[0x96ac40]
    0x3b,0x05, XX4,       // 305a5468   3b05 f0ab9600    cmp eax,dword ptr ds:[0x96abf0]
    0x75, 0x11,           // 305a546e   75 11            jnz short 305a5481
    0xa1, XX4,            // 305a5470   a1 44ac9600      mov eax,dword ptr ds:[0x96ac44]
    0x3b,0x05, XX4,       // 305a5475   3b05 f4ab9600    cmp eax,dword ptr ds:[0x96abf4]
    0x0f,0x84, XX4,       // 305a547b   0f84 3a000000    je 305a54bb
    0x83,0x05, XX4, 0x24, // 305a5481   8305 00ac9600 24 add dword ptr ds:[0x96ac00],0x24
    0x9f,                 // 305a5488   9f               lahf
    0x66,0xc1,0xf8, 0x0f, // 305a5489   66:c1f8 0f       sar ax,0xf
    0x98                  // 305a548d   98               cwde
  };
  enum { addr_offset = 0x305a5454 - 0x305a5424 };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPS2Memory(bytes, sizeof(bytes));
  //addr = 0x30403967;
  if (!addr)
    ConsoleOutput("TypeMoon PS2: pattern not found");
  else {
    //GROWL_DWORD(addr + addr_offset);
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.type = USING_STRING|NO_CONTEXT; // no context to get rid of return address
    hp.text_fun = SpecialPS2HookTypeMoon;
    ConsoleOutput("TypeMoon PS2: INSERT");
    //GROWL_DWORD(hp.address);
    succ|=NewHook(hp, "TypeMoon PS2");
  }

  ConsoleOutput("TypeMoon PS2: leave");
  return succ;
}

/** 8/3/2014 jichi
 *  Tested game: School Rumble ねる娘�育つ
 *
 *  Fixed memory address.
 *  There is only one matched address.
 *
 *  Debug method: Predict text location.
 *  There are a couple of locations that are OK to hook.
 *  The last one is used.
 *
 *  Issue: the order of chara and scenario is reversed: 「scenario」chara
 *
 *  eax 20000000
 *  ecx 202d5ab3
 *  edx 00000000
 *  ebx 3026e299
 *  esp 0c14f910
 *  ebp 0c14f918
 *  esi 0014f470
 *  edi 00000000
 *  eip 3026e296
 *
 *  3026e1d5  -0f88 a530d7d2    js pcsx2.02fe1280
 *  3026e1db   0f1202           movlps xmm0,qword ptr ds:[edx]
 *  3026e1de   0f1301           movlps qword ptr ds:[ecx],xmm0
 *  3026e1e1   ba 10ac6201      mov edx,0x162ac10
 *  3026e1e6   8b0d d0ac6201    mov ecx,dword ptr ds:[0x162acd0]         ; pcsx2.01ffed00
 *  3026e1ec   83c1 10          add ecx,0x10
 *  3026e1ef   83e1 f0          and ecx,0xfffffff0
 *  3026e1f2   89c8             mov eax,ecx
 *  3026e1f4   c1e8 0c          shr eax,0xc
 *  3026e1f7   8b0485 30006d0d  mov eax,dword ptr ds:[eax*4+0xd6d0030]
 *  3026e1fe   bb 11e22630      mov ebx,0x3026e211
 *  3026e203   01c1             add ecx,eax
 *  3026e205  -0f88 b530d7d2    js pcsx2.02fe12c0
 *  3026e20b   0f280a           movaps xmm1,dqword ptr ds:[edx]
 *  3026e20e   0f2909           movaps dqword ptr ds:[ecx],xmm1
 *  3026e211   ba 00ac6201      mov edx,0x162ac00
 *  3026e216   8b0d d0ac6201    mov ecx,dword ptr ds:[0x162acd0]         ; pcsx2.01ffed00
 *  3026e21c   83e1 f0          and ecx,0xfffffff0
 *  3026e21f   89c8             mov eax,ecx
 *  3026e221   c1e8 0c          shr eax,0xc
 *  3026e224   8b0485 30006d0d  mov eax,dword ptr ds:[eax*4+0xd6d0030]
 *  3026e22b   bb 3ee22630      mov ebx,0x3026e23e
 *  3026e230   01c1             add ecx,eax
 *  3026e232  -0f88 8830d7d2    js pcsx2.02fe12c0
 *  3026e238   0f2812           movaps xmm2,dqword ptr ds:[edx]
 *  3026e23b   0f2911           movaps dqword ptr ds:[ecx],xmm2
 *  3026e23e   31c0             xor eax,eax
 *  3026e240   a3 f4ac6201      mov dword ptr ds:[0x162acf4],eax
 *  3026e245   c705 f0ac6201 d4>mov dword ptr ds:[0x162acf0],0x1498d4
 *  3026e24f   c705 a8ad6201 c0>mov dword ptr ds:[0x162ada8],0x1281c0
 *  3026e259   a1 c0ae6201      mov eax,dword ptr ds:[0x162aec0]
 *  3026e25e   83c0 07          add eax,0x7
 *  3026e261   a3 c0ae6201      mov dword ptr ds:[0x162aec0],eax
 *  3026e266   2b05 809e6101    sub eax,dword ptr ds:[0x1619e80]
 *  3026e26c   0f88 05000000    js 3026e277
 *  3026e272  -e9 895ddfd2      jmp pcsx2.03064000
 *  3026e277   8b0d 40ab6201    mov ecx,dword ptr ds:[0x162ab40]
 *  3026e27d   89c8             mov eax,ecx
 *  3026e27f   c1e8 0c          shr eax,0xc
 *  3026e282   8b0485 30006d0d  mov eax,dword ptr ds:[eax*4+0xd6d0030]
 *  3026e289   bb 99e22630      mov ebx,0x3026e299
 *  3026e28e   01c1             add ecx,eax
 *  3026e290  -0f88 6a2dd7d2    js pcsx2.02fe1000
 *  3026e296   0fb601           movzx eax,byte ptr ds:[ecx] ; jichi: hook here
 *  3026e299   a3 60ab6201      mov dword ptr ds:[0x162ab60],eax
 *  3026e29e   c705 64ab6201 00>mov dword ptr ds:[0x162ab64],0x0
 *  3026e2a8   a1 60ab6201      mov eax,dword ptr ds:[0x162ab60]
 *  3026e2ad   05 7fffffff      add eax,-0x81
 *  3026e2b2   99               cdq
 *  3026e2b3   a3 70ab6201      mov dword ptr ds:[0x162ab70],eax
 *  3026e2b8   8915 74ab6201    mov dword ptr ds:[0x162ab74],edx
 *  3026e2be   b8 01000000      mov eax,0x1
 *  3026e2c3   833d 74ab6201 00 cmp dword ptr ds:[0x162ab74],0x0
 *  3026e2ca   72 0d            jb short 3026e2d9
 *  3026e2cc   77 09            ja short 3026e2d7
 *  3026e2ce   833d 70ab6201 18 cmp dword ptr ds:[0x162ab70],0x18
 *  3026e2d5   72 02            jb short 3026e2d9
 *  3026e2d7   31c0             xor eax,eax
 *  3026e2d9   a3 10ab6201      mov dword ptr ds:[0x162ab10],eax
 *  3026e2de   c705 14ab6201 00>mov dword ptr ds:[0x162ab14],0x0
 *  3026e2e8   c705 20ab6201 00>mov dword ptr ds:[0x162ab20],0x0
 *  3026e2f2   c705 24ab6201 00>mov dword ptr ds:[0x162ab24],0x0
 *  3026e2fc   c705 30ab6201 00>mov dword ptr ds:[0x162ab30],0x0
 *  3026e306   c705 34ab6201 00>mov dword ptr ds:[0x162ab34],0x0
 *  3026e310   833d 10ab6201 00 cmp dword ptr ds:[0x162ab10],0x0
 *  3026e317   0f85 41000000    jnz 3026e35e
 *  3026e31d   833d 14ab6201 00 cmp dword ptr ds:[0x162ab14],0x0
 *  3026e324   0f85 34000000    jnz 3026e35e
 *  3026e32a   31c0             xor eax,eax
 *  3026e32c   a3 50ab6201      mov dword ptr ds:[0x162ab50],eax
 *  3026e331   a3 54ab6201      mov dword ptr ds:[0x162ab54],eax
 *  3026e336   c705 a8ad6201 c0>mov dword ptr ds:[0x162ada8],0x1285c0
 *  3026e340   a1 c0ae6201      mov eax,dword ptr ds:[0x162aec0]
 *  3026e345   83c0 08          add eax,0x8
 *  3026e348   a3 c0ae6201      mov dword ptr ds:[0x162aec0],eax
 *  3026e34d   2b05 809e6101    sub eax,dword ptr ds:[0x1619e80]
 *  3026e353   0f88 96280000    js 30270bef
 *  3026e359  -e9 a25cdfd2      jmp pcsx2.03064000
 *  3026e35e   31c0             xor eax,eax
 *  3026e360   a3 50ab6201      mov dword ptr ds:[0x162ab50],eax
 *  3026e365   a3 54ab6201      mov dword ptr ds:[0x162ab54],eax
 *  3026e36a   c705 a8ad6201 dc>mov dword ptr ds:[0x162ada8],0x1281dc
 *  3026e374   a1 c0ae6201      mov eax,dword ptr ds:[0x162aec0]
 *  3026e379   83c0 08          add eax,0x8
 *  3026e37c   a3 c0ae6201      mov dword ptr ds:[0x162aec0],eax
 *  3026e381   2b05 809e6101    sub eax,dword ptr ds:[0x1619e80]
 *  3026e387   0f88 a61f0000    js 30270333
 *  3026e38d  -e9 6e5cdfd2      jmp pcsx2.03064000
 *  3026e392   b8 01000000      mov eax,0x1
 *  3026e397   833d 64ab6201 00 cmp dword ptr ds:[0x162ab64],0x0
 *  3026e39e   7c 10            jl short 3026e3b0
 *  3026e3a0   7f 0c            jg short 3026e3ae
 *  3026e3a2   813d 60ab6201 80>cmp dword ptr ds:[0x162ab60],0x80
 *  3026e3ac   72 02            jb short 3026e3b0
 *  3026e3ae   31c0             xor eax,eax
 *  3026e3b0   a3 10ab6201      mov dword ptr ds:[0x162ab10],eax
 *  3026e3b5   c705 14ab6201 00>mov dword ptr ds:[0x162ab14],0x0
 *  3026e3bf   31c0             xor eax,eax
 *  3026e3c1   a3 54ab6201      mov dword ptr ds:[0x162ab54],eax
 *  3026e3c6   c705 50ab6201 01>mov dword ptr ds:[0x162ab50],0x1
 *  3026e3d0   c705 a8ad6201 e8>mov dword ptr ds:[0x162ada8],0x1285e8
 *  3026e3da   a1 c0ae6201      mov eax,dword ptr ds:[0x162aec0]
 *  3026e3df   83c0 03          add eax,0x3
 *  3026e3e2   a3 c0ae6201      mov dword ptr ds:[0x162aec0],eax
 *  3026e3e7   2b05 809e6101    sub eax,dword ptr ds:[0x1619e80]
 *  3026e3ed   0f88 05000000    js 3026e3f8
 *  3026e3f3  -e9 085cdfd2      jmp pcsx2.03064000
 *  3026e3f8   833d 10ab6201 00 cmp dword ptr ds:[0x162ab10],0x0
 *  3026e3ff   0f85 49000000    jnz 3026e44e
 *  3026e405   833d 14ab6201 00 cmp dword ptr ds:[0x162ab14],0x0
 *  3026e40c   0f85 3c000000    jnz 3026e44e
 *  3026e412   a1 60ab6201      mov eax,dword ptr ds:[0x162ab60]
 *  3026e417   c1e0 03          shl eax,0x3
 *  3026e41a   99               cdq
 *  3026e41b   a3 30ab6201      mov dword ptr ds:[0x162ab30],eax
 *  3026e420   8915 34ab6201    mov dword ptr ds:[0x162ab34],edx
 *  3026e426   c705 a8ad6201 04>mov dword ptr ds:[0x162ada8],0x128604
 *  3026e430   a1 c0ae6201      mov eax,dword ptr ds:[0x162aec0]
 *  3026e435   83c0 02          add eax,0x2
 *  3026e438   a3 c0ae6201      mov dword ptr ds:[0x162aec0],eax
 *  3026e43d   2b05 809e6101    sub eax,dword ptr ds:[0x1619e80]
 *  3026e443   0f88 93220000    js 302706dc
 *  3026e449  -e9 b25bdfd2      jmp pcsx2.03064000
 *  3026e44e   a1 60ab6201      mov eax,dword ptr ds:[0x162ab60]
 *  3026e453   c1e0 03          shl eax,0x3
 *  3026e456   99               cdq
 *  3026e457   a3 30ab6201      mov dword ptr ds:[0x162ab30],eax
 *  3026e45c   8915 34ab6201    mov dword ptr ds:[0x162ab34],edx
 *  3026e462   c705 a8ad6201 f0>mov dword ptr ds:[0x162ada8],0x1285f0
 *  3026e46c   a1 c0ae6201      mov eax,dword ptr ds:[0x162aec0]
 *  3026e471   83c0 02          add eax,0x2
 *  3026e474   a3 c0ae6201      mov dword ptr ds:[0x162aec0],eax
 *  3026e479   2b05 809e6101    sub eax,dword ptr ds:[0x1619e80]
 *  3026e47f   0f88 91270000    js 30270c16
 *  3026e485  -e9 765bdfd2      jmp pcsx2.03064000
 *  3026e48a   a1 30ab6201      mov eax,dword ptr ds:[0x162ab30]
 *  3026e48f   0305 60ab6201    add eax,dword ptr ds:[0x162ab60]
 *  3026e495   99               cdq
 *  3026e496   a3 30ab6201      mov dword ptr ds:[0x162ab30],eax
 *  3026e49b   8915 34ab6201    mov dword ptr ds:[0x162ab34],edx
 *  3026e4a1   a1 30ab6201      mov eax,dword ptr ds:[0x162ab30]
 *  3026e4a6   c1e0 05          shl eax,0x5
 *  3026e4a9   99               cdq
 *  3026e4aa   a3 30ab6201      mov dword ptr ds:[0x162ab30],eax
 *  3026e4af   8915 34ab6201    mov dword ptr ds:[0x162ab34],edx
 *  3026e4b5   a1 30ab6201      mov eax,dword ptr ds:[0x162ab30]
 *  3026e4ba   05 e01f2b00      add eax,0x2b1fe0
 *  3026e4bf   99               cdq
 *  3026e4c0   a3 20ab6201      mov dword ptr ds:[0x162ab20],eax
 *  3026e4c5   8915 24ab6201    mov dword ptr ds:[0x162ab24],edx
 *  3026e4cb   8b35 f0ac6201    mov esi,dword ptr ds:[0x162acf0]
 *  3026e4d1   8935 a8ad6201    mov dword ptr ds:[0x162ada8],esi
 *  3026e4d7   a1 c0ae6201      mov eax,dword ptr ds:[0x162aec0]
 *  3026e4dc   83c0 07          add eax,0x7
 *  3026e4df   a3 c0ae6201      mov dword ptr ds:[0x162aec0],eax
 *  3026e4e4   2b05 809e6101    sub eax,dword ptr ds:[0x1619e80]
 *  3026e4ea  -0f88 155bdfd2    js pcsx2.03064005
 *  3026e4f0  -e9 0b5bdfd2      jmp pcsx2.03064000
 *  3026e4f5   a1 20ab6201      mov eax,dword ptr ds:[0x162ab20]
 *  3026e4fa   8b15 24ab6201    mov edx,dword ptr ds:[0x162ab24]
 *  3026e500   a3 00ac6201      mov dword ptr ds:[0x162ac00],eax
 *  3026e505   8915 04ac6201    mov dword ptr ds:[0x162ac04],edx
 *  3026e50b   833d 00ac6201 00 cmp dword ptr ds:[0x162ac00],0x0
 *  3026e512   75 0d            jnz short 3026e521
 *  3026e514   833d 04ac6201 00 cmp dword ptr ds:[0x162ac04],0x0
 *  3026e51b   0f84 39000000    je 3026e55a
 *  3026e521   31c0             xor eax,eax
 */
// Use fixed split for this hook
static void SpecialPS2HookMarvelous(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  DWORD text = context->ecx;
  if (BYTE c = *(BYTE *)text) { // BYTE is unsigned 
    buffer->from(text,::LeadByteTable[c]);
    *split = FIXED_SPLIT_VALUE * 3; // merge all threads
    //*split = regof(esi, esp_base);
    //*split = *(DWORD *)(esp_base + 4*5); // esp[5]
  }
}

bool InsertMarvelousPS2Hook()
{
  ConsoleOutput("Marvelous PS2: enter");
  const BYTE bytes[] =  {
    0x2b,0x05, XX4,                     // 3026e266   2b05 809e6101    sub eax,dword ptr ds:[0x1619e80]
    0x0f,0x88, 0x05,0x00,0x00,0x00,     // 3026e26c   0f88 05000000    js 3026e277
    0xe9, XX4,                          // 3026e272  -e9 895ddfd2      jmp pcsx2.03064000
    0x8b,0x0d, XX4,                     // 3026e277   8b0d 40ab6201    mov ecx,dword ptr ds:[0x162ab40]
    0x89,0xc8,                          // 3026e27d   89c8             mov eax,ecx
    0xc1,0xe8, 0x0c,                    // 3026e27f   c1e8 0c          shr eax,0xc
    0x8b,0x04,0x85, XX4,                // 3026e282   8b0485 30006d0d  mov eax,dword ptr ds:[eax*4+0xd6d0030]
    0xbb, XX4,                          // 3026e289   bb 99e22630      mov ebx,0x3026e299
    0x01,0xc1,                          // 3026e28e   01c1             add ecx,eax
    0x0f,0x88, XX4,                     // 3026e290  -0f88 6a2dd7d2    js pcsx2.02fe1000
    0x0f,0xb6,0x01,                     // 3026e296   0fb601           movzx eax,byte ptr ds:[ecx] ; jichi: hook here
    0xa3, XX4,                          // 3026e299   a3 60ab6201      mov dword ptr ds:[0x162ab60],eax
    0xc7,0x05, XX4, 0x00,0x00,0x00,0x00,// 3026e29e   c705 64ab6201 00>mov dword ptr ds:[0x162ab64],0x0
    0xa1, XX4,                          // 3026e2a8   a1 60ab6201      mov eax,dword ptr ds:[0x162ab60]
    0x05, 0x7f,0xff,0xff,0xff,          // 3026e2ad   05 7fffffff      add eax,-0x81
    0x99,                               // 3026e2b2   99               cdq
    0xa3 //70ab6201                     // 3026e2b3   a3 70ab6201      mov dword ptr ds:[0x162ab70],eax
  };
  enum { addr_offset = 0x3026e296 - 0x3026e266 };

  DWORD addr = SafeMatchBytesInPS2Memory(bytes, sizeof(bytes));
  //addr = 0x30403967;
  auto succ=false;
  if (!addr)
    ConsoleOutput("Marvelous PS2: pattern not found");
  else {
    //GROWL_DWORD(addr + addr_offset);
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.type = USING_STRING|NO_CONTEXT; // no context to get rid of return address
    hp.text_fun = SpecialPS2HookMarvelous;
    ConsoleOutput("Marvelous PS2: INSERT");
    //GROWL_DWORD(hp.address);
    succ|=NewHook(hp, "Marvelous PS2");
  }

  ConsoleOutput("Marvelous PS2: leave");
  return succ;
}

/** 8/3/2014 jichi
 *  Tested game: School Rumble 二学� *
 *  Fixed memory address.
 *  There is only one matched address.
 *
 *  Debug method: Breakpoint the memory address.
 *
 *  Issue: It cannot extract character name.
 *
 *  302072bd   a3 c0ae9e01      mov dword ptr ds:[0x19eaec0],eax
 *  302072c2   2b05 809e9d01    sub eax,dword ptr ds:[0x19d9e80]         ; cdvdgiga.5976f736
 *  302072c8  ^0f88 f3cafcff    js 301d3dc1
 *  302072ce  -e9 2dcd21d3      jmp pcsx2.03424000
 *  302072d3   8b0d 50ab9e01    mov ecx,dword ptr ds:[0x19eab50]
 *  302072d9   89c8             mov eax,ecx
 *  302072db   c1e8 0c          shr eax,0xc
 *  302072de   8b0485 3000e511  mov eax,dword ptr ds:[eax*4+0x11e50030]
 *  302072e5   bb f5722030      mov ebx,0x302072f5
 *  302072ea   01c1             add ecx,eax
 *  302072ec  -0f88 0e9d19d3    js pcsx2.033a1000
 *  302072f2   0fb601           movzx eax,byte ptr ds:[ecx]
 *  302072f5   a3 20ab9e01      mov dword ptr ds:[0x19eab20],eax
 *  302072fa   c705 24ab9e01 00>mov dword ptr ds:[0x19eab24],0x0
 *  30207304   8305 60ab9e01 ff add dword ptr ds:[0x19eab60],-0x1
 *  3020730b   9f               lahf
 *  3020730c   66:c1f8 0f       sar ax,0xf
 *  30207310   98               cwde
 *  30207311   a3 64ab9e01      mov dword ptr ds:[0x19eab64],eax
 *  30207316   8305 50ab9e01 01 add dword ptr ds:[0x19eab50],0x1
 *  3020731d   9f               lahf
 *  3020731e   66:c1f8 0f       sar ax,0xf
 *  30207322   98               cwde
 *  30207323   a3 54ab9e01      mov dword ptr ds:[0x19eab54],eax
 *  30207328   8b15 20ab9e01    mov edx,dword ptr ds:[0x19eab20]
 *  3020732e   8b0d 30ab9e01    mov ecx,dword ptr ds:[0x19eab30]
 *  30207334   89c8             mov eax,ecx
 *  30207336   c1e8 0c          shr eax,0xc
 *  30207339   8b0485 3000e511  mov eax,dword ptr ds:[eax*4+0x11e50030]
 *  30207340   bb 4f732030      mov ebx,0x3020734f
 *  30207345   01c1             add ecx,eax
 *  30207347  -0f88 739e19d3    js pcsx2.033a11c0
 *  3020734d   8811             mov byte ptr ds:[ecx],dl    ; jichi: hook here, text in dl
 *  3020734f   8305 30ab9e01 01 add dword ptr ds:[0x19eab30],0x1
 *  30207356   9f               lahf
 *  30207357   66:c1f8 0f       sar ax,0xf
 *  3020735b   98               cwde
 *  3020735c   a3 34ab9e01      mov dword ptr ds:[0x19eab34],eax
 *  30207361   a1 60ab9e01      mov eax,dword ptr ds:[0x19eab60]
 *  30207366   3b05 40ab9e01    cmp eax,dword ptr ds:[0x19eab40]
 *  3020736c   75 11            jnz short 3020737f
 *  3020736e   a1 64ab9e01      mov eax,dword ptr ds:[0x19eab64]
 *  30207373   3b05 44ab9e01    cmp eax,dword ptr ds:[0x19eab44]
 *  30207379   0f84 28000000    je 302073a7
 *  3020737f   c705 a8ad9e01 34>mov dword ptr ds:[0x19eada8],0x17eb34
 *  30207389   a1 c0ae9e01      mov eax,dword ptr ds:[0x19eaec0]
 *  3020738e   83c0 09          add eax,0x9
 *  30207391   a3 c0ae9e01      mov dword ptr ds:[0x19eaec0],eax
 *  30207396   2b05 809e9d01    sub eax,dword ptr ds:[0x19d9e80]         ; cdvdgiga.5976f736
 *  3020739c  ^0f88 31ffffff    js 302072d3
 *  302073a2  -e9 59cc21d3      jmp pcsx2.03424000
 *  302073a7   c705 a8ad9e01 50>mov dword ptr ds:[0x19eada8],0x17eb50
 *  302073b1   a1 c0ae9e01      mov eax,dword ptr ds:[0x19eaec0]
 *  302073b6   83c0 09          add eax,0x9
 *  302073b9   a3 c0ae9e01      mov dword ptr ds:[0x19eaec0],eax
 *  302073be   2b05 809e9d01    sub eax,dword ptr ds:[0x19d9e80]         ; cdvdgiga.5976f736
 *  302073c4  ^0f88 75cbfcff    js 301d3f3f
 *  302073ca  -e9 31cc21d3      jmp pcsx2.03424000
 *  302073cf   8b15 10ac9e01    mov edx,dword ptr ds:[0x19eac10]
 *  302073d5   8b0d 20ac9e01    mov ecx,dword ptr ds:[0x19eac20]
 *  302073db   83c1 04          add ecx,0x4
 *  302073de   89c8             mov eax,ecx
 *  302073e0   c1e8 0c          shr eax,0xc
 *  302073e3   8b0485 3000e511  mov eax,dword ptr ds:[eax*4+0x11e50030]
 *  302073ea   bb f9732030      mov ebx,0x302073f9
 *  302073ef   01c1             add ecx,eax
 *  302073f1  -0f88 499e19d3    js pcsx2.033a1240
 *  302073f7   8911             mov dword ptr ds:[ecx],edx
 *  302073f9   c705 a8ad9e01 5c>mov dword ptr ds:[0x19eada8],0x18d25c
 *  30207403   a1 c0ae9e01      mov eax,dword ptr ds:[0x19eaec0]
 *  30207408   83c0 03          add eax,0x3
 *  3020740b   a3 c0ae9e01      mov dword ptr ds:[0x19eaec0],eax
 *  30207410   2b05 809e9d01    sub eax,dword ptr ds:[0x19d9e80]         ; cdvdgiga.5976f736
 *  30207416   0f88 05000000    js 30207421
 *  3020741c  -e9 dfcb21d3      jmp pcsx2.03424000
 *  30207421   a1 50ac9e01      mov eax,dword ptr ds:[0x19eac50]
 *  30207426   05 00a2ffff      add eax,0xffffa200
 *  3020742b   99               cdq
 *  3020742c   a3 00ac9e01      mov dword ptr ds:[0x19eac00],eax
 *  30207431   8915 04ac9e01    mov dword ptr ds:[0x19eac04],edx
 *  30207437   31d2             xor edx,edx
 *  30207439   8b0d d0ac9e01    mov ecx,dword ptr ds:[0x19eacd0]
 *  3020743f   89c8             mov eax,ecx
 *  30207441   c1e8 0c          shr eax,0xc
 *  30207444   8b0485 3000e511  mov eax,dword ptr ds:[eax*4+0x11e50030]
 *  3020744b   bb 5a742030      mov ebx,0x3020745a
 *  30207450   01c1             add ecx,eax
 *  30207452  -0f88 e89d19d3    js pcsx2.033a1240
 *  30207458   8911             mov dword ptr ds:[ecx],edx
 *  3020745a   a1 00ac9e01      mov eax,dword ptr ds:[0x19eac00]
 *  3020745f   8b15 04ac9e01    mov edx,dword ptr ds:[0x19eac04]
 */
// Use fixed split for this hook
static void SpecialPS2HookMarvelous2(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  DWORD text = context->edx; // get text in dl: 3020734d   8811  mov byte ptr ds:[ecx],dl
  if (BYTE c = *(BYTE *)text) { // BYTE is unsigned
    
    //*split = FIXED_SPLIT_VALUE * 4; // merge all threads
    *split = context->esi;
    //*split = *(DWORD *)(esp_base + 4*5); // esp[5]
    buffer->from(text, 1);
  }
}

bool InsertMarvelous2PS2Hook()
{
  ConsoleOutput("Marvelous2 PS2: enter");
  const BYTE bytes[] =  {
    // The following pattern is not sufficient
    0x89,0xc8,            // 30207334   89c8             mov eax,ecx
    0xc1,0xe8, 0x0c,      // 30207336   c1e8 0c          shr eax,0xc
    0x8b,0x04,0x85, XX4,  // 30207339   8b0485 3000e511  mov eax,dword ptr ds:[eax*4+0x11e50030]
    0xbb, XX4,            // 30207340   bb 4f732030      mov ebx,0x3020734f
    0x01,0xc1,            // 30207345   01c1             add ecx,eax
    0x0f,0x88, XX4,       // 30207347  -0f88 739e19d3    js pcsx2.033a11c0
    0x88,0x11,            // 3020734d   8811             mov byte ptr ds:[ecx],dl    ; jichi: hook here, text in dl
    0x83,0x05, XX4, 0x01, // 3020734f   8305 30ab9e01 01 add dword ptr ds:[0x19eab30],0x1
    0x9f,                 // 30207356   9f               lahf
    0x66,0xc1,0xf8, 0x0f, // 30207357   66:c1f8 0f       sar ax,0xf
    0x98,                 // 3020735b   98               cwde
    // The above pattern is not sufficient
    0xa3, XX4,            // 3020735c   a3 34ab9e01      mov dword ptr ds:[0x19eab34],eax
    0xa1, XX4,            // 30207361   a1 60ab9e01      mov eax,dword ptr ds:[0x19eab60]
    0x3b,0x05, XX4,       // 30207366   3b05 40ab9e01    cmp eax,dword ptr ds:[0x19eab40]
    0x75, 0x11,           // 3020736c   75 11            jnz short 3020737f
    0xa1, XX4,            // 3020736e   a1 64ab9e01      mov eax,dword ptr ds:[0x19eab64]
    0x3b,0x05, XX4,       // 30207373   3b05 44ab9e01    cmp eax,dword ptr ds:[0x19eab44]
    0x0f,0x84, XX4,       // 30207379   0f84 28000000    je 302073a7
    0xc7,0x05, XX8,       // 3020737f   c705 a8ad9e01 34>mov dword ptr ds:[0x19eada8],0x17eb34
    // The above pattern is not sufficient
    0xa1, XX4,            // 30207389   a1 c0ae9e01      mov eax,dword ptr ds:[0x19eaec0]
    0x83,0xc0, 0x09,      // 3020738e   83c0 09          add eax,0x9
    0xa3, XX4,            // 30207391   a3 c0ae9e01      mov dword ptr ds:[0x19eaec0],eax
    0x2b,0x05, XX4,       // 30207396   2b05 809e9d01    sub eax,dword ptr ds:[0x19d9e80]         ; cdvdgiga.5976f736
    0x0f,0x88, XX4,       // 3020739c  ^0f88 31ffffff    js 302072d3
    0xe9, XX4,            // 302073a2  -e9 59cc21d3      jmp pcsx2.03424000
    0xc7,0x05, XX8,       // 302073a7   c705 a8ad9e01 50>mov dword ptr ds:[0x19eada8],0x17eb50
    0xa1, XX4,            // 302073b1   a1 c0ae9e01      mov eax,dword ptr ds:[0x19eaec0]
    0x83,0xc0, 0x09,      // 302073b6   83c0 09          add eax,0x9
    0xa3, XX4,            // 302073b9   a3 c0ae9e01      mov dword ptr ds:[0x19eaec0],eax
    0x2b,0x05, XX4,       // 302073be   2b05 809e9d01    sub eax,dword ptr ds:[0x19d9e80]         ; cdvdgiga.5976f736
    0x0f,0x88, XX4,       // 302073c4  ^0f88 75cbfcff    js 301d3f3f
    0xe9, XX4,            // 302073ca  -e9 31cc21d3      jmp pcsx2.03424000
    0x8b,0x15, XX4,       // 302073cf   8b15 10ac9e01    mov edx,dword ptr ds:[0x19eac10]
    0x8b,0x0d, XX4,       // 302073d5   8b0d 20ac9e01    mov ecx,dword ptr ds:[0x19eac20]
    0x83,0xc1, 0x04,      // 302073db   83c1 04          add ecx,0x4
    0x89,0xc8,            // 302073de   89c8             mov eax,ecx
    0xc1,0xe8, 0x0c,      // 302073e0   c1e8 0c          shr eax,0xc
    0x8b,0x04,0x85, XX4,  // 302073e3   8b0485 3000e511  mov eax,dword ptr ds:[eax*4+0x11e50030]
    0xbb, XX4,            // 302073ea   bb f9732030      mov ebx,0x302073f9
    0x01,0xc1             // 302073ef   01c1             add ecx,eax
  };
  enum { addr_offset = 0x3020734d - 0x30207334 };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPS2Memory(bytes, sizeof(bytes));
  //addr = 0x30403967;
  if (!addr)
    ConsoleOutput("Marvelous2 PS2: pattern not found");
  else {
    //GROWL_DWORD(addr + addr_offset);
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.type = USING_STRING|NO_CONTEXT; // no context to get rid of return address
    hp.text_fun = SpecialPS2HookMarvelous2;
    ConsoleOutput("Marvelous2 PS2: INSERT");
    //GROWL_DWORD(hp.address);
    succ|=NewHook(hp, "Marvelous2 PS2");
  }

  ConsoleOutput("Marvelous2 PS2: leave");
  return succ;
}

#if 0 // jichi 7/19/2014: duplication text

/** 7/19/2014 jichi
 *  Tested game: .hack//G.U. Vol.1
 */
bool InsertNamcoPS2Hook()
{
  ConsoleOutput("Namco PS2: enter");
  const BYTE bytes[1] =  {
  };
  enum { addr_offset = 0 };

  //DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  //DWORD addr = 0x303baf26;
  DWORD addr = 0x303C4B72;
  if (!addr)
    ConsoleOutput("Namco PS2: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.type = USING_STRING|USING_SPLIT; // no context to get rid of return address
    hp.offset=regoffset(ecx); 
    hp.split = hp.offset; // use ecx address to split
    ConsoleOutput("Namco PS2: INSERT");
    //GROWL_DWORD(hp.address);
    NewHook(hp, "Namco PS2");
  }

  ConsoleOutput("Namco PS2: leave");
  return addr;
}
#endif // 0

#if 0 // SEGA: loop text. BANDAI and Imageepoch should be sufficient
/** 7/25/2014 jichi sega.jp PSP engine
 *  Sample game: Shining Hearts
 *  Encoding: UTF-8
 *
 *  Debug method: simply add hardware break points to the matched memory
 *  All texts are in the memory.
 *  There are two memory addresses, but only one function addresses them.
 *
 *  This function seems to be the same as Tecmo?
 *
 *  13513476   f0:90            lock nop                                 ; lock prefix is not allowed
 *  13513478   77 0f            ja short 13513489
 *  1351347a   c705 a8aa1001 38>mov dword ptr ds:[0x110aaa8],0x89cae38
 *  13513484  -e9 7bcb4ff0      jmp 03a10004
 *  13513489   8b05 7ca71001    mov eax,dword ptr ds:[0x110a77c]
 *  1351348f   81e0 ffffff3f    and eax,0x3fffffff
 *  13513495   8bb0 00004007    mov esi,dword ptr ds:[eax+0x7400000] ; jichi: there are too many garbage here
 *  1351349b   8b3d 7ca71001    mov edi,dword ptr ds:[0x110a77c]
 *  135134a1   8d7f 04          lea edi,dword ptr ds:[edi+0x4]
 *  135134a4   8b05 84a71001    mov eax,dword ptr ds:[0x110a784]
 *  135134aa   81e0 ffffff3f    and eax,0x3fffffff
 *  135134b0   89b0 00004007    mov dword ptr ds:[eax+0x7400000],esi ; extract from esi
 *  135134b6   8b2d 84a71001    mov ebp,dword ptr ds:[0x110a784]
 *  135134bc   8d6d 04          lea ebp,dword ptr ss:[ebp+0x4]
 *  135134bf   8b15 78a71001    mov edx,dword ptr ds:[0x110a778]
 *  135134c5   81fa 01000000    cmp edx,0x1
 *  135134cb   8935 70a71001    mov dword ptr ds:[0x110a770],esi
 *  135134d1   893d 7ca71001    mov dword ptr ds:[0x110a77c],edi
 *  135134d7   892d 84a71001    mov dword ptr ds:[0x110a784],ebp
 *  135134dd   c705 88a71001 01>mov dword ptr ds:[0x110a788],0x1
 *  135134e7   0f84 16000000    je 13513503
 *  135134ed   832d c4aa1001 09 sub dword ptr ds:[0x110aac4],0x9
 *  135134f4   e9 23000000      jmp 1351351c
 *  135134f9   013cae           add dword ptr ds:[esi+ebp*4],edi
 *  135134fc   9c               pushfd
 *  135134fd   08e9             or cl,ch
 *  135134ff   20cb             and bl,cl
 *  13513501   4f               dec edi
 *  13513502   f0:832d c4aa1001>lock sub dword ptr ds:[0x110aac4],0x9    ; lock prefix
 *  1351350a   e9 b1000000      jmp 135135c0
 *  1351350f   015cae 9c        add dword ptr ds:[esi+ebp*4-0x64],ebx
 *  13513513   08e9             or cl,ch
 *  13513515   0acb             or cl,bl
 *  13513517   4f               dec edi
 *  13513518   f0:90            lock nop                                 ; lock prefix is not allowed
 *  1351351a   cc               int3
 *  1351351b   cc               int3
 */
// Read text from esi
static void SpecialPSPHookSega(hook_context *context,  HookParam *, uintptr_t *data, uintptr_t *split, size_t*len)
{
  LPCSTR text = LPCSTR(esp_base + regoffset(esi)); // esi address
  if (*text) {
    *data = (DWORD)text;
    *len = !text[0] ? 0 : !text[1] ? 1 : text[2] ? 2 : text[3] ? 3 : 4;
    *split = regof(ebx, esp_base);
  }
}

bool InsertSegaPSPHook()
{
  ConsoleOutput("SEGA PSP: enter");
  const BYTE bytes[] =  {
    0x77, 0x0f,                     // 13513478   77 0f            ja short 13513489
    0xc7,0x05, XX8,                 // 1351347a   c705 a8aa1001 38>mov dword ptr ds:[0x110aaa8],0x89cae38
    0xe9, XX4,                      // 13513484  -e9 7bcb4ff0      jmp 03a10004
    0x8b,0x05, XX4,                 // 13513489   8b05 7ca71001    mov eax,dword ptr ds:[0x110a77c]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 1351348f   81e0 ffffff3f    and eax,0x3fffffff
    0x8b,0xb0, XX4,                 // 13513495   8bb0 00004007    mov esi,dword ptr ds:[eax+0x7400000] ; jichi: here are too many garbage
    0x8b,0x3d, XX4,                 // 1351349b   8b3d 7ca71001    mov edi,dword ptr ds:[0x110a77c]
    0x8d,0x7f, 0x04,                // 135134a1   8d7f 04          lea edi,dword ptr ds:[edi+0x4]
    0x8b,0x05, XX4,                 // 135134a4   8b05 84a71001    mov eax,dword ptr ds:[0x110a784]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 135134aa   81e0 ffffff3f    and eax,0x3fffffff
    0x89,0xb0   //, XX4,            // 135134b0   89b0 00004007    mov dword ptr ds:[eax+0x7400000],esi ; jichi: hook here, get text in esi
  };
  enum { memory_offset = 2 };
  enum { addr_offset = sizeof(bytes) - memory_offset };
  //enum { addr_offset = 0x13513495 - 0x13513478 };

  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("SEGA PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.type = USING_STRING|NO_CONTEXT; // UTF-8
    hp.text_fun = SpecialPSPHookSega;
    ConsoleOutput("SEGA PSP: INSERT");
    NewHook(hp, "SEGA PSP");
  }

  ConsoleOutput("SEGA PSP: leave");
  return addr;
}
#endif // 0


#if 0 // jichi 7/14/2014: TODO there is text duplication issue?

/** 7/13/2014 jichi SHADE.co.jp PSP engine
 *  Sample game: とある科学の趛�磁� (b-railgun.iso)
 *
 *  CheatEngine/Ollydbg shew there are 4 memory hits to full text in SHIFT-JIS.
 *  CheatEngine is not able to trace JIT instructions.
 *  Ollydbg can track the latter two memory accesses > 0x1ffffffff
 *
 *  The third access is 12ab3d64. There is one write access and 3 read accesses.
 *  But all the accesses are in a loop.
 *  So, the extracted text would suffer from infinite loop problem.
 *
 *  Memory range: 0x0400000 - 139f000
 *
 *  13400e10   90               nop
 *  13400e11   cc               int3
 *  13400e12   cc               int3
 *  13400e13   cc               int3
 *  13400e14   77 0f            ja short 13400e25
 *  13400e16   c705 a8aa1001 08>mov dword ptr ds:[0x110aaa8],0x88c1308
 *  13400e20  -e9 dff161f3      jmp 06a20004
 *  13400e25   8b35 78a71001    mov esi,dword ptr ds:[0x110a778]
 *  13400e2b   81c6 01000000    add esi,0x1
 *  13400e31   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
 *  13400e37   81e0 ffffff3f    and eax,0x3fffffff
 *  13400e3d   0fb6b8 00004007  movzx edi,byte ptr ds:[eax+0x7400000] ; jichi: the data is in [eax+0x7400000]
 *  13400e44   8b2d 78a71001    mov ebp,dword ptr ds:[0x110a778]
 *  13400e4a   8d6d 01          lea ebp,dword ptr ss:[ebp+0x1]
 *  13400e4d   81ff 00000000    cmp edi,0x0
 *  13400e53   8935 70a71001    mov dword ptr ds:[0x110a770],esi
 *  13400e59   893d 74a71001    mov dword ptr ds:[0x110a774],edi
 *  13400e5f   892d 78a71001    mov dword ptr ds:[0x110a778],ebp
 *  13400e65   0f84 16000000    je 13400e81
 *  13400e6b   832d c4aa1001 04 sub dword ptr ds:[0x110aac4],0x4
 *  13400e72   e9 21000000      jmp 13400e98
 *  13400e77   010c13           add dword ptr ds:[ebx+edx],ecx
 *  13400e7a   8c08             mov word ptr ds:[eax],cs
 *  13400e7c  -e9 a2f161f3      jmp 06a20023
 *  13400e81   832d c4aa1001 04 sub dword ptr ds:[0x110aac4],0x4
 *  13400e88   e9 7f000000      jmp 13400f0c
 *  13400e8d   0118             add dword ptr ds:[eax],ebx
 *  13400e8f   138c08 e98cf161  adc ecx,dword ptr ds:[eax+ecx+0x61f18ce9>
 *  13400e96   f3:              prefix rep:                              ; superfluous prefix
 *  13400e97   90               nop
 *  13400e98   77 0f            ja short 13400ea9
 *  13400e9a   c705 a8aa1001 0c>mov dword ptr ds:[0x110aaa8],0x88c130c
 *  13400ea4  -e9 5bf161f3      jmp 06a20004
 *  13400ea9   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
 *  13400eaf   81e0 ffffff3f    and eax,0x3fffffff
 *  13400eb5   0fb6b0 00004007  movzx esi,byte ptr ds:[eax+0x7400000]
 *  13400ebc   8b3d 78a71001    mov edi,dword ptr ds:[0x110a778]
 *  13400ec2   8d7f 01          lea edi,dword ptr ds:[edi+0x1]
 *  13400ec5   81fe 00000000    cmp esi,0x0
 *  13400ecb   8935 74a71001    mov dword ptr ds:[0x110a774],esi
 *  13400ed1   893d 78a71001    mov dword ptr ds:[0x110a778],edi
 *  13400ed7   0f84 16000000    je 13400ef3
 *  13400edd   832d c4aa1001 03 sub dword ptr ds:[0x110aac4],0x3
 *  13400ee4  ^e9 afffffff      jmp 13400e98
 *  13400ee9   010c13           add dword ptr ds:[ebx+edx],ecx
 *  13400eec   8c08             mov word ptr ds:[eax],cs
 *  13400eee  -e9 30f161f3      jmp 06a20023
 *  13400ef3   832d c4aa1001 03 sub dword ptr ds:[0x110aac4],0x3
 *  13400efa   e9 0d000000      jmp 13400f0c
 *  13400eff   0118             add dword ptr ds:[eax],ebx
 *  13400f01   138c08 e91af161  adc ecx,dword ptr ds:[eax+ecx+0x61f11ae9>
 *  13400f08   f3:              prefix rep:                              ; superfluous prefix
 *  13400f09   90               nop
 *  13400f0a   cc               int3
 *  13400f0b   cc               int3
 */
static void SpecialPSPHookShade(hook_context *context,  HookParam *hp, BYTE, uintptr_t *data, uintptr_t *split, size_t*len)
{
  DWORD eax = regof(eax, esp_base);
  LPCSTR text = LPCSTR(eax + hp->user_value);
  if (*text) {
    *data = (DWORD)text;
    *len = ::strlen(text);
  }
}

bool InsertShadePSPHook()
{
  ConsoleOutput("Shade PSP: enter");
  // TODO: Query MEM_Mapped at runtime
  // http://msdn.microsoft.com/en-us/library/windows/desktop/aa366902%28v=vs.85%29.aspx
  enum : DWORD { StartAddress = 0x13390000, StopAddress = 0x13490000 };

  const BYTE bytes[] =  {
    0xcc,                           // 13400e12   cc               int3
    0xcc,                           // 13400e13   cc               int3
    0x77, 0x0f,                     // 13400e14   77 0f            ja short 13400e25
    0xc7,0x05, XX8,                 // 13400e16   c705 a8aa1001 08>mov dword ptr ds:[0x110aaa8],0x88c1308
    0xe9, XX4,                      // 13400e20  -e9 dff161f3      jmp 06a20004
    0x8b,0x35, XX4,                 // 13400e25   8b35 78a71001    mov esi,dword ptr ds:[0x110a778]
    0x81,0xc6, 0x01,0x00,0x00,0x00, // 13400e2b   81c6 01000000    add esi,0x1
    0x8b,0x05, XX4,                 // 13400e31   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13400e37   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xb6,0xb8, XX4,            // 13400e3d   0fb6b8 00004007  movzx edi,byte ptr ds:[eax+0x7400000] ; jichi: the data is in [eax+0x7400000]
    0x8b,0x2d, XX4,                 // 13400e44   8b2d 78a71001    mov ebp,dword ptr ds:[0x110a778]
    0x8d,0x6d, 0x01,                // 13400e4a   8d6d 01          lea ebp,dword ptr ss:[ebp+0x1]
    0x81,0xff, 0x00,0x00,0x00,0x00  // 13400e4d   81ff 00000000    cmp edi,0x0
  };
  enum{ memory_offset = 3 };
  enum { addr_offset = 0x13400e3d - 0x13400e12 };

  ULONG addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("Shade PSP: failed");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.text_fun = SpecialPSPHookShade;
    hp.type = USING_STRING;
    ConsoleOutput("Shade PSP: INSERT");

    // CHECKPOINT 7/14/2014: This would crash vnrcli
    // I do not have permission to modify the JIT code region?
    NewHook(hp, "Shade PSP");
  }

  //DWORD peek = 0x13400e14;
  //GROWL_DWORD(*(BYTE *)peek); // supposed to be 0x77 ja
  ConsoleOutput("Shade PSP: leave");
  return addr;
}

#endif // 0

#if 0 // jichi 7/17/2014: Disabled as there are so many text threads
/** jichi 7/17/2014 alternative Alchemist hook
 *
 *  Sample game: your diary+ (moe-ydp.iso)
 *  The debugging method is the same as Alchemist1.
 *
 *  It seems that hooks found in Alchemist games
 *  also exist in other games.
 *
 *  This function is executed in a looped.
 *
 *  13400e12   cc               int3
 *  13400e13   cc               int3
 *  13400e14   77 0f            ja short 13400e25
 *  13400e16   c705 a8aa1001 84>mov dword ptr ds:[0x110aaa8],0x8931084
 *  13400e20  -e9 dff148f0      jmp 03890004
 *  13400e25   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
 *  13400e2b   81e0 ffffff3f    and eax,0x3fffffff
 *  13400e31   0fbeb0 00004007  movsx esi,byte ptr ds:[eax+0x7400000] ; jichi: hook here
 *  13400e38   8b3d 78a71001    mov edi,dword ptr ds:[0x110a778]
 *  13400e3e   81fe 00000000    cmp esi,0x0
 *  13400e44   893d 7ca71001    mov dword ptr ds:[0x110a77c],edi
 *  13400e4a   8935 80a71001    mov dword ptr ds:[0x110a780],esi
 *  13400e50   0f85 16000000    jnz 13400e6c
 *  13400e56   832d c4aa1001 03 sub dword ptr ds:[0x110aac4],0x3
 *  13400e5d   e9 16010000      jmp 13400f78
 *  13400e62   01a0 109308e9    add dword ptr ds:[eax+0xe9089310],esp
 *  13400e68   b7 f1            mov bh,0xf1
 *  13400e6a   48               dec eax
 *  13400e6b   f0:832d c4aa1001>lock sub dword ptr ds:[0x110aac4],0x3    ; lock prefix
 *  13400e73   e9 0c000000      jmp 13400e84
 *  13400e78   0190 109308e9    add dword ptr ds:[eax+0xe9089310],edx
 *  13400e7e   a1 f148f090      mov eax,dword ptr ds:[0x90f048f1]
 *  13400e83   cc               int3
 *  13400e84   77 0f            ja short 13400e95
 *  13400e86   c705 a8aa1001 90>mov dword ptr ds:[0x110aaa8],0x8931090
 *  13400e90  -e9 6ff148f0      jmp 03890004
 *  13400e95   8b35 78a71001    mov esi,dword ptr ds:[0x110a778]
 *  13400e9b   8d76 01          lea esi,dword ptr ds:[esi+0x1]
 *  13400e9e   8bc6             mov eax,esi
 *  13400ea0   81e0 ffffff3f    and eax,0x3fffffff
 *  13400ea6   0fbeb8 00004007  movsx edi,byte ptr ds:[eax+0x7400000]
 *  13400ead   81ff 00000000    cmp edi,0x0
 *  13400eb3   8935 78a71001    mov dword ptr ds:[0x110a778],esi
 *  13400eb9   893d 80a71001    mov dword ptr ds:[0x110a780],edi
 *  13400ebf   0f84 25000000    je 13400eea
 *  13400ec5   8b35 78a71001    mov esi,dword ptr ds:[0x110a778]
 *  13400ecb   8d76 01          lea esi,dword ptr ds:[esi+0x1]
 *  13400ece   8935 78a71001    mov dword ptr ds:[0x110a778],esi
 *  13400ed4   832d c4aa1001 04 sub dword ptr ds:[0x110aac4],0x4
 *  13400edb   e9 24000000      jmp 13400f04
 *  13400ee0   019410 9308e939  add dword ptr ds:[eax+edx+0x39e90893],ed>
 *  13400ee7   f1               int1
 *  13400ee8   48               dec eax
 *  13400ee9   f0:832d c4aa1001>lock sub dword ptr ds:[0x110aac4],0x4    ; lock prefix
 *  13400ef1   e9 82000000      jmp 13400f78
 *  13400ef6   01a0 109308e9    add dword ptr ds:[eax+0xe9089310],esp
 *  13400efc   23f1             and esi,ecx
 *  13400efe   48               dec eax
 *  13400eff   f0:90            lock nop                                 ; lock prefix is not allowed
 *  13400f01   cc               int3
 *  13400f02   cc               int3
 */
// jichi 7/17/2014: Why this function is exactly the same as SpecialPSPHookImageepoch?
static void SpecialPSPHookAlchemist3(hook_context *context,  HookParam *hp, BYTE, uintptr_t *data, uintptr_t *split, size_t*len)
{
  DWORD eax = regof(eax, esp_base);
  DWORD text = eax + hp->user_value;
  static DWORD lasttext;
  if (text != lasttext && *(LPCSTR)text) {
    *data = lasttext = text;
    *len = ::strlen((LPCSTR)text);
    *split = regof(ecx, esp_base); // use ecx "this" as split value?
  }
}
bool InsertAlchemist3PSPHook()
{
  ConsoleOutput("Alchemist3 PSP: enter");
  const BYTE bytes[] =  {
    //0xcc,                         // 13400e12   cc               int3
    //0xcc,                         // 13400e13   cc               int3
    0x77, 0x0f,                     // 13400e14   77 0f            ja short 13400e25
    0xc7,0x05, XX8,                 // 13400e16   c705 a8aa1001 84>mov dword ptr ds:[0x110aaa8],0x8931084
    0xe9, XX4,                      // 13400e20  -e9 dff148f0      jmp 03890004
    0x8b,0x05, XX4,                 // 13400e25   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13400e2b   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xbe,0xb0, XX4,            // 13400e31   0fbeb0 00004007  movsx esi,byte ptr ds:[eax+0x7400000] ; jichi: hook here
    0x8b,0x3d, XX4,                 // 13400e38   8b3d 78a71001    mov edi,dword ptr ds:[0x110a778]
    0x81,0xfe, 0x00,0x00,0x00,0x00, // 13400e3e   81fe 00000000    cmp esi,0x0
    0x89,0x3d, XX4,                 // 13400e44   893d 7ca71001    mov dword ptr ds:[0x110a77c],edi
    0x89,0x35, XX4,                 // 13400e4a   8935 80a71001    mov dword ptr ds:[0x110a780],esi
    0x0f,0x85 //, 16000000          // 13400e50   0f85 16000000    jnz 13400e6c
  };
  enum { memory_offset = 3 };
  enum { addr_offset = 0x13407711 - 0x134076f4 };

  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("Alchemist3 PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset); // use module to pass membase
    hp.text_fun = SpecialPSPHookAlchemist3;
    hp.type = USING_STRING|NO_CONTEXT; // no context is needed to get rid of variant retaddr
    ConsoleOutput("Alchemist3 PSP: INSERT");
    NewHook(hp, "Alchemist3 PSP");
  }

  ConsoleOutput("Alchemist3 PSP: leave");
  return addr;
}
#endif // 0
/** jichi 7/19/2014 PCSX2
 *  Tested wit  pcsx2-v1.2.1-328-gef0e3fe-windows-x86, built at http://buildbot.orphis.net/pcsx2
 */
bool InsertPCSX2Hooks()
{
    memcpy(spDefault.pattern, Array<BYTE>{ 0x89, 0xc8, 0xc1, 0xe8, 0x0c }, spDefault.length = 5);
	spDefault.minAddress = 0;
	spDefault.maxAddress = -1ULL;
    spDefault.offset = 0;
    spDefault.searchTime = 60'000;
    spDefault.maxRecords = 500'000;
    spDefault.padding = 0x20000000;
    ConsoleOutput("PCSX2 detected (searching for hooks may work)");
  // TODO: Add generic hooks
  return InsertTypeMoonPS2Hook()
      || InsertMarvelousPS2Hook()
      || InsertMarvelous2PS2Hook();
}

bool PCSX2::attach_function() {
    
    return InsertPCSX2Hooks();
} 