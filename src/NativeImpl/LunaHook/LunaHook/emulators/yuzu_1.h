
struct emfuncinfo
{
    uint64_t type;
    int offset;
    int padding;
    decltype(HookParam::text_fun) hookfunc;
    decltype(HookParam::filter_fun) filterfun;
    std::variant<uint64_t, std::vector<uint64_t>> _id;
    const char *_version;
};
extern void yuzu_load_functions(std::unordered_map<DWORD, emfuncinfo>&);