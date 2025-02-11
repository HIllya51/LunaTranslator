#if 0
/**
 * DictionaryInfo structure
 */
struct mecab_dictionary_info_t
{
    /**
     * filename of dictionary
     * On Windows, filename is stored in UTF-8 encoding
     */
    const char *filename;

    /**
     * character set of the dictionary. e.g., "SHIFT-JIS", "UTF-8"
     */
    const char *charset;

    /**
     * How many words are registered in this dictionary.
     */
    unsigned int size;

    /**
     * dictionary type
     * this value should be MECAB_USR_DIC, MECAB_SYS_DIC, or MECAB_UNK_DIC.
     */
    int type;

    /**
     * left attributes size
     */
    unsigned int lsize;

    /**
     * right attributes size
     */
    unsigned int rsize;

    /**
     * version of this dictionary
     */
    unsigned short version;

    /**
     * pointer to the next dictionary info.
     */
    struct mecab_dictionary_info_t *next;
};

/**
 * Node structure
 */
struct mecab_node_t
{
    /**
     * pointer to the previous node.
     */
    struct mecab_node_t *prev;

    /**
     * pointer to the next node.
     */
    struct mecab_node_t *next;

    /**
     * pointer to the node which ends at the same position.
     */
    struct mecab_node_t *enext;

    /**
     * pointer to the node which starts at the same position.
     */
    struct mecab_node_t *bnext;

    /**
     * pointer to the right path.
     * this value is NULL if MECAB_ONE_BEST mode.
     */
    struct mecab_path_t *rpath;

    /**
     * pointer to the right path.
     * this value is NULL if MECAB_ONE_BEST mode.
     */
    struct mecab_path_t *lpath;

    /**
     * surface string.
     * this value is not 0 terminated.
     * You can get the length with length/rlength members.
     */
    const char *surface;

    /**
     * feature string
     */
    const char *feature;

    /**
     * unique node id
     */
    unsigned int id;

    /**
     * length of the surface form.
     */
    unsigned short length;

    /**
     * length of the surface form including white space before the morph.
     */
    unsigned short rlength;

    /**
     * right attribute id
     */
    unsigned short rcAttr;

    /**
     * left attribute id
     */
    unsigned short lcAttr;

    /**
     * unique part of speech id. This value is defined in "pos.def" file.
     */
    unsigned short posid;

    /**
     * character type
     */
    unsigned char char_type;

    /**
     * status of this model.
     * This value is MECAB_NOR_NODE, MECAB_UNK_NODE, MECAB_BOS_NODE, MECAB_EOS_NODE, or MECAB_EON_NODE.
     */
    unsigned char stat;

    /**
     * set 1 if this node is best node.
     */
    unsigned char isbest;

    /**
     * forward accumulative log summation.
     * This value is only available when MECAB_MARGINAL_PROB is passed.
     */
    float alpha;

    /**
     * backward accumulative log summation.
     * This value is only available when MECAB_MARGINAL_PROB is passed.
     */
    float beta;

    /**
     * marginal probability.
     * This value is only available when MECAB_MARGINAL_PROB is passed.
     */
    float prob;

    /**
     * word cost.
     */
    short wcost;

    /**
     * best accumulative cost from bos node to this node.
     */
    long cost;
};

/**
 * Parameters for MeCab::Node::stat
 */
enum
{
    /**
     * Normal node defined in the dictionary.
     */
    MECAB_NOR_NODE = 0,
    /**
     * Unknown node not defined in the dictionary.
     */
    MECAB_UNK_NODE = 1,
    /**
     * Virtual node representing a beginning of the sentence.
     */
    MECAB_BOS_NODE = 2,
    /**
     * Virtual node representing a end of the sentence.
     */
    MECAB_EOS_NODE = 3,

    /**
     * Virtual node representing a end of the N-best enumeration.
     */
    MECAB_EON_NODE = 4
};

typedef struct mecab_t mecab_t;
mecab_t *(*mecab_new)(int argc, char **argv);
const mecab_node_t *(*mecab_sparse_tonode)(mecab_t *mecab, const char *);
void (*mecab_destroy)(mecab_t *mecab);
const mecab_dictionary_info_t *(*mecab_dictionary_info)(mecab_t *mecab);
HMODULE mecablib;
DECLARE_API mecab_t *mecab_init(char *utf8path, wchar_t *mepath)
{
    mecablib = LoadLibraryW(mepath);
    mecab_new = (decltype(mecab_new))GetProcAddress(mecablib, "mecab_new");
    char *argv[] = {"fugashi", "-C", "-r", "nul", "-d", utf8path, "-Owakati"};
    return mecab_new(ARRAYSIZE(argv), argv);
}
DECLARE_API void mecab_end(mecab_t *tagger)
{
    if (!tagger)
        return;
    mecab_destroy = (decltype(mecab_destroy))GetProcAddress(mecablib, "mecab_destroy");
    mecab_destroy(tagger);
}

DECLARE_API bool mecab_parse(mecab_t *tagger, char *utf8string, void (*callback)(const char *, const char *))
{
    if (!tagger)
        return false;
    mecab_sparse_tonode = (decltype(mecab_sparse_tonode))GetProcAddress(mecablib, "mecab_sparse_tonode");

    std::string cstr = utf8string;
    auto node = mecab_sparse_tonode((mecab_t *)tagger, cstr.c_str());

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

DECLARE_API const char *mecab_dictionary_codec(mecab_t *tagger)
{
    if (!tagger)
        return nullptr;
    mecab_dictionary_info = (decltype(mecab_dictionary_info))GetProcAddress(mecablib, "mecab_dictionary_info");
    return mecab_dictionary_info(tagger)->charset;
}
#endif
