#include "Escude.h"
/** jichi 7/23/2015 Escude
 *  Sample game: Re;Lord ��ルフォルト�魔女とぬぁ�るみ *  See: http://capita.tistory.com/m/post/210
 *
 *  ENCODEKOR,FORCEFONT(5),HOOK(0x0042CB40,TRANS([[ESP+0x4]+0x20],PTRCHEAT,PTRBACKUP,SAFE),RETNPOS(SOURCE)),FONT(Malgun Gothic,-13)
 *
 *  GDI functions: TextOutA, GetTextExtentPoint32A
 *  It requires changing function to MS Gothic using configure.exe
 *
 *  Text in arg1 + 0x20
 *
 *  0042CB3C   CC               INT3
 *  0042CB3D   CC               INT3
 *  0042CB3E   CC               INT3
 *  0042CB3F   CC               INT3
 *  0042CB40   56               PUSH ESI
 *  0042CB41   8B7424 08        MOV ESI,DWORD PTR SS:[ESP+0x8]
 *  0042CB45   8B06             MOV EAX,DWORD PTR DS:[ESI]
 *  0042CB47   50               PUSH EAX
 *  0042CB48   E8 53FC0A00      CALL .004DC7A0
 *  0042CB4D   8B56 04          MOV EDX,DWORD PTR DS:[ESI+0x4]
 *  0042CB50   83C4 04          ADD ESP,0x4
 *  0042CB53   5E               POP ESI
 *  0042CB54   85D2             TEST EDX,EDX
 *  0042CB56   74 7E            JE SHORT .0042CBD6
 *  0042CB58   85C0             TEST EAX,EAX
 *  0042CB5A   74 07            JE SHORT .0042CB63
 *  0042CB5C   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  0042CB5E   8B49 04          MOV ECX,DWORD PTR DS:[ECX+0x4]
 *  0042CB61   EB 02            JMP SHORT .0042CB65
 *  0042CB63   33C9             XOR ECX,ECX
 *  0042CB65   890A             MOV DWORD PTR DS:[EDX],ECX
 *  0042CB67   85C0             TEST EAX,EAX
 *  0042CB69   74 07            JE SHORT .0042CB72
 *  0042CB6B   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  0042CB6D   8B49 08          MOV ECX,DWORD PTR DS:[ECX+0x8]
 *  0042CB70   EB 02            JMP SHORT .0042CB74
 *  0042CB72   33C9             XOR ECX,ECX
 *  0042CB74   894A 04          MOV DWORD PTR DS:[EDX+0x4],ECX
 *  0042CB77   85C0             TEST EAX,EAX
 *  0042CB79   74 08            JE SHORT .0042CB83
 *  0042CB7B   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  0042CB7D   0FB749 0E        MOVZX ECX,WORD PTR DS:[ECX+0xE]
 *  0042CB81   EB 02            JMP SHORT .0042CB85
 *  0042CB83   33C9             XOR ECX,ECX
 *  0042CB85   0FB7C9           MOVZX ECX,CX
 *  0042CB88   894A 08          MOV DWORD PTR DS:[EDX+0x8],ECX
 *  0042CB8B   85C0             TEST EAX,EAX
 *  0042CB8D   74 19            JE SHORT .0042CBA8
 *  0042CB8F   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  0042CB91   8379 04 00       CMP DWORD PTR DS:[ECX+0x4],0x0
 *  0042CB95   76 11            JBE SHORT .0042CBA8
 *  0042CB97   8B49 08          MOV ECX,DWORD PTR DS:[ECX+0x8]
 *  0042CB9A   85C9             TEST ECX,ECX
 *  0042CB9C   76 0A            JBE SHORT .0042CBA8
 *  0042CB9E   49               DEC ECX
 *  0042CB9F   0FAF48 0C        IMUL ECX,DWORD PTR DS:[EAX+0xC]
 *  0042CBA3   0348 04          ADD ECX,DWORD PTR DS:[EAX+0x4]
 *  0042CBA6   EB 02            JMP SHORT .0042CBAA
 *  0042CBA8   33C9             XOR ECX,ECX
 *  0042CBAA   894A 0C          MOV DWORD PTR DS:[EDX+0xC],ECX
 *  0042CBAD   85C0             TEST EAX,EAX
 *  0042CBAF   74 16            JE SHORT .0042CBC7
 *  0042CBB1   8B48 0C          MOV ECX,DWORD PTR DS:[EAX+0xC]
 *  0042CBB4   F7D9             NEG ECX
 *  0042CBB6   894A 10          MOV DWORD PTR DS:[EDX+0x10],ECX
 *  0042CBB9   8B00             MOV EAX,DWORD PTR DS:[EAX]
 *  0042CBBB   83C0 28          ADD EAX,0x28
 *  0042CBBE   8942 14          MOV DWORD PTR DS:[EDX+0x14],EAX
 *  0042CBC1   B8 01000000      MOV EAX,0x1
 *  0042CBC6   C3               RETN
 *  0042CBC7   33C9             XOR ECX,ECX
 *  0042CBC9   F7D9             NEG ECX
 *  0042CBCB   894A 10          MOV DWORD PTR DS:[EDX+0x10],ECX
 *  0042CBCE   8B00             MOV EAX,DWORD PTR DS:[EAX]
 *  0042CBD0   83C0 28          ADD EAX,0x28
 *  0042CBD3   8942 14          MOV DWORD PTR DS:[EDX+0x14],EAX
 *  0042CBD6   B8 01000000      MOV EAX,0x1
 *  0042CBDB   C3               RETN
 *  0042CBDC   CC               INT3
 *  0042CBDD   CC               INT3
 *  0042CBDE   CC               INT3
 *  0042CBDF   CC               INT3
 *  0042CBE0   8B4424 04        MOV EAX,DWORD PTR SS:[ESP+0x4]
 *  0042CBE4   8B48 10          MOV ECX,DWORD PTR DS:[EAX+0x10]
 *  0042CBE7   8B50 0C          MOV EDX,DWORD PTR DS:[EAX+0xC]
 *  0042CBEA   51               PUSH ECX
 *  0042CBEB   8B48 08          MOV ECX,DWORD PTR DS:[EAX+0x8]
 *  0042CBEE   52               PUSH EDX
 *  0042CBEF   8B50 04          MOV EDX,DWORD PTR DS:[EAX+0x4]
 *  0042CBF2   8B00             MOV EAX,DWORD PTR DS:[EAX]
 *  0042CBF4   51               PUSH ECX
 *  0042CBF5   52               PUSH EDX
 *  0042CBF6   50               PUSH EAX
 *  0042CBF7   E8 E4FD0A00      CALL .004DC9E0
 *  0042CBFC   83C4 14          ADD ESP,0x14
 *  0042CBFF   C3               RETN
 *  0042CC00   8B4424 04        MOV EAX,DWORD PTR SS:[ESP+0x4]
 *  0042CC04   8B48 10          MOV ECX,DWORD PTR DS:[EAX+0x10]
 *  0042CC07   8B50 0C          MOV EDX,DWORD PTR DS:[EAX+0xC]
 *  0042CC0A   51               PUSH ECX
 *  0042CC0B   8B48 08          MOV ECX,DWORD PTR DS:[EAX+0x8]
 *  0042CC0E   52               PUSH EDX
 *  0042CC0F   8B50 04          MOV EDX,DWORD PTR DS:[EAX+0x4]
 *  0042CC12   8B00             MOV EAX,DWORD PTR DS:[EAX]
 *  0042CC14   51               PUSH ECX
 *  0042CC15   52               PUSH EDX
 *  0042CC16   50               PUSH EAX
 *  0042CC17   E8 C4FF0A00      CALL .004DCBE0
 *  0042CC1C   83C4 14          ADD ESP,0x14
 *  0042CC1F   C3               RETN
 *  0042CC20   8B4424 04        MOV EAX,DWORD PTR SS:[ESP+0x4]
 *  0042CC24   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  0042CC26   894C24 04        MOV DWORD PTR SS:[ESP+0x4],ECX
 *  0042CC2A   E9 71FB0A00      JMP .004DC7A0
 *  0042CC2F   CC               INT3
 *  0042CC30   56               PUSH ESI
 *  0042CC31   8B7424 08        MOV ESI,DWORD PTR SS:[ESP+0x8]
 *  0042CC35   8B06             MOV EAX,DWORD PTR DS:[ESI]
 *  0042CC37   50               PUSH EAX
 *  0042CC38   E8 63FB0A00      CALL .004DC7A0
 *  0042CC3D   D946 0C          FLD DWORD PTR DS:[ESI+0xC]
 *  0042CC40   D91C24           FSTP DWORD PTR SS:[ESP]
 *  0042CC43   83EC 08          SUB ESP,0x8
 *  0042CC46   D946 08          FLD DWORD PTR DS:[ESI+0x8]
 *  0042CC49   D95C24 04        FSTP DWORD PTR SS:[ESP+0x4]
 *  0042CC4D   D946 04          FLD DWORD PTR DS:[ESI+0x4]
 *  0042CC50   D91C24           FSTP DWORD PTR SS:[ESP]
 *  0042CC53   50               PUSH EAX
 *  0042CC54   E8 27680400      CALL .00473480
 *  0042CC59   83C4 10          ADD ESP,0x10
 *  0042CC5C   B8 01000000      MOV EAX,0x1
 *  0042CC61   5E               POP ESI
 *  0042CC62   C3               RETN
 *  0042CC63   CC               INT3
 *  0042CC64   CC               INT3
 *  0042CC65   CC               INT3
 *  0042CC66   CC               INT3
 *  0042CC67   CC               INT3
 *  0042CC68   CC               INT3
 *  0042CC69   CC               INT3 *
 */
namespace
{ // unnamed
  /**
   *  Handle new lines and ruby.
   *
   *  そ�日、彼の言葉に耳を傾ける�ぁ�かった� *  ザールラント歴丹�〹�　二ノ月二十日<r>グローセン州　ヘルフォルト区郊� *
   *  僁�な霋�の後�r><ruby text='まぶ�>瞼</ruby>の裏を焼く陽光に気付いた� *
   *  気�く重�ruby text='まぶ�>瞼</ruby>を開け��r>見覚えのある輪郭が瞳に�り込む� *
   *  そ�日、彼の言葉に耳を傾ける�ぁ�かった。――尊厳を捨てて媚�る。それが生きることか？――��ぁ�敗北したのた誰しも少年の声を聞かず、蔑み、そして冷笑してぁ�。安寧の世がぁ�までも続くと信じてぁ�から。それでも、私�――。ザールラント歴丹�〹�　二ノ月二十日<r>グローセン州　ヘルフォルト区郊外僅かな霋�の後�r><ruby text='まぶ�>瞼</ruby>の裏を焼く陽光に気付いた。気�く重�ruby text='まぶ�>瞼</ruby>を開け��r>見覚えのある輪郭が瞳に�り込む
   */
  void EscudeFilter(TextBuffer *buffer, HookParam *)
  {
    auto s = buffer->strA();
    strReplace(s, "<r>", "\n");
    s = re::sub(s, "<ruby(.*?)>(.*?)</ruby>", "$2");
    buffer->from(s);
  }
  LPCSTR _escudeltrim(LPCSTR text)
  {
    if (text && *text == '<')
      for (auto p = text; (signed char)*p > 0; p++)
        if (*p == '>')
          return p + 1;
    return text;
  }
  void SpecialHookEscude(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    DWORD arg1 = context->stack[1];
    if (!arg1 || (LONG)arg1 == -1 || ::IsBadWritePtr((LPVOID)arg1, 4)) // this is indispensable
      return;
    LPCSTR text = (LPCSTR) * (DWORD *)(arg1 + 0x20);
    if (!text || ::IsBadWritePtr((LPVOID)text, 1) || !*text) // this is indispensable
      return;
    text = _escudeltrim(text);
    if (!text)
      return;
    *split = *(DWORD *)arg1;
    buffer->from(text);
  }
  struct HookArgument
  {
    ULONG split;
    // ULONG unknown1[3];
    // LPCSTR text1; // 0x10 only for old games
    ULONG unknown[7];
    LPCSTR text; // 0x20

    bool isValid() const { return Engine::isAddressWritable(text) && *text; }

    Engine::TextRole role() const
    {
      if (split >= 0xff)
        return Engine::OtherRole;
      static ULONG maxSplit_ = 0;
      if (split > maxSplit_)
        maxSplit_ = split;
      if (split == maxSplit_)
        return Engine::ScenarioRole;
      return Engine::NameRole; // scenario role is larger than name role
    }
  };
  LPCSTR trimmedText;
  void hook_before(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
  {

    auto arg = (HookArgument *)s->stack[1];
    if ((long)arg == -1 || !Engine::isAddressWritable(arg) || !arg->isValid())
      return;
    trimmedText = _escudeltrim(arg->text);
    *role = arg->role();
    buffer->from(trimmedText);
  }
  void embed_fun(hook_context *s, TextBuffer buffer)
  {
    auto data_ = buffer.strA();
    auto arg = (HookArgument *)s->stack[1];
    if (trimmedText != arg->text)
      data_.insert(0, std::string(arg->text, trimmedText - arg->text));
    arg->text = allocateString(data_);
  }
} // unnamed namespace
bool InsertEscudeHook()
{
  const BYTE bytes[] = {
      0x76, 0x0a,            // 0042cb9c   76 0a            jbe short .0042cba8
      0x49,                  // 0042cb9e   49               dec ecx
      0x0f, 0xaf, 0x48, 0x0c // 0042cb9f   0faf48 0c        imul ecx,dword ptr ds:[eax+0xc]
  };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  // GROWL(addr);
  if (!addr)
  {
    ConsoleOutput("Escude: pattern not found");
    return false;
  }
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
  {
    ConsoleOutput("Escude: enclosing function not found");
    return false;
  }
  HookParam hp;
  hp.address = addr;
  hp.text_fun = hook_before;
  hp.embed_fun = embed_fun;
  hp.embed_hook_font = F_TextOutA | F_GetTextExtentPoint32A;
  hp.text_fun = SpecialHookEscude;
  hp.filter_fun = EscudeFilter;
  hp.type = USING_STRING | USING_SPLIT | NO_CONTEXT | EMBED_ABLE | EMBED_DYNA_SJIS; // NO_CONTEXT as this function is only called by one caller anyway
  hp.lineSeparator = L"<r>";
  ConsoleOutput("INSERT Escude");

  return NewHook(hp, "Escude");
}

bool Escude::attach_function()
{
  return InsertEscudeHook();
}