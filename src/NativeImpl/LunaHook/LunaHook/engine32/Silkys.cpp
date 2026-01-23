#include "Silkys.h"
#include "util/textunion.h"

/** jichi: 6/17/2015
 *  Sample games
 *  - 堕ちてぁ�新妻 trial
 *  - 根雪の幻影 trial
 *
 *  This function is found by backtracking GetGlyphOutlineA.
 *  There are two GetGlyphOutlineA, which are in the same function.
 *  That function are called by two other functions.
 *  The second function is hooked.
 *
 *  堕ちてぁ�新妻
 *  baseaddr = 08e0000
 *
 *  0096652E   CC               INT3
 *  0096652F   CC               INT3
 *  00966530   55               PUSH EBP
 *  00966531   8BEC             MOV EBP,ESP
 *  00966533   83EC 18          SUB ESP,0x18
 *  00966536   A1 00109F00      MOV EAX,DWORD PTR DS:[0x9F1000]
 *  0096653B   33C5             XOR EAX,EBP
 *  0096653D   8945 FC          MOV DWORD PTR SS:[EBP-0x4],EAX
 *  00966540   53               PUSH EBX
 *  00966541   8B5D 0C          MOV EBX,DWORD PTR SS:[EBP+0xC]
 *  00966544   56               PUSH ESI
 *  00966545   8B75 08          MOV ESI,DWORD PTR SS:[EBP+0x8]
 *  00966548   57               PUSH EDI
 *  00966549   6A 00            PUSH 0x0
 *  0096654B   894D EC          MOV DWORD PTR SS:[EBP-0x14],ECX
 *  0096654E   8B0D FCB7A200    MOV ECX,DWORD PTR DS:[0xA2B7FC]
 *  00966554   68 90D29D00      PUSH .009DD290                           ; ASCII "/Config/SceneSkip"
 *  00966559   895D F0          MOV DWORD PTR SS:[EBP-0x10],EBX
 *  0096655C   E8 2F4A0100      CALL .0097AF90
 *  00966561   83F8 01          CMP EAX,0x1
 *  00966564   0F84 E0010000    JE .0096674A
 *  0096656A   8B55 EC          MOV EDX,DWORD PTR SS:[EBP-0x14]
 *  0096656D   85DB             TEST EBX,EBX
 *  0096656F   75 09            JNZ SHORT .0096657A
 *  00966571   8B42 04          MOV EAX,DWORD PTR DS:[EDX+0x4]
 *  00966574   8B40 38          MOV EAX,DWORD PTR DS:[EAX+0x38]
 *  00966577   8945 F0          MOV DWORD PTR SS:[EBP-0x10],EAX
 *  0096657A   33C0             XOR EAX,EAX
 *  0096657C   C645 F8 00       MOV BYTE PTR SS:[EBP-0x8],0x0
 *  00966580   33C9             XOR ECX,ECX
 *  00966582   66:8945 F9       MOV WORD PTR SS:[EBP-0x7],AX
 *  00966586   3946 14          CMP DWORD PTR DS:[ESI+0x14],EAX
 *  00966589   0F86 BB010000    JBE .0096674A
 *
 *  Scenario stack:
 *
 *  002FF9DC   00955659  RETURN to .00955659 from .00966530
 *  002FF9E0   002FFA10  ; jichi: text in [arg1+4]
 *  002FF9E4   00000000  ; arg2 is zero
 *  002FF9E8   00000001
 *  002FF9EC   784B8FC7
 *
 *  Name stack:
 *
 *  002FF59C   00930A76  RETURN to .00930A76 from .00966530
 *  002FF5A0   002FF5D0 ; jichi: text in [arg1+4]
 *  002FF5A4   004DDEC0 ; arg2 is a pointer
 *  002FF5A8   00000001
 *  002FF5AC   784B8387
 *  002FF5B0   00000182
 *  002FF5B4   00000000
 *
 *  Scenario and Name are called by different callers.
 *
 *  根雪の幻影
 *
 *  00A1A00E   CC               INT3
 *  00A1A00F   CC               INT3
 *  00A1A010   55               PUSH EBP
 *  00A1A011   8BEC             MOV EBP,ESP
 *  00A1A013   83EC 18          SUB ESP,0x18
 *  00A1A016   A1 0050AA00      MOV EAX,DWORD PTR DS:[0xAA5000]
 *  00A1A01B   33C5             XOR EAX,EBP
 *  00A1A01D   8945 FC          MOV DWORD PTR SS:[EBP-0x4],EAX
 *  00A1A020   53               PUSH EBX
 *  00A1A021   56               PUSH ESI
 *  00A1A022   8B75 0C          MOV ESI,DWORD PTR SS:[EBP+0xC]
 *  00A1A025   57               PUSH EDI
 *  00A1A026   8B7D 08          MOV EDI,DWORD PTR SS:[EBP+0x8]
 *  00A1A029   6A 00            PUSH 0x0
 *  00A1A02B   894D F0          MOV DWORD PTR SS:[EBP-0x10],ECX
 *  00A1A02E   8B0D C434AE00    MOV ECX,DWORD PTR DS:[0xAE34C4]
 *  00A1A034   68 F816A900      PUSH .00A916F8                           ; ASCII "/Config/SceneSkip"
 *  00A1A039   8975 EC          MOV DWORD PTR SS:[EBP-0x14],ESI
 *  00A1A03C   E8 7F510100      CALL .00A2F1C0
 *  00A1A041   83F8 01          CMP EAX,0x1
 *  00A1A044   0F84 3A010000    JE .00A1A184
 *  00A1A04A   8B4D F0          MOV ECX,DWORD PTR SS:[EBP-0x10]
 *  00A1A04D   85F6             TEST ESI,ESI
 *  00A1A04F   75 09            JNZ SHORT .00A1A05A
 *  00A1A051   8B41 04          MOV EAX,DWORD PTR DS:[ECX+0x4]
 *  00A1A054   8B40 38          MOV EAX,DWORD PTR DS:[EAX+0x38]
 *  00A1A057   8945 EC          MOV DWORD PTR SS:[EBP-0x14],EAX
 *  00A1A05A   33C0             XOR EAX,EAX
 *  00A1A05C   C645 F8 00       MOV BYTE PTR SS:[EBP-0x8],0x0
 *  00A1A060   33DB             XOR EBX,EBX
 *  00A1A062   66:8945 F9       MOV WORD PTR SS:[EBP-0x7],AX
 *  00A1A066   3947 14          CMP DWORD PTR DS:[EDI+0x14],EAX
 *  00A1A069   0F86 15010000    JBE .00A1A184
 *  00A1A06F   90               NOP
 *  00A1A070   837F 18 10       CMP DWORD PTR DS:[EDI+0x18],0x10
 *  00A1A074   72 05            JB SHORT .00A1A07B
 *  00A1A076   8B47 04          MOV EAX,DWORD PTR DS:[EDI+0x4]
 *  00A1A079   EB 03            JMP SHORT .00A1A07E
 *  00A1A07B   8D47 04          LEA EAX,DWORD PTR DS:[EDI+0x4]
 *  00A1A07E   803C18 00        CMP BYTE PTR DS:[EAX+EBX],0x0
 *  00A1A082   0F84 FC000000    JE .00A1A184
 *  00A1A088   837F 18 10       CMP DWORD PTR DS:[EDI+0x18],0x10
 *  00A1A08C   72 05            JB SHORT .00A1A093
 *  00A1A08E   8B47 04          MOV EAX,DWORD PTR DS:[EDI+0x4]
 *  00A1A091   EB 03            JMP SHORT .00A1A096
 *  00A1A093   8D47 04          LEA EAX,DWORD PTR DS:[EDI+0x4]
 *  00A1A096   8A0418           MOV AL,BYTE PTR DS:[EAX+EBX]
 *  00A1A099   3C 81            CMP AL,0x81
 *  00A1A09B   72 04            JB SHORT .00A1A0A1
 *  00A1A09D   3C 9F            CMP AL,0x9F
 *  00A1A09F   76 06            JBE SHORT .00A1A0A7
 *  00A1A0A1   04 20            ADD AL,0x20
 *  00A1A0A3   3C 0F            CMP AL,0xF
 *  00A1A0A5   77 40            JA SHORT .00A1A0E7
 *  00A1A0A7   837F 18 10       CMP DWORD PTR DS:[EDI+0x18],0x10
 *  00A1A0AB   72 05            JB SHORT .00A1A0B2
 *  00A1A0AD   8B47 04          MOV EAX,DWORD PTR DS:[EDI+0x4]
 *  00A1A0B0   EB 03            JMP SHORT .00A1A0B5
 *  00A1A0B2   8D47 04          LEA EAX,DWORD PTR DS:[EDI+0x4]
 *  00A1A0B5   837F 18 10       CMP DWORD PTR DS:[EDI+0x18],0x10
 *  00A1A0B9   8A0418           MOV AL,BYTE PTR DS:[EAX+EBX]
 *  00A1A0BC   8845 F8          MOV BYTE PTR SS:[EBP-0x8],AL
 *  00A1A0BF   72 13            JB SHORT .00A1A0D4
 *  00A1A0C1   8B47 04          MOV EAX,DWORD PTR DS:[EDI+0x4]
 *  00A1A0C4   C645 F7 02       MOV BYTE PTR SS:[EBP-0x9],0x2
 *  00A1A0C8   8A4418 01        MOV AL,BYTE PTR DS:[EAX+EBX+0x1]
 *  00A1A0CC   83C3 02          ADD EBX,0x2
 *  00A1A0CF   8845 F9          MOV BYTE PTR SS:[EBP-0x7],AL
 *  00A1A0D2   EB 30            JMP SHORT .00A1A104
 *  00A1A0D4   8D47 04          LEA EAX,DWORD PTR DS:[EDI+0x4]
 *  00A1A0D7   C645 F7 02       MOV BYTE PTR SS:[EBP-0x9],0x2
 *  00A1A0DB   8A4418 01        MOV AL,BYTE PTR DS:[EAX+EBX+0x1]
 *  00A1A0DF   83C3 02          ADD EBX,0x2
 *  00A1A0E2   8845 F9          MOV BYTE PTR SS:[EBP-0x7],AL
 *  00A1A0E5   EB 1D            JMP SHORT .00A1A104
 *  00A1A0E7   837F 18 10       CMP DWORD PTR DS:[EDI+0x18],0x10
 *  00A1A0EB   72 05            JB SHORT .00A1A0F2
 *  00A1A0ED   8B47 04          MOV EAX,DWORD PTR DS:[EDI+0x4]
 *  00A1A0F0   EB 03            JMP SHORT .00A1A0F5
 *  00A1A0F2   8D47 04          LEA EAX,DWORD PTR DS:[EDI+0x4]
 *  00A1A0F5   8A0418           MOV AL,BYTE PTR DS:[EAX+EBX]
 *  00A1A0F8   43               INC EBX
 *  00A1A0F9   8845 F8          MOV BYTE PTR SS:[EBP-0x8],AL
 *  00A1A0FC   C645 F9 00       MOV BYTE PTR SS:[EBP-0x7],0x0
 *  00A1A100   C645 F7 01       MOV BYTE PTR SS:[EBP-0x9],0x1
 *  00A1A104   807F 48 01       CMP BYTE PTR DS:[EDI+0x48],0x1
 *  00A1A108   75 21            JNZ SHORT .00A1A12B
 *  00A1A10A   8B49 08          MOV ECX,DWORD PTR DS:[ECX+0x8]
 *  00A1A10D   8D47 38          LEA EAX,DWORD PTR DS:[EDI+0x38]
 *  00A1A110   50               PUSH EAX
 *  00A1A111   FF77 28          PUSH DWORD PTR DS:[EDI+0x28]
 *  00A1A114   8B47 24          MOV EAX,DWORD PTR DS:[EDI+0x24]
 *  00A1A117   03C0             ADD EAX,EAX
 *  00A1A119   50               PUSH EAX
 *  00A1A11A   8D47 20          LEA EAX,DWORD PTR DS:[EDI+0x20]
 *  00A1A11D   50               PUSH EAX
 *  00A1A11E   8D47 1C          LEA EAX,DWORD PTR DS:[EDI+0x1C]
 *  00A1A121   50               PUSH EAX
 *  00A1A122   8D45 F8          LEA EAX,DWORD PTR SS:[EBP-0x8]
 *  00A1A125   50               PUSH EAX
 *  00A1A126   E8 85220000      CALL .00A1C3B0
 *  00A1A12B   FF77 34          PUSH DWORD PTR DS:[EDI+0x34]
 *  00A1A12E   8B4D EC          MOV ECX,DWORD PTR SS:[EBP-0x14]
 *  00A1A131   8D45 F8          LEA EAX,DWORD PTR SS:[EBP-0x8]
 *  00A1A134   FF77 4C          PUSH DWORD PTR DS:[EDI+0x4C]
 *  00A1A137   FF77 30          PUSH DWORD PTR DS:[EDI+0x30]
 *  00A1A13A   FF77 2C          PUSH DWORD PTR DS:[EDI+0x2C]
 *  00A1A13D   FF77 20          PUSH DWORD PTR DS:[EDI+0x20]
 *  00A1A140   FF77 1C          PUSH DWORD PTR DS:[EDI+0x1C]
 *  00A1A143   50               PUSH EAX
 *  00A1A144   E8 1733FFFF      CALL .00A0D460
 *  00A1A149   0FBE45 F7        MOVSX EAX,BYTE PTR SS:[EBP-0x9]
 *  00A1A14D   0FAF47 24        IMUL EAX,DWORD PTR DS:[EDI+0x24]
 *  00A1A151   0147 1C          ADD DWORD PTR DS:[EDI+0x1C],EAX
 *  00A1A154   807F 48 00       CMP BYTE PTR DS:[EDI+0x48],0x0
 *  00A1A158   8B47 1C          MOV EAX,DWORD PTR DS:[EDI+0x1C]
 *  00A1A15B   75 1B            JNZ SHORT .00A1A178
 *  00A1A15D   3947 40          CMP DWORD PTR DS:[EDI+0x40],EAX
 *  00A1A160   7F 16            JG SHORT .00A1A178
 *  00A1A162   8B47 38          MOV EAX,DWORD PTR DS:[EDI+0x38]
 *  00A1A165   8B4F 28          MOV ECX,DWORD PTR DS:[EDI+0x28]
 *  00A1A168   014F 20          ADD DWORD PTR DS:[EDI+0x20],ECX
 *  00A1A16B   8947 1C          MOV DWORD PTR DS:[EDI+0x1C],EAX
 *  00A1A16E   8B47 20          MOV EAX,DWORD PTR DS:[EDI+0x20]
 *  00A1A171   03C1             ADD EAX,ECX
 *  00A1A173   3B47 44          CMP EAX,DWORD PTR DS:[EDI+0x44]
 *  00A1A176   7D 0C            JGE SHORT .00A1A184
 *  00A1A178   8B4D F0          MOV ECX,DWORD PTR SS:[EBP-0x10]
 *  00A1A17B   3B5F 14          CMP EBX,DWORD PTR DS:[EDI+0x14]
 *  00A1A17E  ^0F82 ECFEFFFF    JB .00A1A070
 *  00A1A184   8B4D FC          MOV ECX,DWORD PTR SS:[EBP-0x4]
 *  00A1A187   5F               POP EDI
 *  00A1A188   5E               POP ESI
 *  00A1A189   33CD             XOR ECX,EBP
 *  00A1A18B   5B               POP EBX
 *  00A1A18C   E8 87600200      CALL .00A40218
 *  00A1A191   8BE5             MOV ESP,EBP
 *  00A1A193   5D               POP EBP
 *  00A1A194   C2 0C00          RETN 0xC
 *  00A1A197   CC               INT3
 *  00A1A198   CC               INT3
 */
static void SpecialHookSilkys(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  // DWORD arg1 = *(DWORD *)(esp_base + 0x4);
  DWORD arg1 = context->stack[1],
        arg2 = context->stack[2];

  int size = *(DWORD *)(arg1 + 0x14);
  if (size <= 0)
    return;

  enum
  {
    ShortTextCapacity = 0x10
  };

  DWORD text = 0;
  // if (arg2 == 0) {
  if (size >= ShortTextCapacity)
  {
    text = *(DWORD *)(arg1 + 4);
    if (text && ::IsBadReadPtr((LPCVOID)text, size)) // this might not be needed though
      text = 0;
  }
  if (!text)
  { // short text
    text = arg1 + 4;
    size = min(size, ShortTextCapacity);
  }
  buffer->from(text, size);
  *split = arg2 == 0 ? 1 : 2; // arg2 == 0 ? scenario : name
}
void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
{
  auto arg = (TextUnionA *)(s->stack[0] + sizeof(DWORD)); // arg1
  if (!arg || !arg->isValid())
    return;

  // FIXME: I am not able to distinguish choice out
  *role =
      s->stack[1] ? Engine::NameRole : // arg2 != 0 for name
                                       // s->ebx > 0x0fffffff ? Engine::ChoiceRole : // edx is a pointer for choice
          Engine::ScenarioRole;

  buffer->from(arg->view());
}
TextUnionA *arg_,
    argValue_;
void hookafter1(hook_context *s, TextBuffer buffer, HookParam *)
{
  auto newData = buffer.strA();
  auto arg = (TextUnionA *)(s->stack[0] + sizeof(DWORD)); // arg1
  arg_ = arg;
  argValue_ = *arg;
  arg->setText(newData);
}

void hookAfter(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  if (arg_)
  {
    *arg_ = argValue_;
    arg_ = nullptr;
  }
}
bool InsertSilkysHook()
{
  const BYTE bytes[] = {
      0x66, 0x89, 0x45, 0xf9, // 00a1a062   66:8945 f9       mov word ptr ss:[ebp-0x7],ax
      0x39, 0x47, 0x14        // 00a1a066   3947 14          cmp dword ptr ds:[edi+0x14],eax
  };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
  {
    ConsoleOutput("Silkys: pattern not found");
    return false;
  }

  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
  {
    ConsoleOutput("Silkys: function not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.text_fun = SpecialHookSilkys;
  hp.type = USING_STRING | NO_CONTEXT; // = 9

  ConsoleOutput("INSERT Silkys");
  auto succ = NewHook(hp, "SilkysPlus");
  auto fun = [](ULONG addr) -> bool
  {
    auto succ_ = false;
    {
      HookParam hp;
      hp.address = addr;
      hp.type = USING_STRING | NO_CONTEXT | EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT;
      hp.text_fun = hookBefore;
      hp.embed_fun = hookafter1;
      hp.embed_hook_font = F_GetGlyphOutlineA;
      succ_ |= NewHook(hp, "EmbedSilkys");
    }
    {
      HookParam hp;
      hp.address = addr + 5;
      hp.text_fun = hookAfter;
      succ_ |= NewHook(hp, "EmbedSilkys");
    }
    return succ_; // replace all functions
  };
  succ |= MemDbg::iterNearCallAddress(fun, addr, processStartAddress, processStopAddress);
  return succ;
}
bool InsertSilkysHook2()
{
  //[230825] [コンフィチュールソフト] ギャル×オタ ～織川きららはお世話したい～
  auto addr = MemDbg::findCallerAddressAfterInt3((DWORD)GetCharacterPlacementW, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  BYTE sig[] = {
      0x8b, 0x80, XX4,
      0xff, 0xd0,
      0x8b, 0xf0};
  addr = MemDbg::findBytes(sig, sizeof(sig), addr, addr + 0x100);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr + 8;
  hp.type = CODEC_UTF16 | USING_STRING;
  hp.offset = regoffset(eax);
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    static int idx = 0;
    if (idx % 2)
      buffer->clear();
    idx += 1;
  };
  return NewHook(hp, "SilkysPlus2");
}
namespace
{
  bool _s()
  {
    /// https://vndb.org/r68491
    // 徒花異譚 / Adabana Odd Tales
    BYTE sig[] = {
        0xBA, 0x00, 0x01, 0x00, 0x00,
        0xC7, 0x45, 0x08, 0x14, 0x20, 0x00, 0x00,
        0x8D, 0x49, 0x00};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = findfuncstart(addr);
    if (!addr)
      return 0;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.lineSeparator = L"\\n";
    hp.type = USING_STRING | CODEC_UTF16 | EMBED_ABLE | EMBED_AFTER_NEW;
    return NewHook(hp, "EmbedSilkysX");
  }
}
namespace
{

  bool InsertSilkys2Hook()
  {
    // https://vndb.org/r89173
    // 同级生Remake
    const BYTE bytes[] = {
        // (unsigned __int16)v13 < 0x100u || (_WORD)v13 == 8212
        0xC7, 0x45, XX, 0x00, 0x01, 0x00, 0x00,
        0xC7, 0x45, XX, 0x14, 0x20, 0x00, 0x00};
    const BYTE bytes2[] = {
        // v6 = (_WORD *)(*v8 + *(_DWORD *)(v7 + 4 * v27));
        // hook v6
        0x8b, 0x4d, 0xf4,
        0x8b, 0x3c, 0x8f,
        0x03, 0x38};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = reverseFindBytes(bytes2, sizeof(bytes2), addr - 0x100, addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr + sizeof(bytes2);
    hp.offset = regoffset(edi);
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
      StringCharReplacer(buffer, TEXTANDLEN(L"\\i"), L'\'');
    };
    hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
    return NewHook(hp, "Silkys2");
  }
}
namespace
{
  bool saiminset()
  {
    //[230929][1237052][シルキーズSAKURA] 催眠奪女Set パッケージ版
    auto addr1 = findiatcallormov((DWORD)GetGlyphOutlineA, processStartAddress, processStartAddress, processStopAddress);
    if (addr1 == 0)
      return false;
    auto func1 = MemDbg::findEnclosingAlignedFunction(addr1);
    if (func1 == 0)
      return false;
    BYTE check[] = {
        0x80, 0xf9, 0x81, XX2, // cmp     cl, 81h
        0x80, 0xf9, 0x9f, XX2, // cmp     cl, 9Fh
    };
    if (MemDbg::findBytes(check, sizeof(check), func1, addr1) == 0)
      return false;
    auto xrefs = findxref_reverse_checkcallop(func1, processStartAddress, processStopAddress, 0xe8);
    if (xrefs.size() == 0)
      return false;
    auto addr2 = xrefs[0];
    auto addr = MemDbg::findEnclosingAlignedFunction(addr2);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.index = 0;
    hp.split = stackoffset(6);
    hp.type = USING_SPLIT | DATA_INDIRECT;
    return NewHook(hp, "Silkys3");
  }
}
namespace
{
  // 言の葉舞い散る夏の風鈴
  // https://vndb.org/v23466
  bool silkys4()
  {
    BYTE check[] = {
        0x80, 0xFA, 0x81,
        0x72, XX,
        0x80, 0xFA, 0x9F,
        0x76, XX};
    auto addr = MemDbg::findCallerAddress((ULONG)GetGlyphOutlineA, 0xec8b55, processStartAddress, processStopAddress);
    if (!addr)
      return false;
    if (MemDbg::findBytes(check, sizeof(check), addr, addr + 0x100) == 0)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_CHAR | DATA_INDIRECT | USING_SPLIT;
    hp.split = stackoffset(1);
    hp.offset = stackoffset(1); // thiscall arg1
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
      static int idx = 0;
      if ((idx++) % 2)
        buffer->clear();
    };
    return NewHook(hp, "Silkys4");
  }
}
namespace
{
  //[240531][1274293][シルキーズSAKURA] 淫魔淫姦 ～触手と合体して思い通りにやり返す～ DL版
  bool silkys5()
  {
    BYTE sig[] = {
        0xff, 0xd0, // call eax
        //<-- eax
        0x8b, 0x0f,
        0x8b, 0xf0, // mov esi,eax
        0x68, 0x80, 0, 0, 0,
        0x68, 0x80, 0, 0, 0,
        0x6a, 0,
        0x8b, 0x11,
        0x6a, 0};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr + 2;
    hp.type = USING_CHAR | DATA_INDIRECT | CODEC_UTF16;
    hp.offset = regoffset(eax);
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
      static int idx = 0;
      if ((idx++) % 2)
        buffer->clear();
    };
    return NewHook(hp, "silkys5");
  }
}
bool Silkys::attach_function()
{
  auto b1 = InsertSilkys2Hook();
  return InsertSilkysHook() || InsertSilkysHook2() || _s() || b1 || saiminset() || silkys4() || silkys5();
}

bool SilkysOld::attach_function()
{
  // 愛姉妹・蕾…汚してください
  auto addr = MemDbg::findCallerAddressAfterInt3((DWORD)TextOutA, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(3);
  hp.type = DATA_INDIRECT;
  return NewHook(hp, "SilkysOld");
}

bool Siglusold::attach_function()
{
  // 女系家族
  // https://vndb.org/v5650
  //   int __cdecl sub_410C20(char *a1, _DWORD *a2)
  // {
  //   unsigned __int16 v2; // dx
  //   int v3; // edi
  //   int result; // eax
  //   int v5; // eax

  //   HIBYTE(v2) = *a1;
  //   LOBYTE(v2) = a1[1];
  //   v3 = *a1;
  //   *a2 = 24 * (v2 & 0xF);
  //   if ( v2 < 0x8140u || v2 > 0x84FFu )
  //   {
  //     if ( v2 < 0x8740u || v2 > 0x879Fu )
  //     {
  //       if ( v2 < 0x8890u || v2 > 0x88FFu )
  //       {
  //         if ( v2 < 0x8940u || v2 > 0x9FFFu )
  //         {
  //           if ( v2 < 0xE040u || v2 > 0xEAA4u )
  //           {
  //             if ( v2 < 0xFA40u || v2 > 0xFAFCu )
  //             {
  //               if ( v2 < 0xFB40u || v2 > 0xFBFCu )
  //               {
  //                 if ( v2 < 0xFC40u || v2 > 0xFC4Bu )
  //                 {
  BYTE bytes[] = {
      0x66,
      XX,
      0x40,
      0x87,
      XX2,
      0x66,
      XX,
      0x9f,
      0x87,
  };
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction_strict(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_CHAR | DATA_INDIRECT;
  hp.offset = stackoffset(1);
  auto succ = NewHook(hp, "Siglusold_slow"); // 文本速度是慢速时这个有用，调成快速以后有无法过滤的重复
  auto addrs = findxref_reverse_checkcallop(addr, addr - 0x1000, addr + 0x1000, 0xe8);
  for (auto addr : addrs)
  {
    // 寻找调用者，速度为快速时调用者有正确的文本
    addr = MemDbg::findEnclosingAlignedFunction_strict(addr);
    if (!addr)
      continue;
    HookParam hpref;
    hpref.address = addr;
    hpref.codepage = 932;
    hpref.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      auto a2 = (DWORD *)context->stack[2];

      auto len1 = context->stack[3]; // 慢速时是1
      auto len2 = a2[7] - a2[6];
      if (len1 == 0 || len2 == 0)
        return;
      DWORD data, len;
      if (len1 == 1)
      { // 慢速
        hp->type = USING_CHAR;
        data = a2[5] + a2[6];
        data = *(WORD *)data;
        auto check = (BYTE)data; // 换行符
        if (IsShiftjisLeadByte(check))
        {
          buffer->from_t<WORD>(data);
        }
        else
          buffer->from_t<BYTE>(data);
      }
      else
      { // 快速&&慢速下立即显示
        data = a2[5];
        len = len1;
        buffer->from(data, len);
      }
    };
    hpref.type = USING_STRING;
    succ |= NewHook(hpref, "Siglusold_fast");
  }
  return succ;
}

bool Silkyssakura::attach_function()
{
  auto addr = MemDbg::findCallerAddressAfterInt3((DWORD)GetGlyphOutlineW, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(3);
  hp.split = stackoffset(5);
  hp.type = DATA_INDIRECT | USING_CHAR | USING_SPLIT | CODEC_UTF16;

  auto xrefs = findxref_reverse_checkcallop(addr, processStartAddress, processStopAddress, 0xe8);
  if (xrefs.size() == 1)
  {
    addr = MemDbg::findEnclosingAlignedFunction(xrefs[0]);
    if (addr)
    {
      xrefs = findxref_reverse_checkcallop(addr, processStartAddress, processStopAddress, 0xe8);
      if (xrefs.size() == 1)
      {
        addr = MemDbg::findEnclosingAlignedFunction(xrefs[0]);
        if (addr)
        {
          HookParam hp_embed;
          hp_embed.address = addr;
          hp_embed.offset = stackoffset(2);
          hp_embed.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | CODEC_UTF16;
          hp_embed.embed_hook_font = F_GetGlyphOutlineW;
          return NewHook(hp_embed, "embedSilkyssakura"); // 这个是分两层分别绘制文字和阴影，需要两个都内嵌。
        }
      }
    }
  }

  return NewHook(hp, "Silkyssakura");
}

namespace
{
  // flutter of birds II 天使たちの翼  DMM版
  // EDSNHS932#-8@42650:Angel.exe √
  // HS932#-8@44D90:Angel.exe
  bool fob2()
  {
    const BYTE bytes[] = {
        0x53,
        0x56,
        0x8b, 0xf1,
        0x8b, 0xde,
        0x8d, 0x4b, 0x01,
        0x8d, 0xa4, 0x24, 0x00, 0x00, 0x00, 0x00,
        0x8a, 0x03,
        0x43,
        0x84, 0xc0,
        0x75, XX,
        0x2b, 0xd9,
        0xb8, 0xa8, 0x00, 0x00, 0x00,
        0x3b, 0xd8,
        0x68, 0xac, 0x00, 0x00, 0x00};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(ecx);
    hp.lineSeparator = L"\\n";
    hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
    return NewHook(hp, "SilkysX");
  }
}

bool Silkysveryveryold_attach_function()
{
  // flutter of birds II 天使たちの翼
  // https://vndb.org/v2380
  const BYTE bytes[] = {
      0x8b, XX, XX,
      0x03, XX, XX,
      0x33, XX,
      0x8a, 0x02,
      0x83, XX, 0x5c,
      0x0f, 0x85, XX4,
      0x8b, XX, XX,
      0x03, XX, XX,
      0x33, XX,
      0x8a, XX, 0x01,
      0x83, XX, 0x6e};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.lineSeparator = L"\\n";
  hp.type = USING_STRING;
  return NewHook(hp, "SilkysX");
}
namespace
{

  // flutter of birds～鳥達の羽ばたき～ 旧版本
  // https://vndb.org/v2379
  bool bird()
  {
    const BYTE bytes[] = {
        0x8b, 0x45, 0xf4,
        0x33, 0xc9,
        0x8a, 0x88, XX4,
        0x81, 0xf9, 0x81, 0x00, 0x00, 0x00,
        0x0f, 0x85, XX4,
        0x8b, 0x55, 0xf4,
        0x33, 0xc0,
        0x8a, 0x82, XX4,
        0x83, 0xf8, 0x75,
        0x74, 0x14,
        0x8b, 0x4d, 0xf4,
        0x33, 0xd2,
        0x8a, 0x91, XX4,
        0x83, 0xfa, 0x77,
        0x0f, 0x85, XX4,
        0x8b, 0x45, 0xf4,
        0x50};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = findfuncstart(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
    hp.embed_hook_font = F_TextOutA;
    hp.offset = stackoffset(1);
    hp.lineSeparator = L"\\n";
    return NewHook(hp, "SilkysX");
  }
}
namespace
{
  /*
  call->sub_413050->hook
  else if ( byte_4510E6 == 1 )
  {
    if ( *((_WORD *)&dword_452104 + dword_4510E8) == 29811 && !sub_414A90() )
    {
      sub_414A80(1);
      sub_414AF0(*((_WORD *)&word_452102 + dword_4510E8));
      sub_415AF0();
      sub_413050((const char *)(2 * (dword_451084 + *((unsigned __int16 *)&dword_452104 + dword_4510E8 + 1)) + 4530432));
      byte_44A10C = 1;
    }
    sub_40A3C0();
    v2 = 5 * ((unsigned __int8)byte_44A10B * (unsigned __int8)sub_406DF0() + 75);
    v0 = sub_423820() + 4 * v2;
    dword_44A0D0 = v0;
  }

  else if ( byte_4510E6 == 1 )
  {
    if ( *((_WORD *)&dword_452104 + dword_4510E8) == 29811 && !sub_414A90() )
    {
      sub_414A80(1);
      sub_413050((const char *)(2 * (dword_451084 + *((unsigned __int16 *)&dword_452104 + dword_4510E8 + 1)) + 4530432));
      byte_44A10C = 1;
    }
    dword_44A0D0 = sub_423820();
    sub_40A3C0();
    LOBYTE(v0) = sub_413030(0);
  }
  */
  // v5188
  // 肉体転移
  bool old2()
  {
    BYTE sig1[] = {
        0x66, 0x81, 0x3c, 0x55, 0x04, 0x21, 0x45, 0x00, 0x73, 0x74};
    ULONG addr = MemDbg::findBytes(sig1, sizeof(sig1), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    BYTE sig2[] = {
        0x33, XX,                // xor     eax, eax||  xor     edx, edx
        0x66, 0x8b, XX, XX, XX4, // mov     ax, word ptr dword_452104+2[ecx*2]||mov     dx, word ptr dword_452104+2[eax*2]
        0x03, XX,                // add     eax, edx||  add     edx, esi
        0x8d, XX, XX, XX4,       // lea     edx, ds:452100h[eax*2]||lea     ecx, ds:452100h[edx*2]
        XX,                      // push    edx||push    ecx
        0xe8, XX4};
    addr = MemDbg::findBytes(sig2, sizeof(sig2), addr, addr + 0x100);
    if (!addr)
      return false;
    auto target = addr + sizeof(sig2) - 5;
    target = target + 5 + (*(int *)(target + 1));
    HookParam hp;
    hp.address = target;
    hp.type = USING_STRING | EMBED_ABLE | EMBED_DYNA_SJIS;
    hp.offset = stackoffset(1);
    hp.lineSeparator = L"\\n";
    static bool isnewlinefirst = false;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      // 格式是:人名\n每一行text。每一行的text可以过滤掉。如果人名为空也可以过滤掉。
      StringReplacer(buffer, TEXTANDLEN("\x84\xa5\x84\xa7"), TEXTANDLEN("\x81\x5b\x81\x5b"));
      StringCharReplacer(buffer, TEXTANDLEN("\\n"), '\n');
      std::string result;
      bool hasFirstNewline = false;
      for (char c : buffer->viewA())
      {
        if (c == '\n')
        {
          if (!hasFirstNewline)
          {
            result += c;
            hasFirstNewline = true;
          }
        }
        else
          result += c;
      }
      if (result[0] == '\n')
      {
        isnewlinefirst = true;
        result = result.substr(1);
      }
      else
      {
        isnewlinefirst = false;
      }
      buffer->from(result);
    };
    hp.embed_fun = [](hook_context *context, TextBuffer buffer, HookParam *)
    {
      auto va = buffer.strA();
      if (isnewlinefirst)
      {
        va = "\\n" + va;
      }
      context->argof(1) = (DWORD)allocateString(va);
    };
    return NewHook(hp, "SilkysX");
  }
}
bool Silkysveryveryold::attach_function()
{
  return Silkysveryveryold_attach_function() || fob2() || bird() || old2();
}

bool Aisystem6::attach_function()
{
  // 肢体を洗う
  const BYTE bytes[] = {
      // if ( *(_WORD *)lpString == 0x9381 && v9 == 2 )
      0x66, 0x8B, 0x01, 0xF7, // mov     ax, [ecx]
      0xDD, 0x1B,
      0xED, 0x83, 0xC5, 0x02,
      0xD1, 0xEB,
      0x0F, 0xAF, 0xDD,
      0x66, 0x3D, 0x81, 0x93, // cmp     ax, 9381h
  };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  // 有三个这个同型的函数，分别显示不同的内容，各自只调用一次，在xref里面分发。
  auto addrs = findxref_reverse_checkcallop(addr, addr - 0x1000, addr + 0x1000, 0xe8);
  if (addrs.size() != 1)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addrs[0]);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING | NO_CONTEXT; // 男主自定义人名会被分开
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    StringCharReplacer(buffer, TEXTANDLEN("\x81\x93"), '\n');
  };
  return NewHook(hp, "Aisystem6");
}