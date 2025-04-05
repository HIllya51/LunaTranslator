#include "Circus2.h"
namespace
{
  void filter(TextBuffer *buffer, HookParam *hp)
  {
    StringFilter(buffer, TEXTANDLEN("\n\x81\x40"));
    StringFilter(buffer, TEXTANDLEN("@s"));
    auto data = buffer->buff;
    if (strstr((char *)data, "@i") || strstr((char *)data, "@y"))
      return buffer->clear();
    // ｛てんきゅう／天穹｝
    if (strstr((char *)data, "\x81\x6f") && strstr((char *)data, "\x81\x5e") && strstr((char *)data, "\x81\x70"))
    {
      StringFilter(buffer, TEXTANDLEN("\x81\x70"));
      StringFilterBetween(buffer, TEXTANDLEN("\x81\x6f"), TEXTANDLEN("\x81\x5e"));
    }
    CharFilter(buffer, '\n');
  };
}
/**
 *  jichi 6/5/2014: Sample function from DC3 at 0x4201d0
 *  004201ce     cc             int3
 *  004201cf     cc             int3
 *  004201d0  /$ 8b4c24 08      mov ecx,dword ptr ss:[esp+0x8]
 *  004201d4  |. 8a01           mov al,byte ptr ds:[ecx]
 *  004201d6  |. 84c0           test al,al
 *  004201d8  |. 74 1c          je short dc3.004201f6
 *  004201da  |. 8b5424 04      mov edx,dword ptr ss:[esp+0x4]
 *  004201de  |. 8bff           mov edi,edi
 *  004201e0  |> 3c 24          /cmp al,0x24
 *  004201e2  |. 75 05          |jnz short dc3.004201e9
 *  004201e4  |. 83c1 02        |add ecx,0x2
 *  004201e7  |. eb 04          |jmp short dc3.004201ed
 *  004201e9  |> 8802           |mov byte ptr ds:[edx],al
 *  004201eb  |. 42             |inc edx
 *  004201ec  |. 41             |inc ecx
 *  004201ed  |> 8a01           |mov al,byte ptr ds:[ecx]
 *  004201ef  |. 84c0           |test al,al
 *  004201f1  |.^75 ed          \jnz short dc3.004201e0
 *  004201f3  |. 8802           mov byte ptr ds:[edx],al
 *  004201f5  |. c3             retn
 *  004201f6  |> 8b4424 04      mov eax,dword ptr ss:[esp+0x4]
 *  004201fa  |. c600 00        mov byte ptr ds:[eax],0x0
 *  004201fd  \. c3             retn
 */
bool InsertCircusHook2() // jichi 10/2/2013: Change return type to bool
{
  for (DWORD i = processStartAddress + 0x1000; i < processStopAddress - 4; i++)
    if ((*(DWORD *)i & 0xffffff) == 0x75243c)
    { // cmp al, 24; je
      if (DWORD j = SafeFindEnclosingAlignedFunction(i, 0x80))
      {
        HookParam hp;
        hp.address = j;
        hp.offset = stackoffset(2);
        // hp.filter_fun = CharNewLineFilter; // \n\s* is used to remove new line
        hp.type = USING_STRING;
        // GROWL_DWORD(hp.address); // jichi 6/5/2014: 0x4201d0 for DC3

        // RegisterEngineType(ENGINE_CIRCUS);
        return NewHook(hp, "Circus");
      }
      break;
    }
  // ConsoleOutput("Unknown CIRCUS engine.");
  ConsoleOutput("CIRCUS: failed");
  return false;
}
namespace
{
  bool c2()
  {
    // D.C.III Dream Days～ダ・カーポIII～ドリームデイズ
    auto entry = Util::FindImportEntry(processStartAddress, (DWORD)GetGlyphOutlineA);
    if (!entry)
      return false;
    auto addrs = Util::SearchMemory(&entry, 4, PAGE_EXECUTE, processStartAddress, processStopAddress);
    if (!addrs.size())
      return false;
    auto addr = addrs[addrs.size() - 1];
    DWORD _ = 0xCCCCCCCC;
    BYTE SIG[] = {0x8B, 0xB4, 0x24, XX2, 0x00, 0x00, 0x80, 0x3E, 0x00};
    auto funcaddr = reverseFindBytes((BYTE *)&_, 4, addr - 0x1000, addr, 4, true);
    auto funcaddr2 = reverseFindBytes(SIG, sizeof(SIG), addr - 0x1000, addr);
    // 有些作不够4个CC对齐，而且不是stack[2]，而是1，且没办法确定是哪个，所以只好这样
    if (funcaddr)
    {
      HookParam hp;
      hp.address = funcaddr;
      hp.offset = stackoffset(2);
      hp.type = USING_STRING; //|EMBED_ABLE|EMBED_AFTER_NEW|EMBED_DYNA_SJIS;
      // hp.embed_hook_font=F_GetGlyphOutlineA;
      // it will split a long to many lines
      hp.filter_fun = filter;
      NewHook(hp, "Circus2");
    }
    if (funcaddr2)
    {
      HookParam hp;
      hp.address = funcaddr2 + 7;
      hp.offset = regoffset(esi);
      hp.type = USING_STRING | NO_CONTEXT; //|EMBED_ABLE|EMBED_AFTER_NEW|EMBED_DYNA_SJIS;
      // hp.embed_hook_font=F_GetGlyphOutlineA;
      // it will split a long to many lines
      hp.filter_fun = filter;
      NewHook(hp, "Circus2");
    }
    return funcaddr || funcaddr2;
  }
  bool c3()
  {
    // v17743 D.C.III With You～ダ・カーポIII～ウィズユー
    // v21192 D.C.III Dream Days～ダ・カーポIII～ドリームデイズ
    /*
    //sub_434D40   <---- c2的目标，但他有时是stack[1]有时是stack[2]，不如这个函数稳定stack[1]
    int __thiscall sub_435C00(void *this, char *Str)
{
  char *v2; // esi
  char *v5; // edi
  char v6[260]; // [esp+8h] [ebp-108h] BYREF

  v2 = Str;
  if ( strlen(Str) > 0x104 )
    return MessageBoxA(
             0,
             "SetStr暥帤悢僆乕僶乕",
             "D.C.嘨 With You 乣僟丒僇乕億嘨乣 僂傿僘儐乕",
             0x42000u);
  if ( strstr(Str, word_47983C) )
  {
    strcpy(v6, Str);
    v2 = v6;
    if ( strstr(v6, word_47983C) )
    {
      do
      {
        v5 = strstr(v2, word_47983C);
        *v5 = 0;
        sub_434D40((int)this, v2);
        v2 = v5 + 1;
      }
      while ( strstr(v5 + 1, word_47983C) );
    }
  }
  return sub_434D40((int)this, v2);
}
    */
    /*
    int __thiscall sub_43FA40(_DWORD *this, char *Str)
 {
   char *v2; // esi
   int result; // eax
   int v5; // ebp
   char *v6; // edi
   char v7[260]; // [esp+8h] [ebp-108h] BYREF

   v2 = Str;
   if ( strlen(Str) > 0x104 )
     return MessageBoxA(0, "SetStr overflow", "D.C.嘨 DreamDays乣僟丒僇乕億嘨乣僪儕乕儉僨僀僘", 0x42000u);
   v5 = this[17];
   if ( strstr(Str, word_484938) )
   {
     strcpy(v7, Str);
     v2 = v7;
     if ( strstr(v7, word_484938) )
     {
       do
       {
         v6 = strstr(v2, word_484938);
         *v6 = 0;
         sub_43F860((int)this, v2);
         v2 = v6 + 1;
       }
       while ( strstr(v6 + 1, word_484938) );
     }
   }
   result = sub_43F860((int)this, v2);
   this[17] = v5;
   this[30] = 0;
   return result;
 }
    */
    auto check1 = []() -> uintptr_t
    {
      char overflow[] = "\x53\x65\x74\x53\x74\x72\x95\xB6\x8E\x9A\x90\x94\x83\x49\x81\x5b\x83\x6f\x81\x5b"; // SetStr文字数オーバー
      char overflow2[] = "SetStr overflow";
      auto addr = MemDbg::findBytes(overflow, sizeof(overflow), processStartAddress, processStopAddress);
      if (!addr)
        addr = MemDbg::findBytes(overflow2, ::strlen(overflow2), processStartAddress, processStopAddress);
      if (!addr)
        return 0;
      addr = MemDbg::findPushAddress(addr, processStartAddress, processStopAddress);
      if (!addr)
        return 0;
      return addr;
    };
    auto addr = check1();
    if (!addr)
    {
      const BYTE bytes[] = {
          /*
          if ( strlen(Str) > 0x104 )
       return MessageBoxA(0,。。。)
          */
          0x8a, 0x08,
          0x40,
          0x84, 0xc9,
          0x75, 0xf9,
          0x2b, 0xc2,
          0x3d, 0x04, 0x01, 0x00, 0x00,
          0x76, XX,
          0x68, 0x00, 0x20, 0x04, 0x00,
          0x68, XX4,
          0x68, XX4,
          0x6a, 0x00,
          0xff, 0x15, XX4};
      addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    }
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING; //|EMBED_ABLE|EMBED_AFTER_NEW|EMBED_DYNA_SJIS;
    hp.filter_fun = filter;
    return NewHook(hp, "Circus2");
  }
}

namespace
{ // unnamed

  // Skip leading tags such as @K and @c5
  template <typename strT>
  strT ltrim(strT s)
  {
    if (s && *s == '@')
      while ((signed char)*++s > 0)
        ;
    return s;
  }

  namespace ScenarioHook
  {
    namespace Private
    {

      DWORD nameReturnAddress_,
          scenarioReturnAddress_;

      /**
       *  Sample game: DC3, function: 0x4201d0
       *
       *  IDA: sub_4201D0      proc near
       *  - arg_0 = dword ptr  4
       *  - arg_4 = dword ptr  8
       *
       *  Observations:
       *  - arg1: LPVOID, pointed to unknown object
       *  - arg2: LPCSTR, the actual text
       *
       *  Example runtime stack:
       *  0012F15C   0040C208  RETURN to .0040C208 from .00420460
       *  0012F160   0012F7CC ; jichi: unknown stck
       *  0012F164   0012F174 ; jichi: text
       *  0012F168   0012F6CC
       *  0012F16C   0012F7CC
       *  0012F170   0012F7CC
       */
      void hookafter(hook_context *s, TextBuffer buffer)
      {
        auto newData = buffer.strA();
        LPCSTR text = (LPCSTR)s->stack[2], // arg2
            trimmedText = ltrim(text);
        if (trimmedText != text)
          newData.insert(0, std::string(text, trimmedText - text));
        s->stack[2] = (DWORD)allocateString(newData);
      }
      void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
      {

        LPCSTR text = (LPCSTR)s->stack[2], // arg2
            trimmedText = ltrim(text);
        if (!trimmedText || !*trimmedText)
          return;
        auto retaddr = s->stack[0]; // retaddr
        *role = retaddr == scenarioReturnAddress_ ? Engine::ScenarioRole : retaddr == nameReturnAddress_ ? Engine::NameRole
                                                                                                         : Engine::OtherRole;
        // s->ebx? Engine::OtherRole : // other threads ebx is not zero
        //// 004201e4  |. 83c1 02        |add ecx,0x2
        //// 004201e7  |. eb 04          |jmp short dc3.004201ed
        //*(BYTE *)(retaddr + 3) == 0xe9 // old name
        //? Engine::NameRole : // retaddr+3 is jmp
        // Engine::ScenarioRole;
        buffer->from(trimmedText);
      }

      // Alternatively, using the following pattern bytes also works:
      //
      // 3c24750583c102eb0488024241
      //
      // 004201e0  |> 3c 24          /cmp al,0x24
      // 004201e2  |. 75 05          |jnz short dc3.004201e9
      // 004201e4  |. 83c1 02        |add ecx,0x2
      // 004201e7  |. eb 04          |jmp short dc3.004201ed
      // 004201e9  |> 8802           |mov byte ptr ds:[edx],al
      // 004201eb  |. 42             |inc edx
      // 004201ec  |. 41             |inc ecx
      ULONG findFunctionAddress(ULONG startAddress, ULONG stopAddress) // find the function to hook
      {
        // return 0x4201d0; // DC3 function address
        for (ULONG i = startAddress + 0x1000; i < stopAddress - 4; i++)
          // *  004201e0  |> 3c 24          /cmp al,0x24
          // *  004201e2  |. 75 05          |jnz short dc3.004201e9
          if ((*(ULONG *)i & 0xffffff) == 0x75243c)
          { // cmp al, 24; je
            enum
            {
              range = 0x80
            }; // the range is small, since it is a small function
            if (ULONG addr = MemDbg::findEnclosingAlignedFunction(i, range))
              return addr;
          }
        return 0;
      }

    } // namespace Private

    /**
     *  jichi 6/5/2014: Sample function from DC3 at 0x4201d0
     *
     *  Sample game: DC3PP
     *  0042CE1E   68 E0F0B700      PUSH .00B7F0E0
     *  0042CE23   A3 0C824800      MOV DWORD PTR DS:[0x48820C],EAX
     *  0042CE28   E8 A352FFFF      CALL .004220D0  ; jichi: name thread
     *  0042CE2D   C705 08024D00 01>MOV DWORD PTR DS:[0x4D0208],0x1
     *  0042CE37   EB 52            JMP SHORT .0042CE8B
     *  0042CE39   392D 08024D00    CMP DWORD PTR DS:[0x4D0208],EBP
     *  0042CE3F   74 08            JE SHORT .0042CE49
     *  0042CE41   392D 205BB900    CMP DWORD PTR DS:[0xB95B20],EBP
     *  0042CE47   74 07            JE SHORT .0042CE50
     *  0042CE49   C605 E0F0B700 00 MOV BYTE PTR DS:[0xB7F0E0],0x0
     *  0042CE50   8D5424 40        LEA EDX,DWORD PTR SS:[ESP+0x40]
     *  0042CE54   52               PUSH EDX
     *  0042CE55   68 30B5BA00      PUSH .00BAB530
     *  0042CE5A   892D 08024D00    MOV DWORD PTR DS:[0x4D0208],EBP
     *  0042CE60   E8 6B52FFFF      CALL .004220D0  ; jichi: scenario thread
     *  0042CE65   C705 A0814800 FF>MOV DWORD PTR DS:[0x4881A0],-0x1
     *  0042CE6F   892D 2C824800    MOV DWORD PTR DS:[0x48822C],EBP
     *
     *  Sample game: 水夏弐律
     *
     *  004201ce     cc             int3
     *  004201cf     cc             int3
     *  004201d0  /$ 8b4c24 08      mov ecx,dword ptr ss:[esp+0x8]
     *  004201d4  |. 8a01           mov al,byte ptr ds:[ecx]
     *  004201d6  |. 84c0           test al,al
     *  004201d8  |. 74 1c          je short dc3.004201f6
     *  004201da  |. 8b5424 04      mov edx,dword ptr ss:[esp+0x4]
     *  004201de  |. 8bff           mov edi,edi
     *  004201e0  |> 3c 24          /cmp al,0x24
     *  004201e2  |. 75 05          |jnz short dc3.004201e9
     *  004201e4  |. 83c1 02        |add ecx,0x2
     *  004201e7  |. eb 04          |jmp short dc3.004201ed
     *  004201e9  |> 8802           |mov byte ptr ds:[edx],al
     *  004201eb  |. 42             |inc edx
     *  004201ec  |. 41             |inc ecx
     *  004201ed  |> 8a01           |mov al,byte ptr ds:[ecx]
     *  004201ef  |. 84c0           |test al,al
     *  004201f1  |.^75 ed          \jnz short dc3.004201e0
     *  004201f3  |. 8802           mov byte ptr ds:[edx],al
     *  004201f5  |. c3             retn
     *  004201f6  |> 8b4424 04      mov eax,dword ptr ss:[esp+0x4]
     *  004201fa  |. c600 00        mov byte ptr ds:[eax],0x0
     *  004201fd  \. c3             retn
     *
     *  Sample registers:
     *  EAX 0012F998
     *  ECX 000000DB
     *  EDX 00000059
     *  EBX 00000000    ; ebx is zero for name/scenario thread
     *  ESP 0012F96C
     *  EBP 00000003
     *  ESI 00000025
     *  EDI 000000DB
     *  EIP 022C0000
     *
     *  EAX 0012F174
     *  ECX 0012F7CC
     *  EDX FDFBF80C
     *  EBX 0012F6CC
     *  ESP 0012F15C
     *  EBP 0012F5CC
     *  ESI 800000DB
     *  EDI 00000001
     *  EIP 00420460 .00420460
     *
     *  EAX 0012F174
     *  ECX 0012F7CC
     *  EDX FDFBF7DF
     *  EBX 0012F6CC
     *  ESP 0012F15C
     *  EBP 0012F5CC
     *  ESI 00000108
     *  EDI 00000001
     *  EIP 00420460 .00420460
     *
     *  0042DC5D   52               PUSH EDX
     *  0042DC5E   68 E038AC00      PUSH .00AC38E0                           ; ASCII "Ami"
     *  0042DC63   E8 F827FFFF      CALL .00420460  ; jichi: name thread
     *  0042DC68   83C4 08          ADD ESP,0x8
     *  0042DC6B   E9 48000000      JMP .0042DCB8
     *  0042DC70   83FD 58          CMP EBP,0x58
     *  0042DC73   74 07            JE SHORT .0042DC7C
     *  0042DC75   C605 E038AC00 00 MOV BYTE PTR DS:[0xAC38E0],0x0
     *  0042DC7C   8D4424 20        LEA EAX,DWORD PTR SS:[ESP+0x20]
     *  0042DC80   50               PUSH EAX
     *  0042DC81   68 0808AF00      PUSH .00AF0808
     *  0042DC86   E8 D527FFFF      CALL .00420460 ; jichi: scenario thread
     *  0042DC8B   83C4 08          ADD ESP,0x8
     *  0042DC8E   33C0             XOR EAX,EAX
     *  0042DC90   C705 D0DF4700 FF>MOV DWORD PTR DS:[0x47DFD0],-0x1
     *  0042DC9A   A3 0CE04700      MOV DWORD PTR DS:[0x47E00C],EAX
     *  0042DC9F   A3 940EB200      MOV DWORD PTR DS:[0xB20E94],EAX
     *  0042DCA4   A3 2C65AC00      MOV DWORD PTR DS:[0xAC652C],EAX
     *  0042DCA9   C705 50F9AC00 59>MOV DWORD PTR DS:[0xACF950],0x59
     *  0042DCB3   A3 3C70AE00      MOV DWORD PTR DS:[0xAE703C],EAX
     */
    bool attach(ULONG startAddress, ULONG stopAddress)
    {
      ULONG addr = Private::findFunctionAddress(startAddress, stopAddress);
      if (!addr)
        return false;
      // Find the nearest two callers (distance within 100)
      ULONG lastCall = 0;
      auto fun = [&lastCall](ULONG call) -> bool
      {
        // scenario: 0x42b78c
        // name: 0x42b754
        if (call - lastCall < 100)
        {
          Private::scenarioReturnAddress_ = call + 5;
          Private::nameReturnAddress_ = lastCall + 5;
          return false; // found target
        }
        lastCall = call;
        return true; // replace all functions
      };
      MemDbg::iterNearCallAddress(fun, addr, startAddress, stopAddress);
      if (!Private::scenarioReturnAddress_ && lastCall)
      {
        Private::scenarioReturnAddress_ = lastCall + 5;
      }
      HookParam hp;
      hp.address = addr;
      hp.filter_fun = filter;
      hp.text_fun = Private::hookBefore;
      hp.embed_fun = Private::hookafter;
      hp.embed_hook_font = F_GetGlyphOutlineA;
      hp.type = USING_STRING | EMBED_ABLE | NO_CONTEXT | EMBED_DYNA_SJIS;

      return NewHook(hp, "EmbedCircus");
    }

  } // namespace ScenarioHook

} // unnamed namespace

bool Circus2::attach_function()
{
  bool ch2 = InsertCircusHook2();
  bool _1 = ch2 || c3() || c2();
  bool embed = ScenarioHook::attach(processStartAddress, processStopAddress);
  return _1 || embed;
}