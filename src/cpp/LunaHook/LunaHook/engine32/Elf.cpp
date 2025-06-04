#include "Elf.h"

/**
 *  jichi 6/1/2014:
 *  Observations from 愛姉妹4
 *  - Scenario: arg1 + 4*5 is 0, arg1+0xc is address of the text
 *  - Character: arg1 + 4*10 is 0, arg1+0xc is text
 */
static inline size_t _elf_strlen(LPCSTR p) // limit search address which might be bad
{
  // CC_ASSERT(p);
  for (size_t i = 0; i < VNR_TEXT_CAPACITY; i++)
    if (!*p++)
      return i;
  return 0; // when len >= VNR_TEXT_CAPACITY
}

static void SpecialHookElf(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  // DWORD arg1 = *(DWORD *)(esp_base + 0x4);
  DWORD arg1 = context->stack[1];
  DWORD arg2_scene = arg1 + 4 * 5,
        arg2_chara = arg1 + 4 * 10;
  DWORD text; //= 0; // This variable will be killed
  if (*(DWORD *)arg2_scene == 0)
  {
    text = *(DWORD *)(arg2_scene + 4 * 3);
    if (!text || ::IsBadReadPtr((LPCVOID)text, 1)) // Text from scenario could be bad when open backlog while the character is speaking
      return;
    *split = 1;
  }
  else if (*(DWORD *)arg2_chara == 0)
  {
    text = arg2_chara + 4 * 3;
    *split = 2;
  }
  else
    return;
  // if (text && text < MemDbg::UserMemoryStopAddress) {
  // *len = _elf_strlen((LPCSTR)text); // in case the text is bad but still readable
  //*len = ::strlen((LPCSTR)text);
  buffer->from(text, _elf_strlen((LPCSTR)text));
}

/**
 *  jichi 5/31/2014: elf's
 *  Type1: SEXヂ�ーチャー剛史 trial, reladdr = 0x2f0f0, 2 parameters
 *  Type2: 愛姉妹4, reladdr = 0x2f9b0, 3 parameters
 *
 *  IDA: sub_42F9B0 proc near ; bp-based frame
 *    var_8 = dword ptr -8
 *    var_4 = byte ptr -4
 *    var_3 = word ptr -3
 *    arg_0 = dword ptr  8
 *    arg_4 = dword ptr  0Ch
 *    arg_8 = dword ptr  10h
 *
 *  Call graph (Type2):
 *  0x2f9b0 ;  hook here
 *  > 0x666a0 ; called multiple time
 *  > TextOutA ; there are two TextOutA, the second is the right one
 *
 *  Function starts (Type1), pattern offset: 0xc
 *  - 012ef0f0  /$ 55             push ebp ; jichi: hook
 *  - 012ef0f1  |. 8bec           mov ebp,esp
 *  - 012ef0f3  |. 83ec 10        sub esp,0x10
 *  - 012ef0f6  |. 837d 0c 00     cmp dword ptr ss:[ebp+0xc],0x0
 *  - 012ef0fa  |. 53             push ebx
 *  - 012ef0fb  |. 56             push esi
 *  - 012ef0fc  |. 75 0f          jnz short stt_tria.012ef10d ; jicchi: pattern starts
 *  - 012ef0fe  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8]
 *  - 012ef101  |. 8b48 04        mov ecx,dword ptr ds:[eax+0x4]
 *  - 012ef104  |. 8b91 90000000  mov edx,dword ptr ds:[ecx+0x90] ; jichi: pattern stops
 *  - 012ef10a  |. 8955 0c        mov dword ptr ss:[ebp+0xc],edx
 *  - 012ef10d  |> 8b4d 08        mov ecx,dword ptr ss:[ebp+0x8]
 *  - 012ef110  |. 8b51 04        mov edx,dword ptr ds:[ecx+0x4]
 *  - 012ef113  |. 33c0           xor eax,eax
 *  - 012ef115  |. c645 f8 00     mov byte ptr ss:[ebp-0x8],0x0
 *  - 012ef119  |. 66:8945 f9     mov word ptr ss:[ebp-0x7],ax
 *  - 012ef11d  |. 8b82 b0000000  mov eax,dword ptr ds:[edx+0xb0]
 *  - 012ef123  |. 8945 f4        mov dword ptr ss:[ebp-0xc],eax
 *  - 012ef126  |. 33db           xor ebx,ebx
 *  - 012ef128  |> 8b4f 20        /mov ecx,dword ptr ds:[edi+0x20]
 *  - 012ef12b  |. 83f9 10        |cmp ecx,0x10
 *
 *  Function starts (Type2), pattern offset: 0x10
 *  - 0093f9b0  /$ 55             push ebp  ; jichi: hook here
 *  - 0093f9b1  |. 8bec           mov ebp,esp
 *  - 0093f9b3  |. 83ec 08        sub esp,0x8
 *  - 0093f9b6  |. 837d 10 00     cmp dword ptr ss:[ebp+0x10],0x0
 *  - 0093f9ba  |. 53             push ebx
 *  - 0093f9bb  |. 8b5d 0c        mov ebx,dword ptr ss:[ebp+0xc]
 *  - 0093f9be  |. 56             push esi
 *  - 0093f9bf  |. 57             push edi
 *  - 0093f9c0  |. 75 0f          jnz short silkys.0093f9d1 ; jichi: pattern starts
 *  - 0093f9c2  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8]
 *  - 0093f9c5  |. 8b48 04        mov ecx,dword ptr ds:[eax+0x4]
 *  - 0093f9c8  |. 8b91 90000000  mov edx,dword ptr ds:[ecx+0x90] ; jichi: pattern stops
 *  - 0093f9ce  |. 8955 10        mov dword ptr ss:[ebp+0x10],edx
 *  - 0093f9d1  |> 33c0           xor eax,eax
 *  - 0093f9d3  |. c645 fc 00     mov byte ptr ss:[ebp-0x4],0x0
 *  - 0093f9d7  |. 66:8945 fd     mov word ptr ss:[ebp-0x3],ax
 *  - 0093f9db  |. 33ff           xor edi,edi
 *  - 0093f9dd  |> 8b53 20        /mov edx,dword ptr ds:[ebx+0x20]
 *  - 0093f9e0  |. 8d4b 0c        |lea ecx,dword ptr ds:[ebx+0xc]
 *  - 0093f9e3  |. 83fa 10        |cmp edx,0x10
 */
bool InsertElfHook()
{
  const BYTE bytes[] = {
      // 0x55,                             // 0093f9b0  /$ 55             push ebp  ; jichi: hook here
      // 0x8b,0xec,                        // 0093f9b1  |. 8bec           mov ebp,esp
      // 0x83,0xec, 0x08,                  // 0093f9b3  |. 83ec 08        sub esp,0x8
      // 0x83,0x7d, 0x10, 0x00,            // 0093f9b6  |. 837d 10 00     cmp dword ptr ss:[ebp+0x10],0x0
      // 0x53,                             // 0093f9ba  |. 53             push ebx
      // 0x8b,0x5d, 0x0c,                  // 0093f9bb  |. 8b5d 0c        mov ebx,dword ptr ss:[ebp+0xc]
      // 0x56,                             // 0093f9be  |. 56             push esi
      // 0x57,                             // 0093f9bf  |. 57             push edi
      0x75, 0x0f,                        // 0093f9c0  |. 75 0f          jnz short silkys.0093f9d1
      0x8b, 0x45, 0x08,                  // 0093f9c2  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8]
      0x8b, 0x48, 0x04,                  // 0093f9c5  |. 8b48 04        mov ecx,dword ptr ds:[eax+0x4]
      0x8b, 0x91, 0x90, 0x00, 0x00, 0x00 // 0093f9c8  |. 8b91 90000000  mov edx,dword ptr ds:[ecx+0x90]
  };
  // enum { addr_offset = 0xc };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  // GROWL_DWORD(addr);
  // addr = 0x42f170; // 愛姉妹4 Trial
  // reladdr = 0x2f9b0; // 愛姉妹4
  // reladdr = 0x2f0f0; // SEXヂ�ーチャー剛史 trial
  if (!addr)
    return false;

  enum : BYTE
  {
    push_ebp = 0x55
  };
  for (int i = 0; i < 0x20; i++, addr--) // value of i is supposed to be 0xc or 0x10
    if (*(BYTE *)addr == push_ebp)
    { // beginning of the function

      HookParam hp;
      hp.address = addr;
      hp.text_fun = SpecialHookElf;
      hp.type = USING_STRING | NO_CONTEXT; // = 9

      ConsoleOutput("INSERT Elf");

      return NewHook(hp, "Elf");
    }
  ConsoleOutput("Elf: function not found");
  return false;
}
namespace
{
  bool __()
  {
    const BYTE bytes[] = {
        // 姫騎士オリヴィア ～へ、変態、この変態男!少しは恥を知りなさい!～
        // 女系家族III～秘密HIMITSU卑蜜～
        // ベロちゅー！～コスプレメイドをエロメロしちゃう魔法の舌戯～
        0x0F, 0xB7, XX, XX4, // v11 == 30081 // movzx   edx, ds:word_4C285C //word_4C285C dw 7581h
    };

    for (auto addr : Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress))
    {
      BYTE reg = *(BYTE *)(addr + 2);
      if ((reg != 0x05) && (reg != 0x0d) && (reg != 0x1d) && (reg != 0x15))
        continue;
      int word_4C285C_addr = *(int *)(addr + 3);
      if (word_4C285C_addr < processStartAddress || word_4C285C_addr > processStopAddress)
        continue;
      int word_4C285C = *(int *)word_4C285C_addr;
      if ((word_4C285C) != 0x7581)
        continue;
      addr = findfuncstart(addr, 0x200);
      if (!addr)
        continue;
      HookParam hp;
      hp.address = addr;
      hp.offset = stackoffset(1);
      hp.type = USING_STRING;

      return NewHook(hp, "aiwin6");
    }

    return false;
  }
}
namespace
{ // unnamed
  namespace ScenarioHook
  {
    namespace Private
    {

      struct TextArgument
      {
        DWORD _unknown1[5];

        DWORD scenarioFlag; // +4*5, 0 if it is scenario
        DWORD _unknown2[2];
        LPCSTR scenarioText; // +4*5+4*3, could be bad address though
        DWORD _unknown3;

        DWORD nameFlag; // +4*10, 0 if it is name
        DWORD _unknown4[2];
        char nameText[1]; // +4*10+4*3, could be bad address though
      };

      TextArgument *scenarioArg_,
          *nameArg_;
      LPCSTR scenarioText_;

      enum
      {
        MaxNameSize = 100
      };
      char nameText_[MaxNameSize + 1];

      void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
      {
        auto arg = (TextArgument *)s->stack[0]; // arg1 on the top of the stack

        // Scenario
        if (arg->scenarioFlag == 0)
        {
          *role = Engine::ScenarioRole;
          // Text from scenario could be bad when open backlog while the character is speaking
          auto text = arg->scenarioText;
          if (!Engine::isAddressReadable(text))
            return;
          buffer->from(text);
          return;
          // data_ = q->dispatchTextASTD(text, role, sig);
          // scenarioArg_ = arg;
          // scenarioText_ = arg->scenarioText;
          // arg->scenarioText = (LPCSTR)data_.c_str();
        }
        else if (arg->nameFlag == 0)
        {
          *role = Engine::NameRole;
          auto text = arg->nameText;
          buffer->from(text);
          return;
          //  ::memcpy(text, newData.constData(), qMin(oldData.size(), newData.size()));
          // int left = oldData.size() - newData.size();
          // if (left > 0)
          //  ::memset(text + oldData.size() - left, 0, left);
        }
      }
      void hookafter1(hook_context *s, TextBuffer buffer)
      {
        auto newData = buffer.strA();
        auto arg = (TextArgument *)s->stack[0]; // arg1 on the top of the stack

        // Scenario
        if (arg->scenarioFlag == 0)
        {

          auto text = arg->scenarioText;
          if (!Engine::isAddressReadable(text))
            return;
          scenarioArg_ = arg;
          scenarioText_ = arg->scenarioText;
          arg->scenarioText = (LPCSTR)allocateString(newData);
        }
        else if (arg->nameFlag == 0)
        {

          auto text = arg->nameText;
          std::string oldData = text;
          ::memcpy(text, newData.c_str(), min(oldData.size(), newData.size()));
          int left = oldData.size() - newData.size();
          if (left > 0)
            ::memset(text + oldData.size() - left, 0, left);
        }
      }
      void hookAfter(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        if (scenarioArg_)
        {
          scenarioArg_->scenarioText = scenarioText_;
          scenarioArg_ = nullptr;
        }
        if (nameArg_)
        {
          ::strcpy(nameArg_->nameText, nameText_);
          nameArg_ = nullptr;
        }
      }

    } // namespace Private

    /**
     *  jichi 5/31/2014: elf's
     *  Type1: SEXティーチャー剛史 trial, reladdr = 0x2f0f0, 2 parameters
     *  Type2: 愛姉妹4, reladdr = 0x2f9b0, 3 parameters
     *
     *  The hooked function is the caller of the caller of TextOutA.
     */
    bool attach(ULONG startAddress, ULONG stopAddress)
    {
      const uint8_t bytes[] = {
          // 0x55,                             // 0093f9b0  /$ 55             push ebp  ; jichi: hook here
          // 0x8b,0xec,                        // 0093f9b1  |. 8bec           mov ebp,esp
          // 0x83,0xec, 0x08,                  // 0093f9b3  |. 83ec 08        sub esp,0x8
          // 0x83,0x7d, 0x10, 0x00,            // 0093f9b6  |. 837d 10 00     cmp dword ptr ss:[ebp+0x10],0x0
          // 0x53,                             // 0093f9ba  |. 53             push ebx
          // 0x8b,0x5d, 0x0c,                  // 0093f9bb  |. 8b5d 0c        mov ebx,dword ptr ss:[ebp+0xc]
          // 0x56,                             // 0093f9be  |. 56             push esi
          // 0x57,                             // 0093f9bf  |. 57             push edi
          0x75, 0x0f,                        // 0093f9c0  |. 75 0f          jnz short silkys.0093f9d1
          0x8b, 0x45, 0x08,                  // 0093f9c2  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8]
          0x8b, 0x48, 0x04,                  // 0093f9c5  |. 8b48 04        mov ecx,dword ptr ds:[eax+0x4]
          0x8b, 0x91, 0x90, 0x00, 0x00, 0x00 // 0093f9c8  |. 8b91 90000000  mov edx,dword ptr ds:[ecx+0x90]
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return false;
      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        return false;
      int count = 0;
      auto fun = [&count](ULONG addr) -> bool
      {
        bool succ = false;
        HookParam hp;
        hp.address = addr;
        hp.text_fun = Private::hookBefore;
        hp.embed_fun = Private::hookafter1;
        hp.type = USING_STRING | EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT;
        hp.embed_hook_font = F_TextOutA;
        succ |= NewHook(hp, "EmbedElf");
        hp.address = addr + 5;
        hp.text_fun = Private::hookAfter;
        succ |= NewHook(hp, "EmbedElf");
        count += 1;
        return succ; // replace all functions
      };
      MemDbg::iterNearCallAddress(fun, addr, startAddress, stopAddress);
      return count;

      // lastCaller = MemDbg::findEnclosingAlignedFunction(lastCaller);
      // Private::attached_ = false;
      // return winhook::hook_before(lastCaller, [=](winhook::hook_context *s) -> bool {
      //   if (Private::attached_)
      //     return true;
      //   Private::attached_ = true;
      //   if (ULONG addr = MemDbg::findEnclosingAlignedFunction(s->stack[0])) {
      //     DOUT("dynamic pattern found");
      //     Private::oldHookFun = (Private::hook_fun_t)winhook::replace_fun(addr, (ULONG)Private::newHookFun);
      //   }
      //   return true;
      // });
    }

  } // namespace ScenarioHook
} // unnamed namespace
namespace
{
  // flutter of birds～鳥達の羽ばたき～ WIN10版本
  // https://vndb.org/v2379
  // 需要注意的是，不能把文本跳到最快，不然2~4行无法显示。
  // 这个有一大堆候选
  bool elf3()
  {
    bool succ = false;
    BYTE sig[] = {
        0x83, XX, 0x14, 0x10,
        0x72, XX};
    for (auto addr : Util::SearchMemory(sig, sizeof(sig), PAGE_EXECUTE, processStartAddress, processStopAddress))
    {
      auto check1 = *(BYTE *)(addr + 5);
      if (check1 != 0x02 && check1 != 0x04)
        continue;
      auto check = *(BYTE *)(addr + 1);
      HookParam hp;
      hp.address = addr;
      hp.user_value = check;
      hp.type = USING_STRING | NO_CONTEXT | BREAK_POINT; // 有壳minhook太慢了
      hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        DWORD ptr;
        switch (hp->user_value)
        {
        case 0x7a:
          ptr = context->edx;
          break;
        case 0x7b:
          ptr = context->ebx;
          break;
        case 0x79:
          ptr = context->ecx;
          break;
        case 0x78:
          ptr = context->eax;
          break;
        case 0x7e:
          ptr = context->esi;
          break;
        case 0x7f:
          ptr = context->edi;
          break;
        case 0x7d:
          ptr = context->ebp;
          break;
          // esp:
          // 83 7c 24 14 10
        default:
          hp->type = HOOK_EMPTY;
          break;
        }
        auto text = (TextUnionA *)ptr;
        buffer->from(text->view());
      };
      hp.filter_fun = all_ascii_Filter;
      succ |= NewHook(hp, "elf3");
    }
    return succ;
  }
}
namespace
{
  bool elf4()
  {
    // https://vndb.org/v315
    //  WORDS WORTH【Windows10対応】
    //  elf3只能拿到人名，跳过
    // https://vndb.org/v2307
    // 愛のチカラ
    uint8_t bytes[] = {
        0x72, 0x02,
        0x8b, 0x36,
        0x8a, 0x0e,
        0x84, 0xc9,
        0x0f, 0x84, XX4,
        0x8d, 0x57, XX,
        0x8d, 0x5f, XX,
        0x8b, 0xff,
        0x80, 0xf9, 0x81,
        0x72, 0x05,
        0x80, 0xf9, 0x9f,
        0x76, 0x07,
        0x8d, 0x41, 0x20,
        0x3c, 0x0f,
        0x77, XX};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr + 4;
    hp.type = USING_STRING;
    hp.offset = regoffset(esi);
    return NewHook(hp, "Elf4");
  }
}
namespace
{
  bool nvxijiazu()
  {
    // https://vndb.org/v3327
    // 女系家族～淫謀～
    BYTE sig[] = {
        0X55,
        0x8b, 0xec, // mov ebp,esp
        0x51, 0x53, 0x56,
        0x8b, 0xf1,
        0x66, 0xc7, 0x45, 0xfd, 0x00, 0x00,
        0x66, 0x8b, 0x4d, 0x10, // mov ecx,[ebp+10]
        0x66, 0x8b, 0xd1,
        0x66, 0xc1, 0xea, 0x08,
        0x80, 0xfa, 0x81, // cmp dl,0x81
        0x72, 0x05,
        0x80, 0xfa, 0x9f, // cmp dl,0x9f
        0x76, XX};
    ULONG addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_CHAR | CODEC_ANSI_BE | DATA_INDIRECT; // 不可以NO_CONTEXT，因为有彩色可点击文字，会在另一个context有很多垃圾文本
    hp.offset = regoffset(esp);
    hp.index = 0x10;
    return NewHook(hp, "Elf4");
  }
  bool malunohuanzhe()
  {
    // 麻呂の患者はガテン系３完結編
    BYTE sig[] = {
        0x8b, 0x4e, 0x20,
        0x83, 0xf9, 0x10,
        0x72, 0x05,
        0x8b, 0x46, 0x0c,
        0xeb, 0x03,
        0x8d, 0x46, 0x0c,
        0x80, 0x3c, 0x18, 0x00,
        0x0f, 0x84, XX4,
        0x83, 0xf9, 0x10,
        0x72, 0x05,
        0x8b, 0x46, 0x0c,
        0xeb, 0x03,
        0x8d, 0x46, 0x0c,
        0x8a, 0x04, 0x18,
        0x3c, 0x81,
        0x72, 0x04,
        0x3c, 0x9f,
        0x76, 0x06,
        0x04, 0x20,
        0x3c, 0x0f,
        0x77, XX};
    ULONG addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = [addr]() -> uintptr_t
    {
      auto addr1 = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr1)
        return 0;
      auto addr2 = findfuncstart(addr);
      if (!addr2)
        return 0;
      if (addr2 == addr1)
        return addr2;
      return 0;
    }();
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | EMBED_ABLE | EMBED_DYNA_SJIS;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      auto a2 = context->stack[1];
      auto text = (TextUnionA *)(a2 + 12);
      buffer->from(text->view());
    };
    hp.embed_fun = [](hook_context *context, TextBuffer buffer)
    {
      auto a2 = context->stack[1];
      auto text = (TextUnionA *)(a2 + 12);
      text->setText(buffer.viewA());
    };
    hp.embed_hook_font = F_TextOutA;
    return NewHook(hp, "elf5");
  }
}
bool Elf::attach_function()
{

  auto _1 = InsertElfHook() || __() || elf4() || nvxijiazu() || malunohuanzhe() || elf3();
  return ScenarioHook::attach(processStartAddress, processStopAddress) || _1;
}

void SpecialHookElf2(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  static DWORD lasttext;
  DWORD eax = context->eax;
  DWORD edx = context->edx;
  auto c = *(WORD *)(eax + edx);
  if (IsShiftjisWord(c) == false)
  {
    return;
  }
  *split = context->stack[1];
  buffer->from_t(c);
}
bool Elf2attach_function()
{
  // 这个有好多乱码
  //[エルフ]あしたの雪之丞 DVD Special Edition
  const uint8_t bytes[] = {
      0x53,
      0x8a, 0x1c, 0x02,
      0x8b, 0x54, 0x24, 0x08,
      0x03, 0xc2};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr + 1;
  hp.text_fun = SpecialHookElf2;
  hp.type = NO_CONTEXT | USING_CHAR;

  return NewHook(hp, "Elf");
}
bool elf2()
{
  // 勝　あしたの雪之丞２
  const uint8_t bytes[] = {
      0x66, 0x8b, 0x8e, XX4,
      0x66, 0x8b, 0x96, XX4,
      0x66, 0x01, 0x8e, XX4,
      0x66, 0x89, 0x96, XX4,
      0x8b, 0x06,
      0x6a, 0x00,
      0x8b, 0xce,
      0xff, 0x50, 0x08,
      0x84, 0xc0};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;

  hp.type = NO_CONTEXT | USING_CHAR;
  hp.offset = regoffset(ebx);
  //[エルフ]あしたの雪之丞 DVD Special Edition

  const uint8_t bytes2[] = {
      0x66, 0x33, 0xdb,
      0x6a, 0x01,
      0x8a, 0xd8,
      0x8b, 0x06,
      0x8b, 0xce,
      0xff, 0x50, 0x08,
      0x33, 0xc9,
      0x33, 0xd2,
      0x8a, 0xe8,
      0x0b, 0xd9};
  auto addr2 = reverseFindBytes(bytes2, sizeof(bytes2), addr - 0x100, addr);
  if (addr2)
  {
    hp.address = addr2 + sizeof(bytes2);
  }
  else
  {
    hp.address = addr + sizeof(bytes);
  }
  return NewHook(hp, "Elf");
}
namespace
{
  // リフレインブルー【Windows10対応】
  bool _h1()
  {
    // HAN-18*-4@42E12:AI5WIN.exe
    BYTE sig[] = {
        0x33, 0xff,
        0x8b, 0x06,
        0x8b, 0xce,
        0x6a, 0x01,
        0x8b, 0x40, 0x08,
        0xff, 0xd0,
        0x0f, 0x0b6, 0xc0,
        0x8b, 0xce,
        0x66, 0xc1, 0xe0, 0x08,
        0x0f, 0xb7, 0xc0,
        0x89, 0x45, 0xfc,
        0x8b, 0x06,
        0x6a, 0x01,
        0x8b, 0x40, 0x08,
        0xff, 0xd0,
        0x0f, 0xb6, 0xc0,
        0x8b, 0xce,
        0x66, 0x09, 0x45, 0xfc,
        0xff, 0x75, 0xfc,
        0xe8};
    ULONG addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr + sizeof(sig) - 1;
    hp.type = NO_CONTEXT | USING_CHAR | DATA_INDIRECT | CODEC_ANSI_BE;
    hp.offset = regoffset(ebp);
    hp.index = -4;
    return NewHook(hp, "Elf");
  }
  bool _h2()
  {
    // HAN4@49570:AI5WIN.exe

    BYTE sig[] = {
        0x33, 0xc5,
        0x89, 0x45, 0xfc,
        0x8a, 0x81, XX4,

        0x84, 0xc0,
        0x75, 0x0e,
        0x8b, 0x81, XX4,
        0x03, 0x81, XX4,
        0xeb, XX,

        0x3c, 0x01,
        0x75, 0x0e,
        0x8b, 0x81, XX4,
        0x03, 0x81, XX4,
        0xeb, XX,

        0x3c, 0x02,
        0x75, 0x0e,
        0x8b, 0x81, XX4,
        0x03, 0x81, XX4,
        0xeb, XX};
    ULONG addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = NO_CONTEXT | USING_CHAR | CODEC_ANSI_BE;
    hp.offset = stackoffset(1);
    return NewHook(hp, "Elf");
  }
  bool all()
  {
    return _h1() | _h2();
  }
}
namespace
{
  bool el()
  {
    // https://vndb.org/v2293
    // 【el】【Windows10対応】
    BYTE sig[] = {
        // 0x66,0x8b,0x4d,0x0c
        // 0x66,0x8b,0xc1
        0x66, 0xc1, 0xe8, 0x08,
        XX, // 0x57
        0x3c, 0x81,
        0x72, 0x04,
        0x3c, 0x9f,
        0x76, 0x08,
        0x3c, 0xe0,
        0x72, 0x10,
        0x3c, 0xef,
        0x77, 0x0c};
    ULONG addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = NO_CONTEXT | USING_CHAR | CODEC_ANSI_BE;
    hp.offset = regoffset(eax);
    return NewHook(hp, "Elf");
  }
}
bool Elf2::attach_function()
{
  return elf2() || Elf2attach_function() || all() || el();
}

bool ElfFunClubFinal::attach_function()
{
  // mov reg,ds:TextOutA
  bool succ = false;
  for (auto addr : findiatcallormov_all((DWORD)TextOutA, processStartAddress, processStartAddress, processStopAddress, PAGE_EXECUTE, XX))
  {
    BYTE s[] = {XX, 0xCC, 0xCC, 0xCC};
    addr = reverseFindBytes(s, 4, addr - 0x100, addr);
    if (!addr)
      continue;
    HookParam hp;
    hp.address = addr + 4;
    hp.type = CODEC_ANSI_BE | USING_CHAR;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      *split = context->stack[2] > 8;
      buffer->from_t((WORD)context->stack[3]);
    };
    succ |= NewHook(hp, "ElfFunClubFinal");
  }
  return succ;
}