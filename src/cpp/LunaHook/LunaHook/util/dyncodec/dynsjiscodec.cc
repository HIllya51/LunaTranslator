// qtdynsjis.cc
// 6/3/2015 jichi
// http://en.wikipedia.org/wiki/Shift_JIS
#include "dynsjiscodec.h"
#ifdef __clang__
#pragma GCC diagnostic ignored "-Wlogical-op-parentheses"
#endif // __clang__

// #ifdef _MSC_VER
// # pragma warning(disable:4018) // C4018: signed/unsigned mismatch
// #endif // _MSC_VER

// #define SK_NO_QT
// #define DEBUG "dynsjis.cc"
// #include "sakurakit/skdebug.h"

/** Private class */

// See also LeadByte table for Windows:
//
// BYTE LeadByteTable[0x100] = {
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
//   2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
//   2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
//   2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1
// };
//
// -2: 0x00 and 0xff are skipped

class DynamicShiftJISCodecPrivate
{
public:
  UINT codepage;
  std::wstring text; // already saved characters

  UINT minimumSecondByte;

  explicit DynamicShiftJISCodecPrivate(UINT codepage_)
      : codepage(932), minimumSecondByte(0)
  {
    codepage = codepage_;
  }

  size_t capacity() const
  {
    // See: http://en.wikipedia.org/wiki/Shift_JIS
    return                                                  // = 7739
        (3 * 16 - 1) * (4 * 16 + 4 - 1 - minimumSecondByte) // = 3149, 0x00 are skipped
        + (16 + 2) * (256 - 1 - minimumSecondByte)          // = 4590, first/last byte unused
        ;
  }
  bool isFull() const { return text.size() >= capacity(); }
  std::string encodeSTD(const wchar_t *text, size_t length, bool *dynamic);

  std::string encode(const wchar_t *text, size_t length, bool *dynamic);
  std::wstring decode(const char *data, size_t length, bool *dynamic) const;

private:
  std::string encodeCharSTD(wchar_t ch);
  wchar_t decodeChar(UINT8 ch1, UINT8 ch2) const;
};

// Encode
std::string DynamicShiftJISCodecPrivate::encodeSTD(const wchar_t *text, size_t length, bool *dynamic)
{
  std::string ret;
  for (size_t i = 0; i < length; i++)
  {
    wchar_t ch = text[i];
    if (ch <= 127)
      ret.push_back(ch);
    else
    {
      std::wstring ws;
      ws.push_back(ch);
      std::string data = WideStringToString(ws, codepage);
      if (StringToWideString(WideStringToString(ws, codepage), codepage) != ws)
      { // failed to decode
        data = encodeCharSTD(ch);
        if (!data.empty() && dynamic)
          *dynamic = true;
      }
      ret.append(data);
    }
  }
  return ret;
}
std::string DynamicShiftJISCodecPrivate::encodeCharSTD(wchar_t ch)
{
  std::string ret;
  size_t i = text.find(ch);
  if (i == std::wstring::npos)
  {
    if (isFull())
      return ret;
    i = text.size();
    text.push_back(ch);
  }
  if (i < 31 * (4 * 16 + 4 - 1 - minimumSecondByte))
  {
    int v1 = i / (4 * 16 + 4 - 1 - minimumSecondByte) + 0x81,
        v2 = i % (4 * 16 + 4 - 1 - minimumSecondByte) + 1 + minimumSecondByte;
    if (v2 == 0x40)
      v2 = 0x7f;
    else if (v2 >= 0x41)
      v2 += 0xfd - 0x41;
    ret.push_back(v1);
    ret.push_back(v2);
    return ret;
  }
  i -= 31 * (4 * 16 + 4 - 1 - minimumSecondByte);
  if (i < 16 * (4 * 16 + 4 - 1 - minimumSecondByte))
  {
    int v1 = i / (4 * 16 + 4 - 1 - minimumSecondByte) + 0xe0,
        v2 = i % (4 * 16 + 4 - 1 - minimumSecondByte) + 1 + minimumSecondByte;
    if (v2 == 0x40)
      v2 = 0x7f;
    else if (v2 >= 0x41)
      v2 += 0xfd - 0x41;
    ret.push_back(v1);
    ret.push_back(v2);
    return ret;
  }
  i -= 16 * (4 * 16 + 4 - 1 - minimumSecondByte);
  if (i < 256 - 1 - minimumSecondByte)
  {
    int v1 = 0x80,
        v2 = i % (256 - 1 - minimumSecondByte) + 1 + minimumSecondByte;
    ret.push_back(v1);
    ret.push_back(v2);
    return ret;
  }
  i -= 256 - 1 - minimumSecondByte;
  if (i < 256 - 1 - minimumSecondByte)
  {
    int v1 = 0xa0,
        v2 = i % (256 - 1 - minimumSecondByte) + 1 + minimumSecondByte;
    ret.push_back(v1);
    ret.push_back(v2);
    return ret;
  }
  i -= 256 - 1 - minimumSecondByte;
  if (i < 16 * (256 - 1 - minimumSecondByte))
  {
    int v1 = i / (256 - 1 - minimumSecondByte) + 0xf0,
        v2 = i % (256 - 1 - minimumSecondByte) + 1 + minimumSecondByte;
    ret.push_back(v1);
    ret.push_back(v2);
    return ret;
  }
  // This return should be unreachable
  return ret;
}
// Decode

std::wstring DynamicShiftJISCodecPrivate::decode(const char *data, size_t length, bool *dynamic) const
{
  std::wstring ret;
  for (size_t i = 0; i < length; i++)
  {
    UINT8 ch = (UINT8)data[i];
    if (ch <= 127)
      ret.push_back(ch);
    else if (ch >= 0xa1 && ch <= 0xdf) // size == 1
      ret.append(StringToWideString(std::string_view(data + 1, 1), codepage).value());
    else
    {
      if (i + 1 == length) // no enough character
        return ret;
      UINT8 ch2 = (UINT8)data[++i];
      if ((ch >= 0x81 && ch <= 0x9f || ch >= 0xe0 && ch <= 0xef) && (ch2 != 0x7f && ch2 >= 0x40 && ch2 <= 0xfc))
        ret.append(StringToWideString(std::string_view(data + i - 1, 2), codepage).value());
      else if (wchar_t c = decodeChar(ch, ch2))
      {
        ret.push_back(c);
        if (dynamic)
          *dynamic = true;
      }
      else
        ret.push_back(ch + (wchar_t(ch2) << 8)); // preserve the original character
    }
  }
  return ret;
}
wchar_t DynamicShiftJISCodecPrivate::decodeChar(UINT8 ch1, UINT8 ch2) const
{
  if (text.empty())
    return 0;
  if (minimumSecondByte && ch2 < minimumSecondByte)
    return 0;
  size_t i = std::wstring::npos;
  if (ch1 >= 0x81 && ch1 <= 0x9f)
  {
    if (ch2 == 0x7f)
      ch2 = 0x40;
    else if (ch2 >= 0xfd)
      ch2 += 0x41 - 0xfd;
    i = (ch1 - 0x81) * (4 * 16 + 4 - 1 - minimumSecondByte) + ch2 - 1 - minimumSecondByte;
  }
  else if (ch1 >= 0xe0 && ch1 <= 0xef)
  {
    if (ch2 == 0x7f)
      ch2 = 0x40;
    else if (ch2 >= 0xfd)
      ch2 += 0x41 - 0xfd;
    i = (ch1 - 0xe0) * (4 * 16 + 4 - 1 - minimumSecondByte) + ch2 - 1 - minimumSecondByte + 31 * (4 * 16 + 4 - 1 - minimumSecondByte);
  }
  else if (ch1 == 0x80)
    i = ch2 - 1 - minimumSecondByte + 47 * (4 * 16 + 4 - 1 - minimumSecondByte);
  else if (ch1 == 0xa0)
    i = ch2 - 1 - minimumSecondByte + 47 * (4 * 16 + 4 - 1 - minimumSecondByte) + (256 - 1 - minimumSecondByte);
  else if (ch1 >= 0xf0 && ch1 <= 0xff) // 0xff is skipped
    i = (ch1 - 0xf0) * (256 - 1 - minimumSecondByte) + ch2 - 1 - minimumSecondByte + 47 * (4 * 16 + 4 - 1 - minimumSecondByte) + (256 - 1 - minimumSecondByte) * 2;
  if (i != std::wstring::npos && i < text.size())
    return text[i];
  return 0;
}

/** Public class */

DynamicShiftJISCodec::DynamicShiftJISCodec(UINT codec) : d_(new D(codec)) {}

DynamicShiftJISCodec::~DynamicShiftJISCodec() { delete d_; }

int DynamicShiftJISCodec::capacity() const { return d_->capacity(); }

int DynamicShiftJISCodec::size() const { return d_->text.size(); }

bool DynamicShiftJISCodec::isEmpty() const { return d_->text.empty(); }

bool DynamicShiftJISCodec::isFull() const { return d_->isFull(); }

void DynamicShiftJISCodec::clear() { d_->text.clear(); }

int DynamicShiftJISCodec::minimumSecondByte() const { return d_->minimumSecondByte; }

void DynamicShiftJISCodec::setMinimumSecondByte(int v) { d_->minimumSecondByte = v; }

std::string DynamicShiftJISCodec::encodeSTD(const std::wstring &text, bool *dynamic) const
{
  if (dynamic)
    *dynamic = false;
  if (!d_->codepage)
    return WideStringToString(text, GetACP());
  return d_->encodeSTD(reinterpret_cast<const wchar_t *>(text.c_str()), text.size(), dynamic);
}
std::wstring DynamicShiftJISCodec::decode(const std::string &data, bool *dynamic) const
{
  if (dynamic)
    *dynamic = false;
  if (!d_->codepage)
    return (StringToWideString(data, CP_ACP).value());
  if (d_->text.empty())
    return (StringToWideString(data, d_->codepage).value());
  return d_->decode(data.c_str(), data.size(), dynamic);
}

// EOF
