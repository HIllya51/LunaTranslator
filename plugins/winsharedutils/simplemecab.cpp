
#pragma execution_character_set("utf-8")
#include <windows.h>
#include <iostream>
#include <fstream>
#include <vector>
#include "define.h"
#include "cinterface.h"
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
    std::vector<std::string> vargv = {"fugashi", "-C", "-r", "nul", "-d", utf8path, "-Owakati"};

    auto argv = vecstr2c(vargv);
    auto trigger = _mecab_new(vargv.size(), argv);
    freestringlist(argv, vargv.size());
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
bool mecab_parse(void *trigger, char *utf8string, char ***surface, char ***features, int *num)
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

    std::vector<std::string> surfs;
    std::vector<std::string> featuresv;
    while (node->next)
    {
        node = node->next;
        if (node->stat == 3)
        {
            break;
        }
        std::string surf = node->surface;
        surf = surf.substr(0, node->length);
        surfs.emplace_back(surf);
        featuresv.emplace_back(node->feature);
    }
    *surface = vecstr2c(surfs);
    *features = vecstr2c(featuresv);
    *num = surfs.size();
    return true;
}