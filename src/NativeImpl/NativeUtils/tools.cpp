
#include <mecab.h>
#include <rapidfuzz/distance.hpp>
#include <aes.hpp>
#include <md4c-html.h>

DECLARE_API size_t levenshtein_distance(size_t len1, const wchar_t *string1,
                                        size_t len2, const wchar_t *string2)
{
    return rapidfuzz::levenshtein_distance(std::wstring_view(string1, len1), std::wstring_view(string2, len2));
}
DECLARE_API double levenshtein_normalized_similarity(size_t len1, const wchar_t *string1,
                                                     size_t len2, const wchar_t *string2)
{
    return rapidfuzz::levenshtein_normalized_similarity(std::wstring_view(string1, len1), std::wstring_view(string2, len2));
}

DECLARE_API MeCab::Tagger *mecab_init(char *utf8path)
{
    char argv_0[] = "fugashi";
    char argv_1[] = "-C";
    char argv_2[] = "-r";
#if defined(_WIN32)
    char argv_3[] = "nul";
#else
    char argv_3[] = "/dev/null";
#endif
    char argv_4[] = "-d";
    char argv_5[] = "-Owakati";
    char *argv[] = {argv_0, argv_1, argv_2, argv_3, argv_4, utf8path, argv_5};
    MeCab::Tagger *tagger = MeCab::Tagger::create(std::size(argv), argv);
    if (!tagger)
    {
        return nullptr;
    }
    return tagger;
}
DECLARE_API void mecab_end(MeCab::Tagger *tagger)
{
    if (!tagger)
        return;
    delete tagger;
}
static std::mutex parseToNodelock;
DECLARE_API bool mecab_parse(MeCab::Tagger *tagger, char *utf8string, void (*callback)(const char *, const char *))
{
    if (!tagger)
        return false;

    std::string cstr = utf8string;
    const MeCab::Node *node = nullptr;
    {
        std::scoped_lock _(parseToNodelock);
        node = tagger->parseToNode(cstr.c_str());
    }
    if (!node)
        return false;
    while (node->next)
    {
        node = node->next;
        if (node->stat == MECAB_EOS_NODE)
            break;
        std::string surf = std::string(node->surface, node->length);
        callback(surf.c_str(), node->feature);
    }
    return true;
}

DECLARE_API const char *mecab_dictionary_codec(MeCab::Tagger *tagger)
{
    if (!tagger)
        return nullptr;
    return tagger->dictionary_info()->charset;
}


DECLARE_API void AES_decrypt(uint8_t *key, uint8_t *iv, uint8_t *ptr, size_t size)
{
    AES_ctx ctx;
    AES_init_ctx_iv(&ctx, key, iv);
    AES_CBC_decrypt_buffer(&ctx, ptr, size);
}

static void
process_output(const MD_CHAR *text, MD_SIZE size, void *userdata)
{
    reinterpret_cast<std::string *>(userdata)->append(std::string_view(text, size));
}

DECLARE_API void Markdown2Html(const char *str, void (*cb)(const char *))
{
    std::string output;
    md_html(str, strlen(str), process_output, &output, MD_DIALECT_GITHUB, 0);
    cb(output.c_str());
}

// 自然排序比较（Windows 上转发 Shlwapi 的 StrCmpLogicalW）：
// 数字段（含全角数字）按数值比较；数值相等时前导零多者排前；
// 其余字符大小写不敏感（ASCII 与全角各自内部折叠，跨字形不折叠）。
static inline bool _nat_isdigit(wchar_t c)
{
    return (c >= L'0' && c <= L'9') || (c >= 0xFF10 && c <= 0xFF19);
}
static inline wchar_t _nat_digit(wchar_t c)
{
    if (c >= 0xFF10)
        return wchar_t(c - 0xFF10 + L'0');
    return c;
}
static inline wchar_t _nat_tolower(wchar_t c)
{
    if (c >= L'A' && c <= L'Z')
        return wchar_t(c - L'A' + L'a');
    if (c >= 0xFF21 && c <= 0xFF3A) // 全角 Ａ-Ｚ → ａ-ｚ
        return wchar_t(c - 0xFF21 + 0xFF41);
    return c;
}
DECLARE_API int strnatcmp(const wchar_t *a, const wchar_t *b)
{
#if defined(_WIN32)
    return StrCmpLogicalW(a, b);
#else
    size_t ia = 0, ib = 0;
    while (a[ia] && b[ib])
    {
        wchar_t ca = a[ia], cb = b[ib];
        if (_nat_isdigit(ca) && _nat_isdigit(cb))
        {
            size_t ea = ia, eb = ib;
            while (_nat_isdigit(a[ea]))
                ea++;
            while (_nat_isdigit(b[eb]))
                eb++;
            // 去前导零后先比位数再逐位比（数值比较，不经大数转换）
            size_t sa = ia, sb = ib;
            while (sa < ea && _nat_digit(a[sa]) == L'0')
                sa++;
            while (sb < eb && _nat_digit(b[sb]) == L'0')
                sb++;
            size_t la = ea - sa, lb = eb - sb;
            if (la != lb)
                return la < lb ? -1 : 1;
            for (size_t k = 0; k < la; k++)
            {
                wchar_t x = _nat_digit(a[sa + k]), y = _nat_digit(b[sb + k]);
                if (x != y)
                    return x < y ? -1 : 1;
            }
            // 数值相等：前导零多（原数字段更长）者排前，与 StrCmpLogicalW 一致
            if ((ea - ia) != (eb - ib))
                return (ea - ia) > (eb - ib) ? -1 : 1;
            ia = ea;
            ib = eb;
        }
        else
        {
            wchar_t x = _nat_tolower(ca), y = _nat_tolower(cb);
            if (x != y)
                return x < y ? -1 : 1;
            ia++;
            ib++;
        }
    }
    if (a[ia])
        return 1;
    if (b[ib])
        return -1;
    return 0;
#endif
}
