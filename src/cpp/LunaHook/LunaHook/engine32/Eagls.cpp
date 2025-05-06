#include "Eagls.h"

/** jichi 7/26/2014: E.A.G.L.S engine for TechArts games (SQUEEZ, May-Be Soft)
 *  Sample games: [May-Be Soft] ちぽ�んじ� *  Should also work for SQUEEZ's 孕ませシリーズ
 *
 *  Two functions  calls to GetGlyphOutlineA are responsible for painting.
 *  - 0x4094ef
 *  - 0x409e35
 *  However, by default, one of the thread is like: scenario namename scenario
 *  The other thread have infinite loop.
 */
bool InsertEaglsHook()
{

  // Modify the split for GetGlyphOutlineA
  HookParam hp;
  hp.address = (DWORD)::GetGlyphOutlineA;
  hp.type = CODEC_ANSI_BE | USING_SPLIT; // the only difference is the split value
  hp.offset = stackoffset(2);
  hp.split = stackoffset(4);
  // hp.split = arg7_lpmat2;
  ConsoleOutput("INSERT EAGLS");

  return NewHook(hp, "EAGLS");
}

bool Eagls::attach_function()
{
  return InsertEaglsHook();
}