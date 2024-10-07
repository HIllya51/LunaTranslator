
#include "define.h"
struct mecab_node_t
{
    struct mecab_node_t *prev;
    struct mecab_node_t *next;
    struct mecab_node_t *enext;
    struct mecab_node_t *bnext;
    struct mecab_path_t *rpath;
    struct mecab_path_t *lpath;
    const char *surface;
    const char *feature;
    unsigned int id;
    unsigned short length;
    unsigned short rlength;
    unsigned short rcAttr;
    unsigned short lcAttr;
    unsigned short posid;
    unsigned char char_type;
    unsigned char stat;
    unsigned char isbest;
    float alpha;
    float beta;
    float prob;
    short wcost;
    long cost;
};

typedef struct mecab_t mecab_t;
typedef mecab_t *(*mecab_new)(int argc, char **argv);
typedef mecab_node_t *(*mecab_sparse_tonode)(mecab_t *mecab, const char *);
typedef void (*mecab_destroy)(mecab_t *mecab);
HMODULE mecablib;
void *mecab_init(char *utf8path, wchar_t *mepath)
{
    mecablib = LoadLibraryW(mepath);
    if (mecablib == 0)
        return 0;
    auto _mecab_new = (mecab_new)GetProcAddress(mecablib, "mecab_new");
    if (_mecab_new == 0)
        return 0;
    char *argv[] = {"fugashi", "-C", "-r", "nul", "-d", utf8path, "-Owakati"};
    auto trigger = _mecab_new(ARRAYSIZE(argv), argv);
    return trigger;
}
void mecab_end(void *trigger)
{
    if (trigger == 0)
        return;
    if (mecablib == 0)
        return;
    auto _mecab_destroy = (mecab_destroy)GetProcAddress(mecablib, "mecab_destroy");
    if (_mecab_destroy == 0)
        return;
    mecab_destroy((mecab_t *)trigger);
}

bool mecab_parse(void *trigger, char *utf8string, void (*callback)(const char *, const char *))
{
    if (trigger == 0)
        return false;
    if (mecablib == 0)
        return false;
    auto _mecab_sparse_tonode = (mecab_sparse_tonode)GetProcAddress(mecablib, "mecab_sparse_tonode");
    if (_mecab_sparse_tonode == 0)
        return false;

    std::string cstr = utf8string;
    auto node = _mecab_sparse_tonode((mecab_t *)trigger, cstr.c_str());

    while (node->next)
    {
        node = node->next;
        if (node->stat == 3)
        {
            break;
        }
        std::string surf = std::string(node->surface, node->length);
        callback(surf.c_str(), node->feature);
    }
    return true;
}