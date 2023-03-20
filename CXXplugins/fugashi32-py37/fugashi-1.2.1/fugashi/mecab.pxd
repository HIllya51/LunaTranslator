cdef extern from "mecab.h":
    cdef struct mecab_dictionary_info_t:
        char *filename
        char *charset
        unsigned int size
        unsigned short version
        mecab_dictionary_info_t* next
        
    cdef struct mecab_node_t:
        mecab_node_t *prev
        mecab_node_t *next
        const char *surface
        const char *feature
        unsigned int id
        unsigned short length
        unsigned short rlength
        unsigned short posid
        unsigned char char_type
        unsigned char stat
    
    cdef struct mecab_model_t:
        pass

    cdef struct mecab_t:
        pass

    cdef mecab_t* mecab_new(int argc, char **argv)
    cdef mecab_model_t* mecab_model_new(int argc, char **argv)
    cdef const char* mecab_sparse_tostr2(mecab_t *mecab, const char *str, size_t len)
    cdef const mecab_node_t* mecab_sparse_tonode(mecab_t *mecab, const char *str)
    cdef const mecab_dictionary_info_t* mecab_dictionary_info(mecab_t *mecab)

    cdef char* mecab_nbest_sparse_tostr(mecab_t *mecab, size_t N, const char *str)
    cdef int mecab_nbest_init(mecab_t *mecab, const char *str) 
    cdef const char* mecab_strerror(mecab_t *mecab)

    cdef int mecab_dict_index(int argc, char**argv)

    cdef int mecab_nbest_init(mecab_t* mecab, const char* str)
    cdef const mecab_node_t* mecab_nbest_next_tonode(mecab_t* mecab)
