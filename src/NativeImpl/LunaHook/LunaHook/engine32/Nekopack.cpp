#include "Nekopack.h"

/**
 *  mireado 8/01/2016: Add NekoPack hook
 *
 *  See: http://sakuradite.com/topic/1470
 *  https://arallab.hided.net/board_codetalk/2605967
 *
 *  [Pure More] 少女アクティビティ_trial 1.01
 *
 *  base: 0x4000000
 *	binary pattern :: 558BEC81C4C4FDFFFFB8
 */

bool InsertNekopackHook()
{
  const BYTE bytes[] = {
      0x55,                               // 0069637C  /$  55            PUSH EBP
      0x8b, 0xec,                         // 0069637D  |.  8BEC          MOV EBP,ESP
      0x81, 0xc4, 0xC4, 0xFD, 0xFF, 0xFF, // 0069637F  |.  81C4 C4FDFFFF ADD ESP,-23C
      0xb8, XX4,                          // 00696385  |.  B8 A8FF7900   MOV EAX,OFFSET 0079FFA8
      0x53,                               // 0069638A  |.  53            PUSH EBX
      0x56,                               // 0069638B  |.  56            PUSH ESI
      0x57,                               // 0069638C  |.  57            PUSH EDI
      0x8b, 0x5d, 0x08                    // 0069638D  |.  8B5D 08       MOV EBX,DWORD PTR SS:[ARG.1]
  };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);

  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(2);
  hp.type = USING_STRING;

  return NewHook(hp, "NekoPack");
}
static bool LOVEMILF()
{
  // LOVEMILF
  // https://vndb.org/v5259

  const BYTE bytes[] = {
      0x55, 0x8b, 0xec,
      0x83, 0xe4, 0xf8,
      0x83, 0xec, XX,
      0x56,
      0x8b, 0xf1,
      0x8b, 0x06,
      0x8b, 0x90, XX4,
      0xc7, 0x44, XX, XX, 0xf1, 0x00, 0x00, 0x00,
      0xff, 0xd2,
      0x8b, 0x4d, 0x14,
      0x51,
      0x8b, 0x4d, 0x10,
      0x8d, 0x54, XX, XX,
      0x52,
      0x8b, 0x55, 0x0c,
      0x51,
      0x8b, 0x4d, 0x08,
      0x52,
      0x89, 0x44, XX, XX,
      0x8b, 0x06};
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);

  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(3);
  hp.type = USING_STRING;

  return NewHook(hp, "LOVEMILF");
}
bool Nekopack::attach_function()
{
  return InsertNekopackHook() || LOVEMILF();
}