using version_t = std::tuple<WORD, WORD, WORD, WORD>;
std::optional<version_t> QueryVersion(const std::wstring& exe);
std::optional<std::wstring> SearchDllPath(const std::wstring &dll);