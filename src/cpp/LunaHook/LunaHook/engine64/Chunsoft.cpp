#include "Chunsoft.h"
namespace
{
  // https://vndb.org/r124342
  // かまいたちの夜×3
  bool all()
  {
    const uint8_t bytes[] = {
        /*
      switch ( v12 )
          {
            case 0x81A2u:
              v12 = -27705;
              break;
            case 0x835Eu:
              v12 = -32075;
              break;
            case 0x837Bu:
              v12 = -26913;
              break;
            case 0x8393u:
              v12 = -27751;
              break;
          }
        */
        0xba, 0xb5, 0x82, 0x00, 0x00,
        0x85, 0xc0,
        0x75, XX,
        0x0f, 0xb7, 0xcb,
        0x81, 0xe9, 0xa2, 0x81, 0x00, 0x00,
        0x74, XX,
        0x81, 0xe9, 0xbc, 0x01, 0x00, 0x00,
        0x74, XX,
        0x83, 0xe9, 0x1d,
        0x74, XX,
        0x83, 0xf9, 0x18,
        0x75, XX,
        0xbb, 0x99, 0x93, 0x00, 0x00,
        0xeb, XX};
    auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    BYTE bytes2[] = {
        /*
        v10 = *(unsigned __int8 **)(v9 + 416);
        v11 = *v10++;
        *(_QWORD *)(v9 + 416) = v10;
        v12 = *v10 | (unsigned __int16)(v11 << 8);
        */
        0x0f, 0xb6, 0x18,
        0x48, 0xff, 0xc0,
        0x49, XX, XX, XX4,
        0x66, 0xc1, 0xe3, 0x08,
        0x0f, 0xb6, 0x08,
        0x48, 0xff, 0xc0,
        0x66, 0x0b, 0xd9};
    addr = reverseFindBytes(bytes2, sizeof(bytes2), addr - 0x100, addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(rax);
    hp.type = USING_STRING;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      static std::string last;
      auto s = buffer->strA();
      if (s == last)
        return buffer->clear();
      buffer->from(s.substr(0, 2));
      last = s;
    };
    return NewHook(hp, "Chunsoft");
  }
}
bool Chunsoft::attach_function()
{
  return all();
}