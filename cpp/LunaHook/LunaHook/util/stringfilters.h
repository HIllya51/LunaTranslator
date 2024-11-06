
void CharReplacer(TextBuffer *buffer, char fr, char to);
void CharReplacer(TextBuffer *buffer, wchar_t fr, wchar_t to);

void CharFilter(TextBuffer *buffer, char ch);
void CharFilter(TextBuffer *buffer, wchar_t ch);

void CharsFilter(TextBuffer *buffer, const char *chars);
void CharsFilter(TextBuffer *buffer, const wchar_t *chars);

void StringFilter(TextBuffer *buffer, const char *remove, size_t removelen);
void StringFilter(TextBuffer *buffer, const wchar_t *remove, size_t removelen);

void StringFilterBetween(TextBuffer *buffer, const char *fr, size_t frlen, const char *to, size_t tolen);
void StringFilterBetween(TextBuffer *buffer, const wchar_t *fr, size_t frlen, const wchar_t *to, size_t tolen);

void StringCharReplacer(TextBuffer *buffer, const char *src, size_t srclen, char ch);
void StringCharReplacer(TextBuffer *buffer, const wchar_t *src, size_t srclen, wchar_t ch);

void StringReplacer(TextBuffer *buffer, const char *src, size_t srclen, const char *dst, size_t dstlen);
void StringReplacer(TextBuffer *buffer, const wchar_t *src, size_t srclen, const wchar_t *dst, size_t dstlen);

void NewLineCharToSpaceFilterA(TextBuffer *buffer, HookParam*);

void all_ascii_Filter(TextBuffer *buffer, HookParam*);

