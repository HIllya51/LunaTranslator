#include "CaramelBox.h"

static void SpecialHookCaramelBox(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  DWORD reg_ecx = *(DWORD *)(context->base + hp->offset);
  BYTE *ptr = (BYTE *)reg_ecx;
  buffer_index = 0;
  while (ptr[0])
    if (ptr[0] == 0x28)
    { // Furigana format: (Kanji,Furi)
      ptr++;
      while (ptr[0] != 0x2c) // Copy Kanji
        text_buffer[buffer_index++] = *ptr++;
      while (ptr[0] != 0x29) // Skip Furi
        ptr++;
      ptr++;
    }
    else if (ptr[0] == 0x5c)
      ptr += 2;
    else
    {
      text_buffer[buffer_index++] = ptr[0];
      if (LeadByteTable[ptr[0]] == 2)
      {
        ptr++;
        text_buffer[buffer_index++] = ptr[0];
      }
      ptr++;
    }
  buffer->from(text_buffer, buffer_index);
  *split = 0; // 8/3/2014 jichi: use return address as split
}
// jichi 10/1/2013: Change return type to bool
bool InsertCaramelBoxHook()
{
  union
  {
    DWORD i;
    BYTE *pb;
    WORD *pw;
    DWORD *pd;
  };
  DWORD reg = -1;
  for (i = processStartAddress + 0x1000; i < processStopAddress - 4; i++)
  {
    if (*pd == 0x7ff3d) // cmp eax, 7ff
      reg = 0;
    else if ((*pd & 0xfffff8fc) == 0x07fff880) // cmp reg, 7ff
      reg = pb[1] & 0x7;

    if (reg == -1)
      continue;

    DWORD flag = 0;
    if (*(pb - 6) == 3)
    { // add reg, [ebp+$disp_32]
      if (*(pb - 5) == (0x85 | (reg << 3)))
        flag = 1;
    }
    else if (*(pb - 3) == 3)
    { // add reg, [ebp+$disp_8]
      if (*(pb - 2) == (0x45 | (reg << 3)))
        flag = 1;
    }
    else if (*(pb - 2) == 3)
    { // add reg, reg
      if (((*(pb - 1) >> 3) & 7) == reg)
        flag = 1;
    }
    reg = -1;
    if (flag)
    {
      for (DWORD j = i, k = i - 0x100; j > k; j--)
      {
        if ((*(DWORD *)j & 0xffff00ff) == 0x1000b8)
        { // mov eax,10??
          HookParam hp;
          hp.address = j & ~0xf;
          hp.text_fun = SpecialHookCaramelBox;
          hp.type = USING_STRING;
          for (i &= ~0xffff; i < processStopAddress - 4; i++)
            if (pb[0] == 0xe8)
            {
              pb++;
              if (pd[0] + i + 4 == hp.address)
              {
                pb += 4;
                if ((pd[0] & 0xffffff) == 0x04c483)
                  hp.offset = stackoffset(1);
                else
                  hp.offset = regoffset(ecx);
                break;
              }
            }

          if (hp.offset == 0)
          {
            return false;
          }

          // RegisterEngineType(ENGINE_CARAMEL);
          return NewHook(hp, "CaramelBox");
        }
      }
    }
  }
  ConsoleOutput("CaramelBox: failed");
  return false;
  //_unknown_engine:
  // ConsoleOutput("Unknown CarmelBox engine.");
}

bool CaramelBox::attach_function()
{

  return InsertCaramelBoxHook();
}

bool CaramelBoxMilkAji::attach_function()
{
  // 雨芳恋歌
  // https://vndb.org/v6663
  BYTE bytes[] = {
      0x33, 0xD2,
      0xB9, 0x8A, 0x02, 0x00, 0x00,
      0xF7, 0xF1,
      0x6B, 0xC0, 0x44,
      0x6B, 0xC0, 0x03};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING;
  hp.offset = stackoffset(1);

  return NewHook(hp, "CaramelBox");
}
bool CaramelBox2::attach_function()
{
  // https://vndb.org/r19777
  // Otoboku - Maidens Are Falling for Me! - Download Edition
  PcHooks::hookGDIFunctions();
  trigger_fun = [](LPVOID addr1, hook_context *context)
  {
    if (addr1 != TextOutA && addr1 != GetTextExtentPoint32A)
      return false;
    auto addr = context->retaddr;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | USING_SPLIT;
    hp.offset = stackoffset(2);
    hp.split = stackoffset(2);
    NewHook(hp, "CaramelBox");
    return true;
  };
  return true;
}