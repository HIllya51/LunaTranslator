#pragma once

inline size_t str_len(const char *s) { return strlen(s); }
inline size_t str_len(const wchar_t *s) { return wcslen(s); }

template <class CharT>
struct TextUnion
{
  enum
  {
    ShortTextCapacity = 0x10 / sizeof(CharT)
  };

  union
  {
    const CharT *text; // 0x0
    CharT chars[ShortTextCapacity];
  };
  size_t size, // 0x10
      capacity;

  bool isValid() const
  {
    if (size <= 0 || size > capacity)
      return false;
    const CharT *t = getText();
    return Engine::isAddressWritable(t, size) && str_len(t) == size;
  }

  const CharT *getText() const
  {
    return capacity < ShortTextCapacity ? chars : text;
  }

  std::basic_string_view<CharT> view() const
  {
    return std::basic_string_view<CharT>(getText(), size);
  }
  void setText(const CharT *_text, size_t _size)
  {
    if (_size < ShortTextCapacity)
      ::memcpy(chars, _text, (_size + 1) * sizeof(CharT));
    else
    {
      text = allocateString(std::basic_string_view<CharT>{_text, _size});
    }
    capacity = size = _size;
  }

  template <typename StringT, typename = std::enable_if_t<!std::is_pointer_v<StringT>>>
  void setText(const StringT &text)
  {
    setText(text.data(), text.size());
  }
};

using TextUnionA = TextUnion<char>;
using TextUnionW = TextUnion<wchar_t>;
// EOF
