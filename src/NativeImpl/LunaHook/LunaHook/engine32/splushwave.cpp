#include "splushwave.h"
namespace
{
  bool splushwave_(const char *buf, int size)
  {
    auto addr = MemDbg::findBytes(buf, size, processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findPushAddress(addr, processStartAddress, processStopAddress);
    if (!addr)
      return false;
    bool succ = false;
    addr = max(findfuncstart(addr, 0x300), // ドラゴンファーム Version 2.05
               MemDbg::findEnclosingAlignedFunction(addr));
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(eax);
    hp.type = USING_STRING;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      /*
  [VID_Z_RIZ_016]リーゼロッテ「知ってるわ。でも、これから徐々に――」
  提督「強くなれないのに強敵と戦うのか？　それではいつか死ぬだけだ」
  #STM:リーゼロッテ＿怒り[VID_Z_RIZ_017]リーゼロッテ「…………」
  提督「プリンセスクラスとは名ばかりで、今のままでは、君は使い物にならないと上層部は思っている」
  [VID_Z_RIZ_018]リーゼロッテ「評価なんて、覆せばいいだけよ」
  提督「その通りだ。上層部が考えを改めるほどに、俺が君を強くする」

  #EVENT_FLAG_ON:Ｅ＿ＯＰ＿終了#BGM_FADEOUT#FADE_SET#FADEOUT_BK
  #BGM:ＫＭ＿強化#FADE_SET#MES_CLR#MES_OFF#CG_CLR#BG:調教部屋#FADE_IN
  */
      if ((*(char *)buffer->data) == '#')
        return buffer->clear();
      StringFilterBetween(buffer, TEXTANDLEN("["), TEXTANDLEN("]"));
    };
    return NewHook(hp, "splushwave");
  }
}
static bool umw()
{
  const BYTE bytes[] = {
      0x8b, 0x54, 0x24, 0x04,
      0x56, 0x57,
      0x33, 0xf6,
      0x8b, 0xfa,
      0x83, 0xc9, 0xff,
      0x33, 0xc0,
      0x89, XX, XX4,
      0xf2, 0xae,
      0xf7, 0xd1,
      0x49,
      0x89, XX, XX4,
      0xd1, 0xe9,
      0x89, XX, XX4,
      0x89, XX, XX4,
      0x8b, XX, XX4,
      0xb9, 0x14, 0x00, 0x00, 0x00,
      0xb8, 0x18, 0x00, 0x00, 0x00};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING | FULL_STRING | NO_CONTEXT;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    if ((*(char *)buffer->data) == '#')
      return buffer->clear();
    StringFilterBetween(buffer, TEXTANDLEN("["), TEXTANDLEN("]"));
    StringFilter(buffer, TEXTANDLEN("CR"));
  };
  return NewHook(hp, "umw");
}
bool splushwave::attach_function()
{
  // https://vndb.org/r113134
  // 天色戦姫 体験版 https://gyutto.com/i/item128979?select_uaflag=1
  char aErrMesbufS[] = "err:mesbuf %s\0";
  // ドラゴンアカデミー  http://gyutto.com/i/item98617?select_uaflag=1
  // ドラゴンアカデミー3  http://gyutto.com/i/item208616?select_uaflag=1
  char aCidS[] = "CID_%s\0";
  return (splushwave_(aErrMesbufS, sizeof(aErrMesbufS)) | splushwave_(aCidS, sizeof(aCidS))) || umw();
}