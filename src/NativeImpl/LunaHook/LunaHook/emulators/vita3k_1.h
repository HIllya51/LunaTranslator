
struct emfuncinfo
{
    uint64_t type;
    int offset;
    int padding;
    decltype(HookParam::text_fun) hookfunc;
    decltype(HookParam::filter_fun) filterfun;
    std::variant<const char *, std::vector<const char *>> _id;
};
extern void vita3k_load_functions(std::unordered_map<DWORD, emfuncinfo>&);