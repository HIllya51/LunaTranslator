
void CharReplacer(char *str, size_t *size, char fr, char to);
void CharReplacer(wchar_t *str, size_t *size, wchar_t fr, wchar_t to);

void CharFilter(char *str, size_t *size, char ch);
void CharFilter(wchar_t *str, size_t *size, wchar_t ch);

void CharsFilter(char *str, size_t *size, const char *chars);
void CharsFilter(wchar_t *str, size_t *size, const wchar_t *chars);

void StringFilter(char *str, size_t *size, const char *remove, size_t removelen);
void StringFilter(wchar_t *str, size_t *size, const wchar_t *remove, size_t removelen);

void StringFilterBetween(char *str, size_t *size, const char *fr, size_t frlen, const char *to, size_t tolen);
void StringFilterBetween(wchar_t *str, size_t *size, const wchar_t *fr, size_t frlen, const wchar_t *to, size_t tolen);

void StringCharReplacer(char *str, size_t *size, const char *src, size_t srclen, char ch);
void StringCharReplacer(wchar_t *str, size_t *size, const wchar_t *src, size_t srclen, wchar_t ch);

void StringReplacer(char *str, size_t *size, const char *src, size_t srclen, const char *dst, size_t dstlen);
void StringReplacer(wchar_t *str, size_t *size, const wchar_t *src, size_t srclen, const wchar_t *dst, size_t dstlen);

bool NewLineCharFilterA(LPVOID data, size_t *size, HookParam *);
bool NewLineCharFilterW(LPVOID data, size_t *size, HookParam *);
bool NewLineStringFilterA(LPVOID data, size_t *size, HookParam *);
bool NewLineStringFilterW(LPVOID data, size_t *size, HookParam *);
bool NewLineCharToSpaceFilterA(LPVOID data, size_t *size, HookParam *);
bool NewLineCharToSpaceFilterW(LPVOID data, size_t *size, HookParam *);
bool IllegalCharsFilterA(LPVOID data, size_t *size, HookParam *);
bool IllegalCharsFilterW(LPVOID data, size_t *size, HookParam *);

bool all_ascii_Filter(LPVOID data, size_t *size, HookParam *);

