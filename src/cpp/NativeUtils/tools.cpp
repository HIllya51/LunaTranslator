
#include <mecab.h>
#include <rapidfuzz/distance.hpp>
#include <aes.hpp>
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
    char *argv[] = {"fugashi", "-C", "-r", "nul", "-d", utf8path, "-Owakati"};
    MeCab::Tagger *tagger = MeCab::Tagger::create(ARRAYSIZE(argv), argv);
    if (!tagger)
    {
        return 0;
    }
    return tagger;
}
DECLARE_API void mecab_end(MeCab::Tagger *tagger)
{
    if (!tagger)
        return;
    delete tagger;
}

DECLARE_API bool mecab_parse(MeCab::Tagger *tagger, char *utf8string, void (*callback)(const char *, const char *))
{
    if (!tagger)
        return false;

    std::string cstr = utf8string;
    auto node = tagger->parseToNode(cstr.c_str());

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

DECLARE_API LPWSTR str_alloc(LPCWSTR str)
{
    // 从python向c++传递字符串时，需要转成非托管字符串，否则会内存泄漏
    auto _ = new WCHAR[wcslen(str) + 1];
    wcscpy(_, str);
    return _;
}

DECLARE_API void AES_decrypt(uint8_t *key, uint8_t *iv, uint8_t *ptr, size_t size)
{
    AES_ctx ctx;
    AES_init_ctx_iv(&ctx, key, iv);
    AES_CBC_decrypt_buffer(&ctx, ptr, size);
}

// #include <maddy/parser.h>

// DECLARE_API void Markdown2Html(const char *str, void (*cb)(const char *))
// {
//     std::string s = str;
//     std::istringstream iss(s);
//     maddy::Parser p{};
//     auto result = p.Parse(iss);
//     cb(result.c_str());
// }
#include <md4c-html.h>

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