#ifndef QTDYNCODEC_DYNSJIS_H
#define QTDYNCODEC_DYNSJIS_H

#define SK_DECLARE_PRIVATE(_class) \
  friend class _class;             \
  typedef _class D;                \
  D *const d_;

#define SK_DISABLE_COPY(_class) \
  _class(const _class &);       \
  _class &operator=(const _class &);

#define SK_CLASS(_self) \
  typedef _self Self;   \
  Self *self() const { return const_cast<Self *>(this); }

class DynamicShiftJISCodecPrivate;
class DynamicShiftJISCodec
{
  SK_CLASS(DynamicShiftJISCodec)
  SK_DISABLE_COPY(DynamicShiftJISCodec)
  SK_DECLARE_PRIVATE(DynamicShiftJISCodecPrivate)

  // - Construction -
public:
  explicit DynamicShiftJISCodec(UINT codepag);
  ~DynamicShiftJISCodec();

  int capacity() const; // maximum allowed number of characters

  // Minimum value for the second byte, must be larger than 0 and smaller than 0x40
  int minimumSecondByte() const;
  void setMinimumSecondByte(int v);

  ///  Return the number of current characters
  int size() const;
  bool isEmpty() const;
  bool isFull() const;

  // Clear cached codec
  void clear();

  /**
   *  @param  text
   *  @param* dynamic  whether there are unencodable character
   *  @return  data
   */
  std::string encodeSTD(const std::wstring &text, bool *dynamic = nullptr) const;

  /**
   *  @param  data
   *  @param* dynamic  whether there are undecodable character
   *  @return  text
   */
  std::wstring decode(const std::string &data, bool *dynamic = nullptr) const;
};

#endif // QTDYNCODEC_DYNSJIS_H
